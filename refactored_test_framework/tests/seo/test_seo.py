"""
SEO tests for Example Website (Refactored)
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
        assert len(title) >= 30, f"Page title too short ({len(title)} chars): {title}"
        assert len(title) <= 60, f"Page title too long ({len(title)} chars): {title}"
    
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
        assert desc_length >= 120, f"Meta description too short ({desc_length} chars)"
        assert desc_length <= 160, f"Meta description too long ({desc_length} chars)"
