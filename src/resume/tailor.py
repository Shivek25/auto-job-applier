# src/resume/tailor.py
from src.ai.llm_client import LLMClient
from src.ai.prompts import RESUME_TAILOR_PROMPT
from src.resume.models import MasterProfile

class ResumeTailor:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def tailor(self, master_profile: MasterProfile, job_description: str) -> MasterProfile:
        prompt = (
            RESUME_TAILOR_PROMPT
            .replace("{profile_json}", master_profile.model_dump_json(indent=2))
            .replace("{job_description}", job_description)
        )
        tailored_data = self.llm.generate_json(prompt)
        return MasterProfile(**tailored_data)
