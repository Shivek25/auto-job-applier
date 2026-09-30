# src/scraper/job_fetcher.py
import logging
from typing import List, Dict, Any
from jobspy import scrape_jobs
from src.storage.database import Database

logger = logging.getLogger(__name__)

class JobFetcher:
    def __init__(self, database: Database):
        self.db = database

    def fetch_jobs(
        self,
        search_terms: List[str],
        locations: List[str],
        results_wanted: int = 20,
        is_remote: bool = True
    ) -> List[Dict[str, Any]]:
        target_jobs = []
        for term in search_terms:
            for loc in locations:
                logger.info(f"Scraping jobs for '{term}' in '{loc}'...")
                try:
                    jobs_df = scrape_jobs(
                        site_name=["linkedin", "indeed"],
                        search_term=term,
                        location=loc,
                        results_wanted=results_wanted,
                        hours_old=72,
                        is_remote=is_remote
                    )
                    if jobs_df is not None and not jobs_df.empty:
                        for _, row in jobs_df.iterrows():
                            raw_id = row.get("id") or row.get("job_url") or ""
                            job_id = str(raw_id).strip()
                            if not job_id:
                                continue
                            # Skip already applied
                            if self.db.is_already_applied(job_id):
                                continue
                            target_jobs.append({
                                "job_id": job_id,
                                "site": str(row.get("site", "unknown")).lower(),
                                "title": str(row.get("title", "")),
                                "company": str(row.get("company", "")),
                                "location": str(row.get("location", "")),
                                "job_url": str(row.get("job_url", "")),
                                "description": str(row.get("description", ""))
                            })
                except Exception as e:
                    logger.error(f"Error fetching jobs for {term} in {loc}: {e}")
        return target_jobs
