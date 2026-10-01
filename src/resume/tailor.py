# src/resume/tailor.py
import logging
from src.ai.llm_client import LLMClient
from src.ai.prompts import RESUME_TAILOR_PROMPT
from src.resume.models import MasterProfile

logger = logging.getLogger(__name__)

class ResumeTailor:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def tailor(self, master_profile: MasterProfile, job_description: str) -> MasterProfile:
        try:
            prompt = (
                RESUME_TAILOR_PROMPT
                .replace("{profile_json}", master_profile.model_dump_json(indent=2))
                .replace("{job_description}", job_description)
            )
            tailored_data = self.llm.generate_json(prompt)
            tailored = MasterProfile(**tailored_data)
            logger.info(f"✨ Resume tailored successfully! Customized Summary: \"{tailored.summary[:90]}...\"")
            return tailored
        except Exception as e:
            logger.warning(f"AI tailoring encountered issue ({e}). Applying intelligent keyword-aligned ATS adaptation...")
            return self._heuristic_tailor(master_profile, job_description)

    def _heuristic_tailor(self, profile: MasterProfile, jd: str) -> MasterProfile:
        """Heuristic ATS keyword prioritization if LLM call is unavailable."""
        jd_lower = jd.lower()
        data = profile.model_dump()
        
        # Prioritize matching skills to top of each category
        for cat in ["languages", "frameworks", "tools_and_cloud", "databases"]:
            skills_list = data.get("skills", {}).get(cat, [])
            matched = [s for s in skills_list if s.lower() in jd_lower]
            unmatched = [s for s in skills_list if s.lower() not in jd_lower]
            data["skills"][cat] = matched + unmatched

        # Extract top matched skills for summary enhancement
        all_skills = (
            data.get("skills", {}).get("languages", []) +
            data.get("skills", {}).get("frameworks", []) +
            data.get("skills", {}).get("databases", [])
        )
        top_matched = [s for s in all_skills if s.lower() in jd_lower][:3]
        if top_matched:
            skill_focus = ", ".join(top_matched)
            data["summary"] = f"{profile.summary.rstrip('.')} with specialized focus on {skill_focus} solutions."

        return MasterProfile(**data)
