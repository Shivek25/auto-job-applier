import pytest
from pathlib import Path
from src.resume.models import MasterProfile, PersonalInfo, Skills, EducationItem, WorkExperienceItem, ProjectItem
from src.resume.compiler import ResumeCompiler

def test_typst_resume_compilation(tmp_path):
    profile = MasterProfile(
        personal_info=PersonalInfo(
            name="Alex Dev",
            email="alex@dev.io",
            phone="+1-555-0199",
            location="San Francisco, CA",
            linkedin_url="https://linkedin.com/in/alexdev",
            github_url="https://github.com/alexdev"
        ),
        summary="Experienced Software Engineer specialized in backend systems and distributed architectures.",
        skills=Skills(
            languages=["Python", "Go"],
            frameworks=["FastAPI", "React"],
            tools_and_cloud=["Docker", "AWS"],
            databases=["PostgreSQL"]
        ),
        work_experience=[
            WorkExperienceItem(
                company="Tech Innovators",
                role="Backend Engineer",
                start_date="01/2023",
                end_date="Present",
                location="Remote",
                bullets=["Engineered event-driven microservices", "Reduced P99 latency by 35%"]
            )
        ],
        projects=[
            ProjectItem(
                name="AutoApply Copilot",
                tech_stack=["Python", "Playwright"],
                github_link="https://github.com/test/autoapply",
                bullets=["Automated multi-portal job applications"]
            )
        ],
        education=[EducationItem(institution="MIT", degree="B.S. CS", graduation_year="2024")]
    )
    
    compiler = ResumeCompiler(template_path="templates/modern_ats.typ")
    out_pdf = tmp_path / "alex_resume.pdf"
    compiler.compile_pdf(profile, out_pdf)
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 1000
