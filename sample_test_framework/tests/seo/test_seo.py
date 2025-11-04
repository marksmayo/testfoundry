"""
SEO tests for Example Website
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
    
    @pytest.mark.seo
    def test_heading_structure_seo(self, page: Page, base_url: str):
        """Test heading structure for SEO best practices"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Should have exactly one H1 tag
        h1_tags = page.locator("h1")
        h1_count = h1_tags.count()
        assert h1_count == 1, f"Should have exactly one H1 tag, found {h1_count}"
        
        # H1 should not be empty
        h1_text = h1_tags.first.inner_text() if h1_count > 0 else ""
        assert h1_text.strip(), "H1 tag should not be empty"
        
        # Should have H2 tags for content structure
        h2_count = page.locator("h2").count()
        assert h2_count > 0, "Page should have H2 tags for content structure"
    
    @pytest.mark.seo
    def test_meta_robots_tag(self, page: Page, base_url: str):
        """Test meta robots tag for search engine indexing"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Check if robots meta tag exists
        robots_meta = page.locator("meta[name='robots']")
        
        if robots_meta.count() > 0:
            robots_content = robots_meta.get_attribute("content")
            # If robots tag exists, it shouldn't block indexing unless intentional
            blocking_directives = ["noindex", "nofollow", "none"]
            
            for directive in blocking_directives:
                if directive in robots_content.lower():
                    # This might be intentional, but flag for review
                    pytest.skip(f"Robots meta tag contains '{directive}' - review if intentional")
    
    @pytest.mark.seo
    def test_canonical_url(self, page: Page, base_url: str):
        """Test canonical URL tag for duplicate content prevention"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        canonical_link = page.locator("link[rel='canonical']")
        
        if canonical_link.count() > 0:
            canonical_href = canonical_link.get_attribute("href")
            assert canonical_href, "Canonical link should have href attribute"
            
            # Canonical URL should be absolute
            assert canonical_href.startswith("http"), "Canonical URL should be absolute"
        else:
            # Canonical tag is not required but recommended for SEO
            pytest.skip("No canonical tag found - consider adding for SEO best practices")
    
    @pytest.mark.seo
    def test_open_graph_tags(self, page: Page, base_url: str):
        """Test Open Graph meta tags for social media sharing"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Essential Open Graph tags
        required_og_tags = ["og:title", "og:description", "og:type", "og:url"]
        missing_tags = []
        
        for tag in required_og_tags:
            og_tag = page.locator(f"meta[property='{tag}']")
            if og_tag.count() == 0:
                missing_tags.append(tag)
            else:
                content = og_tag.get_attribute("content")
                if not content or not content.strip():
                    missing_tags.append(f"{tag} (empty content)")
        
        if missing_tags:
            pytest.skip(f"Missing or empty Open Graph tags: {missing_tags} - consider adding for social media")
    
    @pytest.mark.seo
    def test_twitter_card_tags(self, page: Page, base_url: str):
        """Test Twitter Card meta tags for Twitter sharing"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Check for Twitter Card tags
        twitter_card = page.locator("meta[name='twitter:card']")
        
        if twitter_card.count() > 0:
            card_type = twitter_card.get_attribute("content")
            valid_card_types = ["summary", "summary_large_image", "app", "player"]
            
            assert card_type in valid_card_types, \
                f"Invalid Twitter card type '{card_type}'. Valid types: {valid_card_types}"
            
            # If Twitter card exists, should also have title and description
            twitter_title = page.locator("meta[name='twitter:title']")
            twitter_desc = page.locator("meta[name='twitter:description']")
            
            assert twitter_title.count() > 0, "Twitter card should have twitter:title"
            assert twitter_desc.count() > 0, "Twitter card should have twitter:description"
        else:
            pytest.skip("No Twitter Card tags found - consider adding for Twitter sharing")
    
    @pytest.mark.seo
    def test_structured_data_schema(self, page: Page, base_url: str):
        """Test for structured data (JSON-LD) for rich snippets"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Look for JSON-LD structured data
        json_ld_scripts = page.locator("script[type='application/ld+json']")
        
        if json_ld_scripts.count() > 0:
            # Basic validation that JSON-LD exists and is valid JSON
            for i in range(json_ld_scripts.count()):
                script_content = json_ld_scripts.nth(i).inner_text()
                try:
                    import json
                    json.loads(script_content)
                except json.JSONDecodeError:
                    pytest.fail(f"Invalid JSON-LD structured data found: {script_content[:100]}...")
        else:
            pytest.skip("No structured data found - consider adding JSON-LD for rich snippets")
    
    @pytest.mark.seo
    def test_page_speed_seo_factors(self, page: Page, base_url: str):
        """Test page speed factors that affect SEO"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Measure basic page load performance
        start_time = page.evaluate("Date.now()")
        home_page.wait_for_load()
        end_time = page.evaluate("Date.now()")
        
        load_time = end_time - start_time
        
        # Page should load within 3 seconds for good SEO
        assert load_time < 3000, f"Page load time {load_time}ms exceeds 3s threshold for SEO"
        
        # Check for render-blocking resources
        css_links = page.locator("link[rel='stylesheet']").count()
        
        # Too many CSS files can impact load time
        assert css_links <= 5, f"Too many CSS files ({css_links}) may impact page speed"
        
        # Check for large images without optimization
        large_images = []
        images = page.locator("img").all()
        
        for img in images:
            src = img.get_attribute("src")
            if src and not any(ext in src.lower() for ext in ['.webp', '.avif']):
                # Check image dimensions
                width = img.evaluate("el => el.naturalWidth")
                height = img.evaluate("el => el.naturalHeight")
                
                if width > 2000 or height > 2000:
                    large_images.append(src)
        
        if large_images:
            pytest.skip(f"Large unoptimized images found: {large_images[:3]} - consider optimization")
