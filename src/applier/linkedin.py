# src/applier/linkedin.py
import logging
import asyncio
from pathlib import Path
from playwright.async_api import Page
from src.applier.browser import BrowserManager
from src.applier.form_filler import FormFiller
from src.storage.verifier import SubmissionVerifier
from src.storage.database import Database

logger = logging.getLogger(__name__)

class LinkedInApplier:
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
            logger.info(f"Navigating to LinkedIn job: {job_url}")
            await page.goto(job_url, timeout=45000)
            await self.bm.random_delay(2, 4)

            # Dismiss any contextual overlay if dismiss button is present
            dismiss_btn = await page.query_selector("button[aria-label='Dismiss'], button[data-tracking-control-name*='modal_dismiss']")
            if dismiss_btn:
                try:
                    await dismiss_btn.click()
                    await self.bm.random_delay(1, 2)
                except Exception:
                    pass

            # Find Easy Apply button (various selectors across LinkedIn layouts)
            apply_btn = await page.query_selector(
                "button.jobs-apply-button, button[data-job-id]:has-text('Easy Apply'), button:has-text('Easy Apply')"
            )
            if not apply_btn:
                # Check if page is asking for login
                is_logged_out = await page.query_selector(
                    "a[href*='login'], button:has-text('Sign in'), div.contextual-sign-in-modal, [data-tracking-control-name*='sign-in-modal']"
                )
                if is_logged_out:
                    logger.warning("⚠️ LinkedIn is not logged in or is displaying a sign-in modal!")
                    if self.mode == "review":
                        logger.info("👉 Review mode: Please log in in the opened browser window now. Waiting up to 45s...")
                        for _ in range(15):
                            await asyncio.sleep(3)
                            apply_btn = await page.query_selector("button.jobs-apply-button, button:has-text('Easy Apply')")
                            if apply_btn:
                                logger.info("✅ Login detected! Proceeding with Easy Apply...")
                                break

                if not apply_btn:
                    logger.info(f"No Easy Apply button found for {job_id} (or sign-in required). Skipping.")
                    self.db.update_status(job_id, "SKIPPED", error_message="No Easy Apply button or sign-in required")
                    return False

            await apply_btn.click()
            await self.bm.random_delay(2, 3)

            # Multi-step wizard traversal
            max_steps = 10
            submitted = False
            for step in range(max_steps):
                # Upload and select tailored resume if file input present
                file_input = await page.query_selector("input[type='file']")
                if file_input:
                    try:
                        abs_pdf = str(tailored_pdf_path.resolve())
                        logger.info(f"Uploading tailored resume to LinkedIn: {abs_pdf}")
                        await file_input.set_input_files(abs_pdf)
                        await self.bm.random_delay(2, 3)

                        # Explicitly ensure the newly uploaded resume card / radio is checked
                        resume_cards = await page.query_selector_all(
                            "div.jobs-document-upload-resume-card, [data-test-document-upload-resume], label.jobs-document-upload__title"
                        )
                        if resume_cards:
                            # The most recently uploaded resume is placed first in the list
                            card_radio = await resume_cards[0].query_selector("input[type='radio']")
                            if card_radio:
                                await card_radio.check(force=True)
                            else:
                                await resume_cards[0].click()
                            logger.info("Selected newly uploaded tailored resume.")
                    except Exception as e:
                        logger.warning(f"File upload note: {e}")

                # Fill other questions on current modal step
                await self.filler.fill_current_modal(page)
                await self.bm.random_delay(1, 2)

                # Check for Submit button
                submit_btn = await page.query_selector(
                    "button[aria-label='Submit application'], button:has-text('Submit application'), button.artdeco-button--primary:has-text('Submit')"
                )
                if submit_btn:
                    if self.mode == "review":
                        logger.info("👉 Review mode: pausing 15s for user inspection before final submission...")
                        await asyncio.sleep(15)
                    await submit_btn.click()
                    await self.bm.random_delay(3, 5)
                    
                    # Verify modal closed or dismiss button appears
                    dismiss_btn = await page.query_selector("button[aria-label='Dismiss'], button:has-text('Done')")
                    if dismiss_btn:
                        try:
                            await dismiss_btn.click()
                        except Exception:
                            pass
                    submitted = True
                    break

                # Otherwise check for Next / Review button
                next_btn = await page.query_selector(
                    "button[aria-label='Continue to next step'], button[aria-label='Review your application'], button:has-text('Next'), button:has-text('Review'), button.artdeco-button--primary:has-text('Next'), button.artdeco-button--primary:has-text('Review')"
                )
                if next_btn:
                    is_disabled = await next_btn.is_disabled()
                    if is_disabled:
                        logger.warning("Next button is disabled. Attempting to re-check fields...")
                        await self.filler.fill_current_modal(page)
                        await self.bm.random_delay(1, 2)
                    
                    # Check for inline error messages on the form
                    error_el = await page.query_selector(
                        "span.artdeco-inline-feedback__message, div.artdeco-inline-feedback--error, p.t-12.t-red, .jobs-easy-apply-form-section__error-text"
                    )
                    if error_el:
                        err_text = await error_el.inner_text()
                        logger.warning(f"Validation error on step {step+1}: '{err_text}'. Re-filling with clean numeric inputs...")
                        await self.filler.fill_current_modal(page)
                        await self.bm.random_delay(1, 2)

                    await next_btn.click()
                    await self.bm.random_delay(2, 3)
                else:
                    # No next or submit button, break
                    break

            receipt_path = await self.verifier.verify_and_capture(page, company, job_id)
            if submitted:
                self.db.update_status(
                    job_id=job_id,
                    status="SUBMITTED",
                    resume_path=str(tailored_pdf_path),
                    screenshot_path=str(receipt_path)
                )
                logger.info(f"Successfully applied to {company} ({job_id}) on LinkedIn!")
                return True
            else:
                err_msg = "Form had validation errors or was not able to reach the final Submit button"
                logger.error(f"Application to {company} ({job_id}) failed: {err_msg}")
                self.db.update_status(
                    job_id=job_id,
                    status="FAILED",
                    error_message=err_msg,
                    screenshot_path=str(receipt_path)
                )
                return False

        except Exception as e:
            logger.error(f"Failed applying to {job_id} on LinkedIn: {e}")
            self.db.update_status(job_id=job_id, status="FAILED", error_message=str(e))
            return False
        finally:
            try:
                await page.close()
            except Exception:
                pass
