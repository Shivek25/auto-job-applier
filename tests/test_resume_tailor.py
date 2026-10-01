import pytest
from unittest.mock import MagicMock
from src.resume.models import MasterProfile, PersonalInfo, Skills
from src.resume.tailor import ResumeTailor

def test_resume_tailor():
    mock_llm = MagicMock()
    mock_llm.generate_json.return_value = {
        "personal_info": {
            "name": "Alex Dev",
            "email": "alex@dev.io",
            "phone": "+1-555-0199",
            "location": "San Francisco, CA"
        },
        "summary": "Tailored Python & React summary matching JD.",
        "skills": {
            "languages": ["Python"],
            "frameworks": ["FastAPI"],
            "tools_and_cloud": ["Docker"],
            "databases": ["PostgreSQL"]
        },
        "work_experience": [],
        "projects": [],
        "education": []
    }
    tailor = ResumeTailor(mock_llm)
    profile = MasterProfile(
        personal_info=PersonalInfo(name="Alex Dev", email="alex@dev.io", phone="123", location="SF"),
        summary="Generic summary",
        skills=Skills(languages=["Python", "C++"], frameworks=["FastAPI", "Django"])
    )
    tailored = tailor.tailor(profile, "Job description requiring Python and FastAPI")
    assert tailored.summary == "Tailored Python & React summary matching JD."
    assert "Python" in tailored.skills.languages

def test_resume_tailor_heuristic_fallback():
    mock_llm = MagicMock()
    mock_llm.generate_json.side_effect = Exception("API rate limited")
    tailor = ResumeTailor(mock_llm)
    profile = MasterProfile(
        personal_info=PersonalInfo(name="Shivek Sharma", email="s@s.com", phone="123", location="Delhi"),
        summary="Data Engineer experienced in pipelines.",
        skills=Skills(languages=["SQL", "Python"], databases=["Snowflake", "MySQL"])
    )
    jd = "We are seeking a Python specialist with extensive Snowflake experience."
    tailored = tailor.tailor(profile, jd)
    # Python should be moved to first in languages
    assert tailored.skills.languages[0] == "Python"
    # Summary should mention specialized focus on matched skills
    assert "specialized focus" in tailored.summary.lower()
