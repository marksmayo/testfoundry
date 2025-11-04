// TestFoundry Web UI JavaScript

class TestFoundryUI {
    constructor() {
        this.presets = [];
        this.currentJobId = null;
        this.websocket = null;

        this.initializeApp();
    }

    async initializeApp() {
        await this.loadSystemInfo();
        this.bindEvents();
        this.populatePresets();
    }

    async loadSystemInfo() {
        try {
            const response = await fetch('/api/system-info');
            const data = await response.json();
            this.presets = data.available_presets;

            console.log('System info loaded:', data);
        } catch (error) {
            console.error('Failed to load system info:', error);
            this.showError('Failed to load system information');
        }
    }

    populatePresets() {
        const presetSelect = document.getElementById('presetSelect');

        this.presets.forEach(preset => {
            const option = document.createElement('option');
            option.value = preset.name;
            option.textContent = `${preset.name} - ${preset.description}`;
            presetSelect.appendChild(option);
        });
    }

    bindEvents() {
        // Form submission
        document.getElementById('generatorForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateFramework();
        });

        // Validation button
        document.getElementById('validateBtn').addEventListener('click', () => {
            this.validateConfiguration();
        });

        // Preset loading
        document.getElementById('presetSelect').addEventListener('change', (e) => {
            const loadBtn = document.getElementById('loadPresetBtn');
            loadBtn.disabled = !e.target.value;
        });

        document.getElementById('loadPresetBtn').addEventListener('click', () => {
            this.loadPreset();
        });

        // Download and new project buttons
        document.getElementById('downloadBtn').addEventListener('click', () => {
            this.downloadProject();
        });

        document.getElementById('newProjectBtn').addEventListener('click', () => {
            this.resetForm();
        });

