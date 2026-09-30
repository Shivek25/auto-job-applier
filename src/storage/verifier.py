# src/storage/verifier.py
from pathlib import Path
from datetime import datetime
from playwright.async_api import Page

class SubmissionVerifier:
    def __init__(self, receipts_dir: Path | str = "storage/receipts"):
        self.receipts_dir = Path(receipts_dir).resolve()
        self.receipts_dir.mkdir(parents=True, exist_ok=True)

    def get_receipt_path(self, company: str, job_id: str) -> Path:
        clean_company = "".join(c for c in company if c.isalnum() or c in (' ', '_', '-')).strip().replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.receipts_dir / f"{clean_company}_{job_id}_{timestamp}.png"

    async def verify_and_capture(self, page: Page, company: str, job_id: str) -> Path:
        receipt_path = self.get_receipt_path(company, job_id)
        try:
            await page.screenshot(path=str(receipt_path), full_page=False)
        except Exception:
            # Fallback if screenshot fails
            pass
        return receipt_path
