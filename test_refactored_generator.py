#!/usr/bin/env python3
"""
Test script for the refactored Test Automation Framework Generator
Creates a sample project to verify all components work correctly with the new modular structure
"""

import sys
import shutil
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from framework_generator.framework_generator import FrameworkGenerator
from framework_generator.config.models import GeneratorConfig


def test_refactored_generator():
    """Test the refactored generator with sample configuration"""
    
    # Clean up any existing test project
    test_project_path = Path("refactored_test_framework")
    if test_project_path.exists():
        shutil.rmtree(test_project_path)
    
    print("Testing Refactored Test Automation Framework Generator...")
    
    # Create test configuration
    config = GeneratorConfig(
        project_name='refactored_test_framework',
        site_name='Example Website (Refactored)',
        base_url='https://example.com',
        include_accessibility=True,
        include_lighthouse=True,
        include_broken_links=True,
        include_seo=True,
        html_reports=True,
        github_actions=True
    )
    
    print(f"Configuration: {config.to_dict()}")
    
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
            test_project_path / "tests" / "broken_links" / "test_broken_links.py",
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
        
        if all_files_exist:
            print("\\n[SUCCESS] All expected files generated successfully!")
            
            # Verify some content
            readme_content = (test_project_path / "README.md").read_text(encoding='utf-8')
            requirements_content = (test_project_path / "requirements.txt").read_text(encoding='utf-8')
            
            print("\\nContent verification:")
            print(f"README mentions site name: {'Example Website (Refactored)' in readme_content}")
            print(f"Requirements includes pytest: {'pytest' in requirements_content}")
            print(f"Requirements includes playwright: {'playwright' in requirements_content}")
            print(f"Requirements includes axe-playwright: {'axe-playwright' in requirements_content}")
            
            # Test configuration model
            print("\\nConfiguration model test:")
            config_dict = config.to_dict()
            reconstructed_config = GeneratorConfig.from_dict(config_dict)
            print(f"Config serialization/deserialization: {config.project_name == reconstructed_config.project_name}")
            print(f"Enabled test types: {config.get_enabled_test_types()}")
            
            return True
        else:
            print("\\n[ERROR] Some files are missing!")
            return False
            
    except Exception as e:
        print(f"\\n[ERROR] Error during generation: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration_validation():
    """Test configuration validation"""
    print("\\nTesting configuration validation...")
    
    # Test valid configuration
    try:
        valid_config = GeneratorConfig(
            project_name="test_project",
            site_name="Test Site", 
            base_url="https://example.com"
        )
        print("[OK] Valid configuration accepted")
    except Exception as e:
        print(f"[ERROR] Valid configuration rejected: {e}")
        return False
    
    # Test invalid configurations
    test_cases = [
        ("empty project name", {"project_name": "", "site_name": "Test", "base_url": "https://example.com"}),
        ("empty site name", {"project_name": "test", "site_name": "", "base_url": "https://example.com"}),
        ("invalid URL", {"project_name": "test", "site_name": "Test", "base_url": "not-a-url"}),
        ("missing protocol", {"project_name": "test", "site_name": "Test", "base_url": "example.com"}),
    ]
    
    for test_name, config_data in test_cases:
        try:
            GeneratorConfig(**config_data)
            print(f"[ERROR] {test_name} should have been rejected")
            return False
        except ValueError:
            print(f"[OK] {test_name} correctly rejected")
        except Exception as e:
            print(f"[ERROR] {test_name} failed with unexpected error: {e}")
            return False
    
    return True


if __name__ == "__main__":
    print("=== Testing Refactored Framework Generator ===\\n")
    
    # Test configuration validation
    config_test_passed = test_configuration_validation()
    
    # Test generator functionality
    generator_test_passed = test_refactored_generator()
    
    # Summary
    print("\\n=== Test Summary ===")
    print(f"Configuration validation: {'PASSED' if config_test_passed else 'FAILED'}")
    print(f"Generator functionality: {'PASSED' if generator_test_passed else 'FAILED'}")
    
    if config_test_passed and generator_test_passed:
        print("\\n[SUCCESS] All tests passed! Refactored generator is working correctly.")
        exit(0)
    else:
        print("\\n[FAILED] Some tests failed!")
        exit(1)