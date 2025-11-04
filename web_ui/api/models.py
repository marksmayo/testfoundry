"""
API models for the web UI.
Defines request/response models for the REST API.
"""

from pydantic import BaseModel, HttpUrl, Field, validator
from typing import List, Optional
from enum import Enum


class TestType(str, Enum):
    """Available test types"""
    ACCESSIBILITY = "accessibility"
    LIGHTHOUSE = "lighthouse"
    BROKEN_LINKS = "broken_links"
    SEO = "seo"


class GeneratorRequest(BaseModel):
    """Request model for framework generation"""
    project_name: str = Field(..., min_length=3, max_length=50, description="Project folder name")
    site_name: str = Field(..., min_length=2, max_length=100, description="Site name for documentation")
    base_url: HttpUrl = Field(..., description="Base URL of the site to test")
    test_types: List[TestType] = Field(default=[], description="Test types to include")
    html_reports: bool = Field(default=True, description="Generate HTML reports")
    github_actions: bool = Field(default=False, description="Generate GitHub Actions workflow")

    @validator('project_name')
    def validate_project_name(cls, v):
        """Validate project name format"""
        import re
        if not re.match(r'^[a-zA-Z0-9_\-]+$', v):
            raise ValueError('Project name can only contain letters, numbers, hyphens, and underscores')

        reserved_names = {'test', 'tests', 'src', 'lib', 'bin', 'config', 'utils', 'pages'}
        if v.lower() in reserved_names:
            raise ValueError(f"'{v}' is a reserved name, please choose a different name")

        return v


class ValidationError(BaseModel):
    """Validation error model"""
    field: str
    message: str


class ValidationResponse(BaseModel):
    """Response model for validation"""
    valid: bool
    errors: List[ValidationError] = []
    suggestions: List[str] = []


class GenerationStatus(str, Enum):
    """Generation status values"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationStep(BaseModel):
    """Individual generation step"""
    name: str
    status: GenerationStatus
    message: Optional[str] = None
    timestamp: Optional[str] = None


class GenerationProgress(BaseModel):
    """Progress tracking for generation"""
    job_id: str
    status: GenerationStatus
    progress_percent: int = 0
    current_step: int = 0
    total_steps: int = 0
    steps: List[GenerationStep] = []
    message: Optional[str] = None
    error: Optional[str] = None
    created_files: List[str] = []
    project_name: Optional[str] = None
    project_path: Optional[str] = None


class GenerationResponse(BaseModel):
    """Response model for generation request"""
    job_id: str
    status: GenerationStatus
    message: str


class FileInfo(BaseModel):
    """Information about a generated file"""
    path: str
    name: str
    size: int
    type: str  # 'file' or 'directory'
    content_preview: Optional[str] = None


class ProjectStructure(BaseModel):
    """Generated project structure"""
    project_name: str
    files: List[FileInfo]
    total_files: int
    total_size: int


class ConfigPreset(BaseModel):
    """Configuration preset model"""
    name: str
    description: str
    config: GeneratorRequest


class SystemInfo(BaseModel):
    """System information"""
    python_version: str
    platform: str
    available_presets: List[ConfigPreset]
    supported_test_types: List[TestType]