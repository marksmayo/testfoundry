"""
CI/CD generator.
Generates CI/CD configuration files for various platforms.
"""

from pathlib import Path
from .base import BaseGenerator


class CICDGenerator(BaseGenerator):
    """Generates CI/CD configuration files"""
    
    def generate_github_actions(self, project_path: Path) -> None:
        """Generate GitHub Actions workflow file"""
        workflow_content = f'''name: Test Automation for {self.config.site_name}

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

{self._get_specialized_jobs()}
'''
        
        self.write_file(project_path / ".github" / "workflows" / "test.yml", workflow_content)
    
    def _get_github_actions_test_jobs(self) -> str:
        """Get GitHub Actions test job steps for enabled test types"""
        jobs = []
        
        if self.config.include_accessibility:
            jobs.append('''    - name: Run accessibility tests
      run: |
        pytest tests/accessibility/ \\
          --browser ${{ matrix.browser }} \\
          --html=reports/accessibility-report-${{ matrix.browser }}.html \\
          --self-contained-html \\
          -v''')
          
        if self.config.include_lighthouse:
            jobs.append('''    - name: Run performance tests
      run: |
        pytest tests/lighthouse/ \\
          --browser ${{ matrix.browser }} \\
          --html=reports/performance-report-${{ matrix.browser }}.html \\
          --self-contained-html \\
          -v''')
          
        if self.config.include_broken_links:
            jobs.append('''    - name: Run broken links tests
      run: |
        pytest tests/broken_links/ \\
          --browser ${{ matrix.browser }} \\
          --html=reports/broken-links-report-${{ matrix.browser }}.html \\
          --self-contained-html \\
          -v''')
          
        if self.config.include_seo:
            jobs.append('''    - name: Run SEO tests
      run: |
        pytest tests/seo/ \\
          --browser ${{ matrix.browser }} \\
          --html=reports/seo-report-${{ matrix.browser }}.html \\
          --self-contained-html \\
          -v''')
        
        return "\\n\\n".join(jobs)
    
    def _get_specialized_jobs(self) -> str:
        """Get specialized jobs for different test types"""
        jobs = []
        
        # Accessibility audit job
        if self.config.include_accessibility:
            jobs.append('''
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
        pytest tests/accessibility/ \\
          --browser chromium \\
          --html=reports/accessibility-audit.html \\
          --self-contained-html \\
          -v
        
    - name: Upload accessibility report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: accessibility-report
        path: reports/''')
        
        # Performance audit job  
        if self.config.include_lighthouse:
            jobs.append('''
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
        pytest tests/lighthouse/ \\
          --browser chromium \\
          --html=reports/performance-audit.html \\
          --self-contained-html \\
          -v
        
    - name: Upload performance report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: performance-report
        path: reports/''')
        
        return "".join(jobs)
    
    def generate_gitlab_ci(self, project_path: Path) -> None:
        """Generate GitLab CI configuration"""
        gitlab_content = f'''# GitLab CI configuration for {self.config.site_name} test automation

stages:
  - test
  - report

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - node_modules/

before_script:
  - python -m pip install --upgrade pip
  - pip install -r requirements.txt
  - playwright install

test:smoke:
  stage: test
  script:
    - pytest tests/test_basic.py --html=reports/smoke-report.html --self-contained-html -v
  artifacts:
    when: always
    paths:
      - reports/
    expire_in: 1 week

{self._get_gitlab_test_jobs()}

pages:
  stage: report
  script:
    - mkdir public
    - cp -r reports/* public/ || true
  artifacts:
    paths:
      - public
  only:
    - main
'''
        
        self.write_file(project_path / ".gitlab-ci.yml", gitlab_content)
    
    def _get_gitlab_test_jobs(self) -> str:
        """Get GitLab CI test jobs for enabled test types"""
        jobs = []
        
        if self.config.include_accessibility:
            jobs.append('''
test:accessibility:
  stage: test
  script:
    - pytest tests/accessibility/ --html=reports/accessibility-report.html --self-contained-html -v
  artifacts:
    when: always
    paths:
      - reports/
    expire_in: 1 week''')
        
        if self.config.include_lighthouse:
            jobs.append('''
test:performance:
  stage: test
  before_script:
    - python -m pip install --upgrade pip
    - pip install -r requirements.txt
    - playwright install
    - npm install -g lighthouse
  script:
    - pytest tests/lighthouse/ --html=reports/performance-report.html --self-contained-html -v
  artifacts:
    when: always
    paths:
      - reports/
    expire_in: 1 week''')
        
        if self.config.include_broken_links:
            jobs.append('''
test:links:
  stage: test
  script:
    - pytest tests/broken_links/ --html=reports/links-report.html --self-contained-html -v
  artifacts:
    when: always
    paths:
      - reports/
    expire_in: 1 week''')
        
        if self.config.include_seo:
            jobs.append('''
test:seo:
  stage: test
  script:
    - pytest tests/seo/ --html=reports/seo-report.html --self-contained-html -v
  artifacts:
    when: always
    paths:
      - reports/
    expire_in: 1 week''')
        
        return "".join(jobs)
    
    def generate_all_cicd(self, project_path: Path) -> None:
        """Generate all CI/CD files based on configuration"""
        if self.config.github_actions:
            self.generate_github_actions(project_path)