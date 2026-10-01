# src/applier/indeed.py
import logging
import asyncio
from pathlib import Path
from playwright.async_api import Page
from src.applier.browser import BrowserManager
from src.applier.form_filler import FormFiller
from src.storage.verifier import SubmissionVerifier
from src.storage.database import Database

logger = logging.getLogger(__name__)

class IndeedApplier:
    def __init__(
        self,
        browser_manager: BrowserManager,
        form_filler: FormFiller,
        verifier: SubmissionVerifier,
        database: Database,
        mode: str = "auto"
    ):
        self.bm = browser_manager
        self.filler = form_filler
        self.verifier = verifier
        self.db = database
        self.mode = mode

    async def apply(self, job: dict, tailored_pdf_path: Path) -> bool:
        page = await self.bm.new_stealth_page()
        job_id = job["job_id"]
        job_url = job["job_url"]
        company = job["company"]

        try:
            logger.info(f"Navigating to Indeed job: {job_url}")
            await page.goto(job_url, timeout=45000)
            await self.bm.random_delay(2, 4)

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
