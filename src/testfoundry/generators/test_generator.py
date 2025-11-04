"""
Test file generator.
Generates test files for different test types based on configuration.
"""

from pathlib import Path
from .base import BaseGenerator
from ..templates.test_templates import (
    get_basic_test_template,
    get_accessibility_test_template,
    get_performance_test_template
)


class TestGenerator(BaseGenerator):
    """Generates test files based on configuration"""
    
    def generate_basic_tests(self, project_path: Path) -> None:
        """Generate basic smoke tests (always included)"""
        test_content = get_basic_test_template(self.config.site_name)
        self.write_file(project_path / "tests" / "test_basic.py", test_content)
    
    def generate_accessibility_tests(self, project_path: Path) -> None:
        """Generate accessibility tests if enabled"""
        if not self.config.include_accessibility:
            return
            
        test_content = get_accessibility_test_template(self.config.site_name)
        self.write_file(
            project_path / "tests" / "accessibility" / "test_accessibility.py", 
            test_content
        )
    
    def generate_performance_tests(self, project_path: Path) -> None:
        """Generate performance/lighthouse tests if enabled"""
        if not self.config.include_lighthouse:
            return
            
        test_content = get_performance_test_template(self.config.site_name)
        self.write_file(
            project_path / "tests" / "lighthouse" / "test_performance.py", 
            test_content
        )
    
    def generate_broken_links_tests(self, project_path: Path) -> None:
        """Generate broken links tests if enabled"""
        if not self.config.include_broken_links:
            return
            
        test_content = self._get_broken_links_template()
        self.write_file(
            project_path / "tests" / "broken_links" / "test_broken_links.py", 
            test_content
        )
    
    def generate_seo_tests(self, project_path: Path) -> None:
        """Generate SEO tests if enabled"""
        if not self.config.include_seo:
            return
            
        test_content = self._get_seo_template()
        self.write_file(
            project_path / "tests" / "seo" / "test_seo.py", 
            test_content
        )
    
    def generate_all_tests(self, project_path: Path) -> None:
        """Generate all test files based on configuration"""
        self.generate_basic_tests(project_path)
        self.generate_accessibility_tests(project_path)
        self.generate_performance_tests(project_path)
        self.generate_broken_links_tests(project_path)
        self.generate_seo_tests(project_path)
    
    def _get_broken_links_template(self) -> str:
        """Get broken links test template - simplified for now"""
        return f'''"""
Broken links tests for {self.config.site_name}
Tests for dead links, redirects, and link accessibility
"""

import pytest
import requests
from urllib.parse import urljoin, urlparse
from playwright.sync_api import Page
from pages.home_page import HomePage


class TestBrokenLinks:
    """Broken links and link validation tests"""
    
    @pytest.mark.broken_links
    def test_no_broken_internal_links(self, page: Page, base_url: str):
        """Test that all internal links are working"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Get all links on the page
        links = page.locator("a[href]").all()
        
        broken_links = []
        base_domain = urlparse(base_url).netloc
        
        for link in links:
            href = link.get_attribute("href")
            if not href:
                continue
                
            # Convert relative URLs to absolute
            full_url = urljoin(base_url, href)
            parsed_url = urlparse(full_url)
            
            # Only test internal links (same domain)
            if parsed_url.netloc == base_domain or not parsed_url.netloc:
                try:
                    response = requests.head(full_url, timeout=10, allow_redirects=True)
                    if response.status_code >= 400:
                        broken_links.append({{
                            "url": full_url,
                            "status_code": response.status_code,
                            "text": link.inner_text()[:50]
                        }})
                except requests.RequestException as e:
                    broken_links.append({{
                        "url": full_url,
                        "error": str(e),
                        "text": link.inner_text()[:50]
                    }})
        
        assert not broken_links, f"Broken internal links found: {{broken_links}}"
'''
    
    def _get_seo_template(self) -> str:
        """Get SEO test template - simplified for now"""
        return f'''"""
SEO tests for {self.config.site_name}
Tests for search engine optimization best practices
"""

import pytest
from playwright.sync_api import Page
from pages.home_page import HomePage


class TestSEO:
    """SEO and search engine optimization tests"""
    
    @pytest.mark.seo
    def test_page_title_length(self, page: Page, base_url: str):
        """Test that page title is appropriate length for SEO"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        title = home_page.get_title()
        
        # Title should be between 30-60 characters for optimal SEO
        assert len(title) >= 30, f"Page title too short ({{len(title)}} chars): {{title}}"
        assert len(title) <= 60, f"Page title too long ({{len(title)}} chars): {{title}}"
    
    @pytest.mark.seo
    def test_meta_description_exists(self, page: Page, base_url: str):
        """Test that meta description exists and is appropriate length"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        meta_description = page.locator("meta[name='description']")
        assert meta_description.count() > 0, "Meta description tag is missing"
        
        description_content = meta_description.get_attribute("content")
        assert description_content and description_content.strip(), "Meta description content is empty"
        
        # Description should be between 120-160 characters for optimal SEO
        desc_length = len(description_content)
        assert desc_length >= 120, f"Meta description too short ({{desc_length}} chars)"
        assert desc_length <= 160, f"Meta description too long ({{desc_length}} chars)"
'''