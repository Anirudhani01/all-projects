// Admin Patients Management JavaScript

// DOM Elements
const patientsTable = document.getElementById('patients-table');
const searchInput = document.getElementById('search-input');
const ageFilter = document.getElementById('age-filter');
const genderFilter = document.getElementById('gender-filter');
const dateFrom = document.getElementById('date-from');
const dateTo = document.getElementById('date-to');
const patientModal = document.getElementById('patient-modal');
const patientDetailsContent = document.getElementById('patient-details-content');

// State
let patients = [];
let appointments = [];
let currentPage = 1;
let totalPages = 1;
let currentPatientId = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Authentication disabled - load data directly
    console.log('Patients page loaded, initializing without authentication...');
    
    // Set user info
    setUserInfo();
    
    // Load data
    loadPatients();
    loadAppointments();
    
    // Setup event listeners
    setupEventListeners();
});

// Set user information in header
function setUserInfo() {
    // Authentication disabled - set default admin info
    const userNameElement = document.getElementById('user-name');
    const userRoleElement = document.getElementById('user-role');
    const userAvatarElement = document.getElementById('user-avatar');
    
    if (userNameElement) userNameElement.textContent = 'Admin';
    if (userRoleElement) userRoleElement.textContent = 'Administrator';
    if (userAvatarElement) userAvatarElement.textContent = 'A';
}

// Setup event listeners
function setupEventListeners() {
    // Filter changes
    searchInput.addEventListener('input', debounce(applyFilters, 300));
    ageFilter.addEventListener('change', applyFilters);
    genderFilter.addEventListener('change', applyFilters);
    dateFrom.addEventListener('change', applyFilters);
    dateTo.addEventListener('change', applyFilters);
}

// Load patients from API
async function loadPatients() {
    try {
        showLoading(patientsTable);
        
        const response = await fetch(`${AdminAuth.API_BASE_URL}/admin/patients/`);
        if (!response.ok) {
            throw new Error('Failed to fetch patients');
        }
        
        const data = await response.json();
        patients = data || [];
        
        displayPatients(patients);
        updatePagination();
        
    } catch (error) {
        console.error('Error loading patients:', error);
        showError(patientsTable, 'Failed to load patients');
    }
}

// Load appointments for patient statistics
async function loadAppointments() {
    try {
        const response = await fetch(`${AdminAuth.API_BASE_URL}/admin/appointments/`);
        if (!response.ok) {
            throw new Error('Failed to fetch appointments');
        }
        
        const data = await response.json();
        appointments = data || [];
        
    } catch (error) {
        console.error('Error loading appointments:', error);
    }
}

