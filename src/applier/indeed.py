# src/applier/indeed.py
import logging
import asyncio
from pathlib import Path
from playwright.async_api import Page
from src.applier.browser import BrowserManager
from src.applier.form_filler import FormFiller
from src.storage.verifier import SubmissionVerifier
from src.storage.database import Database

from typing import Optional
from src.scraper.matcher import JobMatcher
from src.resume.tailor import ResumeTailor
from src.resume.compiler import ResumeCompiler
from src.resume.models import MasterProfile
from src.applier.brain import BrowserBrain

logger = logging.getLogger(__name__)

class IndeedApplier:
    def __init__(
        self,
        browser_manager: BrowserManager,
        form_filler: FormFiller,
        verifier: SubmissionVerifier,
        database: Database,
        matcher: Optional[JobMatcher] = None,
        tailor: Optional[ResumeTailor] = None,
        compiler: Optional[ResumeCompiler] = None,
        master_profile: Optional[MasterProfile] = None,
        brain: Optional[BrowserBrain] = None,
        mode: str = "auto"
    ):
        self.bm = browser_manager
        self.filler = form_filler
        self.verifier = verifier
        self.db = database
        self.matcher = matcher
        self.tailor = tailor
        self.compiler = compiler
        self.master_profile = master_profile
        self.brain = brain
        if not self.brain and hasattr(form_filler, "llm") and form_filler.llm:
            self.brain = BrowserBrain(form_filler.llm, master_profile=master_profile)
        self.mode = mode

    async def extract_full_description(self, page: Page) -> str:
        try:
            full_text = await page.evaluate("""() => {
                const descContainer = document.querySelector(
                    '#jobDescriptionText, .jobsearch-JobComponent-description, .jobsearch-jobDescriptionText'
                );
                return descContainer ? (descContainer.innerText || '').trim() : '';
            }""")
            return full_text
        except Exception as e:
            logger.debug(f"Note on extracting Indeed live description: {e}")
            return ""

    async def apply(self, job: dict, tailored_pdf_path: Path) -> bool:
        page = await self.bm.new_stealth_page()
        job_id = job["job_id"]
        job_url = job["job_url"]
        company = job["company"]

        try:
            logger.info(f"Navigating to Indeed job: {job_url}")
            await page.goto(job_url, timeout=45000)
            await self.bm.random_delay(2, 4)

            # 1. Expand and extract full live job description
            live_desc = await self.extract_full_description(page)
            if live_desc and len(live_desc) > 50:
                logger.info(f"📋 Extracted full live Indeed JD ({len(live_desc)} chars) from page.")
                
                # Check experience mismatch against full live description
                if self.matcher:
                    mismatch = self.matcher.check_experience_mismatch(live_desc, job.get("title", ""))
                    if mismatch:
                        logger.info(f"🚫 Skipping {company} ({job_id}): Full JD requirement mismatch - {mismatch}")
                        self.db.update_status(job_id, "SKIPPED", error_message=mismatch)
                        return False

                # If initial description was missing or incomplete, re-tailor with the full live JD
                initial_desc = job.get("description", "")
                if (not initial_desc or len(initial_desc) < 150 or initial_desc.strip().lower() in ["none", "nan"]) and self.tailor and self.compiler and self.master_profile:
                    logger.info(f"🎯 Re-tailoring resume using full live job description for {company}...")
                    job["description"] = live_desc
                    tailored_profile = self.tailor.tailor(self.master_profile, live_desc)
                    self.compiler.compile_pdf(tailored_profile, tailored_pdf_path)

            apply_btn = await page.query_selector("button.ia-IndeedApplyButton, #indeedApplyButton, button:has-text('Apply now')")
            if not apply_btn and self.brain:
                logger.info("🧠 [Brain] Indeed Apply button not found immediately. Diagnosing...")
                healed = await self.brain.diagnose_and_heal(
                    page,
                    goal="locate_indeed_apply",
                    context={"job_url": job_url, "company": company, "job_id": job_id}
                )
                if healed:
                    apply_btn = await page.query_selector("button.ia-IndeedApplyButton, #indeedApplyButton, button:has-text('Apply now')")

            if not apply_btn:
                self.db.update_status(job_id, "SKIPPED", error_message="No Indeed Quick Apply button")
                return False

            await apply_btn.click()
            await self.bm.random_delay(2, 4)

            # Upload resume if file input present
            file_input = await page.query_selector("input[type='file']")
            if file_input:
                try:
                    await file_input.set_input_files(str(tailored_pdf_path))
                    await self.bm.random_delay(1, 2)
                except Exception as e:
                    logger.warning(f"File upload note on Indeed: {e}")

            await self.filler.fill_current_modal(page)

            submit_btn = await page.query_selector("button[type='submit'], button:has-text('Submit your application')")
            if submit_btn:
                if self.mode == "review":
                    logger.info("Review mode: pausing 15s for user inspection...")
                    await asyncio.sleep(15)
                await submit_btn.click()
                await self.bm.random_delay(3, 5)

            receipt_path = await self.verifier.verify_and_capture(page, company, job_id)
            self.db.update_status(
                job_id=job_id,
                status="SUBMITTED",
                resume_path=str(tailored_pdf_path),
                screenshot_path=str(receipt_path)
            )
            logger.info(f"Successfully applied to {company} ({job_id}) on Indeed!")
            return True
        except Exception as e:
            logger.error(f"Indeed apply failed for {job_id}: {e}")
            self.db.update_status(job_id=job_id, status="FAILED", error_message=str(e))
            return False
        finally:
            try:
                await page.close()
            except Exception:
                pass
