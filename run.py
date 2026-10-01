# run.py
import os
import sys
import re
import shutil
import json
import asyncio
import logging
import argparse
from pathlib import Path

from src.config_loader import load_config
from src.storage.database import Database
from src.storage.verifier import SubmissionVerifier
from src.ai.llm_client import LLMClient
from src.resume.models import MasterProfile
from src.resume.tailor import ResumeTailor
from src.resume.compiler import ResumeCompiler
from src.scraper.job_fetcher import JobFetcher
from src.scraper.matcher import JobMatcher
from src.applier.browser import BrowserManager
from src.applier.form_filler import FormFiller
from src.applier.linkedin import LinkedInApplier
from src.applier.indeed import IndeedApplier

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AutoJobForge")

async def main():
    parser = argparse.ArgumentParser(description="AutoJobForge Autonomous Job Applier")
    parser.add_argument("--mode", choices=["auto", "review"], default=None, help="Autonomy mode: auto or review")
    parser.add_argument("--limit", type=int, default=None, help="Daily application limit")
    parser.add_argument("--platform", choices=["all", "linkedin", "indeed"], default="all", help="Target job platform")
    parser.add_argument("--login", choices=["linkedin", "indeed"], default=None, help="Open browser to log in and save session permanently")
    args = parser.parse_args()

    config = load_config()

    if args.login:
        logger.info(f"Launching headful browser for one-time login to {args.login}...")
        bm = BrowserManager(
            headless=False,
            user_data_dir=config.browser.chrome_user_data_dir,
            profile_name=config.browser.chrome_profile_name
        )
        await bm.login_wizard(platform=args.login)
        await bm.close()
        return

    mode = args.mode or config.app.mode
    daily_limit = args.limit or config.app.daily_application_limit

    db = Database()
    stats = db.get_stats()
    logger.info(f"Loaded database. Applications today: {stats['today_submitted']} / {daily_limit}")
    if stats["today_submitted"] >= daily_limit:
        logger.info(f"Daily limit of {daily_limit} applications already reached today. Exiting.")
        return

    profile_path = Path("config/master_profile.json")
    if not profile_path.exists():
        example_path = Path("config/master_profile.example.json")
        if example_path.exists():
            logger.warning("config/master_profile.json not found. Using config/master_profile.example.json for this run.")
            profile_path = example_path
        else:
            logger.error("No master profile found. Please upload your CV via Web Dashboard or create config/master_profile.json.")
            sys.exit(1)

    with open(profile_path, "r", encoding="utf-8") as f:
        master_profile = MasterProfile(**json.load(f))

    llm = LLMClient(
        provider=config.llm.provider,
        model=config.llm.model,
        api_key=config.llm.api_key,
        ollama_base_url=config.llm.ollama_base_url
    )
    matcher = JobMatcher(
        llm, 
        min_score=config.app.min_match_score,
        max_experience_years=config.search.max_experience_years
    )
    tailor = ResumeTailor(llm)
    compiler = ResumeCompiler()
    verifier = SubmissionVerifier()
    bm = BrowserManager(
        headless=config.browser.headless,
        user_data_dir=config.browser.chrome_user_data_dir,
        profile_name=config.browser.chrome_profile_name
    )

    fetcher = JobFetcher(db)
    logger.info("Searching for fresh job postings on LinkedIn and Indeed...")
    jobs = fetcher.fetch_jobs(
        search_terms=config.search.job_titles,
        locations=config.search.locations,
        results_wanted=config.search.results_wanted,
        is_remote=config.search.is_remote,
        hours_old=config.search.hours_old,
        easy_apply_only=config.search.easy_apply_only
    )
    logger.info(f"Discovered {len(jobs)} candidate jobs across platforms.")

    filler = FormFiller(llm, master_profile)
    linkedin_applier = LinkedInApplier(bm, filler, verifier, db, mode=mode)
    indeed_applier = IndeedApplier(bm, filler, verifier, db, mode=mode)

    submitted_count = stats["today_submitted"]
    for job in jobs:
        if submitted_count >= daily_limit:
            logger.info("Reached daily application limit. Stopping batch.")
            break

        job_id = job["job_id"]
        site = job["site"].lower()

        if args.platform != "all" and args.platform not in site:
            continue

        # AI & Heuristic Match Scoring
        try:
            eval_result = matcher.evaluate(master_profile, job.get("description", ""), job_title=job.get("title", ""))
        except Exception as e:
            logger.warning(f"Could not score match for {job['company']}: {e}")
            eval_result = {"is_match": True, "match_score": 75}

        if not eval_result["is_match"]:
            logger.info(f"Skipping {job['company']} - Match score: {eval_result['match_score']}% (below {config.app.min_match_score}% threshold)")
            db.add_application(
                job_id=job_id,
                platform=job["site"],
                title=job["title"],
                company=job["company"],
                location=job["location"],
                job_url=job["job_url"],
                match_score=eval_result["match_score"],
                status="SKIPPED",
                error_message=f"Score below threshold: {eval_result.get('summary_reason', '')}"
            )
            continue

        logger.info(f"Eligible Match ({eval_result['match_score']}%)! Tailoring resume for {job['company']}...")
        tailored_profile = tailor.tailor(master_profile, job["description"])

        # Format professional filename for LinkedIn upload (e.g. Shivek_Sharma_Honasa_Consumer_li-4473593785.pdf)
        clean_company = re.sub(r"[^a-zA-Z0-9]+", "_", job.get("company", "Company")).strip("_")
        clean_name = re.sub(r"[^a-zA-Z0-9]+", "_", getattr(master_profile.personal_info, "name", "Resume")).strip("_")
        clean_name = clean_name or "Resume"
        prof_filename = f"{clean_name}_{clean_company}_{job_id}.pdf"
        pdf_path = Path(f"storage/tailored_resumes/{prof_filename}")
        compiler.compile_pdf(tailored_profile, pdf_path)

        # Also maintain job_id.pdf for backward compatibility
        legacy_path = Path(f"storage/tailored_resumes/{job_id}.pdf")
        if legacy_path != pdf_path:
            shutil.copyfile(pdf_path, legacy_path)

        # Track application as PENDING in database
        db.add_application(
            job_id=job_id,
            platform=job["site"],
            title=job["title"],
            company=job["company"],
            location=job["location"],
            job_url=job["job_url"],
            match_score=eval_result["match_score"],
            status="PENDING"
        )

        # Apply based on platform
        success = False
        if "linkedin" in site and config.platforms.linkedin:
            success = await linkedin_applier.apply(job, pdf_path)
        elif "indeed" in site and config.platforms.indeed:
            success = await indeed_applier.apply(job, pdf_path)

        if success:
            submitted_count += 1
            logger.info(f"Progress today: {submitted_count}/{daily_limit} submitted.")
            await bm.random_delay(config.app.delay_between_applications_min, config.app.delay_between_applications_max)

    await bm.close()
    logger.info("Job application run completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())
