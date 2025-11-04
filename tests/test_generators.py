"""
Unit tests for generator classes.
"""

import pytest
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from framework_generator.config.models import GeneratorConfig
from framework_generator.generators.base import BaseGenerator
from framework_generator.generators.core_generator import CoreGenerator
from framework_generator.generators.test_generator import TestGenerator


class TestBaseGenerator:
    """Test the BaseGenerator class"""
    
    def setup_method(self):
        """Set up test configuration and temporary directory"""
        self.config = GeneratorConfig(
            project_name="test_project",
            site_name="Test Site",
            base_url="https://example.com",
            include_accessibility=True,
            include_lighthouse=True
        )
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_path = self.temp_dir / "test_project"
    
    def teardown_method(self):
        """Clean up temporary directory"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_create_directory_structure(self):
        """Test that directory structure is created correctly"""
        generator = BaseGenerator(self.config)
        generator.create_directory_structure(self.project_path)
        
        # Verify main directories exist
        expected_dirs = [
            self.project_path,
            self.project_path / "tests",
            self.project_path / "tests" / "accessibility",
            self.project_path / "tests" / "lighthouse",
            self.project_path / "tests" / "broken_links",
            self.project_path / "tests" / "seo",
            self.project_path / "pages",
            self.project_path / "utils",
            self.project_path / "reports",
            self.project_path / "config",
            self.project_path / ".github" / "workflows"
        ]
        
        for directory in expected_dirs:
            assert directory.exists(), f"Directory {directory} should exist"
            assert directory.is_dir(), f"{directory} should be a directory"
        
        # Verify __init__.py files exist
        expected_init_files = [
            self.project_path / "tests" / "__init__.py",
            self.project_path / "pages" / "__init__.py",
            self.project_path / "utils" / "__init__.py",
            self.project_path / "config" / "__init__.py"
        ]
        
        for init_file in expected_init_files:
            assert init_file.exists(), f"Init file {init_file} should exist"
    
    def test_write_file(self):
        """Test that files are written with correct encoding"""
        generator = BaseGenerator(self.config)
        generator.create_directory_structure(self.project_path)
        
        test_content = "Test content with unicode: ✅ 🚀 📊"
        test_file = self.project_path / "test_file.txt"
        
        generator.write_file(test_file, test_content)
        
        assert test_file.exists()
        
        # Read back and verify content
        read_content = test_file.read_text(encoding='utf-8')
        assert read_content == test_content
    
    def test_get_requirements_basic(self):
        """Test requirements for basic configuration"""
        basic_config = GeneratorConfig(
            project_name="basic_test",
            site_name="Basic Site",
            base_url="https://basic.example.com"
        )
        
        generator = BaseGenerator(basic_config)
        requirements = generator.get_requirements()
        
        # Should include basic requirements
        basic_requirements = [
            "pytest>=7.4.0",
            "playwright>=1.40.0",
            "pytest-playwright>=0.4.0",
            "requests>=2.31.0"
        ]
        
        for req in basic_requirements:
            assert any(req.split(">=")[0] in r for r in requirements), f"Missing requirement: {req}"
        
        # Should not include optional requirements
        assert not any("axe-playwright" in r for r in requirements)
        assert not any("python-lighthouse" in r for r in requirements)
    
    def test_get_requirements_with_accessibility(self):
        """Test requirements when accessibility is enabled"""
        accessibility_config = GeneratorConfig(
            project_name="accessibility_test",
            site_name="Accessibility Site",
            base_url="https://accessibility.example.com",
            include_accessibility=True
        )
        
        generator = BaseGenerator(accessibility_config)
        requirements = generator.get_requirements()
        
        # Should include accessibility requirements
        assert any("axe-playwright" in r for r in requirements)
        assert any("pytest-axe" in r for r in requirements)
    
    def test_get_requirements_with_lighthouse(self):
        """Test requirements when lighthouse is enabled"""
        lighthouse_config = GeneratorConfig(
            project_name="lighthouse_test",
            site_name="Lighthouse Site",
            base_url="https://lighthouse.example.com",
            include_lighthouse=True
        )
        
        generator = BaseGenerator(lighthouse_config)
        requirements = generator.get_requirements()
        
        # Should include lighthouse requirements
        assert any("python-lighthouse" in r for r in requirements)


class TestCoreGenerator:
    """Test the CoreGenerator class"""
    
    def setup_method(self):
        """Set up test configuration and temporary directory"""
        self.config = GeneratorConfig(
            project_name="core_test",
            site_name="Core Test Site",
            base_url="https://core.example.com",
            include_accessibility=True
        )
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_path = self.temp_dir / "core_test"
    
    def teardown_method(self):
        """Clean up temporary directory"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_generate_requirements(self):
        """Test requirements.txt generation"""
        generator = CoreGenerator(self.config)
        generator.create_directory_structure(self.project_path)
        generator.generate_requirements(self.project_path)
        
        requirements_file = self.project_path / "requirements.txt"
        assert requirements_file.exists()
        
        content = requirements_file.read_text(encoding='utf-8')
        assert "pytest>=" in content
        assert "playwright>=" in content
        assert "axe-playwright>=" in content  # because accessibility is enabled
    
    def test_generate_pytest_config(self):
        """Test pytest.ini generation"""
        generator = CoreGenerator(self.config)
        generator.create_directory_structure(self.project_path)
        generator.generate_pytest_config(self.project_path)
        
        pytest_file = self.project_path / "pytest.ini"
        assert pytest_file.exists()
        
        content = pytest_file.read_text(encoding='utf-8')
        assert "[tool:pytest]" in content
        assert "testpaths = tests" in content
        assert "accessibility: Accessibility tests" in content
    
    def test_generate_conftest(self):
        """Test conftest.py generation"""
        generator = CoreGenerator(self.config)
        generator.create_directory_structure(self.project_path)
        generator.generate_conftest(self.project_path)
        
        conftest_file = self.project_path / "conftest.py"
        assert conftest_file.exists()
        
        content = conftest_file.read_text(encoding='utf-8')
        assert "import pytest" in content
        assert "from playwright.sync_api import" in content
        assert self.config.base_url in content
    
    def test_generate_page_objects(self):
        """Test page object generation"""
        generator = CoreGenerator(self.config)
        generator.create_directory_structure(self.project_path)
        generator.generate_page_objects(self.project_path)
        
        base_page_file = self.project_path / "pages" / "base_page.py"
        home_page_file = self.project_path / "pages" / "home_page.py"
        
        assert base_page_file.exists()
        assert home_page_file.exists()
        
        base_content = base_page_file.read_text(encoding='utf-8')
        home_content = home_page_file.read_text(encoding='utf-8')
        
        assert "class BasePage:" in base_content
        assert "class HomePage(BasePage):" in home_content
        assert self.config.site_name in home_content


