// Appointment booking JavaScript

// DOM Elements
const appointmentForm = document.getElementById('appointment-form');
const doctorSelect = document.getElementById('doctor-select');
const appointmentDate = document.getElementById('appointment-date');
const timeSlotsContainer = document.getElementById('time-slots-container');
const timeNextBtn = document.getElementById('time-next-btn');

// State
let currentStep = 1;
let selectedTimeSlot = null;
let availableTimeSlots = [];
let doctors = [];

// Initialize the booking page
document.addEventListener('DOMContentLoaded', function() {
    loadDoctors();
    setupEventListeners();
    setMinDate();
});

// Load doctors from API
async function loadDoctors() {
    try {
        const response = await fetch(`${HMS.API_BASE_URL}/doctors/`);
        if (!response.ok) {
            throw new Error('Failed to fetch doctors');
        }
        
        const data = await response.json();
        doctors = data.doctors;
        
        // Populate doctor select
        doctorSelect.innerHTML = '<option value="">Choose a doctor...</option>';
        doctors.forEach(doctor => {
            const option = document.createElement('option');
            option.value = doctor.id;
            option.textContent = `${doctor.name} - ${doctor.specialization}`;
            doctorSelect.appendChild(option);
        });
        
        // Check if doctor_id is in URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const doctorId = urlParams.get('doctor_id');
        if (doctorId) {
            doctorSelect.value = doctorId;
            updateSummary();
        }
    } catch (error) {
        console.error('Error loading doctors:', error);
        HMS.showNotification('Failed to load doctors. Please refresh the page.', 'error');
    }
}

// Setup event listeners
function setupEventListeners() {
    // Doctor selection change
    doctorSelect.addEventListener('change', function() {
        updateSummary();
        if (appointmentDate.value) {
            loadTimeSlots();
        }
    });
    
    // Date selection change
    appointmentDate.addEventListener('change', function() {
        updateSummary();
        if (doctorSelect.value) {
            loadTimeSlots();
        }
    });
    
    // Form submission
    appointmentForm.addEventListener('submit', handleFormSubmission);
    
    // Input validation
    document.querySelectorAll('input[required], select[required]').forEach(input => {
        input.addEventListener('blur', validateField);
    });
}

// Set minimum date to today
function setMinDate() {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const year = tomorrow.getFullYear();
    const month = String(tomorrow.getDate() + 1).padStart(2, '0');
    const day = String(tomorrow.getDate()).padStart(2, '0');
    
    appointmentDate.min = `${year}-${month}-${day}`;
}

// Load available time slots
async function loadTimeSlots() {
    const doctorId = doctorSelect.value;
    const date = appointmentDate.value;
    
    if (!doctorId || !date) {
        return;
    }
    
    try {
        if (timeSlotsContainer) {
            showLoading(timeSlotsContainer);
        }
        
        const response = await fetch(`${HMS.API_BASE_URL}/appointments/slots?doctor_id=${doctorId}&appointment_date=${date}`);
        if (!response.ok) {
            throw new Error('Failed to fetch time slots');
        }
        
        const slots = await response.json();
        availableTimeSlots = slots;
        displayTimeSlots(slots);
    } catch (error) {
        console.error('Error loading time slots:', error);
        if (timeSlotsContainer) {
            showError(timeSlotsContainer, 'Failed to load time slots. Please try again.');
        }
    }
}

// Display time slots
function displayTimeSlots(slots) {
    if (!timeSlotsContainer) {
        console.error('Cannot display time slots: container is null');
        return;
    }
    
    timeSlotsContainer.innerHTML = '';
    
    if (slots.length === 0) {
        timeSlotsContainer.innerHTML = `
            <div class="no-slots">
                <i class="fas fa-calendar-times"></i>
                <p>No available time slots for this date. Please select another date.</p>
            </div>
        `;
        return;
    }
    
    slots.forEach(slot => {
        const slotElement = createTimeSlotElement(slot);
        timeSlotsContainer.appendChild(slotElement);
    });
}

