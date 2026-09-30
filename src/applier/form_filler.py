# src/applier/form_filler.py
import logging
from typing import Dict, Any, List, Optional
from playwright.async_api import Page
from src.ai.llm_client import LLMClient
from src.ai.prompts import FORM_ANSWER_PROMPT
from src.resume.models import MasterProfile

logger = logging.getLogger(__name__)

class FormFiller:
    def __init__(self, llm_client: LLMClient, profile: MasterProfile):
        self.llm = llm_client
        self.profile = profile

    async def answer_question(self, question_text: str, field_type: str, options: Optional[List[str]] = None) -> Any:
        extra_options = f"Available options: {options}" if options else ""
        prompt = (
            FORM_ANSWER_PROMPT
            .replace("{profile_json}", self.profile.model_dump_json(indent=2))
            .replace("{question_text}", question_text)
            .replace("{field_type}", field_type)
            .replace("{extra_options}", extra_options)
        )
        res = self.llm.generate_json(prompt)
        return res.get("answer", "")

    async def fill_current_modal(self, page: Page):
        try:
            # Fill text/number inputs and textareas
            inputs = await page.query_selector_all("input[type='text'], input[type='number'], input[type='tel'], textarea")
            for inp in inputs:
                val = await inp.input_value()
                if not val:
                    # Attempt to find associated label
                    inp_id = await inp.get_attribute("id")
                    label_text = ""
                    if inp_id:
                        label_el = await page.query_selector(f"label[for='{inp_id}']")
                        if label_el:
                            label_text = await label_el.inner_text()
                    if not label_text:
                        label_text = (await inp.get_attribute("aria-label")) or (await inp.get_attribute("name")) or "field"
                    
                    # Direct autofill for obvious contact fields
                    lbl_lower = label_text.lower()
                    if "phone" in lbl_lower or "mobile" in lbl_lower:
                        await inp.fill(self.profile.personal_info.phone)
                    elif "email" in lbl_lower:
                        await inp.fill(self.profile.personal_info.email)
                    elif "first name" in lbl_lower:
                        await inp.fill(self.profile.personal_info.name.split()[0])
                    elif "last name" in lbl_lower:
                        parts = self.profile.personal_info.name.split()
                        await inp.fill(parts[-1] if len(parts) > 1 else "")
                    elif "linkedin" in lbl_lower and self.profile.personal_info.linkedin_url:
                        await inp.fill(self.profile.personal_info.linkedin_url)
                    elif "github" in lbl_lower and self.profile.personal_info.github_url:
                        await inp.fill(self.profile.personal_info.github_url)
                    else:
                        ans = await self.answer_question(label_text, "text")
                        await inp.fill(str(ans))

            # Handle radio buttons (e.g. sponsorship, authorization, background check)
            radios = await page.query_selector_all("input[type='radio']")
            for radio in radios:
                label_text = await page.evaluate("(el) => el.closest('fieldset')?.innerText || el.parentElement?.innerText || ''", radio)
                if label_text:
                    lbl_lower = label_text.lower()
                    # Common positive questions: authorized to work, 18+ years old
                    if "authorized to work" in lbl_lower or "legally authorized" in lbl_lower:
                        radio_val = await page.evaluate("(el) => el.parentElement?.innerText?.toLowerCase() || ''", radio)
                        if "yes" in radio_val:
                            await radio.check()
                    # Common negative questions: require visa sponsorship
                    elif "sponsorship" in lbl_lower or "require sponsor" in lbl_lower:
                        radio_val = await page.evaluate("(el) => el.parentElement?.innerText?.toLowerCase() || ''", radio)
                        if "no" in radio_val:
                            await radio.check()
        except Exception as e:
            logger.warning(f"Error during form modal filling: {e}")
