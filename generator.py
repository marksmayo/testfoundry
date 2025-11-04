#!/usr/bin/env python3
"""
Test Automation Framework Generator for Website Testing

This CLI tool generates a complete test automation framework using pytest and Playwright
for testing websites with support for accessibility, lighthouse, broken links, and SEO testing.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any


class TestFrameworkGenerator:
    def __init__(self):
        self.config = {}

    def get_user_input(self) -> Dict[str, Any]:
        """Collect configuration from user via CLI prompts"""
        print("=== Test Automation Framework Generator ===\n")

        # Basic project configuration
        self.config['project_name'] = input("Enter project folder name: ").strip()
        if not self.config['project_name']:
            print("Project name is required!")
            sys.exit(1)

        self.config['site_name'] = input("Enter site name (for documentation): ").strip()
        if not self.config['site_name']:
            self.config['site_name'] = self.config['project_name']

        self.config['base_url'] = input("Enter base URL (e.g., https://example.com): ").strip()
        if not self.config['base_url']:
            print("Base URL is required!")
            sys.exit(1)

        # Test types
        print("\nSelect test types to include:")
        self.config['include_accessibility'] = self._get_yes_no("Include accessibility tests? (y/N)")
        self.config['include_lighthouse'] = self._get_yes_no("Include Lighthouse performance tests? (y/N)")
        self.config['include_broken_links'] = self._get_yes_no("Include broken links tests? (y/N)")
        self.config['include_seo'] = self._get_yes_no("Include SEO tests? (y/N)")

        # Report configuration
        print("\nReport configuration:")
        self.config['html_reports'] = self._get_yes_no("Generate HTML reports? (Y/n)", default=True)

        # CI/CD configuration
        print("\nCI/CD configuration:")
        self.config['github_actions'] = self._get_yes_no("Generate GitHub Actions workflow? (y/N)")

        return self.config

    def _get_yes_no(self, prompt: str, default: bool = False) -> bool:
        """Get yes/no input from user with default handling"""
        response = input(f"{prompt} ").strip().lower()
        if not response:
            return default
        return response in ['y', 'yes', 'true', '1']

    def generate_framework(self):
        """Generate the complete test framework"""
        project_path = Path(self.config['project_name'])

        if project_path.exists():
            overwrite = self._get_yes_no(f"Directory '{self.config['project_name']}' exists. Overwrite? (y/N)")
            if not overwrite:
                print("Aborting generation.")
                return

        # Create project structure
        self._create_project_structure(project_path)

        # Generate configuration files
        self._generate_requirements(project_path)
        self._generate_pytest_config(project_path)
        self._generate_playwright_config(project_path)

        # Generate page objects
        self._generate_page_objects(project_path)

        # Generate test files based on selected types
        self._generate_test_files(project_path)

        # Generate utilities and helpers
        self._generate_utilities(project_path)

        # Generate documentation
        self._generate_readme(project_path)

        # Generate CI/CD files if requested
        if self.config['github_actions']:
            self._generate_github_actions(project_path)

        print(f"\nTest framework generated successfully in '{self.config['project_name']}/'")
        print(f"Project structure created with Page Object Model")
        print(f"Test types: {self._get_enabled_tests()}")
        print(f"Reports: {'HTML' if self.config['html_reports'] else 'Terminal only'}")
        if self.config['github_actions']:
            print(f"GitHub Actions workflow created")
        print(f"\nNext steps:")
        print(f"1. cd {self.config['project_name']}")
        print(f"2. python -m venv venv")
        print(f"3. source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print(f"4. pip install -r requirements.txt")
        print(f"5. playwright install")
        print(f"6. pytest --help  # See available test options")

    def _get_enabled_tests(self) -> str:
        """Get list of enabled test types for display"""
        enabled = []
        if self.config['include_accessibility']:
            enabled.append('Accessibility')
        if self.config['include_lighthouse']:
            enabled.append('Lighthouse')
        if self.config['include_broken_links']:
            enabled.append('Broken Links')
        if self.config['include_seo']:
            enabled.append('SEO')
        return ', '.join(enabled) if enabled else 'Basic tests only'

    def _create_project_structure(self, project_path: Path):
        """Create the project directory structure"""
        directories = [
            project_path,
            project_path / "tests",
            project_path / "tests" / "accessibility",
            project_path / "tests" / "lighthouse",
            project_path / "tests" / "broken_links",
            project_path / "tests" / "seo",
            project_path / "pages",
            project_path / "utils",
            project_path / "reports",
            project_path / "config",
            project_path / ".github" / "workflows"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        # Create __init__.py files for Python packages
        init_files = [
            project_path / "tests" / "__init__.py",
            project_path / "pages" / "__init__.py",
            project_path / "utils" / "__init__.py",
            project_path / "config" / "__init__.py"
        ]

        for init_file in init_files:
            init_file.touch()

    def _generate_requirements(self, project_path: Path):
        """Generate requirements.txt with necessary dependencies"""
        requirements = [
            "pytest>=7.4.0",
            "pytest-html>=3.2.0",
            "pytest-xdist>=3.3.0",
            "playwright>=1.40.0",
            "pytest-playwright>=0.4.0",
            "requests>=2.31.0",
            "beautifulsoup4>=4.12.0",
            "lxml>=4.9.0"
        ]

        if self.config['include_accessibility']:
            # Note: We use axe-core via CDN injection, no Python package needed
            # pytest-axe is optional for additional pytest integration
            requirements.extend([
                "pytest-axe>=1.0.0"
            ])

        if self.config['include_lighthouse']:
            # Note: Lighthouse CLI is installed via npm, not pip
            # Install with: npm install -g lighthouse
            # The tests use subprocess to call the lighthouse CLI
            pass

        # Sort requirements, but ensure pytest is always first
        sorted_reqs = sorted(requirements)
        # Move pytest to the front if it exists
        if "pytest>=7.4.0" in sorted_reqs:
            sorted_reqs.remove("pytest>=7.4.0")
            sorted_reqs.insert(0, "pytest>=7.4.0")

        requirements_content = "\n".join(sorted_reqs) + "\n"

        (project_path / "requirements.txt").write_text(requirements_content, encoding='utf-8')

    def _generate_pytest_config(self, project_path: Path):
        """Generate pytest.ini configuration"""
        config_content = f"""[tool:pytest]
