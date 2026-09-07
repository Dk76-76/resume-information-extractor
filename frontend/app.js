// Resume Information Extraction System - Frontend Application Logic

let selectedFile = null;
let currentExtractedJson = null;

// DOM Elements
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const filePreview = document.getElementById('filePreview');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const fileTypeIcon = document.getElementById('fileTypeIcon');
const btnClearFile = document.getElementById('btnClearFile');
const btnExtract = document.getElementById('btnExtract');
const extractSpinner = document.getElementById('extractSpinner');
const btnText = btnExtract.querySelector('.btn-text');
const alertBox = document.getElementById('alertBox');

const emptyState = document.getElementById('emptyState');
const overviewTab = document.getElementById('overviewTab');
const jsonTab = document.getElementById('jsonTab');
const outputActions = document.getElementById('outputActions');
const tabButtons = document.querySelectorAll('.tab-btn');

const btnCopyJson = document.getElementById('btnCopyJson');
const copyText = document.getElementById('copyText');
const btnDownloadJson = document.getElementById('btnDownloadJson');
const jsonDisplay = document.getElementById('jsonDisplay');

// Extracted UI Elements
const avatarInitial = document.getElementById('avatarInitial');
const dispName = document.getElementById('dispName');
const dispEmail = document.getElementById('dispEmail');
const dispPhone = document.getElementById('dispPhone');
const dispLinkedin = document.getElementById('dispLinkedin');
const dispGithub = document.getElementById('dispGithub');
const dispSkills = document.getElementById('dispSkills');
const skillsCount = document.getElementById('skillsCount');
const dispEducation = document.getElementById('dispEducation');
const educationCount = document.getElementById('educationCount');
const dispExperience = document.getElementById('dispExperience');
const experienceCount = document.getElementById('experienceCount');

