#!/usr/bin/env python3
"""
Main entry point for TestFoundry - Test Automation Framework Generator.
"""

import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from testfoundry.framework_generator import FrameworkGenerator


def main():
    """Main entry point"""
    generator = FrameworkGenerator()
    generator.run_interactive()


if __name__ == "__main__":
    main()