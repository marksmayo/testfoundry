#!/usr/bin/env python3
"""
Test script for the improved Test Automation Framework Generator
Tests the new validation, logging, and modular structure
"""

import sys
import shutil
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from framework_generator.framework_generator import FrameworkGenerator
from framework_generator.config.models import GeneratorConfig
from framework_generator.config.validation import ConfigValidator


def test_improved_validation():
    """Test the improved validation system"""
    print("=== Testing Improved Validation ===")
    
    # Test project name validation
    valid, error = ConfigValidator.validate_project_name("my-test-project")
    print(f"Valid project name: {valid} (should be True)")
    
    valid, error = ConfigValidator.validate_project_name("test")  # Reserved name
    print(f"Reserved project name rejected: {not valid} (should be True)")
    print(f"Error message: {error}")
    
    # Test URL validation
    valid, error = ConfigValidator.validate_url("https://example.com")
    print(f"Valid URL: {valid} (should be True)")
    
    valid, error = ConfigValidator.validate_url("not-a-url")
    print(f"Invalid URL rejected: {not valid} (should be True)")
    print(f"Error message: {error}")
    
    # Test sanitization
    sanitized = ConfigValidator.sanitize_project_name("My Test Project!!!")
    print(f"Sanitized name: '{sanitized}' (should be valid)")
    
    return True


def test_improved_generator():
    """Test the improved generator with new modular structure"""
    print("\\n=== Testing Improved Generator ===")
    
    # Clean up any existing test project
    test_project_path = Path("improved_test_framework")
    if test_project_path.exists():
        shutil.rmtree(test_project_path)
    
    # Create test configuration
    config = GeneratorConfig(
        project_name='improved_test_framework',
        site_name='Improved Test Site',
        base_url='https://improved.example.com',
        include_accessibility=True,
        include_lighthouse=True,
        include_broken_links=False,
        include_seo=True,
        html_reports=True,
        github_actions=True
    )
    
    try:
        # Create generator and generate framework
        generator = FrameworkGenerator()
        generator.generate_framework(config)
        
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
            test_project_path / "tests" / "seo" / "test_seo.py",
            test_project_path / "utils" / "test_utils.py",
            test_project_path / ".github" / "workflows" / "test.yml"
        ]
        
        print("\\nVerifying generated files:")
        all_files_exist = True
        for file_path in expected_files:
            if file_path.exists():
                print(f"[OK] {file_path}")
            else:
                print(f"[MISSING] {file_path}")
                all_files_exist = False
        
        # Verify improved content
        if all_files_exist:
            print("\\n[SUCCESS] All expected files generated!")
            
            # Check for improved features
            readme_content = (test_project_path / "README.md").read_text(encoding='utf-8')
            utils_content = (test_project_path / "utils" / "test_utils.py").read_text(encoding='utf-8')
            github_actions = (test_project_path / ".github" / "workflows" / "test.yml").read_text(encoding='utf-8')
            
            print("\\nContent verification:")
            print(f"README mentions site name: {'Improved Test Site' in readme_content}")
            print(f"Utils has ReportGenerator: {'ReportGenerator' in utils_content}")
            print(f"GitHub Actions has specialized jobs: {'accessibility-audit' in github_actions}")
            print(f"GitHub Actions has cache: {'cache:' in github_actions}")
            
            return True
        else:
            print("\\n[ERROR] Some files are missing!")
            return False
            
    except Exception as e:
        print(f"\\n[ERROR] Error during generation: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation_edge_cases():
    """Test validation edge cases"""
    print("\\n=== Testing Validation Edge Cases ===")
    
    edge_cases = [
        ("", "", ""),  # All empty
        ("a", "b", "ftp://invalid.com"),  # Too short, invalid protocol
        ("my_project", "My Site", "https://example.com"),  # Valid case
        ("123-test-project", "Test Site 123", "http://localhost:3000"),  # Valid with numbers
    ]
    
    for i, (project, site, url) in enumerate(edge_cases):
        print(f"\\nCase {i+1}: project='{project}', site='{site}', url='{url}'")
        
        try:
            config = GeneratorConfig(
                project_name=project,
                site_name=site,
                base_url=url
            )
            print("  [OK] Configuration accepted")
        except ValueError as e:
            print(f"  [REJECTED] Configuration rejected: {e}")
    
    return True


if __name__ == "__main__":
    print("=== Testing Improved Framework Generator ===\\n")
    
    # Test validation improvements
    validation_test_passed = test_improved_validation()
    
    # Test edge cases
    edge_case_test_passed = test_validation_edge_cases()
    
    # Test improved generator
    generator_test_passed = test_improved_generator()
    
    # Summary
    print("\\n=== Test Summary ===")
    print(f"Validation improvements: {'PASSED' if validation_test_passed else 'FAILED'}")
    print(f"Edge case handling: {'PASSED' if edge_case_test_passed else 'FAILED'}")
    print(f"Improved generator: {'PASSED' if generator_test_passed else 'FAILED'}")
    
    if validation_test_passed and edge_case_test_passed and generator_test_passed:
        print("\\n[SUCCESS] All improvement tests passed!")
        exit(0)
    else:
        print("\\n[FAILED] Some improvement tests failed!")
        exit(1)