"""
CLI interface for collecting user input and configuration.
Handles interactive prompts and user input validation.
"""

import sys
from typing import Optional
from ..config.models import GeneratorConfig


class CLIInterface:
    """Command line interface for the test framework generator"""
    
    def __init__(self):
        self.config_data = {}
    
    def collect_configuration(self) -> GeneratorConfig:
        """Collect configuration from user via CLI prompts"""
        print("=== TestFoundry - Test Automation Framework Generator ===\n")
        
        try:
            self._collect_project_details()
            self._collect_test_types()
            self._collect_report_configuration()
            self._collect_cicd_configuration()
            
            return GeneratorConfig.from_dict(self.config_data)
        
        except KeyboardInterrupt:
            print("\n\nGeneration cancelled by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\nError collecting configuration: {e}")
            sys.exit(1)
    
    def _collect_project_details(self):
        """Collect basic project configuration"""
        self.config_data['project_name'] = self._get_required_input(
            "Enter project folder name"
        )
        
        self.config_data['site_name'] = self._get_input_with_default(
            "Enter site name (for documentation)",
            default=self.config_data['project_name']
        )
        
        self.config_data['base_url'] = self._get_required_input(
            "Enter base URL (e.g., https://example.com)"
        )
    
    def _collect_test_types(self):
        """Collect test type selections"""
        print("\nSelect test types to include:")
        
        self.config_data['include_accessibility'] = self._get_yes_no(
            "Include accessibility tests? (y/N)", default=False
        )
        
        self.config_data['include_lighthouse'] = self._get_yes_no(
            "Include Lighthouse performance tests? (y/N)", default=False
        )
        
        self.config_data['include_broken_links'] = self._get_yes_no(
            "Include broken links tests? (y/N)", default=False
        )
        
        self.config_data['include_seo'] = self._get_yes_no(
            "Include SEO tests? (y/N)", default=False
        )
    
    def _collect_report_configuration(self):
        """Collect reporting configuration"""
        print("\nReport configuration:")
        
        self.config_data['html_reports'] = self._get_yes_no(
            "Generate HTML reports? (Y/n)", default=True
        )
    
    def _collect_cicd_configuration(self):
        """Collect CI/CD configuration"""
        print("\nCI/CD configuration:")
        
        self.config_data['github_actions'] = self._get_yes_no(
            "Generate GitHub Actions workflow? (y/N)", default=False
        )
    
    def _get_required_input(self, prompt: str) -> str:
        """Get required input from user"""
        while True:
            value = input(f"{prompt}: ").strip()
            if value:
                return value
            print("This field is required. Please enter a value.")
    
    def _get_input_with_default(self, prompt: str, default: str) -> str:
        """Get input with default value"""
        value = input(f"{prompt} [{default}]: ").strip()
        return value if value else default
    
    def _get_yes_no(self, prompt: str, default: bool = False) -> bool:
        """Get yes/no input from user with default handling"""
        response = input(f"{prompt} ").strip().lower()
        if not response:
            return default
        return response in ['y', 'yes', 'true', '1']
    
    def display_configuration_summary(self, config: GeneratorConfig):
        """Display configuration summary to user"""
        print(f"\n=== Configuration Summary ===")
        print(f"Project: {config.project_name}")
        print(f"Site: {config.site_name}")
        print(f"Base URL: {config.base_url}")
        
        enabled_tests = config.get_enabled_test_types()
        if enabled_tests:
            print(f"Test Types: {', '.join(enabled_tests)}")
        else:
            print("Test Types: Basic tests only")
        
        print(f"HTML Reports: {'Yes' if config.html_reports else 'No'}")
        print(f"GitHub Actions: {'Yes' if config.github_actions else 'No'}")
        print()
    
    def confirm_generation(self) -> bool:
        """Ask user to confirm generation"""
        return self._get_yes_no("Generate framework with this configuration? (Y/n)", default=True)