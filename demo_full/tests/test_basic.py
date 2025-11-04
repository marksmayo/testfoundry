"""
Basic smoke tests for Demo Full Featured Site
These tests verify core functionality and page loading
"""

import pytest
from playwright.sync_api import Page, expect
from pages.home_page import HomePage


class TestBasicFunctionality:
    """Basic functionality and smoke tests"""
    
    @pytest.mark.smoke
    def test_homepage_loads(self, page: Page, base_url: str):
        """Test that homepage loads successfully"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Verify page loads
        expect(page).to_have_url(base_url)
        
        # Verify page has content
        assert home_page.get_title(), "Page should have a title"
        
    @pytest.mark.smoke  
    def test_page_title_is_not_empty(self, page: Page, base_url: str):
        """Test that page has a meaningful title"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        title = home_page.get_title()
        assert title and title.strip(), "Page title should not be empty"
        assert title.lower() not in ["untitled", "document"], "Page should have meaningful title"
        
    @pytest.mark.smoke
    def test_basic_navigation_exists(self, page: Page, base_url: str):
        """Test that basic navigation elements exist"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Check for common navigation patterns
        nav_exists = (
            page.locator("nav").count() > 0 or
            page.locator(".navigation").count() > 0 or
            page.locator("header a").count() > 0
        )
        
        assert nav_exists, "Page should have some form of navigation"
        
    @pytest.mark.smoke
    def test_no_javascript_errors(self, page: Page, base_url: str):
        """Test that page loads without JavaScript errors"""
        js_errors = []
        
        def handle_console_message(msg):
            if msg.type == "error":
                js_errors.append(msg.text)
                
        page.on("console", handle_console_message)
        
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Allow time for any async JavaScript to run
        page.wait_for_timeout(2000)
        
        assert not js_errors, f"JavaScript errors found: {js_errors}"
