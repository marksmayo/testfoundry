"""
Core framework generator.
Generates pytest configuration, base page objects, and core framework files.
"""

from pathlib import Path
from .base import BaseGenerator
from ..templates.base_templates import (
    get_pytest_config_template,
    get_conftest_template,
    get_base_page_template,
    get_home_page_template
)


class CoreGenerator(BaseGenerator):
    """Generates core framework files"""
    
    def generate_requirements(self, project_path: Path) -> None:
        """Generate requirements.txt file"""
        requirements = self.get_requirements()
        requirements_content = "\n".join(requirements) + "\n"
        self.write_file(project_path / "requirements.txt", requirements_content)
    
    def generate_pytest_config(self, project_path: Path) -> None:
        """Generate pytest.ini configuration"""
        config_content = get_pytest_config_template()
        self.write_file(project_path / "pytest.ini", config_content)
    
    def generate_conftest(self, project_path: Path) -> None:
        """Generate conftest.py with Playwright configuration"""
        config_content = get_conftest_template(self.config.base_url)
        self.write_file(project_path / "conftest.py", config_content)
    
    def generate_page_objects(self, project_path: Path) -> None:
        """Generate base page objects"""
        # Base page object
        base_page_content = get_base_page_template()
        self.write_file(project_path / "pages" / "base_page.py", base_page_content)
        
        # Sample home page object
        home_page_content = get_home_page_template(self.config.site_name)
        self.write_file(project_path / "pages" / "home_page.py", home_page_content)
    
    def generate_all_core_files(self, project_path: Path) -> None:
        """Generate all core framework files"""
        self.generate_requirements(project_path)
        self.generate_pytest_config(project_path)
        self.generate_conftest(project_path)
        self.generate_page_objects(project_path)
        self.copy_logo_file(project_path)