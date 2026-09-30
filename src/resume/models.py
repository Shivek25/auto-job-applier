# src/resume/models.py
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class PersonalInfo(BaseModel):
    name: str
    email: str
    phone: str
    location: str
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

class Skills(BaseModel):
    languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    tools_and_cloud: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)

class WorkExperienceItem(BaseModel):
    company: str
    role: str
    start_date: str
    end_date: str
    location: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)

class ProjectItem(BaseModel):
    name: str
    tech_stack: List[str] = Field(default_factory=list)
    github_link: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)

class EducationItem(BaseModel):
    institution: str
    degree: str
    graduation_year: str

class MasterProfile(BaseModel):
    personal_info: PersonalInfo
    summary: str
    skills: Skills
    work_experience: List[WorkExperienceItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
