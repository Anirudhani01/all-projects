// Global variables
let selectedFile = null;
const API_BASE_URL = 'http://localhost:8001';

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const processBtn = document.getElementById('processBtn');
const resultsSection = document.getElementById('resultsSection');
const resultsData = document.getElementById('resultsData');
const loading = document.getElementById('loading');
const recentResults = document.getElementById('recentResults');
const resultsList = document.getElementById('resultsList');
const toastContainer = document.getElementById('toastContainer');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadRecentResults();
});

// Event Listeners
function initializeEventListeners() {
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop events
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // Processor selection change
    document.querySelectorAll('input[name="processor"]').forEach(radio => {
        radio.addEventListener('change', updateProcessButton);
    });
}

// File handling functions
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        selectFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        selectFile(files[0]);
    }
}

function selectFile(file) {
    // Validate file type
    const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg', 'image/tiff', 'image/bmp'];
    if (!allowedTypes.includes(file.type)) {
        showToast('Please select a valid file type (PDF, PNG, JPG, JPEG, TIFF, BMP)', 'error');
        return;
    }
    
    // Validate file size (50MB limit)
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
        showToast('File size must be less than 50MB', 'error');
        return;
    }
    
    selectedFile = file;
    displayFileInfo(file);
    updateProcessButton();
}

function displayFileInfo(file) {
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.style.display = 'block';
    uploadArea.style.display = 'none';
}

function removeFile() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.style.display = 'none';
    uploadArea.style.display = 'block';
    updateProcessButton();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function updateProcessButton() {
    const processor = document.querySelector('input[name="processor"]:checked').value;
    const isEnabled = selectedFile !== null;
    
    processBtn.disabled = !isEnabled;
    
    if (isEnabled) {
        processBtn.innerHTML = `<i class="fas fa-play"></i><span>Process Document</span>`;
    } else {
        processBtn.innerHTML = `<i class="fas fa-play"></i><span>Select a file to process</span>`;
    }
}

// Processing functions
async function processFile() {
    if (!selectedFile) {
        showToast('Please select a file first', 'error');
        return;
    }
    
    const processor = document.querySelector('input[name="processor"]:checked').value;
    
    // Show loading state
    showLoading(true);
    resultsSection.style.display = 'block';
    
    try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('processor_type', processor);
        
        const response = await fetch(`${API_BASE_URL}/process`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Processing failed');
        }
        
        const result = await response.json();
        displayResults(result);
        loadRecentResults(); // Refresh recent results
        
    } catch (error) {
        console.error('Processing error:', error);
        showToast(`Processing failed: ${error.message}`, 'error');
        resultsData.innerHTML = `
            <div class="result-card">
                <h4><i class="fas fa-exclamation-triangle"></i> Processing Error</h4>
                <div class="result-content">
                    <p>${error.message}</p>
                </div>
            </div>
        `;
    } finally {
        showLoading(false);
    }
}

