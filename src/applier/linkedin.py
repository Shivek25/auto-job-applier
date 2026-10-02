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
            resume_uploaded = False
            for step in range(max_steps):
                # Detect Resume step
                is_resume_step = False
                if not resume_uploaded:
                    try:
                        is_resume_step = await page.evaluate("""() => {
                            const modal = document.querySelector('.jobs-easy-apply-modal, [data-test-modal], div[role="dialog"]');
                            const text = (modal ? modal.innerText : document.body.innerText) || '';
                            const hasResumeHeading = /resume/i.test(text) && (/upload/i.test(text) || /doc, docx/i.test(text) || /pdf/i.test(text));
                            const hasFileInput = !!document.querySelector("input[type='file']");
                            const hasUploadBtn = Array.from(document.querySelectorAll('label, button, span')).some(el => /upload resume/i.test(el.innerText || ''));
                            return hasResumeHeading || hasFileInput || hasUploadBtn;
                        }""")
                    except Exception as e:
                        logger.debug(f"Resume detection note: {e}")
                        is_resume_step = bool(await page.query_selector("input[type='file']"))
                
                if is_resume_step:
                    try:
                        abs_pdf = str(tailored_pdf_path.resolve())
                        target_filename = tailored_pdf_path.name
                        logger.info(f"📄 Resume step detected! Uploading tailored resume: {abs_pdf}")

                        # Delete oldest resume if limit (4) reached
                        await page.evaluate("""() => {
                            const cards = document.querySelectorAll(
                                'div.jobs-document-upload-resume-card, div[data-test-document-upload-resume], li.jobs-document-upload-resume-card'
                            );
                            if (cards.length >= 4) {
                                const last = cards[cards.length - 1];
                                const del = last.querySelector('button[aria-label*="Delete"], button[data-test-document-delete-button]');
                                if (del) del.click();
                            }
                        }""")

                        uploaded = False
                        # Method A: Trigger upload via file chooser on 'Upload resume' button/label
                        upload_el = await page.query_selector(
                            "label:has-text('Upload resume'), button:has-text('Upload resume'), [aria-label*='Upload resume'], label[for*='upload-resume']"
                        )
                        if upload_el:
                            try:
                                async with page.expect_file_chooser(timeout=3000) as fc_info:
                                    await upload_el.click()
                                fc = await fc_info.value
                                await fc.set_files(abs_pdf)
                                uploaded = True
                                logger.info(f"Resume uploaded via file chooser: {target_filename}")
                            except Exception as e:
                                logger.debug(f"File chooser dialog note: {e}")

                        # Method B: Direct set_input_files on input[type='file']
                        if not uploaded:
                            file_input = await page.query_selector("input[type='file']")
                            if file_input:
                                await file_input.set_input_files(abs_pdf)
                                uploaded = True
                                logger.info(f"Resume uploaded via set_input_files: {target_filename}")

                        # Wait for upload processing (up to 5s)
                        for _ in range(5):
                            await asyncio.sleep(1)
                            is_loading = await page.evaluate("""() => {
                                return !!document.querySelector('.artdeco-inline-feedback--loading, [role="progressbar"], .jobs-document-upload--loading');
                            }""")
                            if not is_loading:
                                break

                        # Pure JavaScript selection (safe against any viewport errors)
                        selected_name = await page.evaluate("""(targetName) => {
                            const cards = Array.from(document.querySelectorAll(
                                'div.jobs-document-upload-resume-card, div[data-test-document-upload-resume], li.jobs-document-upload-resume-card, .jobs-document-upload'
                            ));
                            
                            let target = null;
                            if (targetName) {
                                target = cards.find(c => c.innerText.toLowerCase().includes(targetName.toLowerCase()));
                            }
                            if (!target && cards.length > 0) {
                                target = cards[0];
                            }
                            
                            if (target) {
                                target.scrollIntoView({ behavior: 'instant', block: 'center' });
                                const radio = target.querySelector('input[type="radio"]');
                                if (radio) {
                                    radio.checked = true;
                                    radio.dispatchEvent(new Event('input', { bubbles: true }));
                                    radio.dispatchEvent(new Event('change', { bubbles: true }));
                                }
                                const lbl = target.querySelector('label') || target;
                                try { lbl.click(); } catch(e) {}
                                return target.innerText.split('\\n')[0];
                            }
                            
                            // Fallback to first radio in resume section
                            const radios = document.querySelectorAll('input[type="radio"][name*="resume"], .jobs-document-upload input[type="radio"]');
                            if (radios.length > 0) {
                                radios[0].scrollIntoView({ behavior: 'instant', block: 'center' });
                                radios[0].checked = true;
                                radios[0].dispatchEvent(new Event('input', { bubbles: true }));
                                radios[0].dispatchEvent(new Event('change', { bubbles: true }));
                                try { radios[0].click(); } catch(e) {}
                                return 'first_resume_radio';
                            }
                            return null;
                        }""", target_filename)

                        if selected_name:
                            logger.info(f"✅ Tailored resume verified & selected: {selected_name}")
                            resume_uploaded = True
                        else:
                            logger.info(f"Tailored resume uploaded: {target_filename} (active on LinkedIn)")
                            resume_uploaded = True
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
                    # Explicitly uncheck any 'Follow company' checkbox on the review screen
                    await page.evaluate("""() => {
                        const checkboxes = Array.from(document.querySelectorAll('input[type="checkbox"]'));
                        for (const cb of checkboxes) {
                            const id = (cb.id || '').toLowerCase();
                            const name = (cb.name || '').toLowerCase();
                            const lblText = (
                                (cb.id ? document.querySelector(`label[for="${cb.id}"]`)?.innerText : '') ||
                                cb.closest('label')?.innerText ||
                                cb.closest('.fb-form-element')?.innerText ||
                                cb.parentElement?.innerText || ''
                            ).toLowerCase();
                            
                            if (id.includes('follow') || name.includes('follow') || lblText.includes('follow') || lblText.includes('stay up to date')) {
                                if (cb.checked) {
                                    try {
                                        const clickable = (cb.id ? document.querySelector(`label[for="${cb.id}"]`) : null) || cb.closest('label') || cb;
                                        clickable.click();
                                    } catch(e) {}
                                    if (cb.checked) {
                                        cb.checked = false;
                                        cb.dispatchEvent(new Event('input', { bubbles: true }));
                                        cb.dispatchEvent(new Event('change', { bubbles: true }));
                                    }
                                }
                            }
                        }
                    }""")

                    if self.mode == "review":
                        logger.info("👉 Review mode: pausing 15s for user inspection before final submission...")
                        await asyncio.sleep(15)
                    await submit_btn.click()
                    
                    # Wait 3-4s for the submission confirmation modal ('Your application was sent to...') to render
                    await asyncio.sleep(3)
                    
                    # CAPTURE PROOF RECEIPT OF THE SUCCESSFUL SUBMISSION CONFIRMATION MODAL
                    receipt_path = await self.verifier.verify_and_capture(page, company, job_id)
                    logger.info(f"📸 Captured submission proof receipt: {receipt_path.name}")
                    submitted = True

                    # Dismiss / close the post-apply confirmation dialog
                    dismiss_btn = await page.query_selector(
                        "button:has-text('Not now'), button[aria-label='Dismiss'], button:has-text('Done'), button.artdeco-modal__dismiss"
                    )
                    if dismiss_btn:
                        try:
                            await dismiss_btn.click()
                            await asyncio.sleep(1)
                        except Exception:
                            pass
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

            if not submitted:
                # Capture failure state screenshot for debugging
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