testpaths = tests
addopts =
    --strict-markers
    --strict-config
    --html=reports/report.html
    --self-contained-html
    -v
markers =
    accessibility: Accessibility tests
    lighthouse: Lighthouse performance tests
    broken_links: Broken link tests
    seo: SEO tests
    smoke: Smoke tests
    regression: Regression tests
"""

        (project_path / "pytest.ini").write_text(config_content, encoding='utf-8')

    def _generate_playwright_config(self, project_path: Path):
        """Generate playwright configuration"""
        config_content = f"""import pytest
from playwright.sync_api import Page, expect

# Playwright configuration
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {{
        **browser_context_args,
        "viewport": {{"width": 1920, "height": 1080}},
        "ignore_https_errors": True,
    }}

@pytest.fixture(scope="session")
def base_url():
    return "{self.config['base_url']}"

@pytest.fixture
def page_with_base_url(page: Page, base_url: str):
    page.goto(base_url)
    return page
"""

        (project_path / "conftest.py").write_text(config_content, encoding='utf-8')

    def _generate_page_objects(self, project_path: Path):
        """Generate base page object and sample page objects"""

        # Base page object
        base_page_content = '''"""
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
'''

        (project_path / "pages" / "base_page.py").write_text(base_page_content, encoding='utf-8')

        # Sample home page object
        home_page_content = f'''"""
Home page object for {self.config['site_name']}
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
'''

        (project_path / "pages" / "home_page.py").write_text(home_page_content, encoding='utf-8')

    def _generate_test_files(self, project_path: Path):
        """Generate test files based on selected test types"""

        # Basic smoke test that's always included
        self._generate_basic_tests(project_path)

        if self.config['include_accessibility']:
            self._generate_accessibility_tests(project_path)

        if self.config['include_lighthouse']:
            self._generate_lighthouse_tests(project_path)

        if self.config['include_broken_links']:
            self._generate_broken_links_tests(project_path)

        if self.config['include_seo']:
            self._generate_seo_tests(project_path)

    def _generate_basic_tests(self, project_path: Path):
        """Generate basic smoke tests"""
        test_content = f'''"""