function displayResults(result) {
    if (!result.success) {
        resultsData.innerHTML = `
            <div class="result-card">
                <h4><i class="fas fa-exclamation-triangle"></i> Processing Failed</h4>
                <div class="result-content">
                    <p>${result.error || 'Unknown error occurred'}</p>
                </div>
            </div>
        `;
        return;
    }
    
    const extractedData = result.extracted_data;
    const metadata = extractedData.metadata || {};
    const pages = extractedData.pages || [];
    
    let html = `
        <div class="result-card">
            <h4><i class="fas fa-check-circle"></i> Processing Successful</h4>
            <div class="result-content">
                <div class="summary-table">
                    <table class="info-table">
                        <tr>
                            <td><strong><i class="fas fa-cogs"></i> Processor:</strong></td>
                            <td>${metadata.processor || 'Unknown'}</td>
                        </tr>
                        <tr>
                            <td><strong><i class="fas fa-file-alt"></i> Total Pages:</strong></td>
                            <td>${metadata.total_pages || pages.length}</td>
                        </tr>
                        <tr>
                            <td><strong><i class="fas fa-clock"></i> Processing Time:</strong></td>
                            <td>${result.processing_time ? result.processing_time.toFixed(2) + 's' : 'N/A'}</td>
                        </tr>
                        <tr>
                            <td><strong><i class="fas fa-calendar"></i> Processed At:</strong></td>
                            <td>${new Date().toLocaleString()}</td>
                        </tr>
                    </table>
                </div>
            </div>
            <div class="download-buttons">
                <a href="${API_BASE_URL}/results/${result.result_folder.split('/').pop()}" class="download-btn" target="_blank">
                    <i class="fas fa-download"></i> Download JSON
                </a>
                <a href="${API_BASE_URL}/results/${result.result_folder.split('/').pop()}" class="download-btn secondary" target="_blank">
                    <i class="fas fa-table"></i> Download CSV
                </a>
            </div>
        </div>
    `;
    
    // Display page content
    pages.forEach((page, index) => {
        const pageNumber = page.page_number || index + 1;
        const text = page.text || page.combined_text || '';
        const tables = page.tables || [];
        const images = page.images || [];
        const handwrittenText = page.handwritten_text || '';
        
        html += `
            <div class="result-card">
                <h4><i class="fas fa-file-alt"></i> Page ${pageNumber}</h4>
                <div class="result-content">
                    ${text ? `<div class="text-content"><h5>Extracted Text:</h5><div class="text-preview">${formatMedicalText(text)}</div></div>` : ''}
                    ${handwrittenText ? `<div class="handwritten-content"><h5>Handwritten Text:</h5><div class="text-preview">${handwrittenText.substring(0, 300)}${handwrittenText.length > 300 ? '...' : ''}</div></div>` : ''}
                    ${tables.length > 0 ? displayTables(tables) : ''}
                    ${images.length > 0 ? `<div class="images-content"><h5>Images Found: ${images.length}</h5><p>Images processed with OCR</p></div>` : ''}
                    ${page.extraction_stats ? displayPageStats(page.extraction_stats, pageNumber) : ''}
                </div>
            </div>
        `;
    });
    
    resultsData.innerHTML = html;
    showToast('Document processed successfully!', 'success');
}

// Recent results functions
async function loadRecentResults() {
    try {
        const response = await fetch(`${API_BASE_URL}/results`);
        if (!response.ok) return;
        
        const data = await response.json();
        const results = data.results || [];
        
        if (results.length > 0) {
            displayRecentResults(results);
            recentResults.style.display = 'block';
        } else {
            recentResults.style.display = 'none';
        }
        
    } catch (error) {
        console.error('Error loading recent results:', error);
    }
}

function displayRecentResults(results) {
    const html = results.map(result => {
        const resultId = result.result_id;
        const created = new Date(result.created * 1000).toLocaleString();
        const metadata = result.metadata || {};
        
        return `
            <div class="result-item">
                <div class="result-info">
                    <div class="result-name">${resultId}</div>
                    <div class="result-meta">
                        Created: ${created} | 
                        Processor: ${metadata.processor_name || 'Unknown'} | 
                        Pages: ${metadata.extraction_stats?.total_pages || 'N/A'}
                    </div>
                </div>
                <div class="result-actions">
                    <button class="action-btn" onclick="downloadResult('${resultId}')">
                        <i class="fas fa-download"></i> Download
                    </button>
                    <button class="action-btn" onclick="viewResult('${resultId}')">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="action-btn delete-btn" onclick="deleteResult('${resultId}')">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `;
    }).join('');
    
    resultsList.innerHTML = html;
}

function downloadResult(resultId) {
    window.open(`${API_BASE_URL}/results/${resultId}`, '_blank');
}

