// Admin Doctors Management JavaScript

// DOM Elements
const doctorsTable = document.getElementById('doctors-table');
const addDoctorForm = document.getElementById('add-doctor-form');
const doctorForm = document.getElementById('doctor-form');
const editModal = document.getElementById('edit-modal');
const editDoctorForm = document.getElementById('edit-doctor-form');

// State
let doctors = [];
let currentEditId = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    if (!AdminAuth.isLoggedIn()) {
        window.location.href = '../login.html';
        return;
    }
    
    // Set user info
    setUserInfo();
    
    // Load doctors
    loadDoctors();
    
    // Setup event listeners
    setupEventListeners();
});

// Set user information in header
function setUserInfo() {
    const user = AdminAuth.getCurrentUser();
    if (user) {
        document.getElementById('user-name').textContent = user.username;
        document.getElementById('user-role').textContent = user.role;
        document.getElementById('user-avatar').textContent = user.username.charAt(0).toUpperCase();
    }
}

// Setup event listeners
function setupEventListeners() {
    // Add doctor form
    if (doctorForm) {
        doctorForm.addEventListener('submit', handleAddDoctor);
    }
    
    // Edit doctor form
    if (editDoctorForm) {
        editDoctorForm.addEventListener('submit', handleEditDoctor);
    }
}

