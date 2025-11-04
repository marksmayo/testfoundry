"""
Utilities generator.
Generates utility files and helper functions for the test framework.
"""

from pathlib import Path
from .base import BaseGenerator


class UtilsGenerator(BaseGenerator):
    """Generates utility files for the test framework"""
    
    def generate_test_utils(self, project_path: Path) -> None:
        """Generate test utilities file"""
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
    def save_test_data(data: Dict[str, Any], filename: str) -> str:
        """Save test data to JSON file in reports directory"""
        reports_dir = Path("reports/test_data")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = reports_dir / f"{filename}_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    @staticmethod
    def get_browser_info(page: Page) -> Dict[str, str]:
        """Get browser information for debugging"""
        return page.evaluate("""
            () => ({
                userAgent: navigator.userAgent,
                language: navigator.language,
                platform: navigator.platform,
                cookieEnabled: navigator.cookieEnabled,
                onLine: navigator.onLine,
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight
            })
        """)


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
    
    @staticmethod
    def generate_summary_report(test_results: Dict[str, Any]) -> str:
        """Generate overall test summary report"""
        report = [
            "Test Execution Summary",
            "=" * 50,
            ""
        ]
        
        if 'total_tests' in test_results:
            report.append(f"Total Tests: {test_results['total_tests']}")
        
        if 'passed' in test_results:
            report.append(f"Passed: {test_results['passed']}")
        
        if 'failed' in test_results:
            report.append(f"Failed: {test_results['failed']}")
        
        if 'duration' in test_results:
            report.append(f"Duration: {test_results['duration']:.2f}s")
        
        return "\\n".join(report)
'''
        
        self.write_file(project_path / "utils" / "test_utils.py", utils_content)
    
    def generate_all_utils(self, project_path: Path) -> None:
        """Generate all utility files"""
        self.generate_test_utils(project_path)