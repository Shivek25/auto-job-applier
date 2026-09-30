# src/scraper/matcher.py
from typing import Dict, Any
from src.ai.llm_client import LLMClient
from src.ai.prompts import JOB_MATCH_PROMPT
from src.resume.models import MasterProfile

class JobMatcher:
    def __init__(self, llm_client: LLMClient, min_score: int = 70):
        self.llm = llm_client
        self.min_score = min_score

    def evaluate(self, master_profile: MasterProfile, job_description: str) -> Dict[str, Any]:
        prompt = (
            JOB_MATCH_PROMPT
            .replace("{profile_json}", master_profile.model_dump_json(indent=2))
            .replace("{job_description}", job_description)
        )
        res = self.llm.generate_json(prompt)
        score = int(res.get("match_score", 0))
        return {
            "is_match": score >= self.min_score,
            "match_score": score,
            "summary_reason": res.get("summary_reason", ""),
            "missing_critical_skills": res.get("missing_critical_skills", []),
            "matched_skills": res.get("matched_skills", [])
        }
