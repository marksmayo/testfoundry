#!/usr/bin/env python3
"""
Test script for the Test Automation Framework Generator
Creates a sample project to verify all components work correctly
"""

import os
import shutil
from pathlib import Path
from generator import TestFrameworkGenerator


def test_generator():
    """Test the generator with sample configuration"""
    
    # Clean up any existing test project
    test_project_path = Path("sample_test_framework")
    if test_project_path.exists():
        shutil.rmtree(test_project_path)
    
    # Create generator instance
    generator = TestFrameworkGenerator()
    
    # Set up test configuration manually (bypass user input)
    generator.config = {
        'project_name': 'sample_test_framework',
        'site_name': 'Example Website',
        'base_url': 'https://example.com',
        'include_accessibility': True,
        'include_lighthouse': True,
        'include_broken_links': True,
        'include_seo': True,
        'html_reports': True,
        'github_actions': True
    }
    
    print("Testing Test Automation Framework Generator...")
    print(f"Configuration: {generator.config}")
    
    try:
        # Generate the framework
        generator.generate_framework()
        
        # Verify key files were created
        expected_files = [
            test_project_path / "requirements.txt",
            test_project_path / "pytest.ini", 
            test_project_path / "conftest.py",
            test_project_path / "README.md",
            test_project_path / "pages" / "base_page.py",
            test_project_path / "pages" / "home_page.py",
            test_project_path / "tests" / "test_basic.py",
            test_project_path / "tests" / "accessibility" / "test_accessibility.py",
            test_project_path / "tests" / "lighthouse" / "test_performance.py",
            test_project_path / "tests" / "broken_links" / "test_broken_links.py",
            test_project_path / "tests" / "seo" / "test_seo.py",
            test_project_path / "utils" / "test_utils.py",
            test_project_path / ".github" / "workflows" / "test.yml"
        ]
        
        print("\nVerifying generated files:")
        all_files_exist = True
        for file_path in expected_files:
            if file_path.exists():
                print(f"[OK] {file_path}")
            else:
                print(f"[MISSING] {file_path}")
                all_files_exist = False
        
        if all_files_exist:
            print("\n[SUCCESS] All expected files generated successfully!")
            
            # Verify some content
            readme_content = (test_project_path / "README.md").read_text()
            requirements_content = (test_project_path / "requirements.txt").read_text()
            
            print("\nSample content verification:")
            print(f"README mentions site name: {'Example Website' in readme_content}")
            print(f"Requirements includes pytest: {'pytest' in requirements_content}")
            print(f"Requirements includes playwright: {'playwright' in requirements_content}")
            
            return True
        else:
            print("\n[ERROR] Some files are missing!")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Error during generation: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_generator()
    if success:
        print("\n[SUCCESS] Generator test completed successfully!")
    else:
        print("\n[FAILED] Generator test failed!")
        exit(1)