async function viewResult(resultId) {
    try {
        const response = await fetch(`${API_BASE_URL}/results/${resultId}`);
        if (!response.ok) {
            throw new Error('Result not found');
        }
        
        const result = await response.json();
        displayResults({ success: true, extracted_data: result, result_folder: resultId });
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        showToast(`Error loading result: ${error.message}`, 'error');
    }
}

async function deleteResult(resultId) {
    try {
        // Show confirmation dialog
        if (!confirm(`Are you sure you want to delete result "${resultId}"? This action cannot be undone.`)) {
            return;
        }
        
        const response = await fetch(`${API_BASE_URL}/results/${resultId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to delete result');
        }
        
        const result = await response.json();
        showToast(`Result deleted successfully: ${resultId}`, 'success');
        
        // Refresh the recent results list
        loadRecentResults();
        
    } catch (error) {
        console.error('Delete error:', error);
        showToast(`Error deleting result: ${error.message}`, 'error');
    }
}

// Table display functions
function displayTables(tables) {
    if (!tables || tables.length === 0) return '';
    
    let html = `<div class="tables-content"><h5><i class="fas fa-table"></i> Tables Found: ${tables.length}</h5>`;
    
    tables.forEach((table, index) => {
        html += `
            <div class="table-container">
                <h6>Table ${index + 1}</h6>
                <div class="table-wrapper">
                    ${formatTableAsHTML(table)}
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    return html;
}

function formatTableAsHTML(table) {
    if (!table || !table.data) return '<p>No table data available</p>';
    
    const data = table.data;
    if (!Array.isArray(data) || data.length === 0) return '<p>Empty table</p>';
    
    // Check if this is a medical table
    const isMedicalTable = table.type === 'medical_table' || 
                          table.title?.includes('Blood Count') || 
                          table.title?.includes('Differential') ||
                          table.title?.includes('HbA1c') ||
                          table.title?.includes('Test Result') ||
                          table.title?.includes('Medical Test') ||
                          table.title?.includes('Patient Information') ||
                          table.title?.includes('Medical History') ||
                          table.title?.includes('Vital Signs');
    
    let html = `<table class="extracted-table ${isMedicalTable ? 'medical-table' : ''}">`;
    
    // Add table headers if available
    if (data[0] && Array.isArray(data[0])) {
        html += '<thead><tr>';
        data[0].forEach((cell, index) => {
            const cellClass = isMedicalTable ? getMedicalHeaderClass(cell, index) : '';
            html += `<th class="${cellClass}">${escapeHtml(cell || '')}</th>`;
        });
        html += '</tr></thead>';
    }
    
    // Add table body
    html += '<tbody>';
    const startRow = data[0] && Array.isArray(data[0]) ? 1 : 0;
    for (let i = startRow; i < data.length; i++) {
        if (Array.isArray(data[i])) {
            html += '<tr>';
            data[i].forEach((cell, index) => {
                const cellClass = isMedicalTable ? getMedicalCellClass(cell, index) : '';
                html += `<td class="${cellClass}">${escapeHtml(cell || '')}</td>`;
            });
            html += '</tr>';
        }
    }
    html += '</tbody></table>';
    
    return html;
}

function getMedicalHeaderClass(cell, index) {
    const cellText = (cell || '').toLowerCase();
    if (cellText.includes('investigation') || cellText.includes('cell type')) return 'medical-header-test';
    if (cellText.includes('result')) return 'medical-header-result';
    if (cellText.includes('normal') || cellText.includes('reference')) return 'medical-header-range';
    if (cellText.includes('status')) return 'medical-header-status';
    return '';
}

function getMedicalCellClass(cell, index) {
    const cellText = (cell || '').toLowerCase();
    if (cellText === 'low') return 'medical-status-low';
    if (cellText === 'high') return 'medical-status-high';
    if (cellText === 'normal') return 'medical-status-normal';
    return '';
}

function formatMedicalText(text) {
    if (!text) return '';
    
    // Look for medical patterns and format them better
    let formattedText = text;
    
    // Format HbA1c results
    const hba1cPattern = /(HbA1c|HbAlc).*?(\d+\.?\d*)\s*%.*?(\d+\.?\d*)\s*-\s*(\d+\.?\d*)\s*%/gi;
    formattedText = formattedText.replace(hba1cPattern, (match, test, result, min, max) => {
        const status = determineStatus(parseFloat(result), parseFloat(min), parseFloat(max));
        return `<div class="medical-result-item">
            <strong>${test}:</strong> 
            <span class="result-value">${result}%</span> 
            <span class="reference-range">(${min} - ${max}%)</span> 
            <span class="status-badge ${status.toLowerCase()}">${status}</span>
        </div>`;
    });
    
    // Format other medical results
    const medicalPattern = /([A-Za-z\s\(\)]+?)\s+([0-9\.\-\s]+[A-Za-z\/%]+)\s+([0-9\.\-\s]+[A-Za-z\/%]+)/g;
    formattedText = formattedText.replace(medicalPattern, (match, test, result, range) => {
        if (test.length > 3 && result.includes('%') && range.includes('-')) {
            return `<div class="medical-result-item">
                <strong>${test}:</strong> 
                <span class="result-value">${result}</span> 
                <span class="reference-range">${range}</span>
            </div>`;
        }
        return match;
    });
    
    // Limit text length
    if (formattedText.length > 1000) {
        formattedText = formattedText.substring(0, 1000) + '...';
    }
    
    return formattedText;
}

function determineStatus(value, min, max) {
    if (value < min) return 'Low';
    if (value > max) return 'High';
    return 'Normal';
}

function escapeHtml(text) {
    if (typeof text !== 'string') return '';
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function displayPageStats(stats, pageNumber) {
    if (!stats) return '';
    
    let html = `
        <div class="stats-content">
            <h5><i class="fas fa-chart-bar"></i> Page ${pageNumber} Statistics</h5>
            <div class="stats-table">
                <table class="info-table">
    `;
    
    // Add various statistics in a tabular format
    if (stats.total_text_blocks !== undefined) {
        html += `<tr><td><strong>Text Blocks:</strong></td><td>${stats.total_text_blocks}</td></tr>`;
    }
    if (stats.total_words !== undefined) {
        html += `<tr><td><strong>Total Words:</strong></td><td>${stats.total_words}</td></tr>`;
    }
    if (stats.total_characters !== undefined) {
        html += `<tr><td><strong>Total Characters:</strong></td><td>${stats.total_characters}</td></tr>`;
    }
    if (stats.tables_detected !== undefined) {
        html += `<tr><td><strong>Tables Detected:</strong></td><td>${stats.tables_detected}</td></tr>`;
    }
    if (stats.images_processed !== undefined) {
        html += `<tr><td><strong>Images Processed:</strong></td><td>${stats.images_processed}</td></tr>`;
    }
    if (stats.handwritten_regions !== undefined) {
        html += `<tr><td><strong>Handwritten Regions:</strong></td><td>${stats.handwritten_regions}</td></tr>`;
    }
    if (stats.ocr_confidence !== undefined) {
        html += `<tr><td><strong>OCR Confidence:</strong></td><td>${(stats.ocr_confidence * 100).toFixed(1)}%</td></tr>`;
    }
    
    html += `
                </table>
            </div>
        </div>
    `;
    
    return html;
}

// Utility functions
function showLoading(show) {
    loading.style.display = show ? 'block' : 'none';
    resultsData.style.display = show ? 'none' : 'block';
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

// Health check on page load
async function checkServerHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('Server is running');
        } else {
            showToast('Server is not responding. Please make sure the backend is running.', 'error');
        }
    } catch (error) {
        console.error('Server health check failed:', error);
        showToast('Cannot connect to server. Please make sure the backend is running on port 8001.', 'error');
    }
}

// Check server health when page loads
document.addEventListener('DOMContentLoaded', checkServerHealth);