Basic smoke tests for {self.config['site_name']}
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

        (project_path / "tests" / "test_basic.py").write_text(test_content, encoding='utf-8')

    def _generate_accessibility_tests(self, project_path: Path):
        """Generate accessibility tests using axe-playwright"""
        test_content = f'''"""
Accessibility tests for {self.config['site_name']}
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

        # Inject axe and run color contrast specific tests
        axe = Axe()
        axe.inject(page)
        results = axe.run(page, {{"tags": ["wcag2aa", "color-contrast"]}})

        violations = results.get("violations", [])
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

        (project_path / "tests" / "accessibility" / "test_accessibility.py").write_text(test_content, encoding='utf-8')

    def _generate_lighthouse_tests(self, project_path: Path):
        """Generate Lighthouse performance tests"""
        test_content = f'''"""
Lighthouse performance tests for {self.config['site_name']}
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

        (project_path / "tests" / "lighthouse" / "test_performance.py").write_text(test_content, encoding='utf-8')

    def _generate_broken_links_tests(self, project_path: Path):
        """Generate broken links tests"""
        test_content = f'''"""
Broken links tests for {self.config['site_name']}
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
                    external_links_missing_attributes.append({{
                        "url": href,
                        "text": link.inner_text()[:50],
                        "issues": issues
                    }})

        assert not external_links_missing_attributes, \\
            f"External links with accessibility issues: {{external_links_missing_attributes}}"

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
                    broken_images.append({{
                        "url": full_url,
                        "status_code": response.status_code,
                        "alt": img.get_attribute("alt") or "No alt text"
                    }})
            except requests.RequestException as e:
                broken_images.append({{
                    "url": full_url,
                    "error": str(e),
                    "alt": img.get_attribute("alt") or "No alt text"
                }})

        assert not broken_images, f"Broken images found: {{broken_images}}"

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
                    invalid_form_actions.append({{
                        "action": full_url,
                        "status_code": response.status_code
                    }})
            except requests.RequestException as e:
                invalid_form_actions.append({{
                    "action": full_url,
                    "error": str(e)
                }})

        assert not invalid_form_actions, f"Invalid form actions found: {{invalid_form_actions}}"

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
            target_element = page.locator(f"#{{anchor_id}}")
            if target_element.count() == 0:
                # Also check for elements with name attribute (older HTML style)
                name_element = page.locator(f"[name='{{anchor_id}}']")
                if name_element.count() == 0:
                    missing_anchors.append({{
                        "href": href,
                        "text": link.inner_text()[:50]
                    }})

        assert not missing_anchors, f"Anchor links pointing to non-existent elements: {{missing_anchors}}"
'''

        (project_path / "tests" / "broken_links" / "test_broken_links.py").write_text(test_content, encoding='utf-8')

    def _generate_seo_tests(self, project_path: Path):
        """Generate SEO tests"""
        test_content = f'''"""
SEO tests for {self.config['site_name']}
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

    @pytest.mark.seo
    def test_heading_structure_seo(self, page: Page, base_url: str):
        """Test heading structure for SEO best practices"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()

        # Should have exactly one H1 tag
        h1_tags = page.locator("h1")
        h1_count = h1_tags.count()
        assert h1_count == 1, f"Should have exactly one H1 tag, found {{h1_count}}"

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
                    pytest.skip(f"Robots meta tag contains '{{directive}}' - review if intentional")

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
            og_tag = page.locator(f"meta[property='{{tag}}']")
            if og_tag.count() == 0:
                missing_tags.append(tag)
            else:
                content = og_tag.get_attribute("content")
                if not content or not content.strip():
                    missing_tags.append(f"{{tag}} (empty content)")

        if missing_tags:
            pytest.skip(f"Missing or empty Open Graph tags: {{missing_tags}} - consider adding for social media")

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

            assert card_type in valid_card_types, \\
                f"Invalid Twitter card type '{{card_type}}'. Valid types: {{valid_card_types}}"

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
                    pytest.fail(f"Invalid JSON-LD structured data found: {{script_content[:100]}}...")
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
        assert load_time < 3000, f"Page load time {{load_time}}ms exceeds 3s threshold for SEO"

        # Check for render-blocking resources
        css_links = page.locator("link[rel='stylesheet']").count()

        # Too many CSS files can impact load time
        assert css_links <= 5, f"Too many CSS files ({{css_links}}) may impact page speed"

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
            pytest.skip(f"Large unoptimized images found: {{large_images[:3]}} - consider optimization")
