import pytest
from unittest.mock import MagicMock
from src.scraper.matcher import JobMatcher
from src.resume.models import MasterProfile, PersonalInfo, Skills

def test_job_matcher():
    mock_llm = MagicMock()
    mock_llm.generate_json.return_value = {
        "match_score": 85,
        "summary_reason": "Matches Python and FastAPI requirements perfectly",
        "missing_critical_skills": ["AWS"],
        "matched_skills": ["Python", "FastAPI"]
    }
    matcher = JobMatcher(llm_client=mock_llm, min_score=70)
    profile = MasterProfile(
        personal_info=PersonalInfo(name="Test", email="t@t.com", phone="123", location="Remote"),
        summary="Backend dev",
        skills=Skills(languages=["Python"], frameworks=["FastAPI"])
    )
    result = matcher.evaluate(profile, "Looking for Python and FastAPI developer.")
    assert result["is_match"] is True
    assert result["match_score"] == 85
    assert "Python" in result["matched_skills"]

    # Test experience mismatch (> 2 years)
    exp_res = matcher.evaluate(profile, "Requires 4+ years of work experience with Python.", job_title="Python Developer")
    assert exp_res["is_match"] is False
    assert exp_res["match_score"] == 20
    assert "Requires 4+ years" in exp_res["summary_reason"]

    # Test Senior title rejection
    sr_res = matcher.evaluate(profile, "Looking for a developer.", job_title="Senior Data Engineer")
    assert sr_res["is_match"] is False
    assert "Senior" in sr_res["summary_reason"]