        // Real-time validation
        const inputs = document.querySelectorAll('#generatorForm input[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
        });
    }

    loadPreset() {
        const presetSelect = document.getElementById('presetSelect');
        const selectedPresetName = presetSelect.value;

        if (!selectedPresetName) return;

        const preset = this.presets.find(p => p.name === selectedPresetName);
        if (!preset) return;

        const config = preset.config;

        // Populate form fields
        document.getElementById('projectName').value = config.project_name;
        document.getElementById('siteName').value = config.site_name;
        document.getElementById('baseUrl').value = config.base_url;
        document.getElementById('htmlReports').checked = config.html_reports;
        document.getElementById('githubActions').checked = config.github_actions;

        // Clear existing test type selections
        document.querySelectorAll('input[name="test_types"]').forEach(cb => {
            cb.checked = false;
        });

        // Set test types
        config.test_types.forEach(testType => {
            const checkbox = document.querySelector(`input[value="${testType}"]`);
            if (checkbox) checkbox.checked = true;
        });

        this.showSuccess('Preset loaded successfully!');
    }

    validateField(input) {
        const value = input.value.trim();
        const fieldName = input.name;

        // Remove existing validation styling
        input.classList.remove('field-error', 'field-success');

        if (!value && input.required) {
            input.classList.add('field-error');
            return false;
        }

        if (fieldName === 'project_name') {
            const pattern = /^[a-zA-Z0-9_\-]+$/;
            if (!pattern.test(value)) {
                input.classList.add('field-error');
                return false;
            }
        }

        if (fieldName === 'base_url') {
            try {
                new URL(value);
            } catch {
                input.classList.add('field-error');
                return false;
            }
        }

        input.classList.add('field-success');
        return true;
    }

    async validateConfiguration() {
        const config = this.getFormData();
        if (!config) return;

        this.showLoading();

        try {
            const response = await fetch('/api/validate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            const result = await response.json();
            this.displayValidationResults(result);

        } catch (error) {
            console.error('Validation error:', error);
            this.showError('Failed to validate configuration');
        } finally {
            this.hideLoading();
        }
    }

    displayValidationResults(result) {
        const validationCard = document.getElementById('validationCard');
        const resultsDiv = document.getElementById('validationResults');

        let html = '';

        if (result.valid) {
            html = `
                <div class="validation-success">
                    <i class="fas fa-check-circle"></i>
                    <strong>Configuration is valid!</strong>
                    <p>Your configuration passes all validation checks. You can proceed with framework generation.</p>
                </div>
            `;
        } else {
            html = `
                <div class="validation-errors">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>Configuration errors found:</strong>
                    <ul class="error-list">
                        ${result.errors.map(error => `<li><strong>${error.field}:</strong> ${error.message}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (result.suggestions && result.suggestions.length > 0) {
            html += `
                <div class="validation-suggestions">
                    <i class="fas fa-lightbulb"></i>
                    <strong>Suggestions:</strong>
                    <ul class="suggestion-list">
                        ${result.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        resultsDiv.innerHTML = html;
        validationCard.classList.remove('hidden');
        validationCard.scrollIntoView({ behavior: 'smooth' });
    }

    async generateFramework() {
        const config = this.getFormData();
        if (!config) return;

        this.showLoading();

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Generation failed');
            }

            const result = await response.json();
            this.currentJobId = result.job_id;

            this.hideLoading();
            this.showProgressTracking();
            this.connectWebSocket();

        } catch (error) {
            console.error('Generation error:', error);
            this.showError(`Failed to start generation: ${error.message}`);
            this.hideLoading();
        }
    }

    getFormData() {
        const form = document.getElementById('generatorForm');
        const formData = new FormData(form);

        // Validate required fields
        const projectName = formData.get('project_name')?.trim();
        const siteName = formData.get('site_name')?.trim();
        const baseUrl = formData.get('base_url')?.trim();

        if (!projectName || !siteName || !baseUrl) {
            this.showError('Please fill in all required fields');
            return null;
        }

        // Get selected test types
        const testTypes = [];
        document.querySelectorAll('input[name="test_types"]:checked').forEach(cb => {
            testTypes.push(cb.value);
        });

        return {
            project_name: projectName,
            site_name: siteName,
            base_url: baseUrl,
            test_types: testTypes,
            html_reports: document.getElementById('htmlReports').checked,
            github_actions: document.getElementById('githubActions').checked
        };
    }

    showProgressTracking() {
        document.getElementById('configCard').classList.add('hidden');
        document.getElementById('validationCard').classList.add('hidden');
        document.getElementById('progressCard').classList.remove('hidden');

        // Initialize progress display
        document.getElementById('progressFill').style.width = '0%';
        document.getElementById('progressPercent').textContent = '0%';
        document.getElementById('progressText').textContent = 'Starting generation...';
        document.getElementById('progressSteps').innerHTML = '';
    }

    connectWebSocket() {
        if (!this.currentJobId) return;

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.currentJobId}`;

        this.websocket = new WebSocket(wsUrl);

        this.websocket.onopen = () => {
            console.log('WebSocket connected');
        };

        this.websocket.onmessage = (event) => {
            const progress = JSON.parse(event.data);
            this.updateProgress(progress);
        };

        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
        };
    }

    updateProgress(progress) {
        // Update progress bar
        document.getElementById('progressFill').style.width = `${progress.progress_percent}%`;
        document.getElementById('progressPercent').textContent = `${progress.progress_percent}%`;
        document.getElementById('progressText').textContent = progress.message || 'In progress...';

        // Update steps
        this.updateProgressSteps(progress.steps);

        // Check if completed
        if (progress.status === 'completed') {
            this.onGenerationComplete(progress);
        } else if (progress.status === 'failed') {
            this.onGenerationFailed(progress);
        }
    }

    updateProgressSteps(steps) {
        const stepsContainer = document.getElementById('progressSteps');

        stepsContainer.innerHTML = steps.map(step => `
            <div class="progress-step ${step.status}">
                <div class="step-icon ${step.status}">
                    ${this.getStepIcon(step.status)}
                </div>
                <div class="step-content">
                    <div class="step-name">${step.name}</div>
                    ${step.message ? `<div class="step-message">${step.message}</div>` : ''}
                </div>
            </div>
        `).join('');
    }

    getStepIcon(status) {
        switch (status) {
            case 'completed':
                return '<i class="fas fa-check"></i>';
            case 'running':
                return '<i class="fas fa-spinner fa-spin"></i>';
            case 'failed':
                return '<i class="fas fa-times"></i>';
            default:
                return '<i class="fas fa-clock"></i>';
        }
    }

    async onGenerationComplete(progress) {
        this.closeWebSocket();

        // Hide progress, show results
        document.getElementById('progressCard').classList.add('hidden');
        document.getElementById('resultsCard').classList.remove('hidden');

        // Load project files
        await this.loadProjectFiles();

        // Show summary
        this.displayResultSummary(progress);

        this.showSuccess('Framework generated successfully! 🎉');
    }

    onGenerationFailed(progress) {
        this.closeWebSocket();
        this.showError(`Generation failed: ${progress.error || 'Unknown error'}`);
    }

    async loadProjectFiles() {
        if (!this.currentJobId) return;

        try {
            const response = await fetch(`/api/jobs/${this.currentJobId}/files`);
            const projectStructure = await response.json();

            this.displayProjectFiles(projectStructure);

        } catch (error) {
            console.error('Failed to load project files:', error);
        }
    }

    displayResultSummary(progress) {
        const summaryDiv = document.getElementById('resultSummary');

        const projectPath = progress.project_path || 'Not available';
        const pathDisplay = projectPath ?
            `<div class="project-path">
                <strong><i class="fas fa-folder-open"></i> Project Location:</strong><br>
                <code class="path-text">${projectPath}</code>
                <button class="btn btn-icon btn-copy-path" title="Copy path" aria-label="Copy path"
                    onclick="navigator.clipboard && navigator.clipboard.writeText('${projectPath.replace(/\\/g, "\\\\")}').then(() => window.testFoundryUI?.showSuccess('Path copied to clipboard')).catch(()=>window.testFoundryUI?.showError('Failed to copy path'))">
                    <i class="fas fa-clipboard"></i>
                </button>
            </div>` : '';

        summaryDiv.innerHTML = `
            <h4><i class="fas fa-check-circle text-success"></i> Generation Completed Successfully</h4>
            <p>${progress.message}</p>
            ${pathDisplay}
            <div class="result-stats">
                <div class="stat">
                    <div class="stat-number">${progress.created_files.length}</div>
                    <div class="stat-label">Files Created</div>
                </div>
                <div class="stat">
                    <div class="stat-number">${progress.total_steps}</div>
                    <div class="stat-label">Steps Completed</div>
                </div>
                <div class="stat">
                    <div class="stat-number">${Math.round(progress.progress_percent)}%</div>
                    <div class="stat-label">Progress</div>
                </div>
            </div>
        `;
    }

    displayProjectFiles(projectStructure) {
        const explorerDiv = document.getElementById('fileExplorer');

        const html = `
            <h5><i class="fas fa-folder"></i> Project: ${projectStructure.project_name}</h5>
            <p><strong>${projectStructure.total_files}</strong> files created (${this.formatFileSize(projectStructure.total_size)})</p>
            <ul class="file-tree">
                ${projectStructure.files.map(file => `
                    <li class="file-item">
                        <i class="file-icon ${this.getFileIcon(file.type, file.name)}"></i>
                        <span class="file-name">${file.path}</span>
                        <span class="file-size">${file.type === 'file' ? this.formatFileSize(file.size) : ''}</span>
                    </li>
                `).join('')}
            </ul>
        `;

        explorerDiv.innerHTML = html;
    }

    getFileIcon(type, name) {
        if (type === 'directory') return 'fas fa-folder';

        const extension = name.split('.').pop()?.toLowerCase();

        switch (extension) {
            case 'py': return 'fab fa-python';
            case 'yml':
            case 'yaml': return 'fas fa-cogs';
            case 'md': return 'fab fa-markdown';
            case 'txt': return 'fas fa-file-alt';
            case 'json': return 'fas fa-file-code';
            default: return 'fas fa-file';
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    async downloadProject() {
        if (!this.currentJobId) return;

        try {
            const response = await fetch(`/api/jobs/${this.currentJobId}/download`);

            if (!response.ok) {
                throw new Error('Download failed');
            }

            // Create download link
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `test-framework-${this.currentJobId.substring(0, 8)}.zip`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            this.showSuccess('Project downloaded successfully!');

        } catch (error) {
            console.error('Download error:', error);
            this.showError('Failed to download project');
        }
    }

    resetForm() {
        // Hide result cards
        document.getElementById('resultsCard').classList.add('hidden');
        document.getElementById('progressCard').classList.add('hidden');
        document.getElementById('validationCard').classList.add('hidden');

        // Show config card
        document.getElementById('configCard').classList.remove('hidden');

        // Reset form
        document.getElementById('generatorForm').reset();
        document.getElementById('presetSelect').value = '';
        document.getElementById('loadPresetBtn').disabled = true;

        // Reset state
        this.currentJobId = null;
        this.closeWebSocket();

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    closeWebSocket() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
    }

    showLoading() {
        document.getElementById('loadingOverlay').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.add('hidden');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        `;

        // Add styles if not already present
        if (!document.querySelector('.notification-styles')) {
            const styles = document.createElement('style');
            styles.className = 'notification-styles';
            styles.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 1rem 1.5rem;
                    border-radius: 8px;
                    color: white;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    z-index: 10000;
                    max-width: 400px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                    animation: slideIn 0.3s ease;
                }
                .notification-success { background: #28a745; }
                .notification-error { background: #dc3545; }
                .notification-close {
                    background: none;
                    border: none;
                    color: white;
                    font-size: 1.2rem;
                    cursor: pointer;
                    margin-left: auto;
                }
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }

        // Add to page
        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);

        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.testFoundryUI = new TestFoundryUI();
});

// Add CSS for field validation
const validationStyles = document.createElement('style');
validationStyles.textContent = `
    .field-error {
        border-color: #dc3545 !important;
        box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1) !important;
    }
    .field-success {
        border-color: #28a745 !important;
        box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.1) !important;
    }
`;
document.head.appendChild(validationStyles);
