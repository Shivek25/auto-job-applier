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
