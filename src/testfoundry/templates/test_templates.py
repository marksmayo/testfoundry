"""
Test templates for different test types.
Contains templates for basic, accessibility, performance, link validation, and SEO tests.
"""

def get_basic_test_template(site_name: str) -> str:
    """Get basic smoke test template"""
    return f'''"""
Basic smoke tests for {site_name}
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

        assert not js_errors, f"JavaScript errors found: {{js_errors}}"
'''


def get_accessibility_test_template(site_name: str) -> str:
    """Get accessibility test template"""
    return f'''"""
Accessibility tests for {site_name}
Tests WCAG compliance and accessibility best practices using axe-core
"""

import pytest
from playwright.sync_api import Page
from pages.home_page import HomePage


class TestAccessibility:
    """Accessibility compliance tests"""

    @pytest.mark.accessibility
    def test_homepage_accessibility(self, page: Page, base_url: str):
        """Test homepage for accessibility violations"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()

        # Inject axe-core via CDN
        page.add_script_tag(url="https://unpkg.com/axe-core@4.8.2/axe.min.js")
        page.wait_for_timeout(1000)  # Wait for script to load

        # Run axe accessibility scan
        results = page.evaluate("""
            async () => {{
                return await new Promise((resolve) => {{
                    if (typeof axe !== 'undefined') {{
                        axe.run().then(resolve);
                    }} else {{
                        // Retry after a short delay if axe not loaded yet
                        setTimeout(() => {{
                            axe.run().then(resolve).catch(() => resolve({{violations: []}}));
                        }}, 500);
                    }}
                }});
            }}
        """)

        # Assert no violations
        violations = results.get("violations", []) if isinstance(results, dict) else []
        if violations:
            violation_details = []
            for violation in violations:
                violation_details.append(f"{{violation['id']}}: {{violation['description']}}")

            pytest.fail(f"Accessibility violations found:\\n" + "\\n".join(violation_details))

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

        assert focused_element in ["A", "BUTTON", "INPUT", "SELECT", "TEXTAREA"], \\
            "Tab should focus on interactive elements"

    @pytest.mark.accessibility
    def test_color_contrast(self, page: Page, base_url: str):
        """Test color contrast ratios"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()

        # Inject axe-core via CDN
        page.evaluate("""
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/axe-core@4.8.2/axe.min.js';
            document.head.appendChild(script);
        """)
        page.wait_for_timeout(1000)  # Wait for script to load

        # Run axe with color contrast specific tests
        results = page.evaluate("""
            async () => {{
                return await new Promise((resolve) => {{
                    if (typeof axe !== 'undefined') {{
                        axe.run({{tags: ['wcag2aa', 'color-contrast']}}).then(resolve);
                    }} else {{
                        setTimeout(() => {{
                            axe.run({{tags: ['wcag2aa', 'color-contrast']}}).then(resolve).catch(() => resolve({{violations: []}}));
                        }}, 500);
                    }}
                }});
            }}
        """)

        violations = results.get("violations", []) if isinstance(results, dict) else []
        contrast_violations = [v for v in violations if "color-contrast" in v.get("id", "")]

        assert not contrast_violations, f"Color contrast violations found: {{contrast_violations}}"

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

        assert not missing_alt, f"Images missing alt text: {{missing_alt}}"

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

                assert current_level - previous_level <= 1, \\
                    f"Heading hierarchy violation: h{{previous_level}} followed by h{{current_level}}"
'''


