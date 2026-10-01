from pathlib import Path
from typing import List, Optional
import yaml
from pydantic import BaseModel, Field

class AppSettings(BaseModel):
    mode: str = Field(default="auto", description="auto or review")
    daily_application_limit: int = Field(default=25, ge=1, le=100)
    min_match_score: int = Field(default=70, ge=0, le=100)
    delay_between_applications_min: int = Field(default=45)
    delay_between_applications_max: int = Field(default=120)

class SearchSettings(BaseModel):
    job_titles: List[str] = Field(default_factory=lambda: ["Software Engineer"])
    locations: List[str] = Field(default_factory=lambda: ["Remote"])
    distance_miles: int = Field(default=50)
    is_remote: bool = Field(default=True)
    results_wanted: int = Field(default=20)
    hours_old: int = Field(default=336, description="Max job age in hours (336 = 14 days / 2 weeks)")
    easy_apply_only: bool = Field(default=True)

class PlatformSettings(BaseModel):
    linkedin: bool = Field(default=True)
    indeed: bool = Field(default=True)

class LLMSettings(BaseModel):
    provider: str = Field(default="gemini") # gemini, groq, ollama
    model: str = Field(default="gemini-3.5-flash-lite")
    api_key: Optional[str] = None
    ollama_base_url: str = Field(default="http://localhost:11434")

class BrowserSettings(BaseModel):
    headless: bool = Field(default=False)
    chrome_user_data_dir: Optional[str] = None
    chrome_profile_name: str = Field(default="Default")

class AppConfig(BaseModel):
    app: AppSettings = Field(default_factory=AppSettings)
    search: SearchSettings = Field(default_factory=SearchSettings)
    platforms: PlatformSettings = Field(default_factory=PlatformSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    browser: BrowserSettings = Field(default_factory=BrowserSettings)

def load_config(config_path: Path | str = "config/config.yaml") -> AppConfig:
    path = Path(config_path)
    if not path.exists():
        return AppConfig()
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return AppConfig(**data)
