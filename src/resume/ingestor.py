# src/resume/ingestor.py
import json
from pathlib import Path
import pdfplumber
from src.ai.llm_client import LLMClient
from src.ai.prompts import CV_EXTRACTION_PROMPT
from src.resume.models import MasterProfile

class CVIngestor:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def extract_text_from_pdf(self, pdf_path: Path | str) -> str:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text.strip()

    def ingest_cv(self, pdf_path: Path | str, output_json: Path | str = "config/master_profile.json") -> MasterProfile:
        raw_text = self.extract_text_from_pdf(pdf_path)
        prompt = f"{CV_EXTRACTION_PROMPT}\n\nCandidate Resume Raw Text:\n{raw_text}"
        data = self.llm.generate_json(prompt)
        profile = MasterProfile(**data)
        
        out_path = Path(output_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(profile.model_dump_json(indent=2))
        return profile
