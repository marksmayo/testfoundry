"""
Base page object class that all page objects inherit from.
Provides common functionality and patterns for page interaction.
"""

from playwright.sync_api import Page, expect
from typing import Optional


class BasePage:
    """Base page object with common functionality for all pages"""
    
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")
        
    def goto(self, path: str = "") -> None:
        """Navigate to a specific path relative to base URL"""
        url = f"{self.base_url}{path}" if path else self.base_url
        self.page.goto(url)
        
    def wait_for_load(self, timeout: int = 30000) -> None:
        """Wait for page to be fully loaded"""
        self.page.wait_for_load_state("networkidle", timeout=timeout)
        
    def get_title(self) -> str:
        """Get page title"""
        return self.page.title()
        
    def get_url(self) -> str:
        """Get current page URL"""
        return self.page.url
        
    def is_element_visible(self, selector: str) -> bool:
        """Check if element is visible on page"""
        return self.page.locator(selector).is_visible()
        
    def click(self, selector: str) -> None:
        """Click an element"""
        self.page.locator(selector).click()
        
    def fill_input(self, selector: str, text: str) -> None:
        """Fill an input field"""
        self.page.locator(selector).fill(text)
        
    def get_text(self, selector: str) -> str:
        """Get text content of an element"""
        return self.page.locator(selector).inner_text()
        
    def wait_for_selector(self, selector: str, timeout: int = 30000) -> None:
        """Wait for selector to be visible"""
        self.page.wait_for_selector(selector, timeout=timeout)
        
    def get_all_links(self) -> list:
        """Get all links on the page"""
        return self.page.locator("a[href]").all()
        
    def get_all_images(self) -> list:
        """Get all images on the page"""
        return self.page.locator("img").all()
        
    def scroll_to_bottom(self) -> None:
        """Scroll to bottom of page"""
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
    def take_screenshot(self, path: str) -> None:
        """Take screenshot of current page"""
        self.page.screenshot(path=path, full_page=True)
