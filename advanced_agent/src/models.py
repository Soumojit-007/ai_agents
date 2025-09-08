from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator

class CompanyAnalysis(BaseModel):
    """Structured output for LLM company analysis focused on developer tools"""
    pricing_model: str
    is_open_source: Optional[bool] = None
    tech_stack: List[str] = Field(default_factory=list)
    description: str = ""
    api_available: Optional[bool] = None
    language_support: List[str] = Field(default_factory=list)
    integration_capabilities: List[str] = Field(default_factory=list)

    @validator("tech_stack", "language_support", "integration_capabilities", pre=True, always=True)
    def ensure_list(cls, v):
        return v or []

class CompanyInfo(BaseModel):
    """Structured information about a company/tool"""
    name: str
    description: str
    website: Optional[str] = None
    pricing_model: Optional[str] = None
    is_open_source: Optional[bool] = None
    tech_stack: List[str] = Field(default_factory=list)  # corrected
    competitors: List[str] = Field(default_factory=list)
    api_available: Optional[bool] = None
    language_support: List[str] = Field(default_factory=list)
    integration_capabilities: List[str] = Field(default_factory=list)
    developer_experience_rating: Optional[str] = None

    @validator("tech_stack", "competitors", "language_support", "integration_capabilities", pre=True, always=True)
    def ensure_list(cls, v):
        return v or []

class ResearchState(BaseModel):
    query: str
    extracted_tools: List[str] = Field(default_factory=list)
    companies: List[CompanyInfo] = Field(default_factory=list)
    search_results: List[Dict[str, Any]] = Field(default_factory=list)
    analysis: Optional[str] = None

    @validator("extracted_tools", "companies", "search_results", pre=True, always=True)
    def ensure_list(cls, v):
        return v or []
