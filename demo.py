#!/usr/bin/env python3
"""
Demo script showing the refactored generator in action.
"""

import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from framework_generator.framework_generator import FrameworkGenerator
from framework_generator.config.models import GeneratorConfig


def demo_basic_framework():
    """Demo creating a basic framework"""
    print("=== Demo: Basic Framework ===")
    
    config = GeneratorConfig(
        project_name='demo_basic',
        site_name='Demo Basic Site',
        base_url='https://demo-basic.com',
        include_accessibility=False,
        include_lighthouse=False,
        include_broken_links=False,
        include_seo=False,
        html_reports=True,
        github_actions=False
    )
    
    generator = FrameworkGenerator()
    generator.generate_framework(config)


def demo_full_framework():
    """Demo creating a framework with all features"""
    print("\\n=== Demo: Full Framework ===")
    
    config = GeneratorConfig(
        project_name='demo_full',
        site_name='Demo Full Featured Site',
        base_url='https://demo-full.com',
        include_accessibility=True,
        include_lighthouse=True,
        include_broken_links=True,
        include_seo=True,
        html_reports=True,
        github_actions=True
    )
    
    generator = FrameworkGenerator()
    generator.generate_framework(config)


if __name__ == "__main__":
    print("Test Automation Framework Generator - Demo\\n")
    
    # Clean up any existing demo projects
    import shutil
    for project in ['demo_basic', 'demo_full']:
        if Path(project).exists():
            shutil.rmtree(project)
    
    try:
        demo_basic_framework()
        demo_full_framework()
        
        print("\\n=== Demo Complete ===")
        print("Two demo frameworks have been created:")
        print("1. demo_basic/ - Basic framework with smoke tests only")
        print("2. demo_full/ - Full framework with all test types and CI/CD")
        
    except Exception as e:
        print(f"Demo failed: {e}")
        sys.exit(1)