// Load doctors from API
async function loadDoctors() {
    try {
        showLoading(doctorsTable);
        
        const response = await AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/doctors/`);
        if (!response) {
            return;
        }
        
        const data = await response.json();
        doctors = data.doctors || [];
        
        displayDoctors(doctors);
        
    } catch (error) {
        console.error('Error loading doctors:', error);
        showError(doctorsTable, 'Failed to load doctors');
    }
}

// Display doctors in table
function displayDoctors(doctorsList) {
    const tbody = doctorsTable.querySelector('tbody');
    
    if (doctorsList.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="loading">
                    <i class="fas fa-user-md"></i>
                    No doctors found
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = doctorsList.map(doctor => `
        <tr>
            <td>
                <div class="doctor-info">
                    <div class="doctor-avatar">
                        <i class="fas fa-user-md"></i>
                    </div>
                    <div class="doctor-details">
                        <div class="doctor-name">${doctor.name}</div>
                    </div>
                </div>
            </td>
            <td>
                <span class="specialization-badge">${doctor.specialization}</span>
            </td>
            <td>${doctor.education}</td>
            <td>${doctor.experience} years</td>
            <td>
                <span class="status-badge ${doctor.is_active ? 'active' : 'inactive'}">
                    ${doctor.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-outline btn-sm" onclick="editDoctor(${doctor.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteDoctor(${doctor.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Show add doctor form
function showAddDoctorForm() {
    addDoctorForm.style.display = 'block';
    doctorForm.reset();
    addDoctorForm.scrollIntoView({ behavior: 'smooth' });
}

// Cancel add doctor
function cancelAddDoctor() {
    addDoctorForm.style.display = 'none';
    doctorForm.reset();
}

// Handle add doctor form submission
async function handleAddDoctor(event) {
    event.preventDefault();
    
    const formData = new FormData(doctorForm);
    const doctorData = {
        name: formData.get('name'),
        specialization: formData.get('specialization'),
        education: formData.get('education'),
        experience: parseInt(formData.get('experience')),
        image_url: formData.get('image_url') || null,
        is_active: formData.get('is_active') === 'true'
    };
    
    try {
        const response = await AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/doctors/`, {
            method: 'POST',
            body: JSON.stringify(doctorData)
        });
        
        if (!response) {
            return;
        }
        
        if (response.ok) {
            AdminAuth.showNotification('Doctor added successfully!', 'success');
            doctorForm.reset();
            addDoctorForm.style.display = 'none';
            loadDoctors();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to add doctor');
        }
        
    } catch (error) {
        console.error('Error adding doctor:', error);
        AdminAuth.showNotification(error.message || 'Failed to add doctor', 'error');
    }
}

// Edit doctor
function editDoctor(doctorId) {
    const doctor = doctors.find(d => d.id === doctorId);
    if (!doctor) {
        AdminAuth.showNotification('Doctor not found', 'error');
        return;
    }
    
    currentEditId = doctorId;
    
    // Populate form
    document.getElementById('edit-doctor-id').value = doctor.id;
    document.getElementById('edit-doctor-name').value = doctor.name;
    document.getElementById('edit-doctor-specialization').value = doctor.specialization;
    document.getElementById('edit-doctor-education').value = doctor.education;
    document.getElementById('edit-doctor-experience').value = doctor.experience;
    document.getElementById('edit-doctor-image').value = doctor.image_url || '';
    document.getElementById('edit-doctor-active').value = doctor.is_active.toString();
    
    // Show modal
    editModal.style.display = 'flex';
}

// Close edit modal
function closeEditModal() {
    editModal.style.display = 'none';
    currentEditId = null;
    editDoctorForm.reset();
}

// Save doctor edit
async function saveDoctorEdit() {
    if (!currentEditId) {
        AdminAuth.showNotification('No doctor selected for editing', 'error');
        return;
    }
    
    const formData = new FormData(editDoctorForm);
    const doctorData = {
        name: formData.get('name'),
        specialization: formData.get('specialization'),
        education: formData.get('education'),
        experience: parseInt(formData.get('experience')),
        image_url: formData.get('image_url') || null,
        is_active: formData.get('is_active') === 'true'
    };
    
    try {
        const response = await AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/doctors/${currentEditId}`, {
            method: 'PUT',
            body: JSON.stringify(doctorData)
        });
        
        if (!response) {
            return;
        }
        
        if (response.ok) {
            AdminAuth.showNotification('Doctor updated successfully!', 'success');
            closeEditModal();
            loadDoctors();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to update doctor');
        }
        
    } catch (error) {
        console.error('Error updating doctor:', error);
        AdminAuth.showNotification(error.message || 'Failed to update doctor', 'error');
    }
}

// Delete doctor
async function deleteDoctor(doctorId) {
    if (!confirm('Are you sure you want to delete this doctor? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/doctors/${doctorId}`, {
            method: 'DELETE'
        });
        
        if (!response) {
            return;
        }
        
        if (response.ok) {
            AdminAuth.showNotification('Doctor deleted successfully!', 'success');
            loadDoctors();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to delete doctor');
        }
        
    } catch (error) {
        console.error('Error deleting doctor:', error);
        AdminAuth.showNotification(error.message || 'Failed to delete doctor', 'error');
    }
}

// Refresh doctors
function refreshDoctors() {
    loadDoctors();
    AdminAuth.showNotification('Doctors list refreshed', 'success');
}

// Toggle sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');
}

// Utility functions
function showLoading(container) {
    if (!container) return;
    
    const tbody = container.querySelector('tbody');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    Loading doctors...
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
                <td colspan="6" class="loading">
                    <i class="fas fa-exclamation-triangle"></i>
                    ${message}
                </td>
            </tr>
        `;
    }
}

// Add CSS for additional doctor management styles
const additionalStyles = `
    .doctor-info {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .doctor-avatar {
        width: 40px;
        height: 40px;
        background: #e5e7eb;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #6b7280;
        font-size: 1.2rem;
    }
    
    .doctor-details {
        flex: 1;
    }
    
    .doctor-name {
        font-weight: 500;
        color: #1f2937;
    }
    
    .specialization-badge {
        background: #dbeafe;
        color: #1e40af;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .action-buttons {
        display: flex;
        gap: 0.5rem;
    }
    
    .btn-sm {
        padding: 0.25rem 0.5rem;
        font-size: 0.8rem;
    }
    
    .form-container {
        margin-bottom: 2rem;
    }
    
    .modal {
        max-width: 600px;
    }
    
    .modal-body {
        max-height: 60vh;
        overflow-y: auto;
    }
`;

// Add the additional styles to the page
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);
