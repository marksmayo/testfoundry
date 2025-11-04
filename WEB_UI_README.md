# TestFoundry - Web UI

A modern web interface for TestFoundry that provides an intuitive way to create comprehensive test automation frameworks for websites.

## Features

- **🎨 Modern Web Interface**: Clean, responsive design with real-time progress tracking
- **🚀 One-Click Generation**: Generate complete test frameworks with a few clicks
- **📊 Real-Time Progress**: WebSocket-based live updates during framework generation
- **📁 File Preview**: Browse and preview generated files before download
- **📦 ZIP Download**: Download complete projects as ZIP files
- **🎯 Configuration Presets**: Quick-start templates for common testing scenarios
- **✅ Live Validation**: Real-time configuration validation with helpful feedback

## Quick Start

### 1. Install Dependencies

```bash
# Install web UI dependencies
pip install fastapi uvicorn[standard] python-multipart jinja2 websockets aiofiles

# Or use the requirements file
pip install -r web_ui_requirements.txt
```

### 2. Start the Web Server

```bash
# Run the startup script
python run_web_ui.py
```

The web interface will be available at:
- **Main UI**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### 3. Generate a Test Framework

1. Open http://localhost:8000 in your browser
2. Fill in the configuration form:
   - **Project Name**: Folder name for your test framework
   - **Site Name**: Display name for documentation
   - **Base URL**: Website URL to test
   - **Test Types**: Select which types of tests to include
3. Click "Generate Framework"
4. Watch real-time progress updates
5. Download the complete project as a ZIP file

## Configuration Options

### Test Types

- **Accessibility**: WCAG compliance and a11y audits
- **Performance**: Lighthouse audits and Core Web Vitals
- **Broken Links**: Link validation and health checks
- **SEO**: Meta tags, schema, and SEO audits

### Additional Options

- **HTML Reports**: Generate beautiful test reports with screenshots
- **GitHub Actions**: Include CI/CD workflow files

## Configuration Presets

The web UI includes several pre-configured templates:

1. **Basic Website Testing**: Simple smoke tests for basic websites
2. **Full E-commerce Site**: Comprehensive testing for e-commerce platforms
3. **Accessibility Focus**: Specialized accessibility compliance testing
4. **Performance Monitoring**: Performance and Core Web Vitals tracking

## API Endpoints

### Core Endpoints

- `GET /`: Main web interface
- `GET /api/system-info`: System information and available presets
- `POST /api/validate`: Validate configuration without generating
- `POST /api/generate`: Start framework generation
- `GET /api/jobs/{job_id}`: Get generation job status
- `GET /api/jobs/{job_id}/files`: List generated project files
- `GET /api/jobs/{job_id}/download`: Download project as ZIP
- `WS /ws/{job_id}`: WebSocket for real-time progress updates

### Example API Usage

```bash
# Validate configuration
curl -X POST http://localhost:8000/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my_test_framework",
    "site_name": "My Website",
    "base_url": "https://example.com",
    "test_types": ["accessibility", "lighthouse"],
    "html_reports": true,
    "github_actions": false
  }'

# Start generation
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my_test_framework",
    "site_name": "My Website", 
    "base_url": "https://example.com",
    "test_types": ["accessibility"],
    "html_reports": true,
    "github_actions": true
  }'

# Check job status
curl http://localhost:8000/api/jobs/{job_id}

# Download project
curl -O http://localhost:8000/api/jobs/{job_id}/download
```

## Architecture

### Backend (FastAPI)

- **FastAPI Server**: RESTful API with automatic documentation
- **WebSocket Support**: Real-time progress updates
- **Background Tasks**: Asynchronous framework generation
- **File Management**: Project creation and ZIP packaging
- **Validation**: Comprehensive input validation with helpful messages

### Frontend (HTML/CSS/JavaScript)

- **Responsive Design**: Works on desktop and mobile devices
- **Real-Time Updates**: WebSocket connection for live progress
- **Form Validation**: Client-side validation with visual feedback
- **File Explorer**: Browse generated project structure
- **Download Management**: Direct ZIP file downloads

### Integration

- **Generator Classes**: Uses existing modular generator system
- **Configuration Models**: Pydantic models for type safety
- **Error Handling**: Comprehensive error handling and user feedback
- **Progress Tracking**: Step-by-step generation progress

## Customization

### Adding New Presets

Edit `web_ui/api/server.py` and add to the `presets` list in `get_system_info()`:

```python
ConfigPreset(
    name="Custom Preset",
    description="Description of your preset",
    config=GeneratorRequest(
        project_name="custom_tests",
        site_name="Custom Site",
        base_url="https://custom.example.com",
        test_types=[TestType.ACCESSIBILITY],
        html_reports=True,
        github_actions=True
    )
)
```

### Styling

Modify `web_ui/static/css/style.css` to customize the appearance.

### Functionality

Extend `web_ui/static/js/app.js` to add new features or modify behavior.

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed and the `src/` directory is in the Python path
2. **Unicode Errors**: The web UI handles Unicode properly, but console output may need encoding fixes on Windows
3. **Port Conflicts**: Change the port in `run_web_ui.py` if 8000 is already in use
4. **File Permissions**: Ensure the application has write permissions for project generation

### Debug Mode

Run with debug logging:

```bash
# Enable debug logging
UVICORN_LOG_LEVEL=debug python run_web_ui.py
```

### Development Mode

For development, the server runs with auto-reload enabled. Changes to Python files will automatically restart the server.

## Security Notes

- The web UI is intended for local development use
- For production deployment, consider adding authentication and HTTPS
- File downloads are temporary and cleaned up automatically
- Input validation prevents common security issues

## Browser Support

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+
- Mobile browsers with modern JavaScript support