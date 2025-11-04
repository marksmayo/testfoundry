"""
Base templates for core framework files.
Contains templates for pytest configuration, base page objects, etc.
"""

def get_pytest_config_template() -> str:
    """Get pytest.ini configuration template"""
    return """[pytest]
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
    nondestructive: mark test as nondestructive (allows running on any URL)
"""


def get_conftest_template(base_url: str) -> str:
    """Get conftest.py template"""
    return f"""import pytest
from playwright.sync_api import Page, expect
import os
import subprocess
import sys
import webbrowser
from pathlib import Path
import pytest_html

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
    return "{base_url}"

# Mark all tests as nondestructive to bypass pytest-base-url protection
pytestmark = pytest.mark.nondestructive

@pytest.fixture
def page_with_base_url(page: Page, base_url: str):
    page.goto(base_url)
    return page

# Custom HTML report hooks for TestFoundry branding
def pytest_html_report_title(report):
    report.title = "TestFoundry Test Report"

def pytest_html_results_table_header(cells):
    cells.insert(2, "TestFoundry")

def pytest_html_results_table_row(report, cells):
    cells.insert(2, "✓")

def pytest_configure(config):
    \"\"\"Configure pytest and add custom CSS/logo to HTML report\"\"\"
    # Disable sensitive URL protection from pytest-base-url
    config.addinivalue_line("markers", "nondestructive: mark test as nondestructive")

    # Add custom CSS to HTML report
    if hasattr(config, '_html'):
        logo_path = Path("assets/logo.png")
        logo_base64 = ""

        if logo_path.exists():
            import base64
            logo_data = logo_path.read_bytes()
            logo_base64 = base64.b64encode(logo_data).decode('utf-8')

        custom_css = '''
        <style>
            .testfoundry-header {{
                background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                color: white;
                padding: 20px;
                text-align: center;
                margin-bottom: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
            }}
            .testfoundry-logo {{
                height: 60px;
                margin-right: 15px;
                vertical-align: middle;
                filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
            }}
            .testfoundry-title {{
                display: inline-block;
                vertical-align: middle;
                font-size: 2em;
                margin: 0;
                font-weight: 700;
            }}
            body {{
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
        </style>
        '''

        config._html.extra_css.append(custom_css)

        # Store logo base64 for later use in report summary
        if logo_base64:
            config._html.logo_base64 = logo_base64

def pytest_html_results_summary(prefix, summary, postfix, session):
    \"\"\"Add custom header with logo to HTML report summary\"\"\"
    logo_html = ""
    if hasattr(session.config, '_html') and hasattr(session.config._html, 'logo_base64'):
        logo_base64 = session.config._html.logo_base64
        logo_html = f"<img src='data:image/png;base64,{{logo_base64}}' alt='TestFoundry' class='testfoundry-logo'>"

    prefix.insert(0, f'''
    <div class="testfoundry-header">
        {{logo_html}}
        <h1 class="testfoundry-title">TestFoundry Test Report</h1>
    </div>
    ''')

# Auto-open HTML report after tests complete
def pytest_sessionfinish(session, exitstatus):
    \"\"\"Automatically open HTML report after test session completes\"\"\"
    report_path = Path("reports/report.html")
    if report_path.exists():
        # Use webbrowser to open the report (cross-platform)
        try:
            webbrowser.open(f"file://{{report_path.absolute()}}")
        except Exception:
            # Fallback: try to open with system default
            try:
                if sys.platform == "win32":
                    os.startfile(str(report_path.absolute()))
                elif sys.platform == "darwin":
                    subprocess.run(["open", str(report_path.absolute())])
                else:
                    subprocess.run(["xdg-open", str(report_path.absolute())])
            except Exception:
                pass  # Silently fail if we can't open the report
"""


def get_base_page_template() -> str:
    """Get base page object template"""
    return '''"""
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


def get_home_page_template(site_name: str) -> str:
    """Get home page object template"""
    return f'''"""
Home page object for {site_name}
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
