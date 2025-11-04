"""
Broken links tests for Example Website
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
                        broken_links.append({
                            "url": full_url,
                            "status_code": response.status_code,
                            "text": link.inner_text()[:50]
                        })
                except requests.RequestException as e:
                    broken_links.append({
                        "url": full_url,
                        "error": str(e),
                        "text": link.inner_text()[:50]
                    })
        
        assert not broken_links, f"Broken internal links found: {broken_links}"
    
    @pytest.mark.broken_links
    def test_external_links_accessibility(self, page: Page, base_url: str):
        """Test that external links are properly marked and accessible"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Get all external links
        links = page.locator("a[href]").all()
        base_domain = urlparse(base_url).netloc
        
        external_links_missing_attributes = []
        
        for link in links:
            href = link.get_attribute("href")
            if not href:
                continue
                
            full_url = urljoin(base_url, href)
            parsed_url = urlparse(full_url)
            
            # Check external links (different domain)
            if parsed_url.netloc and parsed_url.netloc != base_domain:
                target = link.get_attribute("target")
                rel = link.get_attribute("rel")
                
                issues = []
                
                # External links should open in new tab/window
                if target != "_blank":
                    issues.append("missing target='_blank'")
                
                # External links should have rel='noopener' for security
                if not rel or "noopener" not in rel:
                    issues.append("missing rel='noopener'")
                
                if issues:
                    external_links_missing_attributes.append({
                        "url": href,
                        "text": link.inner_text()[:50],
                        "issues": issues
                    })
        
        assert not external_links_missing_attributes, \
            f"External links with accessibility issues: {external_links_missing_attributes}"
    
    @pytest.mark.broken_links
    def test_image_links_not_broken(self, page: Page, base_url: str):
        """Test that all image sources are accessible"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Get all images
        images = page.locator("img[src]").all()
        
        broken_images = []
        
        for img in images:
            src = img.get_attribute("src")
            if not src:
                continue
                
            # Convert relative URLs to absolute
            full_url = urljoin(base_url, src)
            
            try:
                response = requests.head(full_url, timeout=10)
                if response.status_code >= 400:
                    broken_images.append({
                        "url": full_url,
                        "status_code": response.status_code,
                        "alt": img.get_attribute("alt") or "No alt text"
                    })
            except requests.RequestException as e:
                broken_images.append({
                    "url": full_url,
                    "error": str(e),
                    "alt": img.get_attribute("alt") or "No alt text"
                })
        
        assert not broken_images, f"Broken images found: {broken_images}"
    
    @pytest.mark.broken_links
    def test_form_action_urls(self, page: Page, base_url: str):
        """Test that form action URLs are valid"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Get all forms with action attributes
        forms = page.locator("form[action]").all()
        
        invalid_form_actions = []
        
        for form in forms:
            action = form.get_attribute("action")
            if not action or action == "#":
                continue
                
            # Convert relative URLs to absolute
            full_url = urljoin(base_url, action)
            
            try:
                # Use GET to test if the endpoint exists (don't actually submit)
                response = requests.get(full_url, timeout=10)
                # Accept any 2xx or 3xx status, or 405 (method not allowed - means endpoint exists)
                if response.status_code >= 400 and response.status_code != 405:
                    invalid_form_actions.append({
                        "action": full_url,
                        "status_code": response.status_code
                    })
            except requests.RequestException as e:
                invalid_form_actions.append({
                    "action": full_url,
                    "error": str(e)
                })
        
        assert not invalid_form_actions, f"Invalid form actions found: {invalid_form_actions}"
    
    @pytest.mark.broken_links
    def test_anchor_links_exist(self, page: Page, base_url: str):
        """Test that anchor links point to existing elements"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Get all anchor links (links starting with #)
        anchor_links = page.locator("a[href^='#']").all()
        
        missing_anchors = []
        
        for link in anchor_links:
            href = link.get_attribute("href")
            if not href or href == "#":
                continue
                
            # Extract the anchor ID (remove the #)
            anchor_id = href[1:]
            
            # Check if element with that ID exists
            target_element = page.locator(f"#{anchor_id}")
            if target_element.count() == 0:
                # Also check for elements with name attribute (older HTML style)
                name_element = page.locator(f"[name='{anchor_id}']")
                if name_element.count() == 0:
                    missing_anchors.append({
                        "href": href,
                        "text": link.inner_text()[:50]
                    })
        
        assert not missing_anchors, f"Anchor links pointing to non-existent elements: {missing_anchors}"
