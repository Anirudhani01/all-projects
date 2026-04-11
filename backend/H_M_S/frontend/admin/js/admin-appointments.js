// Admin Appointments Management JavaScript

// DOM Elements
const appointmentsTable = document.getElementById('appointments-table');
const statusFilter = document.getElementById('status-filter');
const doctorFilter = document.getElementById('doctor-filter');
const dateFrom = document.getElementById('date-from');
const dateTo = document.getElementById('date-to');
const searchInput = document.getElementById('search-input');
const editModal = document.getElementById('edit-modal');
const editAppointmentForm = document.getElementById('edit-appointment-form');

// State
let appointments = [];
let doctors = [];
let currentPage = 1;
let totalPages = 1;
let currentEditId = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Authentication disabled - load data directly
    console.log('Appointments page loaded, initializing without authentication...');
    
    // Set user info
    setUserInfo();
    
    // Load data
    loadDoctors();
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
    statusFilter.addEventListener('change', applyFilters);
    doctorFilter.addEventListener('change', applyFilters);
    dateFrom.addEventListener('change', applyFilters);
    dateTo.addEventListener('change', applyFilters);
    searchInput.addEventListener('input', debounce(applyFilters, 300));
    
    // Edit form
    if (editAppointmentForm) {
        editAppointmentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveAppointmentEdit();
        });
    }
}

// Load doctors for filter
async function loadDoctors() {
    try {
        const response = await fetch(`${AdminAuth.API_BASE_URL}/admin/doctors/`);
        if (!response.ok) {
            throw new Error('Failed to fetch doctors');
        }

        const data = await response.json();
        doctors = data.doctors || [];
        
        // Populate doctor filter
        doctorFilter.innerHTML = '<option value="">All Doctors</option>';
        doctors.forEach(doctor => {
            const option = document.createElement('option');
            option.value = doctor.id;
            option.textContent = doctor.name;
            doctorFilter.appendChild(option);
        });

    } catch (error) {
        console.error('Error loading doctors:', error);
    }
}

// Load appointments from API
async function loadAppointments() {
    try {
        showLoading(appointmentsTable);
        
        const response = await fetch(`${AdminAuth.API_BASE_URL}/admin/appointments/`);
        if (!response.ok) {
            throw new Error('Failed to fetch appointments');
        }
        
        const data = await response.json();
        appointments = data || [];
        
        displayAppointments(appointments);
        updatePagination();
        
    } catch (error) {
        console.error('Error loading appointments:', error);
        showError(appointmentsTable, 'Failed to load appointments');
    }
}

