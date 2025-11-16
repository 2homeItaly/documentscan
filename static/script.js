// Document Scanner - Frontend Logic

let sessionId = null;
let uploadedFiles = [];
let profiles = {};

// DOM Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileList = document.getElementById('file-list');
const filesContainer = document.getElementById('files-container');
const fileCount = document.getElementById('file-count');

const uploadSection = document.getElementById('upload-section');
const settingsSection = document.getElementById('settings-section');
const processingSection = document.getElementById('processing-section');
const resultsSection = document.getElementById('results-section');

const processBtn = document.getElementById('process-btn');
const downloadAllBtn = document.getElementById('download-all-btn');
const newScanBtn = document.getElementById('new-scan-btn');

const grayscaleSelect = document.getElementById('grayscale');
const dpiSelect = document.getElementById('dpi');
const qualitySlider = document.getElementById('quality');
const qualityValue = document.getElementById('quality-value');
const singlePdfSelect = document.getElementById('single-pdf');
const pdfNameInput = document.getElementById('pdf-name');

const processedCount = document.getElementById('processed-count');
const outputFiles = document.getElementById('output-files');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadConfigProfiles();
});

function initializeEventListeners() {
    // Drag and drop
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);

    // File input
    fileInput.addEventListener('change', handleFileSelect);

    // Quality slider
    qualitySlider.addEventListener('input', (e) => {
        qualityValue.textContent = e.target.value;
    });

    // Process button
    processBtn.addEventListener('click', processDocuments);

    // Download all button
    downloadAllBtn.addEventListener('click', downloadAll);

    // New scan button
    newScanBtn.addEventListener('click', resetApp);

    // Profile buttons
    document.querySelectorAll('.profile-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const profileName = btn.dataset.profile;
            applyProfile(profileName);

            // Update active state
            document.querySelectorAll('.profile-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
}

// Load configuration profiles from backend
async function loadConfigProfiles() {
    try {
        const response = await fetch('/config-profiles');
        if (response.ok) {
            profiles = await response.json();
        }
    } catch (error) {
        console.error('Error loading profiles:', error);
    }
}

// Apply configuration profile
function applyProfile(profileName) {
    const profile = profiles[profileName];
    if (!profile) return;

    grayscaleSelect.value = profile.grayscale.toString();
    dpiSelect.value = profile.dpi.toString();
    qualitySlider.value = profile.quality;
    qualityValue.textContent = profile.quality;

    if (profile.pdf) {
        singlePdfSelect.value = profile.pdf.single_pdf.toString();
        if (profile.pdf.pdf_name) {
            pdfNameInput.value = profile.pdf.pdf_name;
        }
    }
}

// Drag and drop handlers
function handleDragOver(e) {
    e.preventDefault();
    dropZone.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');

    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
}

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    handleFiles(files);
}

// Handle selected files
async function handleFiles(files) {
    if (files.length === 0) return;

    // Filter only images
    const imageFiles = files.filter(file => file.type.startsWith('image/'));

    if (imageFiles.length === 0) {
        showNotification('Seleziona solo file immagine!', 'error');
        return;
    }

    // Upload files
    await uploadFiles(imageFiles);
}

// Upload files to server
async function uploadFiles(files) {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files[]', file);
    });

    try {
        showNotification('Caricamento file in corso...', 'info');

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        const data = await response.json();
        sessionId = data.session_id;
        uploadedFiles = data.files;

        displayUploadedFiles(data.files);
        showNotification(`${data.count} file caricati con successo!`, 'success');

        // Show settings section
        settingsSection.style.display = 'block';
        settingsSection.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('Upload error:', error);
        showNotification('Errore durante il caricamento dei file', 'error');
    }
}