// Create time slot element
function createTimeSlotElement(slot) {
    const slotDiv = document.createElement('div');
    slotDiv.className = `time-slot ${slot.is_available ? 'available' : 'unavailable'}`;
    
    const timeString = new Date(`2000-01-01T${slot.time}`).toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
    
    slotDiv.innerHTML = `
        <div class="slot-time">${timeString}</div>
        <div class="slot-status">${slot.is_available ? 'Available' : 'Booked'}</div>
    `;
    
    if (slot.is_available) {
        slotDiv.addEventListener('click', function() {
            selectTimeSlot(slot, slotDiv);
        });
    }
    
    return slotDiv;
}

// Select time slot
function selectTimeSlot(slot, element) {
    // Remove previous selection
    document.querySelectorAll('.time-slot.selected').forEach(el => {
        el.classList.remove('selected');
    });
    
    // Select current slot
    element.classList.add('selected');
    selectedTimeSlot = slot;
    
    // Update summary
    updateSummary();
    
    // Enable next button
    timeNextBtn.disabled = false;
}

// Next step
function nextStep() {
    if (!validateCurrentStep()) {
        return;
    }
    
    // Hide current step
    document.getElementById(`step-${currentStep}`).classList.remove('active');
    
    // Show next step
    currentStep++;
    document.getElementById(`step-${currentStep}`).classList.add('active');
    
    // Update summary
    updateSummary();
    
    // Load time slots if moving to step 3
    if (currentStep === 3) {
        loadTimeSlots();
    }
}

// Previous step
function prevStep() {
    // Hide current step
    document.getElementById(`step-${currentStep}`).classList.remove('active');
    
    // Show previous step
    currentStep--;
    document.getElementById(`step-${currentStep}`).classList.add('active');
}

// Validate current step
function validateCurrentStep() {
    const currentStepElement = document.getElementById(`step-${currentStep}`);
    const requiredFields = currentStepElement.querySelectorAll('input[required], select[required]');
    
    for (let field of requiredFields) {
        if (!field.value.trim()) {
            field.classList.add('error');
            HMS.showNotification('Please fill in all required fields.', 'error');
            return false;
        } else {
            field.classList.remove('error');
        }
    }
    
    // Additional validation for step 3
    if (currentStep === 3 && !selectedTimeSlot) {
        HMS.showNotification('Please select a time slot.', 'error');
        return false;
    }
    
    return true;
}

// Validate individual field
function validateField(event) {
    const field = event.target;
    const value = field.value.trim();
    
    // Remove error class
    field.classList.remove('error');
    
    // Validate based on field type
    if (field.type === 'email' && value && !HMS.validateEmail(value)) {
        field.classList.add('error');
        HMS.showNotification('Please enter a valid email address.', 'error');
        return false;
    }
    
    if (field.type === 'tel' && value && !HMS.validatePhone(value)) {
        field.classList.add('error');
        HMS.showNotification('Please enter a valid phone number.', 'error');
        return false;
    }
    
    return true;
}

// Update summary
function updateSummary() {
    const formData = new FormData(appointmentForm);
    
    // Update patient info
    document.getElementById('summary-name').textContent = formData.get('name') || '-';
    document.getElementById('summary-email').textContent = formData.get('email') || '-';
    document.getElementById('summary-phone').textContent = formData.get('phone') || '-';
    
    // Update doctor info
    const doctorId = formData.get('doctor_id');
    if (doctorId) {
        const doctor = doctors.find(d => d.id == doctorId);
        document.getElementById('summary-doctor').textContent = doctor ? doctor.name : '-';
    } else {
        document.getElementById('summary-doctor').textContent = '-';
    }
    
    // Update date
    const date = formData.get('appointment_date');
    if (date) {
        const dateObj = new Date(date);
        document.getElementById('summary-date').textContent = dateObj.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } else {
        document.getElementById('summary-date').textContent = '-';
    }
    
    // Update time
    if (selectedTimeSlot) {
        const timeString = new Date(`2000-01-01T${selectedTimeSlot.time}`).toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
        document.getElementById('summary-time').textContent = timeString;
    } else {
        document.getElementById('summary-time').textContent = '-';
    }
}