class TestTestGenerator:
    """Test the TestGenerator class"""
    
    def setup_method(self):
        """Set up test configuration and temporary directory"""
        self.config = GeneratorConfig(
            project_name="test_gen_test",
            site_name="Test Generator Site",
            base_url="https://testgen.example.com",
            include_accessibility=True,
            include_lighthouse=True,
            include_broken_links=False,
            include_seo=True
        )
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_path = self.temp_dir / "test_gen_test"
    
    def teardown_method(self):
        """Clean up temporary directory"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_generate_basic_tests(self):
        """Test basic test generation (always generated)"""
        generator = TestGenerator(self.config)
        generator.create_directory_structure(self.project_path)
        generator.generate_basic_tests(self.project_path)
        
        basic_test_file = self.project_path / "tests" / "test_basic.py"
        assert basic_test_file.exists()
        
        content = basic_test_file.read_text(encoding='utf-8')
        assert "class TestBasicFunctionality:" in content
        assert "test_homepage_loads" in content
        assert self.config.site_name in content
    
    def test_generate_accessibility_tests_when_enabled(self):
        """Test accessibility test generation when enabled"""
        generator = TestGenerator(self.config)
        generator.create_directory_structure(self.project_path)
        generator.generate_accessibility_tests(self.project_path)
        
        accessibility_test_file = self.project_path / "tests" / "accessibility" / "test_accessibility.py"
        assert accessibility_test_file.exists()
        
        content = accessibility_test_file.read_text(encoding='utf-8')
        assert "class TestAccessibility:" in content
        assert "axe-playwright" in content or "Axe" in content
    
    def test_generate_accessibility_tests_when_disabled(self):
        """Test accessibility test generation when disabled"""
        disabled_config = GeneratorConfig(
            project_name="disabled_test",
            site_name="Disabled Site",
            base_url="https://disabled.example.com",
            include_accessibility=False
        )
        
        generator = TestGenerator(disabled_config)
        generator.create_directory_structure(self.project_path)
        generator.generate_accessibility_tests(self.project_path)
        
        accessibility_test_file = self.project_path / "tests" / "accessibility" / "test_accessibility.py"
        assert not accessibility_test_file.exists()
    
    def test_generate_performance_tests_when_enabled(self):
        """Test performance test generation when enabled"""
        generator = TestGenerator(self.config)
        generator.create_directory_structure(self.project_path)
        generator.generate_performance_tests(self.project_path)
        
        performance_test_file = self.project_path / "tests" / "lighthouse" / "test_performance.py"
        assert performance_test_file.exists()
        
        content = performance_test_file.read_text(encoding='utf-8')
        assert "class TestLighthousePerformance:" in content
        assert "lighthouse" in content.lower()
    
    def test_generate_all_tests(self):
        """Test generating all configured test types"""
        generator = TestGenerator(self.config)
        generator.create_directory_structure(self.project_path)
        generator.generate_all_tests(self.project_path)
        
        # Should generate basic tests (always)
        assert (self.project_path / "tests" / "test_basic.py").exists()
        
        # Should generate enabled test types
        assert (self.project_path / "tests" / "accessibility" / "test_accessibility.py").exists()
        assert (self.project_path / "tests" / "lighthouse" / "test_performance.py").exists()
        assert (self.project_path / "tests" / "seo" / "test_seo.py").exists()
        
        # Should not generate disabled test types
        assert not (self.project_path / "tests" / "broken_links" / "test_broken_links.py").exists()


if __name__ == "__main__":
    pytest.main([__file__])