// Display appointments in table
function displayAppointments(appointmentsList) {
    const tbody = appointmentsTable.querySelector('tbody');
    
    if (appointmentsList.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="loading">
                    <i class="fas fa-calendar-times"></i>
                    No appointments found
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = appointmentsList.map(appointment => `
        <tr>
            <td>
                <div class="patient-info">
                    <div class="patient-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="patient-details">
                        <div class="patient-name">${appointment.patient?.name || 'N/A'}</div>
                        <div class="patient-email">${appointment.patient?.email || ''}</div>
                    </div>
                </div>
            </td>
            <td>
                <div class="doctor-info">
                    <div class="doctor-name">${appointment.doctor?.name || 'N/A'}</div>
                    <div class="doctor-specialization">${appointment.doctor?.specialization || ''}</div>
                </div>
            </td>
            <td>
                <div class="datetime-info">
                    <div class="appointment-date">${formatDate(appointment.appointment_date)}</div>
                    <div class="appointment-time">${formatTime(appointment.appointment_time)}</div>
                </div>
            </td>
            <td>
                <span class="status-badge ${getStatusClass(appointment.status)}">
                    ${appointment.status || 'Scheduled'}
                </span>
            </td>
            <td>
                <div class="notes-preview">
                    ${appointment.notes ? (appointment.notes.length > 50 ? 
                        appointment.notes.substring(0, 50) + '...' : 
                        appointment.notes) : 'No notes'}
                </div>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-outline btn-sm" onclick="editAppointment(${appointment.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-warning btn-sm" onclick="cancelAppointment(${appointment.id})" title="Cancel">
                        <i class="fas fa-times"></i>
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteAppointment(${appointment.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Apply filters
function applyFilters() {
    const status = statusFilter.value;
    const doctorId = doctorFilter.value;
    const fromDate = dateFrom.value;
    const toDate = dateTo.value;
    const searchTerm = searchInput.value.toLowerCase();
    
    let filteredAppointments = [...appointments];
    
    // Filter by status
    if (status) {
        filteredAppointments = filteredAppointments.filter(apt => 
            apt.status?.toLowerCase() === status.toLowerCase()
        );
    }
    
    // Filter by doctor
    if (doctorId) {
        filteredAppointments = filteredAppointments.filter(apt => 
            apt.doctor_id == doctorId
        );
    }
    
    // Filter by date range
    if (fromDate) {
        filteredAppointments = filteredAppointments.filter(apt => 
            apt.appointment_date >= fromDate
        );
    }
    
    if (toDate) {
        filteredAppointments = filteredAppointments.filter(apt => 
            apt.appointment_date <= toDate
        );
    }
    
    // Filter by search term
    if (searchTerm) {
        filteredAppointments = filteredAppointments.filter(apt => 
            (apt.patient?.name && apt.patient.name.toLowerCase().includes(searchTerm)) ||
            (apt.doctor?.name && apt.doctor.name.toLowerCase().includes(searchTerm))
        );
    }
    
    displayAppointments(filteredAppointments);
}

// Clear all filters
function clearFilters() {
    statusFilter.value = '';
    doctorFilter.value = '';
    dateFrom.value = '';
    dateTo.value = '';
    searchInput.value = '';
    displayAppointments(appointments);
}

// Edit appointment
function editAppointment(appointmentId) {
    const appointment = appointments.find(a => a.id === appointmentId);
    if (!appointment) {
        AdminAuth.showNotification('Appointment not found', 'error');
        return;
    }
    
    currentEditId = appointmentId;
    
    // Populate form
    document.getElementById('edit-appointment-id').value = appointment.id;
    document.getElementById('edit-patient-name').value = appointment.patient?.name || '';
    document.getElementById('edit-doctor-name').value = appointment.doctor?.name || '';
    document.getElementById('edit-appointment-date').value = appointment.appointment_date || '';
    document.getElementById('edit-appointment-time').value = appointment.appointment_time || '';
    document.getElementById('edit-appointment-status').value = appointment.status || 'scheduled';
    document.getElementById('edit-appointment-notes').value = appointment.notes || '';
    
    // Show modal
    editModal.style.display = 'flex';
}

// Close edit modal
function closeEditModal() {
    editModal.style.display = 'none';
    currentEditId = null;
    editAppointmentForm.reset();
}

// Save appointment edit
async function saveAppointmentEdit() {
    if (!currentEditId) {
        AdminAuth.showNotification('No appointment selected for editing', 'error');
        return;
    }
    
    const formData = new FormData(editAppointmentForm);
    const appointmentData = {
        appointment_date: formData.get('appointment_date'),
        appointment_time: formData.get('appointment_time'),
        status: formData.get('status'),
        notes: formData.get('notes') || null
    };
    
    try {
        const response = await fetch(`${AdminAuth.API_BASE_URL}/admin/appointments/${currentEditId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(appointmentData)
        });
        
        if (!response) return;
        
        if (response.ok) {
            alert('Appointment updated successfully!');
            closeEditModal();
            loadAppointments();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to update appointment');
        }
        
    } catch (error) {
        console.error('Error updating appointment:', error);
        alert(error.message || 'Failed to update appointment');
    }
}

