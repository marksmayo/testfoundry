"""
FastAPI web server for the Test Framework Generator UI.
Provides REST API endpoints for the web interface.
"""

import sys
import os
import asyncio
import uuid
import platform
import shutil
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, FileResponse
from starlette.middleware.cors import CORSMiddleware

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from testfoundry.framework_generator import FrameworkGenerator
from testfoundry.config.models import GeneratorConfig
from testfoundry.config.validation import ConfigValidator
from .models import (
    GeneratorRequest, ValidationResponse, ValidationError,
    GenerationResponse, GenerationProgress, GenerationStatus,
    GenerationStep, ProjectStructure, FileInfo, SystemInfo,
    ConfigPreset, TestType
)

# Global state for tracking generation jobs
generation_jobs: Dict[str, GenerationProgress] = {}
websocket_connections: Dict[str, WebSocket] = {}

app = FastAPI(
    title="TestFoundry",
    description="Web UI for generating test automation frameworks",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
static_path = Path(__file__).parent.parent / "static"
templates_path = Path(__file__).parent.parent / "templates"

app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
templates = Jinja2Templates(directory=str(templates_path))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main web interface"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/system-info", response_model=SystemInfo)
async def get_system_info():
    """Get system information and available presets"""
    presets = [
        ConfigPreset(
            name="Basic Website Testing",
            description="Basic smoke tests for simple websites",
            config=GeneratorRequest(
                project_name="basic_website_tests",
                site_name="My Website",
                base_url="https://example.com",
                test_types=[],
                html_reports=True,
                github_actions=False
            )
        ),
        ConfigPreset(
            name="Full E-commerce Site",
            description="Comprehensive testing for e-commerce sites",
            config=GeneratorRequest(
                project_name="ecommerce_tests",
                site_name="E-commerce Site",
                base_url="https://shop.example.com",
                test_types=[TestType.ACCESSIBILITY, TestType.LIGHTHOUSE, TestType.BROKEN_LINKS, TestType.SEO],
                html_reports=True,
                github_actions=True
            )
        ),
        ConfigPreset(
            name="Accessibility Focus",
            description="Focused on accessibility compliance testing",
            config=GeneratorRequest(
                project_name="accessibility_tests",
                site_name="Accessible Site",
                base_url="https://accessible.example.com",
                test_types=[TestType.ACCESSIBILITY],
                html_reports=True,
                github_actions=True
            )
        ),
        ConfigPreset(
            name="Performance Monitoring",
            description="Performance and Core Web Vitals monitoring",
            config=GeneratorRequest(
                project_name="performance_tests",
                site_name="Performance Site",
                base_url="https://fast.example.com",
                test_types=[TestType.LIGHTHOUSE],
                html_reports=True,
                github_actions=True
            )
        )
    ]
    
    return SystemInfo(
        python_version=platform.python_version(),
        platform=platform.system(),
        available_presets=presets,
        supported_test_types=list(TestType)
    )


@app.post("/api/validate", response_model=ValidationResponse)
async def validate_configuration(request: GeneratorRequest):
    """Validate configuration without generating"""
    try:
        # Convert to internal config format
        config = GeneratorConfig(
            project_name=request.project_name,
            site_name=request.site_name,
            base_url=str(request.base_url),
            include_accessibility=TestType.ACCESSIBILITY in request.test_types,
            include_lighthouse=TestType.LIGHTHOUSE in request.test_types,
            include_broken_links=TestType.BROKEN_LINKS in request.test_types,
            include_seo=TestType.SEO in request.test_types,
            html_reports=request.html_reports,
            github_actions=request.github_actions
        )
        
        return ValidationResponse(valid=True, errors=[], suggestions=[])
        
    except ValueError as e:
        # Parse validation errors
        error_message = str(e)
        errors = []
        
        if "Project name" in error_message:
            errors.append(ValidationError(field="project_name", message="Invalid project name format"))
        if "Site name" in error_message:
            errors.append(ValidationError(field="site_name", message="Invalid site name"))
        if "Base URL" in error_message:
            errors.append(ValidationError(field="base_url", message="Invalid URL format"))
        
        suggestions = [
            "Project names should be 3-50 characters, alphanumeric with hyphens/underscores",
            "URLs must start with http:// or https://",
            "Avoid reserved names like 'test', 'src', 'config'"
        ]
        
        return ValidationResponse(valid=False, errors=errors, suggestions=suggestions)