// Initialize Event Listeners
function init() {
    // Dropzone drag & drop
    ['dragenter', 'dragover'].forEach(event => {
        dropzone.addEventListener(event, (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(event => {
        dropzone.addEventListener(event, (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
        });
    });

    dropzone.addEventListener('drop', (e) => {
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFileSelection(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    btnClearFile.addEventListener('click', clearSelectedFile);
    btnExtract.addEventListener('click', () => {
        if (selectedFile) {
            extractResume(selectedFile);
        }
    });

    // Tab Switching
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            if (currentExtractedJson) {
                if (targetTab === 'overviewTab') {
                    overviewTab.style.display = 'block';
                    jsonTab.style.display = 'none';
                } else {
                    overviewTab.style.display = 'none';
                    jsonTab.style.display = 'block';
                }
            }
        });
    });

    // Copy & Download
    btnCopyJson.addEventListener('click', copyJsonToClipboard);
    btnDownloadJson.addEventListener('click', downloadJsonFile);

    // Quick Sample Buttons
    document.querySelectorAll('.btn-sample').forEach(btn => {
        btn.addEventListener('click', () => {
            const sampleName = btn.getAttribute('data-sample');
            loadSampleResume(sampleName);
        });
    });
}

function handleFileSelection(file) {
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (ext !== '.pdf' && ext !== '.docx') {
        showAlert('Unsupported file format. Please upload a .pdf or .docx file.', 'error');
        clearSelectedFile();
        return;
    }

    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatBytes(file.size);
    fileTypeIcon.textContent = ext === '.pdf' ? '📕' : '📘';

    filePreview.style.display = 'flex';
    btnExtract.disabled = false;
    hideAlert();
}

function clearSelectedFile() {
    selectedFile = null;
    fileInput.value = '';
    filePreview.style.display = 'none';
    btnExtract.disabled = true;
}

function formatBytes(bytes, decimals = 1) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

async function extractResume(file) {
    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    hideAlert();

    try {
        const response = await fetch('/api/extract', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.message || 'Failed to extract resume data.');
        }

        currentExtractedJson = result.data;
        renderResults(result.data, file.name);
        showAlert('Resume successfully parsed and extracted!', 'success');

    } catch (err) {
        showAlert(err.message || 'An unexpected error occurred during extraction.', 'error');
    } finally {
        setLoading(false);
    }
}

function renderResults(data, filename) {
    // Hide empty state, reveal panels
    emptyState.style.display = 'none';
    outputActions.style.display = 'flex';

    const activeTab = document.querySelector('.tab-btn.active').getAttribute('data-tab');
    if (activeTab === 'overviewTab') {
        overviewTab.style.display = 'block';
        jsonTab.style.display = 'none';
    } else {
        overviewTab.style.display = 'none';
        jsonTab.style.display = 'block';
    }

    // Name & Initial
    const candidateName = data.name || 'Name Not Detected';
    dispName.textContent = candidateName;
    avatarInitial.textContent = candidateName !== 'Name Not Detected' 
        ? candidateName.charAt(0).toUpperCase() 
        : '?';

    // Email
    if (data.email) {
        dispEmail.textContent = data.email;
        dispEmail.parentElement.style.display = 'inline-flex';
    } else {
        dispEmail.textContent = 'Email not provided';
        dispEmail.parentElement.style.display = 'inline-flex';
    }

    // Phone
    if (data.phone) {
        dispPhone.textContent = data.phone;
        dispPhone.parentElement.style.display = 'inline-flex';
    } else {
        dispPhone.textContent = 'Phone not provided';
        dispPhone.parentElement.style.display = 'inline-flex';
    }

    // Social Links
    if (data.linkedin) {
        dispLinkedin.href = data.linkedin;
        dispLinkedin.style.display = 'inline-flex';
    } else {
        dispLinkedin.style.display = 'none';
    }

    if (data.github) {
        dispGithub.href = data.github;
        dispGithub.style.display = 'inline-flex';
    } else {
        dispGithub.style.display = 'none';
    }

    // Skills
    dispSkills.innerHTML = '';
    if (data.skills && data.skills.length > 0) {
        skillsCount.textContent = `${data.skills.length} detected`;
        data.skills.forEach(skill => {
            const span = document.createElement('span');
            span.className = 'skill-tag';
            span.textContent = skill;
            dispSkills.appendChild(span);
        });
    } else {
        skillsCount.textContent = '0 detected';
        dispSkills.innerHTML = '<span class="empty-field-text">No technical skills detected.</span>';
    }

    // Education
    dispEducation.innerHTML = '';
    if (data.education && data.education.length > 0) {
        educationCount.textContent = `${data.education.length} record${data.education.length > 1 ? 's' : ''}`;
        data.education.forEach(edu => {
            const div = document.createElement('div');
            div.className = 'record-item';
            div.innerHTML = `
                <div class="record-top">
                    <span class="record-title">${escapeHtml(edu.degree)}</span>
                    ${edu.year ? `<span class="record-date">${escapeHtml(edu.year)}</span>` : ''}
                </div>
                <div class="record-subtitle">${edu.institution ? escapeHtml(edu.institution) : 'Institution not detected'}</div>
                ${edu.university ? `<div class="record-meta-line" style="font-size: 0.85rem; color: var(--text-muted); margin-top: 2px;">${escapeHtml(edu.university)}</div>` : ''}
                <div class="record-badges" style="display: flex; gap: 6px; margin-top: 4px;">
                    ${edu.cgpa ? `<span class="badge" style="background: rgba(99, 102, 241, 0.15); color: #818cf8; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">CGPA: ${escapeHtml(edu.cgpa)}</span>` : ''}
                    ${edu.percentage ? `<span class="badge" style="background: rgba(16, 185, 129, 0.15); color: #34d399; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">Percentage: ${escapeHtml(edu.percentage)}</span>` : ''}
                </div>
            `;
            dispEducation.appendChild(div);
        });
    } else {
        educationCount.textContent = '0 records';
        dispEducation.innerHTML = '<span class="empty-field-text">No education entries detected.</span>';
    }

    // Work Experience
    dispExperience.innerHTML = '';
    if (data.experience && data.experience.length > 0) {
        experienceCount.textContent = `${data.experience.length} record${data.experience.length > 1 ? 's' : ''}`;
        data.experience.forEach(exp => {
            const div = document.createElement('div');
            div.className = 'record-item';
            div.innerHTML = `
                <div class="record-top">
                    <span class="record-title">${escapeHtml(exp.title)}</span>
                    ${exp.duration ? `<span class="record-date">${escapeHtml(exp.duration)}</span>` : ''}
                </div>
                <div class="record-subtitle">${exp.company ? escapeHtml(exp.company) : 'Company not detected'}</div>
            `;
            dispExperience.appendChild(div);
        });
    } else {
        experienceCount.textContent = '0 records';
        dispExperience.innerHTML = '<span class="empty-field-text">No work experience entries detected.</span>';
    }

    // Raw JSON Display
    jsonDisplay.textContent = JSON.stringify(data, null, 2);
}

function setLoading(isLoading) {
    btnExtract.disabled = isLoading;
    if (isLoading) {
        btnText.textContent = 'Extracting...';
        extractSpinner.style.display = 'inline-block';
    } else {
        btnText.textContent = 'Extract Information';
        extractSpinner.style.display = 'none';
    }
}

function showAlert(message, type = 'error') {
    alertBox.textContent = message;
    alertBox.className = `alert-box alert-${type}`;
    alertBox.style.display = 'block';
}

function hideAlert() {
    alertBox.style.display = 'none';
}

function copyJsonToClipboard() {
    if (!currentExtractedJson) return;
    const jsonStr = JSON.stringify(currentExtractedJson, null, 2);
    navigator.clipboard.writeText(jsonStr).then(() => {
        copyText.textContent = 'Copied!';
        setTimeout(() => {
            copyText.textContent = 'Copy JSON';
        }, 2000);
    }).catch(() => {
        showAlert('Could not copy JSON to clipboard.', 'error');
    });
}

function downloadJsonFile() {
    if (!currentExtractedJson) return;
    const jsonStr = JSON.stringify(currentExtractedJson, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const baseName = selectedFile ? selectedFile.name.replace(/\.[^/.]+$/, "") : "resume";
    a.href = url;
    a.download = `${baseName}_extracted.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

async function loadSampleResume(sampleFilename) {
    try {
        setLoading(true);
        showAlert(`Loading sample ${sampleFilename}...`, 'success');
        
        const response = await fetch(`/samples/${sampleFilename}`);
        if (!response.ok) {
            throw new Error(`Could not load sample file (${response.statusText})`);
        }
        const blob = await response.blob();
        const file = new File([blob], sampleFilename, { type: blob.type });
        handleFileSelection(file);
        await extractResume(file);
    } catch (err) {
        showAlert(err.message, 'error');
    } finally {
        setLoading(false);
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.toString().replace(/[&<>"']/g, m => map[m]);
}

// Start application
document.addEventListener('DOMContentLoaded', init);
