"""
Home page object for Improved Test Site
Extends BasePage with home page specific functionality
"""

from pages.base_page import BasePage
from playwright.sync_api import Page


class HomePage(BasePage):
    """Page object for the home page"""
    
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        
    def navigate_to_home(self) -> None:
        """Navigate to home page"""
        self.goto("/")
        self.wait_for_load()
        
    def is_logo_visible(self) -> bool:
        """Check if site logo is visible"""
        # Update selector based on actual site structure
        logo_selectors = [
            "[data-testid='logo']",
            ".logo",
            "#logo", 
            "img[alt*='logo' i]",
            "h1"
        ]
        
        for selector in logo_selectors:
            if self.is_element_visible(selector):
                return True
        return False
        
    def get_navigation_links(self) -> list:
        """Get main navigation links"""
        nav_selectors = [
            "nav a",
            ".navigation a", 
            ".nav a",
            "header a"
        ]
        
        for selector in nav_selectors:
            links = self.page.locator(selector).all()
            if links:
                return [link.get_attribute("href") for link in links]
        return []
        
    def search(self, query: str) -> None:
        """Perform search if search functionality exists"""
        search_selectors = [
            "input[type='search']",
            "input[placeholder*='search' i]",
            "#search",
            ".search-input"
        ]
        
        for selector in search_selectors:
            if self.is_element_visible(selector):
                self.fill_input(selector, query)
                self.page.keyboard.press("Enter")
                return
                
        raise Exception("Search functionality not found on page")
