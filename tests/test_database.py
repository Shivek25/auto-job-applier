import pytest
from pathlib import Path
from src.storage.database import Database

def test_database_init_and_crud(tmp_path):
    db_path = tmp_path / "test_applications.db"
    db = Database(db_path)
    
    # Test record insertion
    app_id = db.add_application(
        job_id="li-12345",
        platform="linkedin",
        title="Full Stack Engineer",
        company="Acme Corp",
        location="Remote",
        job_url="https://linkedin.com/jobs/view/12345",
        match_score=85,
        status="PENDING"
    )
    assert app_id > 0
    
    # Test check if applied
    assert db.is_already_applied("li-12345") is True
    assert db.is_already_applied("li-99999") is False
    
    # Test status update
    db.update_status(
        job_id="li-12345",
        status="SUBMITTED",
        resume_path="storage/tailored_resumes/li-12345.pdf",
        screenshot_path="storage/receipts/li-12345.png"
    )
    
    record = db.get_application("li-12345")
    assert record["status"] == "SUBMITTED"
    assert record["resume_path"] == "storage/tailored_resumes/li-12345.pdf"
    assert record["screenshot_path"] == "storage/receipts/li-12345.png"

    # Test stats
    stats = db.get_stats()
    assert stats["total_submitted"] == 1
    assert stats["total"] == 1