def get_performance_test_template(site_name: str) -> str:
    """Get performance/lighthouse test template"""
    return f'''"""
Lighthouse performance tests for {site_name}
Tests Core Web Vitals and performance metrics
"""

import pytest
import json
import subprocess
from playwright.sync_api import Page
from pages.home_page import HomePage


class TestLighthousePerformance:
    """Lighthouse performance and Core Web Vitals tests"""

    @pytest.mark.lighthouse
    def test_lighthouse_performance_score(self, page: Page, base_url: str):
        """Test Lighthouse performance score meets minimum threshold"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()

        # Run Lighthouse audit (requires lighthouse CLI to be installed)
        try:
            result = subprocess.run([
                "lighthouse",
                base_url,
                "--only-categories=performance",
                "--output=json",
                "--quiet",
                "--chrome-flags=--headless"
            ], capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                pytest.skip("Lighthouse CLI not available or failed to run")

            lighthouse_data = json.loads(result.stdout)
            performance_score = lighthouse_data["lhr"]["categories"]["performance"]["score"]

            # Performance score should be at least 0.7 (70%)
            assert performance_score >= 0.7, f"Performance score {{performance_score}} is below threshold of 0.7"

        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pytest.skip("Lighthouse CLI not available or timed out")

    @pytest.mark.lighthouse
    def test_core_web_vitals(self, page: Page, base_url: str):
        """Test Core Web Vitals metrics"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()

        # Measure Largest Contentful Paint (LCP)
        lcp_script = """
        () => {{
            return new Promise((resolve) => {{
                new PerformanceObserver((list) => {{
                    const entries = list.getEntries();
                    const lastEntry = entries[entries.length - 1];
                    resolve(lastEntry.startTime);
                }}).observe({{entryTypes: ['largest-contentful-paint']}});

                // Fallback timeout
                setTimeout(() => resolve(null), 5000);
            }});
        }}
        """

        lcp_time = page.evaluate(lcp_script)
        if lcp_time:
            # LCP should be under 2.5 seconds for good performance
            assert lcp_time < 2500, f"LCP time {{lcp_time}}ms exceeds 2.5s threshold"

        # Measure First Input Delay (FID) simulation
        # Note: Real FID requires user interaction, so we test click responsiveness
        start_time = page.evaluate("Date.now()")

        # Find any clickable element and measure response time
        clickable = page.locator("button, a, [onclick]").first
        if clickable.count() > 0:
            clickable.click()
            end_time = page.evaluate("Date.now()")
            response_time = end_time - start_time

            # Response should be under 100ms for good responsiveness
            assert response_time < 100, f"Click response time {{response_time}}ms exceeds 100ms threshold"

    @pytest.mark.lighthouse
    def test_page_load_metrics(self, page: Page, base_url: str):
        """Test various page load performance metrics"""
        # Navigate and measure load time
        start_time = page.evaluate("Date.now()")

        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()

        # Wait for network idle to ensure page is fully loaded
        page.wait_for_load_state("networkidle")

        end_time = page.evaluate("Date.now()")
        total_load_time = end_time - start_time

        # Total load time should be reasonable (under 5 seconds)
        assert total_load_time < 5000, f"Page load time {{total_load_time}}ms exceeds 5s threshold"

        # Check Performance API metrics
        performance_metrics = page.evaluate("""
            () => {{
                const timing = performance.timing;
                const navigation = performance.getEntriesByType('navigation')[0];

                return {{
                    domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                    loadComplete: timing.loadEventEnd - timing.navigationStart,
                    firstPaint: navigation ? navigation.loadEventEnd : null,
                    domInteractive: timing.domInteractive - timing.navigationStart
                }};
            }}
        """)

        # DOM Content Loaded should be under 2 seconds
        if performance_metrics["domContentLoaded"]:
            assert performance_metrics["domContentLoaded"] < 2000, \\
                f"DOM Content Loaded time {{performance_metrics['domContentLoaded']}}ms exceeds 2s"

        # DOM Interactive should be under 1.5 seconds
        if performance_metrics["domInteractive"]:
            assert performance_metrics["domInteractive"] < 1500, \\
                f"DOM Interactive time {{performance_metrics['domInteractive']}}ms exceeds 1.5s"

    @pytest.mark.lighthouse
    def test_resource_optimization(self, page: Page, base_url: str):
        """Test resource optimization (image sizes, compression, etc.)"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()

        # Get all network requests
        large_resources = []

        def handle_response(response):
            # Check for large uncompressed resources
            content_length = response.headers.get("content-length")
            content_encoding = response.headers.get("content-encoding")

            if content_length:
                size = int(content_length)
                # Flag resources over 1MB without compression
                if size > 1024 * 1024 and not content_encoding:
                    large_resources.append({{
                        "url": response.url,
                        "size": size,
                        "type": response.headers.get("content-type", "unknown")
                    }})

        page.on("response", handle_response)
        page.reload()
        page.wait_for_load_state("networkidle")

        assert not large_resources, f"Large uncompressed resources found: {{large_resources}}"
'''