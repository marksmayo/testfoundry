"""
Accessibility tests for Example Website (Refactored)
Tests WCAG compliance and accessibility best practices using axe-core
"""

import pytest
from playwright.sync_api import Page
from axe_playwright import Axe
from pages.home_page import HomePage


class TestAccessibility:
    """Accessibility compliance tests"""
    
    @pytest.mark.accessibility
    def test_homepage_accessibility(self, page: Page, base_url: str):
        """Test homepage for accessibility violations"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Run axe accessibility scan
        axe = Axe()
        axe.inject(page)
        results = axe.run(page)
        
        # Assert no violations
        violations = results.get("violations", [])
        if violations:
            violation_details = []
            for violation in violations:
                violation_details.append(f"{violation['id']}: {violation['description']}")
            
            pytest.fail(f"Accessibility violations found:\n" + "\n".join(violation_details))
    
    @pytest.mark.accessibility
    def test_keyboard_navigation(self, page: Page, base_url: str):
        """Test keyboard navigation functionality"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Get all focusable elements
        focusable_elements = page.locator('a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])').all()
        
        assert len(focusable_elements) > 0, "Page should have focusable elements"
        
        # Test tab navigation
        page.keyboard.press("Tab")
        focused_element = page.evaluate("document.activeElement.tagName")
        
        assert focused_element in ["A", "BUTTON", "INPUT", "SELECT", "TEXTAREA"], \
            "Tab should focus on interactive elements"
    
    @pytest.mark.accessibility
    def test_color_contrast(self, page: Page, base_url: str):
        """Test color contrast ratios"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Inject axe and run color contrast specific tests
        axe = Axe()
        axe.inject(page)
        results = axe.run(page, {"tags": ["wcag2aa", "color-contrast"]})
        
        violations = results.get("violations", [])
        contrast_violations = [v for v in violations if "color-contrast" in v.get("id", "")]
        
        assert not contrast_violations, f"Color contrast violations found: {contrast_violations}"
    
    @pytest.mark.accessibility
    def test_alt_text_for_images(self, page: Page, base_url: str):
        """Test that all images have appropriate alt text"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Get all images
        images = page.locator("img").all()
        
        missing_alt = []
        for img in images:
            alt_text = img.get_attribute("alt")
            src = img.get_attribute("src")
            
            if alt_text is None:
                missing_alt.append(src)
        
        assert not missing_alt, f"Images missing alt text: {missing_alt}"
    
    @pytest.mark.accessibility
    def test_heading_structure(self, page: Page, base_url: str):
        """Test proper heading hierarchy (h1, h2, h3, etc.)"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Check for h1 element
        h1_count = page.locator("h1").count()
        assert h1_count >= 1, "Page should have at least one h1 element"
        assert h1_count <= 1, "Page should have only one h1 element"
        
        # Check heading hierarchy
        headings = page.locator("h1, h2, h3, h4, h5, h6").all()
        heading_levels = []
        
        for heading in headings:
            tag_name = heading.evaluate("el => el.tagName")
            level = int(tag_name[1])
            heading_levels.append(level)
        
        # Verify no level is skipped (e.g., h1 -> h3 without h2)
        if len(heading_levels) > 1:
            for i in range(1, len(heading_levels)):
                current_level = heading_levels[i]
                previous_level = heading_levels[i-1]
                
                assert current_level - previous_level <= 1, \
                    f"Heading hierarchy violation: h{previous_level} followed by h{current_level}"
