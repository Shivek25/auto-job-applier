import pytest
from unittest.mock import MagicMock
from src.applier.form_filler import FormFiller
from src.resume.models import MasterProfile, PersonalInfo, Skills

@pytest.mark.asyncio
async def test_form_filler_answer():
    mock_llm = MagicMock()
    mock_llm.generate_json.return_value = {"answer": "3", "confidence": 0.95}
    profile = MasterProfile(
        personal_info=PersonalInfo(name="Alex", email="a@a.com", phone="123", location="Remote"),
        summary="Dev",
        skills=Skills(languages=["Python"])
    )
    filler = FormFiller(mock_llm, profile)
    ans = await filler.answer_question("How many years of Python experience do you have?", "number")
    assert ans == "3"
