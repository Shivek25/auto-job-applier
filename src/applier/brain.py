# src/applier/brain.py
import json
import logging
import asyncio
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional
from playwright.async_api import Page, Frame

from src.ai.llm_client import LLMClient
from src.ai.prompts import BROWSER_BRAIN_DIAGNOSTIC_PROMPT
from src.resume.models import MasterProfile

logger = logging.getLogger(__name__)

class BrowserBrain:
    def __init__(
        self,
        llm_client: LLMClient,
        master_profile: Optional[MasterProfile] = None,
        memory_path: str = "storage/brain_memory.json"
    ):
        self.llm = llm_client
        self.master_profile = master_profile
        self.memory_path = Path(memory_path)
        self.memory = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        if self.memory_path.exists():
            try:
                with open(self.memory_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load brain memory from {self.memory_path}: {e}")
        return {"domain_rules": {}, "healed_patterns": []}

    def _save_memory(self):
        try:
            self.memory_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save brain memory to {self.memory_path}: {e}")

    def get_learned_rule(self, domain: str, obstacle_type: str) -> Optional[Dict[str, Any]]:
        clean_domain = domain.lower().replace("www.", "")
        domain_rules = self.memory.get("domain_rules", {})
        return domain_rules.get(clean_domain, {}).get(obstacle_type)

    def save_learned_rule(self, domain: str, obstacle_type: str, remedy: Dict[str, Any]):
        clean_domain = domain.lower().replace("www.", "")
        if "domain_rules" not in self.memory:
            self.memory["domain_rules"] = {}
        if clean_domain not in self.memory["domain_rules"]:
            self.memory["domain_rules"][clean_domain] = {}
        self.memory["domain_rules"][clean_domain][obstacle_type] = remedy
        self._save_memory()

    async def inspect_page_state(self, page: Page) -> Dict[str, Any]:
        url = page.url
        domain = urlparse(url).netloc
        try:
            title = await page.title()
        except Exception:
            title = ""

        # Extract normalized state across main page and frames
        state = {
            "url": url,
            "domain": domain,
            "title": title,
            "dialogs": [],
            "interactive_elements": [],
            "validation_errors": []
        }

        try:
            eval_data = await page.evaluate("""() => {
                // 1. Detect open dialogs/modals
                const dialogNodes = Array.from(document.querySelectorAll(
                    'dialog, [role="dialog"], [role="alertdialog"], .jobs-easy-apply-modal, [data-test-modal]'
                )).filter(d => d.offsetParent !== null || window.getComputedStyle(d).display !== 'none');
                
                const dialogs = dialogNodes.map(d => (d.innerText || '').substring(0, 250).trim()).filter(Boolean);

                // Scope to the active application modal when one is open
                const scope = dialogNodes.find(d => d.querySelector('input, select, textarea, button')) || document;

                // 2. Detect visible validation errors (ignore toast notifications such as 'job alert created')
                const toastRe = /job alert|alert was created|manage alerts|saved|copied/i;
                const errorNodes = Array.from(scope.querySelectorAll(
                    '.artdeco-inline-feedback--error, [role="alert"], .form-error, .error, span.error-message'
                )).filter(e => e.offsetParent !== null && !e.closest('.artdeco-toasts, .artdeco-toast-item, [data-test-artdeco-toast]'));
                
                const validationErrors = errorNodes.map(e => (e.innerText || '').trim()).filter(t => t && !toastRe.test(t));

                // 3. Extract visible interactive elements and stamp them so clicks hit the exact same node
                document.querySelectorAll('[data-brain-idx]').forEach(el => el.removeAttribute('data-brain-idx'));
                const interactiveNodes = Array.from(scope.querySelectorAll(
                    'button, input, select, textarea, [role="button"], [role="radio"], [role="checkbox"]'
                )).filter(el => {
                    if (el.type === 'hidden') return false;
                    const style = window.getComputedStyle(el);
                    return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
                });

                const elements = interactiveNodes.slice(0, 40).map((el, idx) => { el.setAttribute('data-brain-idx', String(idx)); return {
                    index: idx,
                    tag: el.tagName.toLowerCase(),
                    type: el.getAttribute('type') || el.type || '',
                    text: (el.innerText || el.value || '').trim().substring(0, 80),
                    aria_label: el.getAttribute('aria-label') || '',
                    name: el.getAttribute('name') || '',
                    id: el.id || '',
                    placeholder: el.getAttribute('placeholder') || '',
                    is_disabled: el.disabled || el.getAttribute('aria-disabled') === 'true',
                    is_checked: el.checked || el.getAttribute('aria-checked') === 'true',
                    required: el.required || el.getAttribute('aria-required') === 'true'
                }; });

                return { dialogs, validationErrors, elements };
            }""")

            state["dialogs"] = eval_data.get("dialogs", [])
            state["validation_errors"] = eval_data.get("validationErrors", [])
            state["interactive_elements"] = eval_data.get("elements", [])
        except Exception as e:
            logger.debug(f"Perception note: {e}")

        return state

    async def diagnose_roadblock(
        self,
        page_state: Dict[str, Any],
        goal: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        current_url = page_state.get("url", "")
        domain = page_state.get("domain", "")
        expected_url = context.get("job_url", "")

        # Fast heuristic diagnosis: URL drift (e.g. navigated away from target job)
        if expected_url and "jobs/view" in expected_url and "jobs/view" not in current_url:
            cached_rule = self.get_learned_rule(domain, "URL_DRIFT")
            if cached_rule:
                return {
                    "diagnosis": "Cached remedy: URL drifted away from job view",
                    "obstacle_type": "URL_DRIFT",
                    "recommended_strategy": cached_rule.get("strategy", "NAVIGATE_BACK"),
                    "action_details": cached_rule.get("action_details", {"action": "go_back"}),
                    "learned_rule": "Navigate back on URL drift"
                }
            return {
                "diagnosis": f"Browser navigated away from target job URL ({current_url})",
                "obstacle_type": "URL_DRIFT",
                "recommended_strategy": "NAVIGATE_BACK",
                "action_details": {"action": "go_back"},
                "learned_rule": "Navigate back when URL drifts from job view"
            }

        # Format elements and dialogs for LLM prompt
        elements_summary = json.dumps(page_state.get("interactive_elements", [])[:20], indent=2)
        dialogs_summary = json.dumps(page_state.get("dialogs", []), indent=2)
        errors_summary = json.dumps(page_state.get("validation_errors", []), indent=2)
        
        candidate_summary = ""
        if self.master_profile:
            candidate_summary = (
                f"Name: {self.master_profile.personal_info.name}, "
                f"Email: {self.master_profile.personal_info.email}, "
                f"Location: {self.master_profile.personal_info.location}, "
                f"Top Skills: {', '.join(self.master_profile.skills.languages[:4])}"
            )

        prompt = (
            BROWSER_BRAIN_DIAGNOSTIC_PROMPT
            .replace("{goal}", goal)
            .replace("{expected_context}", json.dumps(context))
            .replace("{current_url}", current_url)
            .replace("{page_title}", page_state.get("title", ""))
            .replace("{active_dialogs}", dialogs_summary)
            .replace("{error_messages}", errors_summary)
            .replace("{interactive_elements}", elements_summary)
            .replace("{candidate_summary}", candidate_summary)
        )

        try:
            diagnosis_res = self.llm.generate_json(prompt)
            return diagnosis_res
        except Exception as e:
            logger.warning(f"LLM diagnostic fallback ({e})")
            # Default fallback recovery
            return {
                "diagnosis": f"Automated recovery fallback: {e}",
                "obstacle_type": "UNKNOWN",
                "recommended_strategy": "RETRY",
                "action_details": {"action": "wait"},
                "learned_rule": ""
            }

    async def _is_forbidden_click(self, el) -> bool:
        """Never let the brain click job alert, follow, save, or share controls."""
        try:
            desc = await el.evaluate(
                "(e) => ((e.innerText || '') + ' ' + (e.getAttribute('aria-label') || '') + ' ' + (e.getAttribute('role') || '')).toLowerCase()"
            )
        except Exception:
            return False
        forbidden = ["alert", "follow", "save", "share", "switch", "premium", "manage alerts"]
        if any(f in desc for f in forbidden):
            logger.info(f"🧠 Brain refused to click forbidden control: '{desc.strip()[:60]}'")
            return True
        return False

    async def execute_recovery(self, page: Page, diagnosis: Dict[str, Any]) -> bool:
        strategy = diagnosis.get("recommended_strategy", "RETRY")
        details = diagnosis.get("action_details", {})
        action = details.get("action", "")

        logger.info(f"🧠 Brain executing recovery: strategy={strategy}, action={action}")

        try:
            if strategy == "NAVIGATE_BACK" or action == "go_back":
                await page.go_back()
                await asyncio.sleep(2)
                return True

            if strategy == "DISMISS_OVERLAY" or action == "dismiss":
                sel = details.get("element_selector")
                if sel:
                    dismiss_btn = await page.query_selector(sel)
                    if dismiss_btn:
                        await dismiss_btn.click()
                        await asyncio.sleep(1)
                        return True
                # Fallback overlay dismiss
                dismiss_btn = await page.query_selector(
                    "button[aria-label*='Dismiss'], button[aria-label*='Close'], button:has-text('Dismiss'), button:has-text('Close')"
                )
                if dismiss_btn:
                    await dismiss_btn.click()
                    await asyncio.sleep(1)
                    return True
                await page.keyboard.press("Escape")
                await asyncio.sleep(1)
                return True

            if strategy == "CLICK_ELEMENT" or action == "click":
                sel = details.get("element_selector")
                idx = details.get("element_index")
                if sel:
                    el = await page.query_selector(sel)
                    if el and not await self._is_forbidden_click(el):
                        await el.scroll_into_view_if_needed()
                        await el.click()
                        await asyncio.sleep(1)
                        return True
                if idx is not None:
                    el = await page.query_selector(f"[data-brain-idx='{int(idx)}']")
                    if el and not await self._is_forbidden_click(el):
                        await el.click()
                        await asyncio.sleep(1)
                        return True

            if strategy == "ANSWER_FIELD" or action == "answer":
                val = details.get("value_to_fill", "")
                idx = details.get("element_index")
                sel = details.get("element_selector")
                if sel and val:
                    field = await page.query_selector(sel)
                    if field:
                        await field.fill(str(val))
                        await asyncio.sleep(0.5)
                        return True
                if idx is not None and val:
                    filled = await page.evaluate("""({ targetIndex, textValue }) => {
                        const target = document.querySelector(`[data-brain-idx="${targetIndex}"]`);
                        if (target && ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName)) {
                            if (target.type === 'radio' || target.type === 'checkbox') {
                                target.checked = true;
                                target.dispatchEvent(new Event('input', { bubbles: true }));
                                target.dispatchEvent(new Event('change', { bubbles: true }));
                            } else {
                                target.value = textValue;
                                target.dispatchEvent(new Event('input', { bubbles: true }));
                                target.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                            return true;
                        }
                        return false;
                    }""", {"targetIndex": idx, "textValue": val})
                    if filled:
                        await asyncio.sleep(0.5)
                        return True

            if strategy == "SCROLL_INTO_VIEW" or action == "scroll":
                await page.evaluate("() => window.scrollBy(0, 300)")
                await asyncio.sleep(1)
                return True

            if strategy == "RETRY":
                await asyncio.sleep(2)
                return True

        except Exception as e:
            logger.warning(f"Recovery execution exception: {e}")
            return False

        return False

    async def diagnose_and_heal(
        self,
        page: Page,
        goal: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        ctx = context or {}
        max_attempts = 2

        for attempt in range(1, max_attempts + 1):
            logger.info(f"🧠 [Brain] Diagnosing roadblock (Attempt {attempt}/{max_attempts}) for goal: '{goal}'...")
            state = await self.inspect_page_state(page)
            diagnosis = await self.diagnose_roadblock(state, goal, ctx)

            logger.info(
                f"🧠 [Brain] Diagnosis: {diagnosis.get('diagnosis', 'Unknown')} "
                f"| Strategy: {diagnosis.get('recommended_strategy', 'RETRY')}"
            )

            success = await self.execute_recovery(page, diagnosis)
            if success:
                # Cache learned rule if provided
                learned_rule = diagnosis.get("learned_rule")
                obstacle_type = diagnosis.get("obstacle_type", "GENERIC")
                domain = state.get("domain", "")
                if learned_rule and domain:
                    self.save_learned_rule(domain, obstacle_type, {
                        "strategy": diagnosis.get("recommended_strategy"),
                        "action_details": diagnosis.get("action_details"),
                        "rule": learned_rule
                    })
                logger.info(f"✅ [Brain] Recovery action executed successfully on attempt {attempt}.")
                return True

            await asyncio.sleep(1)

        logger.warning(f"⚠️ [Brain] Could not self-heal blocker for goal: '{goal}'.")
        return False
