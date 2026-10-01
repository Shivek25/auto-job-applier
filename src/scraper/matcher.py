# src/scraper/matcher.py
import re
import logging
from typing import Dict, Any, List, Optional
from src.ai.llm_client import LLMClient
from src.ai.prompts import JOB_MATCH_PROMPT
from src.resume.models import MasterProfile

logger = logging.getLogger(__name__)

class JobMatcher:
    def __init__(self, llm_client: LLMClient, min_score: int = 70, max_experience_years: int = 2):
        self.llm = llm_client
        self.min_score = min_score
        self.max_experience_years = max_experience_years

    def check_experience_mismatch(self, job_description: str, job_title: str = "") -> Optional[str]:
        title_lower = job_title.lower()
        desc_lower = job_description.lower()

        # 1. Check Seniority in Title
        senior_indicators = [
            "senior", "sr.", "sr ", "lead", "principal", "staff",
            "architect", "director", "manager", "head of", "vp"
        ]
        for sr in senior_indicators:
            if re.search(r'\b' + re.escape(sr) + r'\b', title_lower):
                return f"Title specifies senior role ('{sr.title()}'), exceeding max {self.max_experience_years} years experience"

        # 2. Check Experience in Description
        exp_patterns = [
            r'(?:proven\s+experience|work\s+experience|experience|exp|hands-on)[\s\(\:\-]*(\d+)\s*\+?\s*(?:to|-)?\s*(\d+)?\s*(?:years?|yrs?)',
            r'(\d+)\s*\+?\s*(?:to|-)?\s*(\d+)?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:work\s+)?experience',
            r'(?:minimum|at\s+least|min\.?)\s*(\d+)\s*\+?\s*(?:years?|yrs?)',
            r'(\d+)\s*\+?\s*(?:years?|yrs?)\s+(?:in|with|of)'
        ]

        found_years = []
        for pat in exp_patterns:
            for match in re.finditer(pat, desc_lower):
                groups = match.groups()
                if groups and groups[0]:
                    y1 = int(groups[0])
                    y2 = int(groups[1]) if len(groups) > 1 and groups[1] else None
                    min_yr = min(y1, y2) if y2 is not None else y1
                    found_years.append((min_yr, y1, y2))

        # Check if any strict requirement exceeds candidate's max experience
        exceeded = [y for y in found_years if y[0] > self.max_experience_years]
        if exceeded:
            req = exceeded[0][1]
            return f"Requires {req}+ years of experience, exceeding candidate max of {self.max_experience_years} years"

        return None

    def _extract_skills(self, master_profile: MasterProfile) -> List[str]:
        skills = []
        for cat, sk_list in master_profile.skills.model_dump().items():
            for s in sk_list:
                s_clean = s.strip().lower()
                if len(s_clean) >= 2:
                    skills.append(s_clean)
        return list(set(skills))

    def evaluate_heuristic(self, master_profile: MasterProfile, job_description: str, job_title: str = "") -> Dict[str, Any]:
        # Fast reject if experience requirements exceeded
        exp_mismatch = self.check_experience_mismatch(job_description, job_title)
        if exp_mismatch:
            return {
                "is_match": False,
                "match_score": 20,
                "summary_reason": exp_mismatch,
                "matched_skills": [],
                "missing_critical_skills": ["Experience requirement exceeded"]
            }

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