@app.post("/api/generate", response_model=GenerationResponse)
async def generate_framework(request: GeneratorRequest, background_tasks: BackgroundTasks):
    """Start framework generation"""
    try:
        # Validate configuration first
        config = GeneratorConfig(
            project_name=request.project_name,
            site_name=request.site_name,
            base_url=str(request.base_url),
            include_accessibility=TestType.ACCESSIBILITY in request.test_types,
            include_lighthouse=TestType.LIGHTHOUSE in request.test_types,
            include_broken_links=TestType.BROKEN_LINKS in request.test_types,
            include_seo=TestType.SEO in request.test_types,
            html_reports=request.html_reports,
            github_actions=request.github_actions
        )
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job tracking
        generation_jobs[job_id] = GenerationProgress(
            job_id=job_id,
            status=GenerationStatus.PENDING,
            total_steps=6,
            steps=[
                GenerationStep(name="Creating directory structure", status=GenerationStatus.PENDING),
                GenerationStep(name="Generating core framework files", status=GenerationStatus.PENDING),
                GenerationStep(name="Generating test files", status=GenerationStatus.PENDING),
                GenerationStep(name="Generating utility files", status=GenerationStatus.PENDING),
                GenerationStep(name="Generating documentation", status=GenerationStatus.PENDING),
                GenerationStep(name="Generating CI/CD configuration", status=GenerationStatus.PENDING),
            ]
        )
        
        # Start generation in background
        background_tasks.add_task(run_generation, job_id, config)
        
        return GenerationResponse(
            job_id=job_id,
            status=GenerationStatus.PENDING,
            message="Framework generation started"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def run_generation(job_id: str, config: GeneratorConfig):
    """Run framework generation in background"""
    try:
        job = generation_jobs[job_id]
        job.status = GenerationStatus.RUNNING
        
        # Notify connected websockets
        await notify_websockets(job_id, job)
        
        # Create generator
        generator = FrameworkGenerator()
        
        # Simulate step-by-step generation with progress updates
        project_path = Path(config.project_name)
        
        # Step 1: Create directory structure
        await update_step(job_id, 0, GenerationStatus.RUNNING, "Creating directories...")
        from testfoundry.generators.base import BaseGenerator
        base_generator = BaseGenerator(config)
        base_generator.create_directory_structure(project_path)
        await update_step(job_id, 0, GenerationStatus.COMPLETED, "Directories created")
        
        # Step 2: Core files
        await update_step(job_id, 1, GenerationStatus.RUNNING, "Generating pytest config and page objects...")
        from testfoundry.generators.core_generator import CoreGenerator
        core_generator = CoreGenerator(config)
        core_generator.generate_all_core_files(project_path)
        await update_step(job_id, 1, GenerationStatus.COMPLETED, "Core files generated")
        
        # Step 3: Test files
        await update_step(job_id, 2, GenerationStatus.RUNNING, "Generating test files...")
        from testfoundry.generators.test_generator import TestGenerator
        test_generator = TestGenerator(config)
        test_generator.generate_all_tests(project_path)
        await update_step(job_id, 2, GenerationStatus.COMPLETED, "Test files generated")
        
        # Step 4: Utilities
        await update_step(job_id, 3, GenerationStatus.RUNNING, "Generating utilities...")
        from testfoundry.generators.utils_generator import UtilsGenerator
        utils_generator = UtilsGenerator(config)
        utils_generator.generate_all_utils(project_path)
        await update_step(job_id, 3, GenerationStatus.COMPLETED, "Utilities generated")
        
        # Step 5: Documentation
        await update_step(job_id, 4, GenerationStatus.RUNNING, "Generating README and docs...")
        from testfoundry.generators.docs_generator import DocsGenerator
        docs_generator = DocsGenerator(config)
        docs_generator.generate_all_docs(project_path)
        await update_step(job_id, 4, GenerationStatus.COMPLETED, "Documentation generated")
        
        # Step 6: CI/CD (if enabled)
        if config.github_actions:
            await update_step(job_id, 5, GenerationStatus.RUNNING, "Generating GitHub Actions...")
            from testfoundry.generators.cicd_generator import CICDGenerator
            cicd_generator = CICDGenerator(config)
            cicd_generator.generate_all_cicd(project_path)
            await update_step(job_id, 5, GenerationStatus.COMPLETED, "CI/CD generated")
        else:
            await update_step(job_id, 5, GenerationStatus.COMPLETED, "CI/CD skipped")
        
        # Collect created files
        created_files = []
        if project_path.exists():
            for file_path in project_path.rglob("*"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(project_path)
                    created_files.append(str(rel_path))
        
        # Mark job as completed
        job.status = GenerationStatus.COMPLETED
        job.progress_percent = 100
        job.current_step = job.total_steps
        job.created_files = created_files
        job.message = f"Framework generated successfully with {len(created_files)} files"
        
        await notify_websockets(job_id, job)
        
    except Exception as e:
        # Mark job as failed
        job = generation_jobs[job_id]
        job.status = GenerationStatus.FAILED
        job.error = str(e)
        job.message = f"Generation failed: {e}"
        
        await notify_websockets(job_id, job)


async def update_step(job_id: str, step_index: int, status: GenerationStatus, message: str):
    """Update a specific step status"""
    job = generation_jobs[job_id]
    job.steps[step_index].status = status
    job.steps[step_index].message = message
    job.steps[step_index].timestamp = datetime.now().isoformat()
    
    # Update overall progress
    completed_steps = sum(1 for step in job.steps if step.status == GenerationStatus.COMPLETED)
    job.current_step = completed_steps
    job.progress_percent = int((completed_steps / job.total_steps) * 100)
    
    await notify_websockets(job_id, job)


async def notify_websockets(job_id: str, job: GenerationProgress):
    """Notify all connected websockets about job progress"""
    disconnected = []
    for conn_id, websocket in websocket_connections.items():
        try:
            await websocket.send_json(job.dict())
        except:
            disconnected.append(conn_id)
    
    # Clean up disconnected websockets
    for conn_id in disconnected:
        websocket_connections.pop(conn_id, None)


@app.get("/api/jobs/{job_id}", response_model=GenerationProgress)
async def get_job_status(job_id: str):
    """Get status of a generation job"""
    if job_id not in generation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return generation_jobs[job_id]


@app.get("/api/jobs/{job_id}/files", response_model=ProjectStructure)
async def get_project_files(job_id: str):
    """Get list of generated files for a job"""
    if job_id not in generation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = generation_jobs[job_id]
    if job.status != GenerationStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job not completed")
    
    # Find the project directory (assumes job creates directory with project name)
    project_path = None
    for file_path in job.created_files:
        if "/" not in file_path and "\\\\" not in file_path:  # Top-level files
            project_name = Path(file_path).stem
            potential_path = Path(project_name)
            if potential_path.exists() and potential_path.is_dir():
                project_path = potential_path
                break
    
    if not project_path:
        # Try to infer from any file path
        if job.created_files:
            first_file = job.created_files[0]
            project_path = Path(first_file).parent
    
    files = []
    total_size = 0
    
    if project_path and project_path.exists():
        for file_path in project_path.rglob("*"):
            rel_path = file_path.relative_to(project_path)
            
            if file_path.is_file():
                size = file_path.stat().st_size
                total_size += size
                
                # Get content preview for small text files
                content_preview = None
                if size < 1000 and file_path.suffix in ['.py', '.txt', '.md', '.yml', '.yaml', '.json']:
                    try:
                        content_preview = file_path.read_text(encoding='utf-8')[:500]
                    except:
                        pass
                
                files.append(FileInfo(
                    path=str(rel_path),
                    name=file_path.name,
                    size=size,
                    type="file",
                    content_preview=content_preview
                ))
            else:
                files.append(FileInfo(
                    path=str(rel_path),
                    name=file_path.name,
                    size=0,
                    type="directory"
                ))
    
    return ProjectStructure(
        project_name=str(project_path.name) if project_path else "unknown",
        files=files,
        total_files=len([f for f in files if f.type == "file"]),
        total_size=total_size
    )


@app.get("/api/jobs/{job_id}/download")
async def download_project(job_id: str):
    """Download generated project as ZIP file"""
    if job_id not in generation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = generation_jobs[job_id]
    if job.status != GenerationStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job not completed")
    
    # Create ZIP file
    zip_path = Path(f"temp_{job_id}.zip")
    
    try:
        project_path = None
        if job.created_files:
            # Infer project directory name
            first_file = job.created_files[0]
            project_name = first_file.split("/")[0] if "/" in first_file else first_file.split("\\\\")[0] if "\\\\" in first_file else first_file
            project_path = Path(project_name)
        
        if not project_path or not project_path.exists():
            raise HTTPException(status_code=404, detail="Project directory not found")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in project_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(project_path.parent)
                    zipf.write(file_path, arcname)
        
        return FileResponse(
            zip_path,
            media_type='application/zip',
            filename=f"{project_path.name}.zip"
        )
    
    finally:
        # Clean up temporary zip file
        if zip_path.exists():
            background_tasks = BackgroundTasks()
            background_tasks.add_task(lambda: zip_path.unlink(missing_ok=True))


@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time progress updates"""
    await websocket.accept()
    
    # Generate connection ID
    conn_id = str(uuid.uuid4())
    websocket_connections[conn_id] = websocket
    
    try:
        # Send current job status if it exists
        if job_id in generation_jobs:
            await websocket.send_json(generation_jobs[job_id].dict())
        
        # Keep connection alive
        while True:
            # Wait for any message (ping/pong)
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        # Clean up connection
        websocket_connections.pop(conn_id, None)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)