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

            # Group radios by name attribute or fieldset
            radio_groups = {}
            for r in question_radios:
                group_key = await r.get_attribute("name")
                if not group_key:
                    group_key = await page.evaluate(
                        "(el) => el.closest('fieldset')?.id || el.closest('.fb-form-element')?.id || 'group_default'", 
                        r
                    )
                radio_groups.setdefault(group_key, []).append(r)

            for g_key, g_radios in radio_groups.items():
                # Extract question / legend text for this group
                q_text = await page.evaluate("""(el) => {
                    const fieldset = el.closest('fieldset');
                    if (fieldset) {
                        const legend = fieldset.querySelector('legend');
                        if (legend) return legend.innerText;
                        return fieldset.innerText;
                    }
                    const group = el.closest('.jobs-easy-apply-form-section__grouping') || 
                                  el.closest('.fb-form-element') || 
                                  el.closest('.jobs-easy-apply-form-element') || 
                                  el.parentElement;
                    return group ? group.innerText : '';
                }""", g_radios[0])
                
                q_low = q_text.lower()
                is_sponsorship = any(w in q_low for w in ["sponsorship", "require sponsor", "visa sponsor", "work authorization sponsor"])
                target_answer = "no" if is_sponsorship else "yes"

                # Check if group already has an answer checked
                already_checked = None
                for r in g_radios:
                    if await r.is_checked():
                        already_checked = r
                        break

                # If already checked, ensure sponsorship is NOT checked 'yes'
                if already_checked:
                    checked_text = await page.evaluate("(el) => el.parentElement?.innerText?.toLowerCase() || ''", already_checked)
                    if is_sponsorship and "yes" in checked_text:
                        # Must switch from yes to no
                        pass
                    else:
                        # Valid existing selection, continue
                        continue

                # Find radio that matches target_answer
                target_radio = None
                for r in g_radios:
                    opt_text = await page.evaluate("""(el) => {
                        const val = el.value || '';
                        let lblText = '';
                        if (el.id) {
                            const lbl = document.querySelector(`label[for="${el.id}"]`);
                            if (lbl) lblText = lbl.innerText;
                        }
                        if (!lblText && el.parentElement) {
                            lblText = el.parentElement.innerText;
                        }
                        return (val + ' ' + lblText).toLowerCase();
                    }""", r)
                    
                    if target_answer in opt_text:
                        target_radio = r
                        break

                # Fallback to first radio in group if target not matched
                if not target_radio and g_radios:
                    target_radio = g_radios[0]

                if target_radio:
                    try:
                        # 1. Force check on input
                        await target_radio.check(force=True)
                        
                        # 2. Click label
                        r_id = await target_radio.get_attribute("id")
                        if r_id:
                            lbl = await container.query_selector(f"label[for='{r_id}']")
                            if lbl:
                                await lbl.click(force=True)
                        else:
                            await target_radio.click(force=True)

                        # 3. JavaScript dispatchEvent to guarantee React catches the change
                        await page.evaluate("""(el) => {
                            el.checked = true;
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        }""", target_radio)
                        
                        short_q = q_text.splitlines()[0] if q_text else g_key
                        logger.info(f"Radio answered: '{short_q.strip()}' -> '{target_answer}'")
                    except Exception as e:
                        logger.warning(f"Could not check radio for {g_key}: {e}")

            # 4. Handle unchecked required checkboxes (e.g. agreement, privacy)
            checkboxes = await container.query_selector_all("input[type='checkbox']")
            for cb in checkboxes:
                is_checked = await cb.is_checked()
                if not is_checked:
                    try:
                        await cb.check(force=True)
                    except Exception:
                        pass

        except Exception as e:
            logger.warning(f"Error during form modal filling: {e}")
