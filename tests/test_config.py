import pytest
from pathlib import Path
from src.config_loader import load_config, AppConfig

def test_load_config_default(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
app:
  mode: auto
  daily_application_limit: 25
  min_match_score: 70
search:
  job_titles:
    - "Full Stack Developer"
    - "Python Developer"
  locations:
    - "Remote"
platforms:
  linkedin: true
  indeed: true
llm:
  provider: "gemini"
  model: "gemini-2.0-flash"
""")
    config = load_config(config_file)
    assert isinstance(config, AppConfig)
    assert config.app.mode == "auto"
    assert config.app.daily_application_limit == 25
    assert config.app.min_match_score == 70
    assert "Remote" in config.search.locations

def test_load_config_missing_file():
    config = load_config("non_existent_file.yaml")
    assert isinstance(config, AppConfig)
    assert config.app.mode == "auto"
