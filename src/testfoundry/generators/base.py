"""
Base generator class and common utilities.
Provides shared functionality for all specific generators.
"""

import os
import shutil
from pathlib import Path
from typing import List
from ..config.models import GeneratorConfig


class BaseGenerator:
    """Base class for all generators"""

    def __init__(self, config: GeneratorConfig):
        self.config = config

    def create_directory_structure(self, project_path: Path) -> None:
        """Create the basic directory structure"""
        directories = [
            project_path,
            project_path / "tests",
            project_path / "tests" / "accessibility",
            project_path / "tests" / "lighthouse",
            project_path / "tests" / "broken_links",
            project_path / "tests" / "seo",
            project_path / "pages",
            project_path / "utils",
            project_path / "reports",
            project_path / "config",
            project_path / "assets",
            project_path / ".github" / "workflows"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        # Create __init__.py files for Python packages
        init_files = [
            project_path / "tests" / "__init__.py",
            project_path / "pages" / "__init__.py",
            project_path / "utils" / "__init__.py",
            project_path / "config" / "__init__.py"
        ]

        for init_file in init_files:
            init_file.touch()

    def write_file(self, file_path: Path, content: str) -> None:
        """Write content to file with UTF-8 encoding"""
        file_path.write_text(content, encoding='utf-8')

    def copy_logo_file(self, project_path: Path) -> None:
        """Copy TestFoundry logo to the project, trying multiple source locations"""
        candidates = []
        try:
            generator_root = Path(__file__).parent.parent.parent.parent
            candidates.append(generator_root / "logo.png")
        except Exception:
            pass

        # Also try alongside this module (packaged asset scenario)
        candidates.append(Path(__file__).parent / "logo.png")

        # Fallback to web UI static asset if present
        candidates.append(Path(__file__).parent.parent.parent.parent / "web_ui" / "static" / "logo.png")

        logo_source = next((p for p in candidates if p.exists()), None)
        if logo_source:
            logo_dest = project_path / "assets" / "logo.png"
            logo_dest.parent.mkdir(exist_ok=True)
            shutil.copy2(logo_source, logo_dest)

    def get_requirements(self) -> List[str]:
        """Get list of requirements based on configuration"""
        requirements = [
            "pytest>=7.4.0",
            "pytest-html>=3.2.0",
            "pytest-xdist>=3.3.0",
            "playwright>=1.40.0",
            "pytest-playwright>=0.4.0",
            "requests>=2.31.0",
            "beautifulsoup4>=4.12.0",
            "lxml>=4.9.0"
        ]

        if self.config.include_accessibility:
            # Note: We use axe-core via CDN injection, no Python package needed
            # pytest-axe is not needed since we inject axe-core directly
            pass

        if self.config.include_lighthouse:
            # Note: Lighthouse CLI is installed via npm, not pip
            # Install with: npm install -g lighthouse
            # The tests use subprocess to call the lighthouse CLI
            pass

        # Sort requirements, but ensure pytest is always first
        sorted_reqs = sorted(requirements)
        # Move pytest to the front if it exists
        if "pytest>=7.4.0" in sorted_reqs:
            sorted_reqs.remove("pytest>=7.4.0")
            sorted_reqs.insert(0, "pytest>=7.4.0")

        return sorted_reqs
