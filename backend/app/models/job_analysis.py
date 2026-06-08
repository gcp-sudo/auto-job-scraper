from pydantic import BaseModel, Field
from typing import List, Optional

class JobAnalysisSchema(BaseModel):
    title: str = Field(description="The formal clean engineering job title.")
    company: str = Field(description="The name of the company hiring.")
    required_skills: List[str] = Field(description="Strict required technical core tools, languages or frameworks.")
    nice_to_have_skills: List[str] = Field(description="Preferred, secondary or beneficial skills listed.")
    remote_policy: str = Field(description="Must evaluate strictly to either: 'remote', 'hybrid', or 'onsite'.")
    requires_sponsorship: bool = Field(description="True if description explicitly mentions they cannot sponsor visas or require existing authorization.")
    salary_min: Optional[float] = Field(None, description="Minimum salary boundary if found, else null.")
    salary_max: Optional[float] = Field(None, description="Maximum salary boundary if found, else null.")
    currency: Optional[str] = Field(None, description="ISO standard Currency code (e.g., USD, EUR, INR) if found.")
    seniority: str = Field(description="Calculated experience profile: 'Junior', 'Mid', 'Senior', or 'Lead'.")