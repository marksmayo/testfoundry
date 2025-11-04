# Improved Test Site Test Automation Framework

This project contains automated tests for **Improved Test Site** using Python, pytest, and Playwright.

## Test Coverage

This framework includes the following test types:
- **Basic Tests**: Homepage loading, navigation, JavaScript error detection
- **Accessibility Tests**: WCAG compliance, keyboard navigation, color contrast\n- **Performance Tests**: Lighthouse scores, Core Web Vitals, page load metrics\n- **SEO Tests**: Meta tags, heading structure, structured data

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd improved_test_framework
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
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

# Accessibility tests\npytest -m accessibility\n\n# Performance tests\npytest -m lighthouse\n\n# SEO tests\npytest -m seo
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
improved_test_framework/
├── tests/                 # Test files organized by type
│   ├── test_basic.py     # Basic smoke tests (always included)
│   ├── accessibility/     # WCAG compliance tests\n│   ├── lighthouse/        # Performance and Core Web Vitals\n│   ├── seo/              # SEO optimization tests\n│   └── __init__.py
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
- `accessibility` - WCAG compliance and accessibility tests\n- `lighthouse` - Performance and Core Web Vitals tests\n- `seo` - SEO optimization and meta tag tests

### Browser Configuration

Browser settings can be modified in `conftest.py`:

```python
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
        # Add more browser options as needed
    }
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

This project includes GitHub Actions workflow for automated testing.

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
```

## Dependencies

Key dependencies used in this framework:

- **pytest**: Testing framework
- **playwright**: Browser automation
- **pytest-playwright**: Playwright integration for pytest
- **pytest-html**: HTML test reports\n- **axe-playwright**: Accessibility testing with axe-core\n- **python-lighthouse**: Lighthouse performance audits\n- **requests**: HTTP requests for link validation\n- **beautifulsoup4**: HTML parsing and analysis

## Contributing

1. Follow the existing code structure and naming conventions
2. Add appropriate test markers
3. Include documentation for new page objects and utilities
4. Ensure all tests pass before submitting changes

## License

This test automation framework is for testing **Improved Test Site** and is subject to your organization's testing and quality assurance policies.

---

Generated by Test Automation Framework Generator