// Display uploaded files
function displayUploadedFiles(files) {
    filesContainer.innerHTML = '';
    fileCount.textContent = files.length;

    files.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <svg class="file-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21 15 16 10 5 21"/>
            </svg>
            <div class="file-details">
                <div class="file-name">${file.name}</div>
                <div class="file-size">${formatFileSize(file.size)}</div>
            </div>
            <button class="file-remove" onclick="removeFile(${index})">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
            </button>
        `;
        filesContainer.appendChild(fileItem);
    });

    fileList.style.display = 'block';
}

// Remove file from list
function removeFile(index) {
    uploadedFiles.splice(index, 1);

    if (uploadedFiles.length === 0) {
        fileList.style.display = 'none';
        settingsSection.style.display = 'none';
    } else {
        displayUploadedFiles(uploadedFiles);
    }
}

// Process documents
async function processDocuments() {
    if (!sessionId || uploadedFiles.length === 0) {
        showNotification('Carica prima dei file!', 'error');
        return;
    }

    // Get settings
    const params = {
        grayscale: grayscaleSelect.value === 'true',
        dpi: parseInt(dpiSelect.value),
        quality: parseInt(qualitySlider.value),
        single_pdf: singlePdfSelect.value === 'true',
        pdf_name: pdfNameInput.value || 'scanned_document.pdf'
    };

    // Show processing section
    uploadSection.style.display = 'none';
    settingsSection.style.display = 'none';
    processingSection.style.display = 'block';
    processingSection.scrollIntoView({ behavior: 'smooth' });

    try {
        const response = await fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                params: params
            })
        });

        if (!response.ok) {
            throw new Error('Processing failed');
        }

        const data = await response.json();

        // Show results
        setTimeout(() => {
            showResults(data);
        }, 1000);

    } catch (error) {
        console.error('Processing error:', error);
        showNotification('Errore durante il processing', 'error');
        resetApp();
    }
}

// Show processing results
function showResults(data) {
    processingSection.style.display = 'none';
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });

    processedCount.textContent = data.processed_count;

    // Display output files
    outputFiles.innerHTML = '';
    data.output_files.forEach(file => {
        const fileDiv = document.createElement('div');
        fileDiv.className = 'output-file';

        const iconSvg = file.type === 'pdf'
            ? '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>'
            : '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>';

        fileDiv.innerHTML = `
            <div class="output-file-info">
                <div class="output-file-icon">${iconSvg}</div>
                <div class="output-file-details">
                    <h4>${file.name}</h4>
                    <p>${formatFileSize(file.size)} - ${file.type.toUpperCase()}</p>
                </div>
            </div>
            <div class="output-file-actions">
                ${file.type !== 'pdf' ? `
                    <button class="btn btn-secondary btn-sm" onclick="previewFile('${file.name}')">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                            <circle cx="12" cy="12" r="3"/>
                        </svg>
                        Anteprima
                    </button>
                ` : ''}
                <button class="btn btn-primary btn-sm" onclick="downloadFile('${file.name}')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="7 10 12 15 17 10"/>
                        <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                    Scarica
                </button>
            </div>
        `;
        outputFiles.appendChild(fileDiv);
    });
}

// Preview file
function previewFile(filename) {
    const url = `/preview/${sessionId}/${filename}`;
    window.open(url, '_blank');
}

// Download single file
function downloadFile(filename) {
    const url = `/download/${sessionId}/${filename}`;
    window.location.href = url;
}

// Download all files as ZIP
function downloadAll() {
    const url = `/download-all/${sessionId}`;
    window.location.href = url;
}

// Reset application
function resetApp() {
    sessionId = null;
    uploadedFiles = [];

    fileList.style.display = 'none';
    filesContainer.innerHTML = '';
    fileInput.value = '';

    uploadSection.style.display = 'block';
    settingsSection.style.display = 'none';
    processingSection.style.display = 'none';
    resultsSection.style.display = 'none';

    uploadSection.scrollIntoView({ behavior: 'smooth' });
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function showNotification(message, type = 'info') {
    // Simple console notification (you can enhance this with a toast library)
    console.log(`[${type.toUpperCase()}] ${message}`);

    // You could add a proper notification system here
    if (type === 'error') {
        alert(message);
    }
}

// Make functions globally available
window.removeFile = removeFile;
window.previewFile = previewFile;
window.downloadFile = downloadFile;
