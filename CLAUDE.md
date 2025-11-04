# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Test Automation Framework Generator** for creating comprehensive website testing frameworks. The generator creates Python-based test frameworks using pytest and Playwright with support for:

- Basic smoke tests
- Accessibility testing (WCAG compliance)
- Performance testing (Lighthouse/Core Web Vitals)  
- Broken link validation
- SEO testing

## Key Commands

### Running the Generator
```bash
# Interactive mode with user prompts
python main.py

# Demo with sample configurations
python demo.py

# Test the refactored generator
python test_refactored_generator.py

# Legacy test (for old monolithic version)
python test_generator.py
```

### Development and Testing
```bash
# Run Python linting (if available)
python -m pylint src/framework_generator/

# Run type checking (if mypy is installed)
python -m mypy src/framework_generator/

# Run the test script to verify generator works
python test_refactored_generator.py
```

### Generated Framework Usage
Once a framework is generated, typical commands for the generated project:
```bash
cd <generated_project_name>
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt  
playwright install
pytest  # Run all tests
pytest -m smoke  # Run smoke tests only
```

## Architecture and Code Structure

### Main Components

**Refactored Modular Structure:**

1. **`main.py`** - New main entry point for interactive CLI
2. **`src/framework_generator/`** - Core generator package
   - **`framework_generator.py`** - Main orchestrator class
   - **`config/models.py`** - Configuration data classes with validation
   - **`cli/interface.py`** - CLI interaction and user input
   - **`generators/`** - Specialized generators for different components
   - **`templates/`** - Template content for generated files

3. **`test_refactored_generator.py`** - Test script for new modular structure
4. **`demo.py`** - Demo script showing basic and full framework generation

**Legacy Files:**
- **`generator.py`** - Original monolithic implementation (kept for reference)
- **`test_generator.py`** - Test script for legacy generator

### Generated Framework Structure

The generator creates projects with this structure:
```
<project_name>/
├── tests/                    # Test files by type
│   ├── test_basic.py        # Always generated
│   ├── accessibility/       # Optional
│   ├── lighthouse/          # Optional  
│   ├── broken_links/        # Optional
│   └── seo/                 # Optional
├── pages/                   # Page Object Model
│   ├── base_page.py        # Base page class
│   └── home_page.py        # Sample page object
├── utils/                   # Test utilities
├── config/                  # Configuration files
├── .github/workflows/       # Optional CI/CD
├── conftest.py             # Pytest configuration
├── pytest.ini             # Pytest settings
├── requirements.txt        # Dependencies
└── README.md              # Comprehensive documentation
```

### Design Patterns Used

- **Page Object Model**: Separates page interactions from test logic
- **Template Generation**: Uses f-strings and multiline templates for code generation
- **Modular Test Types**: Each test type (accessibility, performance, etc.) in separate modules
- **Configuration-Driven**: User choices determine which components are generated

## Refactoring Status

### ✅ Completed Improvements

1. **✅ Modular Architecture**: 
   - Separated concerns into focused modules
   - `config/` for configuration management and validation
   - `cli/` for user interaction
   - `generators/` for specialized generation logic
   - `templates/` for template content

2. **✅ Configuration Validation**: 
   - `GeneratorConfig` dataclass with validation
   - Type hints and proper error handling
   - Serialization/deserialization support

3. **✅ Improved Testing**: 
   - `test_refactored_generator.py` tests both functionality and validation
   - Demo script for showcasing capabilities
   - Better test coverage of the generation process

4. **✅ Fixed Unicode Issues**: 
   - Proper UTF-8 encoding for all file operations
   - Cross-platform compatibility

### 🚧 Remaining Improvements

1. **Unit Tests**: Individual unit tests for each generator class
2. **Enhanced Features**:
   - Support for different test frameworks (not just pytest)
   - Multiple browser configuration options
   - Custom test template support
   - Configuration file input (JSON/YAML)
3. **Template Extraction**: Some templates still embedded in generator code
4. **Documentation Generator**: Extract README/docs generation to separate module

## Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints where possible
- Add docstrings to all public methods
- Keep functions focused and small

### Template Generation
- Use consistent indentation in generated code
- Include comprehensive docstrings in generated files
- Ensure generated code follows best practices
- Test generated code actually works

### Error Handling
- Validate user inputs before processing
- Provide clear error messages
- Handle file system errors gracefully
- Test edge cases (empty inputs, invalid URLs, etc.)

## Testing Strategy

### Current Testing
- `test_generator.py` provides basic end-to-end testing
- Verifies all expected files are generated
- Checks basic content validation

### Needed Testing
- Unit tests for individual generator methods
- Template validation tests
- Configuration validation tests
- Integration tests with actual generated frameworks
- Cross-platform testing (Windows/Mac/Linux)

## Dependencies

### Core Dependencies
- **Python 3.8+**: Core language
- **pathlib**: File system operations
- **json**: Configuration handling (future)

### Generated Framework Dependencies
- **pytest**: Test framework
- **playwright**: Browser automation
- **pytest-playwright**: Playwright pytest integration
- **axe-playwright**: Accessibility testing (optional)
- **requests**: HTTP requests for link validation
- **beautifulsoup4**: HTML parsing

## Future Enhancements

1. **Web UI**: Add optional web interface for generator
2. **Plugin System**: Allow custom test type plugins
3. **Template Customization**: User-provided templates
4. **CI/CD Templates**: Support for other CI systems (GitLab, Jenkins, etc.)
5. **Advanced Configuration**: YAML/JSON config file support
6. **Framework Variants**: Support for other languages/frameworks

## Contributing

When working on this codebase:

1. **Refactoring Priority**: The monolithic `generator.py` needs to be broken into smaller, focused modules
2. **Test Coverage**: Add unit tests before making significant changes
3. **Generated Code Quality**: Ensure generated frameworks follow best practices
4. **Documentation**: Update this file when making architectural changes
5. **Backwards Compatibility**: Maintain compatibility with existing generated frameworks