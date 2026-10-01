# src/scraper/matcher.py
import re
import logging
from typing import Dict, Any, List
from src.ai.llm_client import LLMClient
from src.ai.prompts import JOB_MATCH_PROMPT
from src.resume.models import MasterProfile

logger = logging.getLogger(__name__)

class JobMatcher:
    def __init__(self, llm_client: LLMClient, min_score: int = 70):
        self.llm = llm_client
        self.min_score = min_score

    def _extract_skills(self, master_profile: MasterProfile) -> List[str]:
        skills = []
        for cat, sk_list in master_profile.skills.model_dump().items():
            for s in sk_list:
                s_clean = s.strip().lower()
                if len(s_clean) >= 2:
                    skills.append(s_clean)
        return list(set(skills))

    def evaluate_heuristic(self, master_profile: MasterProfile, job_description: str, job_title: str = "") -> Dict[str, Any]:
        skills = self._extract_skills(master_profile)
        desc_lower = job_description.lower()
        title_lower = job_title.lower()

        matched_skills = []
        for sk in skills:
            pattern = r'\b' + re.escape(sk) + r'\b'
            if re.search(pattern, desc_lower) or sk in title_lower:
                matched_skills.append(sk)

        # Baseline score calculation
        score = 40
        
        # Title alignment bonus
        target_roles = ["data", "engineer", "analyst", "analytics", "sql", "etl", "bi", "snowflake", "bigquery", "database"]
        if any(role in title_lower for role in target_roles):
            score += 25

        # Irrelevant role penalty
        irrelevant_roles = ["frontend", "react", "android", "ios", "sales", "hr", "marketing", "content", "accountant"]
        if any(role in title_lower for role in irrelevant_roles):
            score -= 30

        # Skill match bonus (5 points per matched skill, up to 35 max)
        score += min(35, len(matched_skills) * 5)
        score = max(10, min(95, score))

        is_match = score >= self.min_score
        reason = f"Heuristic match: {len(matched_skills)} matched skills ({', '.join(matched_skills[:4])})" if matched_skills else "Heuristic evaluation based on title and keywords"

        return {
            "is_match": is_match,
            "match_score": score,
            "summary_reason": reason,
            "matched_skills": matched_skills,
            "missing_critical_skills": []
        }

    def evaluate(self, master_profile: MasterProfile, job_description: str, job_title: str = "") -> Dict[str, Any]:
        # Fast heuristic evaluation first (instant, 0 tokens)
        heuristic = self.evaluate_heuristic(master_profile, job_description, job_title)
        
        # If decisively high match (>= 75%) or decisively low (< 50%), use heuristic directly
        if heuristic["match_score"] >= 75 or heuristic["match_score"] < 50:
            return heuristic

        # Otherwise evaluate via LLM for borderline cases
        try:
            prompt = (
                JOB_MATCH_PROMPT
                .replace("{profile_json}", master_profile.model_dump_json(indent=2))
                .replace("{job_description}", job_description)
            )
            res = self.llm.generate_json(prompt)
            score = int(res.get("match_score", heuristic["match_score"]))
            return {
                "is_match": score >= self.min_score,
                "match_score": score,
                "summary_reason": res.get("summary_reason", heuristic["summary_reason"]),
                "missing_critical_skills": res.get("missing_critical_skills", []),
                "matched_skills": res.get("matched_skills", heuristic["matched_skills"])
            }
        except Exception as e:
            logger.warning(f"LLM matcher fallback to heuristic scoring ({e})")
            return heuristic

