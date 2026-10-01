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

        # Contact & Identification
        if "phone" in lbl or "mobile" in lbl or "contact" in lbl:
            return self.profile.personal_info.phone
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

        # Notice period & Compensation
        if "notice" in lbl:
            return "15" if input_type == "number" else "15 days"
        if "current ctc" in lbl or "current salary" in lbl:
            return "600000" if input_type == "number" else "6 LPA"
        if "expected ctc" in lbl or "expected salary" in lbl or "compensation" in lbl or "desired salary" in lbl:
            return "900000" if input_type == "number" else "9 LPA"

        # Experience queries (e.g. "How many years of work experience do you have with SQL?")
        if "years" in lbl or "experience" in lbl:
            return "2" if input_type == "number" else "2 years"

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
            ans = res.get("answer", "")
            if ans:
                return ans
        except Exception as e:
            logger.warning(f"LLM question answer fallback triggered ({e}). Using deterministic default.")
        
        if field_type == "number":
            return "2"
        return "Yes"

    async def fill_current_modal(self, page: Page):
        try:
            # 1. Fill all text, number, tel, email inputs and textareas
            input_selector = (
                "input:not([type]), input[type='text'], input[type='number'], "
                "input[type='tel'], input[type='email'], textarea"
            )
            inputs = await page.query_selector_all(input_selector)
            for inp in inputs:
                val = await inp.input_value()
                if not val:
                    inp_id = await inp.get_attribute("id")
                    inp_type = (await inp.get_attribute("type")) or "text"
                    label_text = ""
                    
                    if inp_id:
                        label_el = await page.query_selector(f"label[for='{inp_id}']")
                        if label_el:
                            label_text = await label_el.inner_text()
                    
                    if not label_text:
                        label_text = await page.evaluate(
                            """(el) => {
                                const group = el.closest('.jobs-easy-apply-form-section__grouping') || 
                                              el.closest('.fb-form-element') || 
                                              el.closest('div');
                                const lbl = group ? group.querySelector('label') : null;
                                return (lbl ? lbl.innerText : '') || 
                                       el.getAttribute('aria-label') || 
                                       el.getAttribute('name') || 
                                       el.placeholder || '';
                            }""",
                            inp
                        )
                    
                    # Solve deterministically first (zero token cost, instant)
                    ans = self.solve_deterministically(label_text, inp_type)
                    if not ans:
                        ans = await self.answer_question(label_text, inp_type)
                    
                    if ans:
                        await inp.fill(str(ans))

            # 2. Handle select / dropdown elements
            selects = await page.query_selector_all("select")
            for sel in selects:
                sel_val = await sel.input_value()
                if not sel_val or sel_val in ["0", "Select an option", ""]:
                    label_text = await page.evaluate(
                        """(el) => {
                            const group = el.closest('.jobs-easy-apply-form-section__grouping') || 
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

            # 3. Handle radio buttons (e.g. sponsorship, authorization, commute)
            radios = await page.query_selector_all("input[type='radio']")
            for radio in radios:
                label_text = await page.evaluate(
                    "(el) => el.closest('fieldset')?.innerText || el.parentElement?.innerText || ''", 
                    radio
                )
                if label_text:
                    lbl_lower = label_text.lower()
                    radio_val = await page.evaluate(
                        "(el) => el.parentElement?.innerText?.toLowerCase() || ''", 
                        radio
                    )
                    
                    if "sponsorship" in lbl_lower or "require sponsor" in lbl_lower or "visa" in lbl_lower:
                        if "no" in radio_val:
                            try:
                                await radio.check(force=True)
                            except Exception:
                                pass
                    elif any(w in lbl_lower for w in ["authorized", "commute", "relocate", "comfortable", "degree", "18"]):
                        if "yes" in radio_val:
                            try:
                                await radio.check(force=True)
                            except Exception:
                                pass

            # 4. Handle unchecked required checkboxes (e.g. agreement, privacy)
            checkboxes = await page.query_selector_all("input[type='checkbox']")
            for cb in checkboxes:
                is_checked = await cb.is_checked()
                if not is_checked:
                    try:
                        await cb.check(force=True)
                    except Exception:
                        pass

        except Exception as e:
            logger.warning(f"Error during form modal filling: {e}")
