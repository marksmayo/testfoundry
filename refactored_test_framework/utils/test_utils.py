"""
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
    def save_test_data(data: Dict[str, Any], filename: str) -> str:
        """Save test data to JSON file in reports directory"""
        reports_dir = Path("reports/test_data")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = reports_dir / f"{filename}_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
