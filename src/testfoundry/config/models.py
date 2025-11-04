"""
Configuration models for the test framework generator.
Defines the structure and validation for generator configuration.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from .validation import ConfigValidator


@dataclass
class GeneratorConfig:
    """Configuration for generating a test automation framework"""
    
    # Project details
    project_name: str
    site_name: str
    base_url: str
    
    # Test types to include
    include_accessibility: bool = False
    include_lighthouse: bool = False
    include_broken_links: bool = False
    include_seo: bool = False
    
    # Report configuration
    html_reports: bool = True
    
    # CI/CD configuration
    github_actions: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate()
    
    def _validate(self):
        """Validate configuration values using advanced validation"""
        validation_errors = ConfigValidator.get_validation_summary(
            self.project_name, self.site_name, self.base_url
        )
        
        if validation_errors:
            error_message = "Configuration validation failed:\\n" + "\\n".join(validation_errors)
            raise ValueError(error_message)
    
    def get_enabled_test_types(self) -> List[str]:
        """Get list of enabled test types"""
        enabled = []
        if self.include_accessibility:
            enabled.append('Accessibility')
        if self.include_lighthouse:
            enabled.append('Lighthouse')
        if self.include_broken_links:
            enabled.append('Broken Links')
        if self.include_seo:
            enabled.append('SEO')
        return enabled
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'project_name': self.project_name,
            'site_name': self.site_name,
            'base_url': self.base_url,
            'include_accessibility': self.include_accessibility,
            'include_lighthouse': self.include_lighthouse,
            'include_broken_links': self.include_broken_links,
            'include_seo': self.include_seo,
            'html_reports': self.html_reports,
            'github_actions': self.github_actions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneratorConfig':
        """Create config from dictionary"""
        return cls(**data)