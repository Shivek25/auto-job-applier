# src/applier/form_filler.py
import re
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
        self.skills_set = set()
        for cat, sk_list in self.profile.skills.model_dump().items():
            for s in sk_list:
                self.skills_set.add(s.lower())

    def solve_deterministically(self, label_text: str, input_type: str = "text") -> Optional[str]:
        lbl = label_text.lower().strip()

        # Phone country code
        if ("country code" in lbl or "phone code" in lbl or "dial" in lbl) and input_type in ["text", "tel"]:
            return "+91"

        # Mobile / Contact Phone Number (Must be direct digits without country code)
        if "phone" in lbl or "mobile" in lbl or "contact" in lbl:
            raw_phone = self.profile.personal_info.phone or ""
            clean_digits = re.sub(r"\D", "", raw_phone)
            # If starts with India 91 and has 12 digits, strip leading 91
            if clean_digits.startswith("91") and len(clean_digits) > 10:
                clean_digits = clean_digits[2:]
            return clean_digits[-10:] if len(clean_digits) >= 10 else clean_digits

        if "email" in lbl:
            return self.profile.personal_info.email
        if "first name" in lbl or "given name" in lbl:
            return self.profile.personal_info.name.split()[0]
        if "last name" in lbl or "surname" in lbl or "family name" in lbl:
            parts = self.profile.personal_info.name.split()
            return parts[-1] if len(parts) > 1 else self.profile.personal_info.name
        if "full name" in lbl or lbl == "name":
            return self.profile.personal_info.name
        
        # Location details
        if "city" in lbl or "location" in lbl or "address" in lbl or "residence" in lbl:
            return self.profile.personal_info.location or "Noida"
        if "state" in lbl or "province" in lbl:
            return "Uttar Pradesh"
        if "country" in lbl and "code" not in lbl:
            return "India"
        if "postal" in lbl or "zip" in lbl or "pin" in lbl:
            return "201301"

        # URLs
        if "linkedin" in lbl and self.profile.personal_info.linkedin_url:
            return self.profile.personal_info.linkedin_url
        if "github" in lbl and self.profile.personal_info.github_url:
            return self.profile.personal_info.github_url
        if "website" in lbl or "portfolio" in lbl or "blog" in lbl:
            return self.profile.personal_info.github_url or self.profile.personal_info.linkedin_url or "https://github.com"

        # Employer & Experience details
        if "current company" in lbl or "current employer" in lbl or "recent company" in lbl:
            return self.profile.work_experience[0].company if self.profile.work_experience else "Nexaquark Consulting"
        if "current title" in lbl or "current role" in lbl or "job title" in lbl:
            return self.profile.work_experience[0].role if self.profile.work_experience else "Data Engineer"
        
        # Education details
        if "degree" in lbl or "qualification" in lbl:
            return self.profile.education[0].degree if self.profile.education else "Bachelor of Technology"
        if "university" in lbl or "college" in lbl or "school" in lbl:
            return self.profile.education[0].institution if self.profile.education else "Jaypee Institute of Information Technology"
        if "graduation year" in lbl or "passing year" in lbl:
            return self.profile.education[0].graduation_year if self.profile.education else "2024"
        if "gpa" in lbl or "percentage" in lbl:
            return "8.0"

        # Notice period (Always numeric or simple days)
        if "notice" in lbl:
            return "15"

        # Compensation & Salary fields (ALWAYS numeric digits only, never words or sentences)
        if "current ctc" in lbl or "current salary" in lbl:
            return "600000"
        if any(w in lbl for w in ["salary", "ctc", "compensation", "expectation", "annual salary"]):
            return "900000"

        # Experience queries (e.g. "How many years of work experience do you have with SQL?")
        # MUST ALWAYS BE A PURE DIGIT "2", never "2 years"
        if "years" in lbl or "experience" in lbl:
            return "2"

        # Common affirmative questions
        if any(w in lbl for w in ["authorized", "authorization", "legally", "18", "commute", "relocate", "hybrid", "onsite"]):
            return "Yes"
        if any(w in lbl for w in ["sponsorship", "require sponsor", "visa"]):
            return "No"

        # Source / Hearing questions
        if "hear about" in lbl or "referral" in lbl:
            return "LinkedIn"

        # Open-ended questions (Cover letter, Why fit, Summary)
        if any(w in lbl for w in ["why", "cover letter", "about yourself", "summary", "objective", "describe"]):
            return "I am a Data Engineer with expertise in Snowflake, dbt, SQL, BigQuery, and building scalable ETL pipelines. I am excited to contribute to this role."

        # Voluntary self-identification
        if any(w in lbl for w in ["gender", "race", "ethnicity", "veteran", "disability"]):
            return "Decline to state"

        # Numeric fallback: safe default
        if input_type == "number":
            return "2"

        return None

    async def answer_question(self, question_text: str, field_type: str, options: Optional[List[str]] = None) -> Any:
        q_lower = question_text.lower()
        extra_options = f"Available options: {options}" if options else ""
        prompt = (
            FORM_ANSWER_PROMPT
            .replace("{profile_json}", self.profile.model_dump_json(indent=2))
            .replace("{question_text}", question_text)
            .replace("{field_type}", field_type)
            .replace("{extra_options}", extra_options)
        )
        try:
            res = self.llm.generate_json(prompt)
            ans = str(res.get("answer", "")).strip()
            
            # Sanitize LLM response - eliminate refusal/fluff text
            if any(ref in ans.lower() for ref in ["not specified", "candidate profile", "not mentioned", "unknown", "n/a"]):
                if field_type == "number" or "year" in q_lower:
                    return "2"
                return "Yes"

            # If field expects number or years, extract digits only
            if field_type == "number" or "year" in q_lower or "salary" in q_lower or "ctc" in q_lower:
                digits = re.findall(r"\d+", ans)
                if digits:
                    return digits[0]
                return "2"

            if ans:
                return ans
        except Exception as e:
            logger.warning(f"LLM question answer fallback triggered ({e}). Using deterministic default.")
        
        if field_type == "number" or "year" in q_lower:
            return "2"
        return "Yes"

    async def fill_current_modal(self, page: Page):
        try:
            # Scope to the modal container to prevent modifying elements outside the modal
            modal = await page.query_selector(
                "div.jobs-easy-apply-modal, div.jobs-easy-apply-content, div[data-test-modal], div[role='dialog']"
            )
            container = modal if modal else page

            # 1. Fill all text, number, tel, email inputs and textareas
            input_selector = (
                "input:not([type]), input[type='text'], input[type='number'], "
                "input[type='tel'], input[type='email'], textarea"
            )
            inputs = await container.query_selector_all(input_selector)
            for inp in inputs:
                inp_id = await inp.get_attribute("id")
                inp_type = (await inp.get_attribute("type")) or "text"
                label_text = ""
                
                # Check label by 'for' attribute
                if inp_id:
                    try:
                        label_el = await container.query_selector(f"label[for='{inp_id}']")
                        if label_el:
                            label_text = await label_el.inner_text()
                    except Exception:
                        pass
                
                # Fallback to parent grouping or aria-label
                if not label_text:
                    label_text = await page.evaluate(
                        """(el) => {
                            const group = el.closest('.jobs-easy-apply-form-section__grouping') || 
                                          el.closest('.fb-form-element') || 
                                          el.closest('.jobs-easy-apply-form-element');
                            const lbl = group ? group.querySelector('label') : null;
                            return (lbl ? lbl.innerText : '') || 
                                   el.getAttribute('aria-label') || 
                                   el.getAttribute('name') || 
                                   el.placeholder || '';
                        }""",
                        inp
                    )
                
                # Determine value to fill
                val = await inp.input_value()
                ans = self.solve_deterministically(label_text, inp_type)
                if not ans:
                    ans = await self.answer_question(label_text, inp_type)
                
                # Enforce clean digits for phone, years, salary
                lbl_low = label_text.lower()
                if "phone" in lbl_low or "mobile" in lbl_low:
                    ans = re.sub(r"\D", "", str(ans))
                    if ans.startswith("91") and len(ans) > 10:
                        ans = ans[2:]
                    ans = ans[-10:] if len(ans) >= 10 else ans
                elif "year" in lbl_low or "experience" in lbl_low:
                    digits = re.findall(r"\d+", str(ans))
                    ans = digits[0] if digits else "2"
                elif any(w in lbl_low for w in ["salary", "ctc", "compensation"]):
                    digits = re.findall(r"\d+", str(ans))
                    ans = digits[0] if digits else "900000"

                # Check if current value already matches or if it needs filling/fixing
                if ans and (not val or val != str(ans) or any(bad in val for bad in ["Not specified", "+91", "years", "LPA"])):
                    # Clear completely and fill freshly
                    try:
                        await inp.click()
                        await inp.fill("")
                        await inp.fill(str(ans))
                    except Exception:
                        try:
                            await page.evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); }", inp, str(ans))
                        except Exception:
                            pass

            # 2. Handle select / dropdown elements
            selects = await container.query_selector_all("select")
            for sel in selects:
                sel_val = await sel.input_value()
                if not sel_val or sel_val in ["0", "Select an option", ""]:
                    label_text = await page.evaluate(
                        """(el) => {
                            const group = el.closest('.jobs-easy-apply-form-section__grouping') || 
                                          el.closest('.fb-form-element') || 
                                          el.closest('div');
                            const lbl = group ? group.querySelector('label') : null;
                            return (lbl ? lbl.innerText : '') || el.getAttribute('aria-label') || '';
                        }""", 
                        sel
                    )
                    options = await sel.query_selector_all("option")
                    opt_texts = []
                    for opt in options:
                        t = (await opt.inner_text()).strip()
                        v = await opt.get_attribute("value")
                        if t and t not in ["Select an option", "Select", "Choose"]:
                            opt_texts.append((t, v))
                    
                    if opt_texts:
                        lbl_low = label_text.lower()
                        chosen_val = None
                        
                        # Country / Phone code dropdown
                        if any(w in lbl_low for w in ["country code", "phone", "dial", "country"]):
                            for t, v in opt_texts:
                                if "india" in t.lower() or "+91" in t:
                                    chosen_val = v
                                    break
                        
                        # Yes / No question dropdown
                        has_yes = any("yes" in t.lower() for t, _ in opt_texts)
                        has_no = any("no" in t.lower() for t, _ in opt_texts)
                        if not chosen_val and (has_yes or has_no):
                            if any(w in lbl_low for w in ["sponsorship", "visa", "require sponsor"]):
                                for t, v in opt_texts:
                                    if "no" in t.lower():
                                        chosen_val = v
                                        break
                            else:
                                for t, v in opt_texts:
                                    if "yes" in t.lower():
                                        chosen_val = v
                                        break

                        # Sponsorship
                        if not chosen_val and any(w in lbl_low for w in ["sponsorship", "visa"]):
                            for t, v in opt_texts:
                                if "no" in t.lower():
                                    chosen_val = v
                                    break
                        
                        # Authorization, relocation, commute, experience
                        if not chosen_val and any(w in lbl_low for w in ["authorized", "commute", "relocate", "degree", "experience", "18"]):
                            for t, v in opt_texts:
                                if "yes" in t.lower():
                                    chosen_val = v
                                    break
                        
                        # Language proficiency
                        if not chosen_val and any(w in lbl_low for w in ["proficiency", "level", "language"]):
                            for t, v in opt_texts:
                                if any(w in t.lower() for w in ["professional", "fluent", "native", "advanced", "full"]):
                                    chosen_val = v
                                    break
                        
                        # Fallback to first non-empty option
                        if not chosen_val and opt_texts:
                            chosen_val = opt_texts[0][1]

                        if chosen_val:
                            try:
                                await sel.select_option(value=chosen_val)
                            except Exception:
                                pass

            # 3. Handle radio buttons (e.g. LLM experience, Python experience, sponsorship, etc.)
            all_radios = await container.query_selector_all("input[type='radio']")
            
            # Filter out resume selection radios
            question_radios = []
            for r in all_radios:
                is_resume = await page.evaluate("""(el) => {
                    if (el.name && el.name.toLowerCase().includes('resume')) return true;
                    if (el.closest('.jobs-document-upload') || el.closest('[data-test-document-upload-resume]')) return true;
                    return false;
                }""", r)
                if not is_resume:
                    question_radios.append(r)

            # 3. Handle radio buttons (screening questions: default Yes, sponsorship No)
            answered_radios = await page.evaluate("""() => {
                const results = [];
                const processedRadios = new Set();
                
                // Helper to process a group of radios
                function processGroup(questionText, radios) {
                    if (!radios || radios.length === 0) return;
                    
                    // Skip resume selection radios
                    if (/resume/i.test(questionText) || radios.some(r => r.name && /resume/i.test(r.name))) {
                        return;
                    }
                    
                    const qLow = (questionText || '').toLowerCase();
                    const isSponsor = qLow.includes('sponsor') || qLow.includes('visa');
                    const target = isSponsor ? 'no' : 'yes';
                    
                    // Check if group already has a valid checked radio
                    let alreadyChecked = radios.find(r => r.checked);
                    if (alreadyChecked) {
                        const checkedText = (alreadyChecked.parentElement?.innerText || '').toLowerCase();
                        if (isSponsor && checkedText.includes('yes')) {
                            // Must switch sponsorship from yes to no
                        } else {
                            // Already answered validly
                            radios.forEach(r => processedRadios.add(r));
                            return;
                        }
                    }
                    
                    // Find matching radio for target
                    let targetRadio = null;
                    for (const r of radios) {
                        const val = (r.value || '').toLowerCase();
                        const lbl = (r.id ? document.querySelector(`label[for="${r.id}"]`)?.innerText : '') || r.parentElement?.innerText || '';
                        const combined = (val + ' ' + lbl).toLowerCase();
                        if (combined.includes(target)) {
                            targetRadio = r;
                            break;
                        }
                    }
                    
                    // Fallback to first radio if target not found
                    if (!targetRadio && radios.length > 0) {
                        targetRadio = radios[0];
                    }
                    
                    if (targetRadio) {
                        // Scroll smoothly inside modal
                        try {
                            targetRadio.scrollIntoView({ behavior: 'instant', block: 'center' });
                        } catch (e) {}
                        
                        targetRadio.checked = true;
                        targetRadio.dispatchEvent(new Event('input', { bubbles: true }));
                        targetRadio.dispatchEvent(new Event('change', { bubbles: true }));
                        
                        // Click label or wrapper to trigger LinkedIn React UI state
                        const clickable = (targetRadio.id ? document.querySelector(`label[for="${targetRadio.id}"]`) : null) || 
                                          targetRadio.closest('label') || 
                                          targetRadio.parentElement;
                        if (clickable) {
                            try { clickable.click(); } catch(e) {}
                        }
                        
                        radios.forEach(r => processedRadios.add(r));
                        results.push({ question: questionText.split('\\n')[0].trim(), answer: target });
                    }
                }
                
                // Process each fieldset or question grouping
                const groups = document.querySelectorAll(
                    'fieldset, div.fb-form-element, div.jobs-easy-apply-form-section__grouping, div.jobs-easy-apply-form-element'
                );
                for (const g of groups) {
                    const radios = Array.from(g.querySelectorAll('input[type="radio"]'));
                    if (radios.length > 0 && !radios.every(r => processedRadios.has(r))) {
                        const qText = g.querySelector('legend')?.innerText || g.querySelector('label')?.innerText || g.innerText;
                        processGroup(qText, radios);
                    }
                }
                
                // Fallback for any orphaned radios grouped by name
                const allRadios = Array.from(document.querySelectorAll('input[type="radio"]')).filter(r => !processedRadios.has(r));
                const byName = {};
                for (const r of allRadios) {
                    const name = r.name || 'orphan';
                    if (!byName[name]) byName[name] = [];
                    byName[name].push(r);
                }
                for (const [name, radios] of Object.entries(byName)) {
                    const parent = radios[0].closest('.fb-form-element') || radios[0].parentElement;
                    const qText = parent ? parent.innerText : name;
                    processGroup(qText, radios);
                }
                
                return results;
            }""")
            for item in (answered_radios or []):
                logger.info(f"Radio answered: '{item.get('question', '')}' -> '{item.get('answer', '')}'")

            # 4. Handle unchecked required checkboxes (e.g. agreement, privacy) via DOM
            await page.evaluate("""() => {
                const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                for (const cb of checkboxes) {
                    if (!cb.checked) {
                        try {
                            cb.scrollIntoView({ behavior: 'instant', block: 'center' });
                            cb.checked = true;
                            cb.dispatchEvent(new Event('input', { bubbles: true }));
                            cb.dispatchEvent(new Event('change', { bubbles: true }));
                            const lbl = cb.id ? document.querySelector(`label[for="${cb.id}"]`) : null;
                            if (lbl) lbl.click(); else cb.click();
                        } catch(e) {}
                    }
                }
            }""")

        except Exception as e:
            logger.warning(f"Error during form modal filling: {e}")
