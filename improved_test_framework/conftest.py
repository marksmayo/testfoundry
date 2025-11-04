import pytest
from playwright.sync_api import Page, expect

# Playwright configuration
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }

@pytest.fixture(scope="session") 
def base_url():
    return "https://improved.example.com"

@pytest.fixture
def page_with_base_url(page: Page, base_url: str):
    page.goto(base_url)
    return page
