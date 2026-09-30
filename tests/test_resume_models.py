import pytest
from src.resume.models import MasterProfile, PersonalInfo, Skills, WorkExperienceItem, ProjectItem, EducationItem

def test_master_profile_validation():
    data = {
        "personal_info": {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "+1234567890",
            "location": "New York, USA",
            "linkedin_url": "https://linkedin.com/in/janedoe"
        },
        "summary": "Full Stack Developer with 3+ years experience.",
        "skills": {
            "languages": ["Python", "TypeScript"],
            "frameworks": ["FastAPI", "React"],
            "tools_and_cloud": ["Git", "Docker"],
            "databases": ["PostgreSQL"]
        },
        "work_experience": [
            {
                "company": "Tech Corp",
                "role": "Software Engineer",
                "start_date": "01/2023",
                "end_date": "Present",
                "location": "Remote",
                "bullets": ["Engineered high-throughput pipelines"]
            }
        ],
        "projects": [
            {
                "name": "AI Job Copilot",
                "tech_stack": ["Python", "Playwright"],
                "github_link": "https://github.com/test/copilot",
                "bullets": ["Automated multi-step portal workflows"]
            }
        ],
        "education": [
            {
                "institution": "MIT",
                "degree": "B.S. Computer Science",
                "graduation_year": "2024"
            }
        ]
    }
    profile = MasterProfile(**data)
    assert profile.personal_info.name == "Jane Doe"
    assert "Python" in profile.skills.languages
    assert profile.work_experience[0].company == "Tech Corp"
    assert profile.projects[0].name == "AI Job Copilot"
