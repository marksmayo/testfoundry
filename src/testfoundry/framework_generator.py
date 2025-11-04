"""
Main framework generator orchestrator.
Coordinates all the individual generators to create a complete test framework.
"""

import sys
from pathlib import Path
from .config.models import GeneratorConfig
from .cli.interface import CLIInterface
from .generators.base import BaseGenerator
from .generators.core_generator import CoreGenerator
from .generators.test_generator import TestGenerator
from .generators.utils_generator import UtilsGenerator
from .generators.docs_generator import DocsGenerator
from .generators.cicd_generator import CICDGenerator
from .utils.logging import logger, GeneratorError, FileSystemError


class FrameworkGenerator:
    """Main orchestrator for generating test automation frameworks"""
    
    def __init__(self):
        self.cli = CLIInterface()
        self.config = None
        
    def run_interactive(self) -> None:
        """Run the generator in interactive mode"""
        try:
            # Collect configuration from user
            self.config = self.cli.collect_configuration()
            
            # Display summary and confirm
            self.cli.display_configuration_summary(self.config)
            if not self.cli.confirm_generation():
                print("Generation cancelled.")
                return
            
            # Generate the framework
            self.generate_framework()
            
        except KeyboardInterrupt:
            print("\n\nGeneration cancelled by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\nError generating framework: {e}")
            sys.exit(1)
    
    def generate_framework(self, config: GeneratorConfig = None) -> None:
        """Generate the complete test framework"""
        if config:
            self.config = config
        
        if not self.config:
            raise GeneratorError("Configuration is required")
        
        project_path = Path(self.config.project_name)
        
        # Check if directory exists
        if project_path.exists():
            logger.warning(f"Directory '{self.config.project_name}' already exists - files will be overwritten")
        
        try:
            logger.section(f"Generating Test Framework: {self.config.site_name}")
            logger.set_total_steps(6)
            
            # Create directory structure
            logger.step("Creating directory structure")
            base_generator = BaseGenerator(self.config)
            base_generator.create_directory_structure(project_path)
            
            # Generate core framework files
            logger.step("Generating core framework files")
            core_generator = CoreGenerator(self.config)
            core_generator.generate_all_core_files(project_path)
            
            # Generate test files
            logger.step("Generating test files")
            test_generator = TestGenerator(self.config)
            test_generator.generate_all_tests(project_path)
            
            # Generate utilities
            logger.step("Generating utility files")
            utils_generator = UtilsGenerator(self.config)
            utils_generator.generate_all_utils(project_path)
            
            # Generate documentation
            logger.step("Generating documentation")
            docs_generator = DocsGenerator(self.config)
            docs_generator.generate_all_docs(project_path)
            
            # Generate CI/CD files if requested
            if self.config.github_actions:
                logger.step("Generating CI/CD configuration")
                cicd_generator = CICDGenerator(self.config)
                cicd_generator.generate_all_cicd(project_path)
            
            # Display success message
            self._display_success_message()
            
        except Exception as e:
            logger.error(f"Framework generation failed: {e}")
            raise GeneratorError(
                f"Failed to generate framework: {e}",
                suggestions=[
                    "Check that you have write permissions to the current directory",
                    "Ensure the project name is valid",
                    "Verify the base URL is accessible"
                ]
            )
    
    
    def _display_success_message(self) -> None:
        """Display success message to user"""
        logger.success(f"Framework generated successfully in '{self.config.project_name}/'")
        logger.info("Project structure created with Page Object Model")
        
        enabled_tests = self.config.get_enabled_test_types()
        if enabled_tests:
            logger.info(f"Test types: {', '.join(enabled_tests)}")
        else:
            logger.info("Test types: Basic tests only")
        
        logger.info(f"Reports: {'HTML' if self.config.html_reports else 'Terminal only'}")
        
        if self.config.github_actions:
            logger.info("GitHub Actions workflow created")
            
        logger.section("Next Steps")
        logger.info(f"1. cd {self.config.project_name}")
        logger.info("2. python -m venv venv")
        logger.info("3. source venv/bin/activate  # On Windows: venv\\\\Scripts\\\\activate")
        logger.info("4. pip install -r requirements.txt")
        logger.info("5. playwright install")
        logger.info("6. pytest --help  # See available test options")