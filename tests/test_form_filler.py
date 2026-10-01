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

    # Test deterministic solver (0 tokens, no mock call)
    assert filler.solve_deterministically("Phone number") == "123"
    assert filler.solve_deterministically("Email address") == "a@a.com"
    assert filler.solve_deterministically("How many years of experience do you have with Python?", "number") == "2"
    assert filler.solve_deterministically("Will you require sponsorship?", "text") == "No"
    assert filler.solve_deterministically("Are you legally authorized to work?", "text") == "Yes"
    assert filler.solve_deterministically("Notice period", "number") == "15"

    # Test Indian phone format +91 stripped to 10 digits
    profile_in = MasterProfile(
        personal_info=PersonalInfo(name="Shivek", email="s@s.com", phone="+91 9650320446", location="Delhi"),
        summary="Data Engineer",
        skills=Skills(languages=["Python"])
    )
    filler_in = FormFiller(mock_llm, profile_in)
    assert filler_in.solve_deterministically("Mobile phone number") == "9650320446"
    assert filler_in.solve_deterministically("What is your expectations in terms of annual salary?") == "900000"
    assert filler_in.solve_deterministically("How many years of Hospitals and Health Care experience do you currently have?") == "2"

    # Test LLM refusal sanitization
    mock_llm.generate_json.return_value = {"answer": "Not specified in the candidate profile"}
    ans_sanitized = await filler_in.answer_question("Random custom query", "text")
    assert ans_sanitized == "Yes"