// Display patients in table
function displayPatients(patientsList) {
    const tbody = patientsTable.querySelector('tbody');
    
    if (patientsList.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="loading">
                    <i class="fas fa-users"></i>
                    No patients found
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = patientsList.map(patient => {
        const patientAppointments = appointments.filter(apt => apt.patient_id === patient.id);
        const age = calculateAge(patient.date_of_birth);
        
        return `
            <tr>
                <td>
                    <div class="patient-info">
                        <div class="patient-avatar">
                            <i class="fas fa-user"></i>
                        </div>
                        <div class="patient-details">
                            <div class="patient-name">${patient.name || 'N/A'}</div>
                            <div class="patient-id">ID: ${patient.id}</div>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="contact-info">
                        <div class="contact-email">${patient.email || 'N/A'}</div>
                        <div class="contact-phone">${patient.phone || 'N/A'}</div>
                    </div>
                </td>
                <td>
                    <span class="age-badge">${age} years</span>
                </td>
                <td>
                    <span class="gender-badge">${patient.gender || 'N/A'}</span>
                </td>
                <td>
                    <div class="registration-date">
                        ${formatDate(patient.created_at)}
                    </div>
                </td>
                <td>
                    <div class="appointments-count">
                        <span class="count-badge">${patientAppointments.length}</span>
                        <span class="count-label">appointments</span>
                    </div>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-outline btn-sm" onclick="viewPatientDetails(${patient.id})" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-primary btn-sm" onclick="viewPatientAppointments(${patient.id})" title="View Appointments">
                            <i class="fas fa-calendar"></i>
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="deletePatient(${patient.id})" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

// Apply filters
function applyFilters() {
    const searchTerm = searchInput.value.toLowerCase();
    const ageRange = ageFilter.value;
    const gender = genderFilter.value;
    const fromDate = dateFrom.value;
    const toDate = dateTo.value;
    
    let filteredPatients = [...patients];
    
    // Filter by search term
    if (searchTerm) {
        filteredPatients = filteredPatients.filter(patient => 
            (patient.name && patient.name.toLowerCase().includes(searchTerm)) ||
            (patient.email && patient.email.toLowerCase().includes(searchTerm))
        );
    }
    
    // Filter by age range
    if (ageRange) {
        filteredPatients = filteredPatients.filter(patient => {
            const age = calculateAge(patient.date_of_birth);
            switch (ageRange) {
                case '0-18': return age >= 0 && age <= 18;
                case '19-35': return age >= 19 && age <= 35;
                case '36-50': return age >= 36 && age <= 50;
                case '51-65': return age >= 51 && age <= 65;
                case '65+': return age >= 65;
                default: return true;
            }
        });
    }
    
    // Filter by gender
    if (gender) {
        filteredPatients = filteredPatients.filter(patient => 
            patient.gender && patient.gender.toLowerCase() === gender.toLowerCase()
        );
    }
    
    // Filter by registration date
    if (fromDate) {
        filteredPatients = filteredPatients.filter(patient => 
            patient.created_at && patient.created_at >= fromDate
        );
    }
    
    if (toDate) {
        filteredPatients = filteredPatients.filter(patient => 
            patient.created_at && patient.created_at <= toDate
        );
    }
    
    displayPatients(filteredPatients);
}

// Clear all filters
function clearFilters() {
    searchInput.value = '';
    ageFilter.value = '';
    genderFilter.value = '';
    dateFrom.value = '';
    dateTo.value = '';
    displayPatients(patients);
}

// View patient details
function viewPatientDetails(patientId) {
    const patient = patients.find(p => p.id === patientId);
    if (!patient) {
        alert('Patient not found');
        return;
    }
    
    currentPatientId = patientId;
    
    const patientAppointments = appointments.filter(apt => apt.patient_id === patientId);
    const age = calculateAge(patient.date_of_birth);
    
    patientDetailsContent.innerHTML = `
        <div class="patient-profile">
            <div class="patient-header">
                <div class="patient-avatar-large">
                    <i class="fas fa-user"></i>
                </div>
                <div class="patient-info-large">
                    <h3>${patient.name || 'N/A'}</h3>
                    <p class="patient-id">Patient ID: ${patient.id}</p>
                </div>
            </div>
            
            <div class="patient-details-grid">
                <div class="detail-group">
                    <h4>Personal Information</h4>
                    <div class="detail-item">
                        <span class="label">Age:</span>
                        <span class="value">${age} years</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Gender:</span>
                        <span class="value">${patient.gender || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Date of Birth:</span>
                        <span class="value">${formatDate(patient.date_of_birth)}</span>
                    </div>
                </div>
                
                <div class="detail-group">
                    <h4>Contact Information</h4>
                    <div class="detail-item">
                        <span class="label">Email:</span>
                        <span class="value">${patient.email || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Phone:</span>
                        <span class="value">${patient.phone || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Address:</span>
                        <span class="value">${patient.address || 'N/A'}</span>
                    </div>
                </div>
                
                <div class="detail-group">
                    <h4>Medical Information</h4>
                    <div class="detail-item">
                        <span class="label">Medical History:</span>
                        <span class="value">${patient.medical_history || 'No medical history recorded'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Allergies:</span>
                        <span class="value">${patient.allergies || 'No known allergies'}</span>
                    </div>
                </div>
                
                <div class="detail-group">
                    <h4>Appointment Statistics</h4>
                    <div class="detail-item">
                        <span class="label">Total Appointments:</span>
                        <span class="value">${patientAppointments.length}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Last Appointment:</span>
                        <span class="value">${patientAppointments.length > 0 ? 
                            formatDate(patientAppointments[patientAppointments.length - 1].appointment_date) : 
                            'No appointments'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Registration Date:</span>
                        <span class="value">${formatDate(patient.created_at)}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Show modal
    patientModal.style.display = 'flex';
}

// Close patient modal
function closePatientModal() {
    patientModal.style.display = 'none';
    currentPatientId = null;
}

// View patient appointments
function viewPatientAppointments(patientId = null) {
    const targetPatientId = patientId || currentPatientId;
    if (!targetPatientId) return;
    
    // Navigate to appointments page with patient filter
    window.location.href = `appointments.html?patient_id=${targetPatientId}`;
}

// Delete patient
async function deletePatient(patientId) {
    if (!confirm('Are you sure you want to delete this patient? This action cannot be undone and will also delete all associated appointments.')) {
        return;
    }
    
    try {
        const response = await fetch(`${AdminAuth.API_BASE_URL}/admin/patients/${patientId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Patient deleted successfully!');
            loadPatients();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to delete patient');
        }
        
    } catch (error) {
        console.error('Error deleting patient:', error);
        alert(error.message || 'Failed to delete patient');
    }
}

// Export patients
function exportPatients() {
    const csvContent = generateCSV(patients);
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `patients_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Generate CSV content
function generateCSV(data) {
    const headers = ['ID', 'Name', 'Email', 'Phone', 'Age', 'Gender', 'Date of Birth', 'Registration Date'];
    const rows = data.map(patient => [
        patient.id || '',
        patient.name || '',
        patient.email || '',
        patient.phone || '',
        calculateAge(patient.date_of_birth),
        patient.gender || '',
        patient.date_of_birth || '',
        patient.created_at || ''
    ]);
    
    return [headers, ...rows].map(row => 
        row.map(field => `"${field}"`).join(',')
    ).join('\n');
}

// Refresh patients
function refreshPatients() {
    loadPatients();
    alert('Patients refreshed');
}

// Update pagination
function updatePagination() {
    const paginationContainer = document.getElementById('pagination-container');
    const pageInfo = document.getElementById('page-info');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    
    if (totalPages <= 1) {
        paginationContainer.style.display = 'none';
        return;
    }
    
    paginationContainer.style.display = 'block';
    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    prevBtn.disabled = currentPage <= 1;
    nextBtn.disabled = currentPage >= totalPages;
}

// Previous page
function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        loadPatients();
    }
}

// Next page
function nextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        loadPatients();
    }
}

// Toggle sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');
}

// Utility functions
function calculateAge(dateOfBirth) {
    if (!dateOfBirth) return 'N/A';
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    
    return age;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function showLoading(container) {
    if (!container) return;
    
    const tbody = container.querySelector('tbody');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    Loading patients...
                </td>
            </tr>
        `;
    }
}

function showError(container, message) {
    if (!container) return;
    
    const tbody = container.querySelector('tbody');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="loading">
                    <i class="fas fa-exclamation-triangle"></i>
                    ${message}
                </td>
            </tr>
        `;
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Add CSS for additional patient management styles
const additionalStyles = `
    .patient-profile {
        max-height: 60vh;
        overflow-y: auto;
    }
    
    .patient-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .patient-avatar-large {
        width: 60px;
        height: 60px;
        background: #e5e7eb;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #6b7280;
        font-size: 1.5rem;
    }
    
    .patient-info-large h3 {
        margin: 0;
        color: #1f2937;
        font-size: 1.5rem;
    }
    
    .patient-id {
        color: #6b7280;
        font-size: 0.9rem;
        margin: 0;
    }
    
    .patient-details-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
    }
    
    .detail-group h4 {
        margin: 0 0 1rem 0;
        color: #1f2937;
        font-size: 1.1rem;
        border-bottom: 1px solid #e5e7eb;
        padding-bottom: 0.5rem;
    }
    
    .detail-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        border-bottom: 1px solid #f3f4f6;
    }
    
    .detail-item:last-child {
        border-bottom: none;
    }
    
    .detail-item .label {
        font-weight: 500;
        color: #6b7280;
    }
    
    .detail-item .value {
        color: #1f2937;
        text-align: right;
    }
    
    .age-badge,
    .gender-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .age-badge {
        background: #dbeafe;
        color: #1e40af;
    }
    
    .gender-badge {
        background: #dcfce7;
        color: #166534;
    }
    
    .count-badge {
        background: #2563eb;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .count-label {
        font-size: 0.8rem;
        color: #6b7280;
        margin-left: 0.5rem;
    }
    
    .contact-info {
        text-align: left;
    }
    
    .contact-email {
        font-weight: 500;
        color: #1f2937;
    }
    
    .contact-phone {
        font-size: 0.8rem;
        color: #6b7280;
    }
    
    .registration-date {
        font-size: 0.9rem;
        color: #6b7280;
    }
    
    .appointments-count {
        display: flex;
        align-items: center;
    }
    
    @media (max-width: 768px) {
        .patient-details-grid {
            grid-template-columns: 1fr;
        }
        
        .detail-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.25rem;
        }
        
        .detail-item .value {
            text-align: left;
        }
    }
`;

// Add the additional styles to the page
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);
