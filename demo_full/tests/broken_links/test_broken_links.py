"""
Broken links tests for Demo Full Featured Site
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