// Handle form submission
async function handleFormSubmission(event) {
    event.preventDefault();
    
    if (!validateCurrentStep()) {
        return;
    }
    
    // Show loading state
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Booking...';
    submitBtn.disabled = true;
    
    try {
        
        // Prepare appointment data
        const formData = new FormData(appointmentForm);
        const appointmentData = {
            patient_id: formData.get('email'), // Using email as patient identifier
            doctor_id: parseInt(formData.get('doctor_id')),
            appointment_date: formData.get('appointment_date'),
            appointment_time: selectedTimeSlot.time,
            notes: formData.get('notes') || ''
        };
        
        // Submit appointment
        const response = await fetch(`${HMS.API_BASE_URL}/appointments/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(appointmentData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to book appointment');
        }
        
        const result = await response.json();
        
        // Show success message
        HMS.showNotification('Appointment booked successfully!', 'success');
        
        // Redirect to confirmation page or home
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 2000);
        
    } catch (error) {
        console.error('Error booking appointment:', error);
        HMS.showNotification(error.message || 'Failed to book appointment. Please try again.', 'error');
    } finally {
        // Reset button state
        const submitBtn = event.target.querySelector('button[type="submit"]');
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// Utility functions
function showLoading(container) {
    if (!container) {
        console.error('Cannot show loading: container is null');
        return;
    }
    
    container.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Loading available time slots...</p>
        </div>
    `;
}

function showError(container, message) {
    if (!container) {
        console.error('Cannot show error: container is null');
        return;
    }
    
    container.innerHTML = `
        <div class="loading">
            <i class="fas fa-exclamation-triangle"></i>
            <p>${message}</p>
        </div>
    `;
}

// Add CSS for booking page
const bookingStyles = `
    .page-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 120px 0 80px;
        text-align: center;
    }
    
    .page-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .page-header p {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    .booking-section {
        padding: 4rem 0;
        background: #f8fafc;
    }
    
    .booking-container {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 3rem;
        max-width: 1000px;
        margin: 0 auto;
    }
    
    .booking-form-container {
        background: white;
        border-radius: 10px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .form-step {
        display: none;
    }
    
    .form-step.active {
        display: block;
    }
    
    .form-step h2 {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 2rem;
        color: #1f2937;
    }
    
    .form-group {
        margin-bottom: 1.5rem;
    }
    
    .form-group label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: #374151;
    }
    
    .form-group input,
    .form-group select,
    .form-group textarea {
        width: 100%;
        padding: 0.75rem;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }
    
    .form-group input:focus,
    .form-group select:focus,
    .form-group textarea:focus {
        outline: none;
        border-color: #2563eb;
    }
    
    .form-group input.error,
    .form-group select.error,
    .form-group textarea.error {
        border-color: #ef4444;
    }
    
    .form-actions {
        display: flex;
        gap: 1rem;
        justify-content: flex-end;
        margin-top: 2rem;
    }
    
    .time-slots-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .time-slot {
        padding: 1rem;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .time-slot.available {
        border-color: #10b981;
        color: #10b981;
    }
    
    .time-slot.available:hover {
        background: #10b981;
        color: white;
    }
    
    .time-slot.selected {
        background: #2563eb;
        border-color: #2563eb;
        color: white;
    }
    
    .time-slot.unavailable {
        border-color: #ef4444;
        color: #ef4444;
        cursor: not-allowed;
        opacity: 0.5;
    }
    
    .slot-time {
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .slot-status {
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    .no-slots {
        text-align: center;
        padding: 2rem;
        color: #6b7280;
    }
    
    .no-slots i {
        font-size: 3rem;
        margin-bottom: 1rem;
        color: #d1d5db;
    }
    
    .booking-summary {
        background: white;
        border-radius: 10px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        height: fit-content;
    }
    
    .booking-summary h3 {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        color: #1f2937;
    }
    
    .summary-content {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .summary-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        border-bottom: 1px solid #f3f4f6;
    }
    
    .summary-item:last-child {
        border-bottom: none;
    }
    
    .summary-item .label {
        font-weight: 500;
        color: #6b7280;
    }
    
    .summary-item .value {
        color: #1f2937;
        text-align: right;
    }
    
    @media (max-width: 768px) {
        .booking-container {
            grid-template-columns: 1fr;
            gap: 2rem;
        }
        
        .page-header h1 {
            font-size: 2rem;
        }
        
        .time-slots-container {
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
        }
        
        .form-actions {
            flex-direction: column;
        }
    }
`;

// Add the booking styles to the page
const bookingStyleSheet = document.createElement('style');
bookingStyleSheet.textContent = bookingStyles;
document.head.appendChild(bookingStyleSheet);