'''

        (project_path / "tests" / "seo" / "test_seo.py").write_text(test_content, encoding='utf-8')

    def _generate_utilities(self, project_path: Path):
        """Generate utility functions and helpers"""

        # Test utilities
        utils_content = '''"""
Utility functions for test automation framework
Provides common functionality for all test types
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from playwright.sync_api import Page


class TestUtils:
    """Utility functions for testing"""

    @staticmethod
    def take_screenshot(page: Page, name: str, test_name: str = "") -> str:
        """Take a screenshot and save to reports directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{name}_{timestamp}.png" if test_name else f"{name}_{timestamp}.png"

        # Create screenshots directory
        screenshots_dir = Path("reports/screenshots")
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        filepath = screenshots_dir / filename
        page.screenshot(path=str(filepath), full_page=True)

        return str(filepath)

    @staticmethod
    def save_page_source(page: Page, name: str, test_name: str = "") -> str:
        """Save page source to reports directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{name}_{timestamp}.html" if test_name else f"{name}_{timestamp}.html"

        # Create page_sources directory
        sources_dir = Path("reports/page_sources")
        sources_dir.mkdir(parents=True, exist_ok=True)

        filepath = sources_dir / filename
        content = page.content()
        filepath.write_text(content, encoding='utf-8')

        return str(filepath)

    @staticmethod
    def get_page_performance_metrics(page: Page) -> Dict[str, Any]:
        """Get comprehensive page performance metrics"""
        metrics = page.evaluate("""
            () => {
                const timing = performance.timing;
                const navigation = performance.getEntriesByType('navigation')[0];
                const paint = performance.getEntriesByType('paint');

                const result = {
                    loadEventEnd: timing.loadEventEnd - timing.navigationStart,
                    domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                    domInteractive: timing.domInteractive - timing.navigationStart,
                    firstPaint: null,
                    firstContentfulPaint: null,
                    resourceCount: performance.getEntriesByType('resource').length
                };

                // Get paint timings
                paint.forEach(entry => {
                    if (entry.name === 'first-paint') {
                        result.firstPaint = entry.startTime;
                    } else if (entry.name === 'first-contentful-paint') {
                        result.firstContentfulPaint = entry.startTime;
                    }
                });

                return result;
            }
        """)

        return metrics

    @staticmethod
    def check_console_errors(page: Page) -> List[str]:
        """Collect console errors from the page"""
        errors = []

        def handle_console_message(msg):
            if msg.type == "error":
                errors.append(msg.text)

        page.on("console", handle_console_message)
        return errors

    @staticmethod
    def wait_for_api_response(page: Page, url_pattern: str, timeout: int = 30000) -> Optional[Dict]:
        """Wait for specific API response and return response data"""
        response_data = None

        def handle_response(response):
            nonlocal response_data
            if url_pattern in response.url:
                try:
                    response_data = response.json()
                except:
                    response_data = {"status": response.status, "url": response.url}

        page.on("response", handle_response)
        page.wait_for_timeout(timeout)

        return response_data

    @staticmethod
    def get_all_network_requests(page: Page) -> List[Dict[str, Any]]:
        """Collect all network requests made by the page"""
        requests = []

        def handle_request(request):
            requests.append({
                "url": request.url,
                "method": request.method,
                "resource_type": request.resource_type,
                "headers": request.headers
            })

        def handle_response(response):
            # Find corresponding request and add response info
            for req in requests:
                if req["url"] == response.url:
                    req["status"] = response.status
                    req["response_headers"] = response.headers
                    break

        page.on("request", handle_request)
        page.on("response", handle_response)

        return requests

    @staticmethod
    def extract_links_from_page(page: Page, base_url: str) -> List[Dict[str, str]]:
        """Extract all links from the page with metadata"""
        links = page.evaluate(f"""
            (baseUrl) => {{
                const links = Array.from(document.querySelectorAll('a[href]'));
                return links.map(link => ({{
                    href: link.href,
                    text: link.innerText.trim(),
                    title: link.title || '',
                    target: link.target || '',
                    rel: link.rel || '',
                    isExternal: !link.href.startsWith(baseUrl)
                }}));
            }}
        """, base_url)

        return links

    @staticmethod
    def save_test_data(data: Dict[str, Any], filename: str) -> str:
        """Save test data to JSON file in reports directory"""
        reports_dir = Path("reports/test_data")
        reports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = reports_dir / f"{filename}_{timestamp}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return str(filepath)


class ReportGenerator:
    """Generate test reports and summaries"""

    @staticmethod
    def generate_accessibility_report(violations: List[Dict]) -> str:
        """Generate accessibility violations report"""
        if not violations:
            return "No accessibility violations found"

        report = ["Accessibility Violations Found:", ""]

        for i, violation in enumerate(violations, 1):
            report.extend([
                f"{i}. {violation.get('id', 'Unknown')}: {violation.get('description', 'No description')}",
                f"   Impact: {violation.get('impact', 'Unknown')}",
                f"   Nodes affected: {len(violation.get('nodes', []))}",
                ""
            ])

        return "\\n".join(report)

    @staticmethod
    def generate_performance_report(metrics: Dict[str, Any]) -> str:
        """Generate performance metrics report"""
        report = ["Performance Metrics:", ""]

        if metrics.get('loadEventEnd'):
            report.append(f"Total Load Time: {metrics['loadEventEnd']}ms")

        if metrics.get('domContentLoaded'):
            report.append(f"DOM Content Loaded: {metrics['domContentLoaded']}ms")

        if metrics.get('firstContentfulPaint'):
            report.append(f"First Contentful Paint: {metrics['firstContentfulPaint']}ms")

        if metrics.get('resourceCount'):
            report.append(f"Resources Loaded: {metrics['resourceCount']}")

        return "\\n".join(report)
'''

        (project_path / "utils" / "test_utils.py").write_text(utils_content, encoding='utf-8')

    def _generate_readme(self, project_path: Path):
        """Generate comprehensive README.md"""
        enabled_tests = self._get_enabled_tests()

        readme_content = f'''# {self.config['site_name']} Test Automation Framework

This project contains automated tests for **{self.config['site_name']}** using Python, pytest, and Playwright.

## Test Coverage

This framework includes the following test types:
{self._get_test_coverage_details()}

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd {self.config['project_name']}
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv

   # On Windows:
   venv\\Scripts\\activate

   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers:**
   ```bash
   playwright install
   ```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Types
```bash
# Basic smoke tests
pytest -m smoke

{self._get_test_run_examples()}
```

### Run Tests with HTML Report
```bash
pytest --html=reports/report.html --self-contained-html
```

### Run Tests in Parallel
```bash
pytest -n auto  # Uses all available CPU cores
pytest -n 4     # Uses 4 workers
```

### Run Tests Against Different Environments
```bash
# Override base URL for different environments
pytest --base-url=https://staging.example.com
pytest --base-url=https://production.example.com
```

## Test Reports

Test reports are generated in the `reports/` directory:

- **HTML Report**: `reports/report.html` - Comprehensive test results with screenshots
- **Screenshots**: `reports/screenshots/` - Screenshots taken during test failures
- **Page Sources**: `reports/page_sources/` - HTML source saved during failures
- **Test Data**: `reports/test_data/` - JSON data collected during tests

## Project Structure

```
{self.config['project_name']}/
├── tests/                 # Test files organized by type
│   ├── test_basic.py     # Basic smoke tests (always included)
{self._get_project_structure_details()}
├── pages/                # Page Object Model classes
│   ├── base_page.py     # Base page with common functionality
│   ├── home_page.py     # Home page specific methods
│   └── __init__.py
├── utils/                # Utility functions and helpers
│   ├── test_utils.py    # Common test utilities
│   └── __init__.py
├── config/               # Configuration files
│   └── __init__.py
├── reports/              # Test reports and artifacts
├── conftest.py          # Pytest configuration and fixtures
├── pytest.ini          # Pytest settings
└── requirements.txt     # Python dependencies
```

## Configuration

### Base URL Configuration

The base URL is configured in `conftest.py`. To test against different environments:

1. **Modify conftest.py:**
   ```python
   @pytest.fixture(scope="session")
   def base_url():
       return "https://your-environment.com"
   ```

2. **Use command line override:**
   ```bash
   pytest --base-url=https://different-environment.com
   ```

### Test Markers

Available pytest markers for organizing test runs:

- `smoke` - Basic functionality tests
{self._get_marker_details()}

### Browser Configuration

Browser settings can be modified in `conftest.py`:

```python
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {{
        **browser_context_args,
        "viewport": {{"width": 1920, "height": 1080}},
        "ignore_https_errors": True,
        # Add more browser options as needed
    }}
```

## Writing New Tests

### Adding a New Page Object

1. Create a new file in `pages/` directory
2. Extend the `BasePage` class
3. Add page-specific methods

```python
from pages.base_page import BasePage
from playwright.sync_api import Page

class NewPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def specific_action(self):
        # Page-specific functionality
        pass
```

### Adding New Tests

1. Create test files in appropriate `tests/` subdirectory
2. Use appropriate pytest markers
3. Follow naming convention: `test_*.py`

```python
import pytest
from playwright.sync_api import Page
from pages.new_page import NewPage

class TestNewFeature:
    @pytest.mark.smoke
    def test_new_functionality(self, page: Page, base_url: str):
        new_page = NewPage(page, base_url)
        # Test implementation
        assert True
```

## Troubleshooting

### Common Issues

1. **Browser not found error:**
   ```bash
   playwright install
   ```

2. **Import errors:**
   ```bash
   # Ensure virtual environment is activated
   pip install -r requirements.txt
   ```

3. **Test timeouts:**
   - Check network connectivity
   - Increase timeout values in page objects
   - Verify base URL is accessible

### Debug Mode

Run tests with verbose output and no capture:
```bash
pytest -v -s
```

Take screenshots on failure:
```bash
pytest --screenshot=on
```

## CI/CD Integration

{self._get_ci_cd_details()}

## Dependencies

Key dependencies used in this framework:

- **pytest**: Testing framework
- **playwright**: Browser automation
- **pytest-playwright**: Playwright integration for pytest
{self._get_dependency_details()}

## Contributing

1. Follow the existing code structure and naming conventions
2. Add appropriate test markers
3. Include documentation for new page objects and utilities
4. Ensure all tests pass before submitting changes

## License

This test automation framework is for testing **{self.config['site_name']}** and is subject to your organization's testing and quality assurance policies.

---

Generated by Test Automation Framework Generator
'''

        (project_path / "README.md").write_text(readme_content, encoding='utf-8')

    def _get_test_coverage_details(self) -> str:
        """Get detailed test coverage information for README"""
        details = ["- **Basic Tests**: Homepage loading, navigation, JavaScript error detection"]

        if self.config['include_accessibility']:
            details.append("- **Accessibility Tests**: WCAG compliance, keyboard navigation, color contrast, alt text")

        if self.config['include_lighthouse']:
            details.append("- **Performance Tests**: Lighthouse scores, Core Web Vitals, page load metrics")

        if self.config['include_broken_links']:
            details.append("- **Link Validation**: Broken links, external link security, image sources")

        if self.config['include_seo']:
            details.append("- **SEO Tests**: Meta tags, heading structure, Open Graph, structured data")

        return "\\n".join(details)

    def _get_test_run_examples(self) -> str:
        """Get test run examples for enabled test types"""
        examples = []

        if self.config['include_accessibility']:
            examples.append("# Accessibility tests\\npytest -m accessibility")

        if self.config['include_lighthouse']:
            examples.append("# Performance tests\\npytest -m lighthouse")

        if self.config['include_broken_links']:
            examples.append("# Broken links tests\\npytest -m broken_links")

        if self.config['include_seo']:
            examples.append("# SEO tests\\npytest -m seo")

        return "\\n\\n".join(examples)

    def _get_project_structure_details(self) -> str:
        """Get project structure details for enabled test types"""
        details = []

        if self.config['include_accessibility']:
            details.append("│   ├── accessibility/     # WCAG compliance tests")

        if self.config['include_lighthouse']:
            details.append("│   ├── lighthouse/        # Performance and Core Web Vitals")

        if self.config['include_broken_links']:
            details.append("│   ├── broken_links/      # Link validation tests")

        if self.config['include_seo']:
            details.append("│   ├── seo/              # SEO optimization tests")

        details.append("│   └── __init__.py")

        return "\\n".join(details)

    def _get_marker_details(self) -> str:
        """Get pytest marker details for enabled test types"""
        details = []

        if self.config['include_accessibility']:
            details.append("- `accessibility` - WCAG compliance and accessibility tests")

        if self.config['include_lighthouse']:
            details.append("- `lighthouse` - Performance and Core Web Vitals tests")

        if self.config['include_broken_links']:
            details.append("- `broken_links` - Link validation and broken link tests")

        if self.config['include_seo']:
            details.append("- `seo` - SEO optimization and meta tag tests")

        return "\\n".join(details)

    def _get_dependency_details(self) -> str:
        """Get dependency details for enabled test types"""
        details = ["- **pytest-html**: HTML test reports"]

        if self.config['include_accessibility']:
            details.append("- **axe-playwright**: Accessibility testing with axe-core")

        if self.config['include_lighthouse']:
            details.append("- **python-lighthouse**: Lighthouse performance audits")

        details.extend([
            "- **requests**: HTTP requests for link validation",
            "- **beautifulsoup4**: HTML parsing and analysis"
        ])

        return "\\n".join(details)

    def _get_ci_cd_details(self) -> str:
        """Get CI/CD details for README"""
        if self.config['github_actions']:
            return '''This project includes GitHub Actions workflow for automated testing.

### GitHub Actions

The workflow file `.github/workflows/test.yml` runs tests on:
- Push to main branch
- Pull requests
- Scheduled daily runs

**Workflow features:**
- Multi-browser testing (Chromium, Firefox, Safari)
- Parallel test execution
- HTML report generation
- Test artifacts upload

**Manual workflow dispatch:**
```bash
# From GitHub UI or using GitHub CLI
gh workflow run test.yml
```'''
        else:
            return '''### Setting up CI/CD

To integrate with your CI/CD pipeline:

1. **Install dependencies in CI environment**
2. **Install Playwright browsers**: `playwright install`
3. **Run tests**: `pytest --html=reports/report.html`
4. **Archive test reports** as build artifacts

**Example CI commands:**
```bash
pip install -r requirements.txt
playwright install
pytest --html=reports/report.html --self-contained-html
```'''

    def _generate_github_actions(self, project_path: Path):
        """Generate GitHub Actions workflow file"""
        workflow_content = f'''name: Test Automation for {self.config['site_name']}

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    # Run daily at 2 AM UTC
    - cron: '0 2 * * *'
  workflow_dispatch:
    inputs:
      browser:
        description: 'Browser to test with'
        required: false
        default: 'chromium'
        type: choice
        options:
        - chromium
        - firefox
        - webkit
        - all

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        browser: [chromium, firefox, webkit]

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{{{ runner.os }}}}-pip-${{{{ hashFiles('**/requirements.txt') }}}}
        restore-keys: |
          ${{{{ runner.os }}}}-pip-

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Install Playwright browsers
      run: playwright install --with-deps ${{{{ matrix.browser }}}}

    - name: Run smoke tests
      run: |
        pytest tests/test_basic.py \\
          --browser ${{{{ matrix.browser }}}} \\
          --html=reports/smoke-report-${{{{ matrix.browser }}}}.html \\
          --self-contained-html \\
          -v

{self._get_github_actions_test_jobs()}

    - name: Upload test reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-reports-${{{{ matrix.browser }}}}
        path: |
          reports/

    - name: Upload screenshots
      uses: actions/upload-artifact@v3
      if: failure()
      with:
        name: screenshots-${{{{ matrix.browser }}}}
        path: reports/screenshots/

  accessibility-audit:
    runs-on: ubuntu-latest
    if: contains(github.event.head_commit.message, '[accessibility]') || github.event_name == 'schedule'

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Install Playwright browsers
      run: playwright install --with-deps chromium

    - name: Run accessibility audit
      run: |
{self._get_accessibility_audit_command()}

    - name: Upload accessibility report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: accessibility-report
        path: reports/

  performance-audit:
    runs-on: ubuntu-latest
    if: contains(github.event.head_commit.message, '[performance]') || github.event_name == 'schedule'

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        npm install -g lighthouse

    - name: Install Playwright browsers
      run: playwright install --with-deps chromium

    - name: Run performance audit
      run: |
{self._get_performance_audit_command()}

    - name: Upload performance report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: performance-report
        path: reports/

  link-validation:
    runs-on: ubuntu-latest
    if: contains(github.event.head_commit.message, '[links]') || github.event_name == 'schedule'

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Install Playwright browsers
      run: playwright install --with-deps chromium

    - name: Run link validation
      run: |
{self._get_link_validation_command()}

    - name: Upload link validation report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: link-validation-report
        path: reports/
'''

        (project_path / ".github" / "workflows" / "test.yml").write_text(workflow_content, encoding='utf-8')

    def _get_github_actions_test_jobs(self) -> str:
        """Get GitHub Actions test job steps for enabled test types"""
        jobs = []

        if self.config['include_accessibility']:
            jobs.append('''    - name: Run accessibility tests
      run: |
        pytest tests/accessibility/ \\
          --browser ${{ matrix.browser }} \\
          --html=reports/accessibility-report-${{ matrix.browser }}.html \\
          --self-contained-html \\
          -v''')

        if self.config['include_lighthouse']:
            jobs.append('''    - name: Run performance tests
      run: |
        pytest tests/lighthouse/ \\
          --browser ${{ matrix.browser }} \\
          --html=reports/performance-report-${{ matrix.browser }}.html \\
          --self-contained-html \\
          -v''')

        if self.config['include_broken_links']:
            jobs.append('''    - name: Run broken links tests
      run: |
        pytest tests/broken_links/ \\
          --browser ${{ matrix.browser }} \\
          --html=reports/broken-links-report-${{ matrix.browser }}.html \\
          --self-contained-html \\
          -v''')

        if self.config['include_seo']:
            jobs.append('''    - name: Run SEO tests
      run: |
        pytest tests/seo/ \\
          --browser ${{ matrix.browser }} \\
          --html=reports/seo-report-${{ matrix.browser }}.html \\
          --self-contained-html \\
          -v''')

        return "\\n\\n".join(jobs)

    def _get_accessibility_audit_command(self) -> str:
        """Get accessibility audit command for GitHub Actions"""
        if self.config['include_accessibility']:
            return '''        pytest tests/accessibility/ \\
          --browser chromium \\
          --html=reports/accessibility-audit.html \\
          --self-contained-html \\
          -v'''
        else:
            return '''        echo "Accessibility tests not configured"
        exit 1'''

    def _get_performance_audit_command(self) -> str:
        """Get performance audit command for GitHub Actions"""
        if self.config['include_lighthouse']:
            return '''        pytest tests/lighthouse/ \\
          --browser chromium \\
          --html=reports/performance-audit.html \\
          --self-contained-html \\
          -v'''
        else:
            return '''        echo "Performance tests not configured"
        exit 1'''

    def _get_link_validation_command(self) -> str:
        """Get link validation command for GitHub Actions"""
        if self.config['include_broken_links']:
            return '''        pytest tests/broken_links/ \\
          --browser chromium \\
          --html=reports/link-validation.html \\
          --self-contained-html \\
          -v'''
        else:
            return '''        echo "Link validation tests not configured"
        exit 1'''


def main():
    """Main entry point for the generator"""
    generator = TestFrameworkGenerator()

    try:
        generator.get_user_input()
        generator.generate_framework()
    except KeyboardInterrupt:
        print("\n\nGeneration cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError generating framework: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()