// Cancel appointment
async function cancelAppointment(appointmentId) {
    if (!confirm('Are you sure you want to cancel this appointment?')) {
        return;
    }
    
    try {
        const response = await fetch(`${AdminAuth.API_BASE_URL}/admin/appointments/${appointmentId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: 'cancelled' })
        });
        
        if (!response) return;
        
        if (response.ok) {
            alert('Appointment cancelled successfully!');
            loadAppointments();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to cancel appointment');
        }
        
    } catch (error) {
        console.error('Error cancelling appointment:', error);
        alert(error.message || 'Failed to cancel appointment');
    }
}

// Delete appointment
async function deleteAppointment(appointmentId) {
    if (!confirm('Are you sure you want to delete this appointment? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${AdminAuth.API_BASE_URL}/admin/appointments/${appointmentId}`, {
            method: 'DELETE'
        });
        
        if (!response) return;
        
        if (response.ok) {
            alert('Appointment deleted successfully!');
            loadAppointments();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to delete appointment');
        }
        
    } catch (error) {
        console.error('Error deleting appointment:', error);
        alert(error.message || 'Failed to delete appointment');
    }
}

// Export appointments
function exportAppointments() {
    const csvContent = generateCSV(appointments);
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `appointments_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Generate CSV content
function generateCSV(data) {
    const headers = ['Patient Name', 'Doctor Name', 'Date', 'Time', 'Status', 'Notes'];
    const rows = data.map(apt => [
        apt.patient?.name || '',
        apt.doctor?.name || '',
        apt.appointment_date || '',
        apt.appointment_time || '',
        apt.status || '',
        apt.notes || ''
    ]);
    
    return [headers, ...rows].map(row => 
        row.map(field => `"${field}"`).join(',')
    ).join('\n');
}

// Refresh appointments
function refreshAppointments() {
    loadAppointments();
    alert('Appointments refreshed');
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
        loadAppointments();
    }
}

// Next page
function nextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        loadAppointments();
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
function getStatusClass(status) {
    const statusMap = {
        'pending': 'pending',
        'scheduled': 'pending',
        'confirmed': 'active',
        'completed': 'completed',
        'cancelled': 'inactive'
    };
    return statusMap[status?.toLowerCase()] || 'pending';
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatTime(timeString) {
    if (!timeString) return 'N/A';
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

function showLoading(container) {
    if (!container) return;
    
    const tbody = container.querySelector('tbody');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    Loading appointments...
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

// Add CSS for additional appointment management styles
const additionalStyles = `
    .filters-container {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        align-items: end;
    }
    
    .filter-group {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .filter-group label {
        font-weight: 500;
        color: #374151;
        font-size: 0.9rem;
    }
    
    .filter-group input,
    .filter-group select {
        padding: 0.5rem;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        font-size: 0.9rem;
    }
    
    .filter-actions {
        display: flex;
        gap: 0.5rem;
        align-items: end;
    }
    
    .patient-info,
    .doctor-info {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .patient-avatar {
        width: 32px;
        height: 32px;
        background: #e5e7eb;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #6b7280;
        font-size: 0.9rem;
    }
    
    .patient-name,
    .doctor-name {
        font-weight: 500;
        color: #1f2937;
    }
    
    .patient-email,
    .doctor-specialization {
        font-size: 0.8rem;
        color: #6b7280;
    }
    
    .datetime-info {
        text-align: left;
    }
    
    .appointment-date {
        font-weight: 500;
        color: #1f2937;
    }
    
    .appointment-time {
        font-size: 0.8rem;
        color: #6b7280;
    }
    
    .notes-preview {
        max-width: 200px;
        font-size: 0.9rem;
        color: #6b7280;
    }
    
    .action-buttons {
        display: flex;
        gap: 0.25rem;
    }
    
    .btn-sm {
        padding: 0.25rem 0.5rem;
        font-size: 0.8rem;
    }
    
    .pagination-container {
        display: flex;
        justify-content: center;
        margin-top: 2rem;
    }
    
    .pagination {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .page-info {
        font-weight: 500;
        color: #6b7280;
    }
    
    @media (max-width: 768px) {
        .filters-container {
            grid-template-columns: 1fr;
        }
        
        .filter-actions {
            justify-content: stretch;
        }
        
        .filter-actions .btn {
            flex: 1;
        }
    }
`;

// Add the additional styles to the page
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);
