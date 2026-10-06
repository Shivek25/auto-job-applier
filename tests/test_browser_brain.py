import pytest
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from src.applier.brain import BrowserBrain
from src.resume.models import MasterProfile, PersonalInfo, Skills

@pytest.fixture
def sample_profile():
    return MasterProfile(
        personal_info=PersonalInfo(
            name="Shivek Sharma",
            email="shivek@example.com",
            phone="+919876543210",
            location="Noida, India"
        ),
        summary="Data Engineer and Analytics Specialist",
        skills=Skills(languages=["Python", "SQL"], frameworks=["FastAPI"], databases=["Snowflake"])
    )

def test_brain_memory(tmp_path, sample_profile):
    mem_file = tmp_path / "brain_memory.json"
    mock_llm = MagicMock()
    brain = BrowserBrain(llm_client=mock_llm, master_profile=sample_profile, memory_path=str(mem_file))
    
    assert brain.get_learned_rule("linkedin.com", "URL_DRIFT") is None
    
    brain.save_learned_rule("linkedin.com", "URL_DRIFT", {
        "strategy": "NAVIGATE_BACK",
        "action": "go_back"
    })
    
    rule = brain.get_learned_rule("linkedin.com", "URL_DRIFT")
    assert rule is not None
    assert rule["strategy"] == "NAVIGATE_BACK"
    
    # Reload from file to ensure persistence
    brain2 = BrowserBrain(llm_client=mock_llm, master_profile=sample_profile, memory_path=str(mem_file))
    rule2 = brain2.get_learned_rule("linkedin.com", "URL_DRIFT")
    assert rule2["action"] == "go_back"

@pytest.mark.asyncio
async def test_brain_diagnose_and_heal_url_drift(tmp_path, sample_profile):
    mem_file = tmp_path / "brain_memory.json"
    mock_llm = MagicMock()
    mock_llm.generate_json.return_value = {
        "diagnosis": "Navigated to company life page instead of remaining on job posting",
        "obstacle_type": "URL_DRIFT",
        "recommended_strategy": "NAVIGATE_BACK",
        "action_details": {"action": "go_back"},
        "learned_rule": "Avoid clicking company life anchor links"
    }
    
    brain = BrowserBrain(llm_client=mock_llm, master_profile=sample_profile, memory_path=str(mem_file))
    
    mock_page = AsyncMock()
    mock_page.url = "https://www.linkedin.com/company/acme/life/"
    mock_page.title.return_value = "Life at Acme"
    mock_page.frames = [mock_page]
    mock_page.evaluate.return_value = {
        "dialogs": [],
        "interactive_elements": [{"index": 0, "tag": "button", "text": "Home"}],
        "validation_errors": []
    }
    
    healed = await brain.diagnose_and_heal(
        mock_page,
        goal="locate_easy_apply",
        context={"job_url": "https://www.linkedin.com/jobs/view/123456"}
    )
    
    assert healed is True
    mock_page.go_back.assert_called_once()
    assert brain.get_learned_rule("www.linkedin.com", "URL_DRIFT") is not None

@pytest.mark.asyncio
async def test_brain_diagnose_and_heal_dismiss_overlay(tmp_path, sample_profile):
    mem_file = tmp_path / "brain_memory.json"
    mock_llm = MagicMock()
    mock_llm.generate_json.return_value = {
        "diagnosis": "Sign-in or feedback dialog overlay is blocking the application form",
        "obstacle_type": "MODAL_OVERLAY",
        "recommended_strategy": "DISMISS_OVERLAY",
        "action_details": {"action": "dismiss", "element_selector": "button[aria-label='Dismiss']"},
        "learned_rule": "Click dismiss on contextual modal"
    }
    
    brain = BrowserBrain(llm_client=mock_llm, master_profile=sample_profile, memory_path=str(mem_file))
    
    mock_page = AsyncMock()
    mock_page.url = "https://www.linkedin.com/jobs/view/123456"
    mock_page.title.return_value = "Data Analyst Job"
    mock_page.frames = [mock_page]
    mock_page.evaluate.return_value = {
        "dialogs": ["Sign in to continue"],
        "interactive_elements": [{"index": 0, "tag": "button", "text": "Dismiss"}],
        "validation_errors": []
    }
    mock_dismiss_btn = AsyncMock()
    mock_page.query_selector.return_value = mock_dismiss_btn
    
    healed = await brain.diagnose_and_heal(
        mock_page,
        goal="unblock_wizard_step",
        context={"step": 1}
    )
    
    assert healed is True
    mock_dismiss_btn.click.assert_called_once()

@pytest.mark.asyncio
async def test_brain_dismiss_fallback_escape(tmp_path, sample_profile):
    mem_file = tmp_path / "brain_memory.json"
    mock_llm = MagicMock()
    mock_llm.generate_json.return_value = {
        "diagnosis": "Modal overlay without standard dismiss button",
        "obstacle_type": "MODAL_OVERLAY",
        "recommended_strategy": "DISMISS_OVERLAY",
        "action_details": {"action": "dismiss"},
        "learned_rule": "Press Escape on modal overlay"
    }
    
    brain = BrowserBrain(llm_client=mock_llm, master_profile=sample_profile, memory_path=str(mem_file))
    
    mock_page = AsyncMock()
    mock_page.url = "https://www.linkedin.com/jobs/view/123456"
    mock_page.title.return_value = "Data Analyst Job"
    mock_page.frames = [mock_page]
    mock_page.evaluate.return_value = {
        "dialogs": ["Modal"],
        "interactive_elements": [],
        "validation_errors": []
    }
    mock_page.query_selector.return_value = None
    
    healed = await brain.diagnose_and_heal(
        mock_page,
        goal="unblock_wizard_step"
    )
    
    assert healed is True
    mock_page.keyboard.press.assert_called_with("Escape")

@pytest.mark.asyncio
async def test_brain_diagnose_and_heal_answer_field(tmp_path, sample_profile):
    mem_file = tmp_path / "brain_memory.json"
    mock_llm = MagicMock()
    mock_llm.generate_json.return_value = {
        "diagnosis": "Missing required field: Experience in Python",
        "obstacle_type": "VALIDATION_ERROR",
        "recommended_strategy": "ANSWER_FIELD",
        "action_details": {"action": "answer", "element_index": 1, "value_to_fill": "2"},
        "learned_rule": "Answer 2 for Python experience"
    }
    
    brain = BrowserBrain(llm_client=mock_llm, master_profile=sample_profile, memory_path=str(mem_file))
    
    mock_page = AsyncMock()
    mock_page.url = "https://www.linkedin.com/jobs/view/123456"
    mock_page.title.return_value = "Job Application"
    mock_page.frames = [mock_page]
    mock_page.evaluate.side_effect = [
        # 1. First inspect_page_state
        {
            "dialogs": ["Application Form"],
            "interactive_elements": [
                {"index": 0, "tag": "button", "text": "Next"},
                {"index": 1, "tag": "input", "text": "", "id": "exp_python"}
            ],
            "validation_errors": ["Please enter a valid answer"]
        },
        # 2. evaluate in execute_recovery (filling input)
        True
    ]
    
    healed = await brain.diagnose_and_heal(
        mock_page,
        goal="unblock_wizard_step"
    )
    
    assert healed is True
