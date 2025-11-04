# TestFoundry Architecture Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERACTION                               │
│                                                                           │
│  ┌──────────────┐                                                        │
│  │  Web Browser │                                                        │
│  │  (JavaScript)│                                                        │
│  └──────┬───────┘                                                        │
│         │ 1. Submit Config                                               │
│         │    (project_name, site_name, base_url, test_types)            │
│         ▼                                                                 │
└─────────────────────────────────────────────────────────────────────────┘
         │
         │ HTTP POST /api/generate
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND                                  │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │  REST API Endpoint                                            │       │
│  │  - Validates config (Pydantic)                               │       │
│  │  - Creates job_id (UUID)                                     │       │
│  │  - Starts background task                                     │       │
│  └───────────────────────┬──────────────────────────────────────┘       │
│                          │                                                │
│                          │ 2. Background Task                            │
│                          ▼                                                │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │  Generator Orchestrator                                       │       │
│  │  (FrameworkGenerator)                                         │       │
│  └───────────────────────┬──────────────────────────────────────┘       │
│                          │                                                │
│                          │ Sequential Generation (6 Steps)               │
│                          ▼                                                │
└─────────────────────────────────────────────────────────────────────────┘
                          │
                          │ Step-by-Step Execution
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    MODULAR GENERATOR ENGINE                              │
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │   Base       │  │    Core      │  │    Test      │                  │
│  │  Generator   │→ │  Generator   │→ │  Generator   │                  │
│  │              │  │              │  │              │                  │
│  │ - Directories│  │ - pytest.ini  │  │ - Basic tests│                  │
│  │ - Structure  │  │ - conftest.py│  │ - Accessibility│                 │
│  │              │  │ - Page objects│  │ - Performance│                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│         │                  │                  │                          │
│         └──────────────────┴──────────────────┘                          │
│                          │                                                 │
│                          ▼                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │   Utils      │  │     Docs      │  │    CI/CD     │                  │
│  │  Generator   │→ │  Generator    │→ │  Generator   │                  │
│  │              │  │               │  │              │                  │
│  │ - TestUtils  │  │ - README.md   │  │ - GitHub     │                  │
│  │ - Reports    │  │ - Docs        │  │   Actions    │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │  Template Engine (Jinja2)                                      │       │
│  │  - Populates templates with user config                       │       │
│  │  - Generates Python code files                                │       │
│  │  - Creates project structure                                  │       │
│  └──────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
                          │
                          │ Files Written to Disk
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    REAL-TIME PROGRESS TRACKING                           │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │  WebSocket Connection                                         │       │
│  │  - Broadcasts progress updates                                │       │
│  │  - Step status (RUNNING/COMPLETED)                           │       │
│  │  - Progress percentage                                        │       │
│  │  - File count updates                                         │       │
│  └───────────────────────┬──────────────────────────────────────┘       │
│                          │                                                │
│                          │ Live Updates                                   │
│                          ▼                                                │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │  Web UI Updates                                               │       │
│  │  - Progress bar (0-100%)                                     │       │
│  │  - Step-by-step status                                       │       │
│  │  - Real-time file count                                      │       │
│  └──────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
                          │
                          │ Generation Complete
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         OUTPUT                                           │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │  Complete Test Framework                                       │       │
│  │                                                                │       │
│  │  📁 project_name/                                             │       │
│  │     ├── 📁 tests/                                             │       │
│  │     │   ├── test_basic.py                                     │       │
│  │     │   ├── 📁 accessibility/                                 │       │
│  │     │   ├── 📁 lighthouse/                                    │       │
│  │     │   ├── 📁 broken_links/                                 │       │
│  │     │   └── 📁 seo/                                           │       │
│  │     ├── 📁 pages/                                             │       │
│  │     │   ├── base_page.py                                      │       │
│  │     │   └── home_page.py                                      │       │
│  │     ├── 📁 utils/                                             │       │
│  │     │   └── test_utils.py                                     │       │
│  │     ├── 📁 .github/workflows/                                │       │
│  │     │   └── test.yml                                          │       │
│  │     ├── conftest.py                                           │       │
│  │     ├── pytest.ini                                            │       │
│  │     ├── requirements.txt                                      │       │
│  │     └── README.md                                              │       │
│  │                                                                │       │
│  │  ✅ Ready to use:                                             │       │
│  │     - pip install -r requirements.txt                         │       │
│  │     - playwright install                                      │       │
│  │     - pytest                                                  │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │  Download Options                                              │       │
│  │  - ZIP file download (REST API)                               │       │
│  │  - Full project path displayed                                │       │
│  │  - File explorer preview                                      │       │
│  └──────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. **Web UI Layer**
- User fills configuration form
- JavaScript sends POST request to FastAPI
- WebSocket connection for real-time updates
- Progress bar and step-by-step status display

### 2. **API Layer (FastAPI)**
- REST endpoint validates configuration
- Creates job tracking with UUID
- Starts async background task
- WebSocket server for progress broadcasting

### 3. **Generator Engine**
- **Modular Architecture**: 6 specialized generators
- **Template-Based**: Jinja2 templates populated with config
- **Sequential Execution**: Each generator runs in order
- **File System**: Creates directory structure and files

### 4. **Real-Time Communication**
- WebSocket connection stays open during generation
- Progress updates broadcast after each step
- UI updates automatically without polling

### 5. **Output**
- Complete Python project structure
- All dependencies configured
- Ready-to-run test framework
- Downloadable as ZIP file

## Data Flow

```
User Config → Validation → Job Creation → Background Task
                                              ↓
                                    Generator Orchestrator
                                              ↓
                                    [6 Generators Sequential]
                                              ↓
                                    Template → Code Files
                                              ↓
                                    WebSocket → UI Updates
                                              ↓
                                    Complete Framework
```

## Technology Stack Flow

```
Frontend (JavaScript/WebSocket)
    ↕ HTTP/WS
Backend (FastAPI/Pydantic)
    ↕ Python
Generator Engine (Modular Classes)
    ↕ Templates (Jinja2)
File System (Path/Directory)
    ↕ Output
Generated Framework (pytest/Playwright)
```
