"""
Unit tests for configuration models.
"""

import pytest
import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from framework_generator.config.models import GeneratorConfig


class TestGeneratorConfig:
    """Test the GeneratorConfig class"""
    
    def test_valid_configuration(self):
        """Test that valid configuration is accepted"""
        config = GeneratorConfig(
            project_name="test_project",
            site_name="Test Site",
            base_url="https://example.com"
        )
        
        assert config.project_name == "test_project"
        assert config.site_name == "Test Site"
        assert config.base_url == "https://example.com"
        assert config.include_accessibility is False  # default
        assert config.html_reports is True  # default
    
    def test_configuration_with_all_options(self):
        """Test configuration with all options enabled"""
        config = GeneratorConfig(
            project_name="full_project",
            site_name="Full Site",
            base_url="https://full.example.com",
            include_accessibility=True,
            include_lighthouse=True,
            include_broken_links=True,
            include_seo=True,
            html_reports=False,
            github_actions=True
        )
        
        assert config.include_accessibility is True
        assert config.include_lighthouse is True
        assert config.include_broken_links is True
        assert config.include_seo is True
        assert config.html_reports is False
        assert config.github_actions is True
    
    def test_empty_project_name_raises_error(self):
        """Test that empty project name raises ValueError"""
        with pytest.raises(ValueError, match="Project name is required"):
            GeneratorConfig(
                project_name="",
                site_name="Test Site",
                base_url="https://example.com"
            )
    
    def test_whitespace_project_name_raises_error(self):
        """Test that whitespace-only project name raises ValueError"""
        with pytest.raises(ValueError, match="Project name is required"):
            GeneratorConfig(
                project_name="   ",
                site_name="Test Site",
                base_url="https://example.com"
            )
    
    def test_empty_site_name_raises_error(self):
        """Test that empty site name raises ValueError"""
        with pytest.raises(ValueError, match="Site name is required"):
            GeneratorConfig(
                project_name="test_project",
                site_name="",
                base_url="https://example.com"
            )
    
    def test_empty_base_url_raises_error(self):
        """Test that empty base URL raises ValueError"""
        with pytest.raises(ValueError, match="Base URL is required"):
            GeneratorConfig(
                project_name="test_project",
                site_name="Test Site",
                base_url=""
            )
    
    def test_invalid_base_url_raises_error(self):
        """Test that invalid base URL raises ValueError"""
        with pytest.raises(ValueError, match="Base URL must start with http"):
            GeneratorConfig(
                project_name="test_project",
                site_name="Test Site",
                base_url="not-a-url"
            )
    
    def test_base_url_without_protocol_raises_error(self):
        """Test that base URL without protocol raises ValueError"""
        with pytest.raises(ValueError, match="Base URL must start with http"):
            GeneratorConfig(
                project_name="test_project",
                site_name="Test Site",
                base_url="example.com"
            )
    
    def test_get_enabled_test_types_none(self):
        """Test get_enabled_test_types with no test types enabled"""
        config = GeneratorConfig(
            project_name="test_project",
            site_name="Test Site",
            base_url="https://example.com"
        )
        
        enabled_types = config.get_enabled_test_types()
        assert enabled_types == []
    
    def test_get_enabled_test_types_some(self):
        """Test get_enabled_test_types with some test types enabled"""
        config = GeneratorConfig(
            project_name="test_project",
            site_name="Test Site",
            base_url="https://example.com",
            include_accessibility=True,
            include_seo=True
        )
        
        enabled_types = config.get_enabled_test_types()
        assert "Accessibility" in enabled_types
        assert "SEO" in enabled_types
        assert "Lighthouse" not in enabled_types
        assert "Broken Links" not in enabled_types
        assert len(enabled_types) == 2
    
    def test_get_enabled_test_types_all(self):
        """Test get_enabled_test_types with all test types enabled"""
        config = GeneratorConfig(
            project_name="test_project",
            site_name="Test Site",
            base_url="https://example.com",
            include_accessibility=True,
            include_lighthouse=True,
            include_broken_links=True,
            include_seo=True
        )
        
        enabled_types = config.get_enabled_test_types()
        expected_types = ["Accessibility", "Lighthouse", "Broken Links", "SEO"]
        assert set(enabled_types) == set(expected_types)
        assert len(enabled_types) == 4
    
    def test_to_dict(self):
        """Test converting config to dictionary"""
        config = GeneratorConfig(
            project_name="test_project",
            site_name="Test Site",
            base_url="https://example.com",
            include_accessibility=True
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["project_name"] == "test_project"
        assert config_dict["site_name"] == "Test Site"
        assert config_dict["base_url"] == "https://example.com"
        assert config_dict["include_accessibility"] is True
        assert config_dict["include_lighthouse"] is False
    
    def test_from_dict(self):
        """Test creating config from dictionary"""
        config_data = {
            "project_name": "from_dict_project",
            "site_name": "From Dict Site",
            "base_url": "https://fromdict.example.com",
            "include_accessibility": True,
            "include_lighthouse": False,
            "include_broken_links": True,
            "include_seo": False,
            "html_reports": False,
            "github_actions": True
        }
        
        config = GeneratorConfig.from_dict(config_data)
        
        assert config.project_name == "from_dict_project"
        assert config.site_name == "From Dict Site"
        assert config.base_url == "https://fromdict.example.com"
        assert config.include_accessibility is True
        assert config.include_lighthouse is False
        assert config.include_broken_links is True
        assert config.include_seo is False
        assert config.html_reports is False
        assert config.github_actions is True
    
    def test_roundtrip_serialization(self):
        """Test that config can be serialized and deserialized without loss"""
        original_config = GeneratorConfig(
            project_name="roundtrip_test",
            site_name="Roundtrip Site",
            base_url="https://roundtrip.example.com",
            include_accessibility=True,
            include_lighthouse=False,
            include_broken_links=True,
            include_seo=True,
            html_reports=False,
            github_actions=True
        )
        
        # Serialize to dict and back
        config_dict = original_config.to_dict()
        reconstructed_config = GeneratorConfig.from_dict(config_dict)
        
        # Verify all fields match
        assert original_config.project_name == reconstructed_config.project_name
        assert original_config.site_name == reconstructed_config.site_name
        assert original_config.base_url == reconstructed_config.base_url
        assert original_config.include_accessibility == reconstructed_config.include_accessibility
        assert original_config.include_lighthouse == reconstructed_config.include_lighthouse
        assert original_config.include_broken_links == reconstructed_config.include_broken_links
        assert original_config.include_seo == reconstructed_config.include_seo
        assert original_config.html_reports == reconstructed_config.html_reports
        assert original_config.github_actions == reconstructed_config.github_actions


if __name__ == "__main__":
    pytest.main([__file__])