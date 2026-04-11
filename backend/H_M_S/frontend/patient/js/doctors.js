// Doctors page JavaScript

// Prevent multiple script execution using IIFE
(function() {
    'use strict';
    
    // Check if already initialized
    if (window.doctorsPageInitialized) {
        console.log('Doctors page already initialized, skipping...');
        return;
    }
    window.doctorsPageInitialized = true;

    // DOM Elements
    const doctorsGrid = document.getElementById('doctors-grid');
    const searchInput = document.getElementById('search-input');
    const specializationFilter = document.getElementById('specialization-filter');
    const clearFiltersBtn = document.getElementById('clear-filters');
    const loadMoreBtn = document.getElementById('load-more-btn');
    const loadMoreContainer = document.getElementById('load-more-container');

    // State
    let allDoctors = [];
    let filteredDoctors = [];
    let currentPage = 1;
    let isLoading = false;
    const doctorsPerPage = 6;

    // Initialize the doctors page
    document.addEventListener('DOMContentLoaded', function() {
        loadDoctors();
        loadSpecializations();
        setupEventListeners();
    });

    // Load doctors from API
    async function loadDoctors() {
        try {
            showLoading(doctorsGrid);
            isLoading = true;
            
            const response = await fetch(`${HMS.API_BASE_URL}/doctors/`);
            if (!response.ok) {
                throw new Error('Failed to fetch doctors');
            }
            
            const data = await response.json();
            allDoctors = data.doctors;
            filteredDoctors = [...allDoctors];
            
            displayDoctors();
            updateLoadMoreButton();
        } catch (error) {
            console.error('Error loading doctors:', error);
            showError(doctorsGrid, 'Failed to load doctors. Please try again later.');
        } finally {
            isLoading = false;
        }
    }

    // Load specializations for filter
    async function loadSpecializations() {
        try {
            const response = await fetch(`${HMS.API_BASE_URL}/doctors/specializations/list`);
            if (!response.ok) {
                throw new Error('Failed to fetch specializations');
            }
            
            const specializations = await response.json();
            
            // Clear existing options except the first one
            specializationFilter.innerHTML = '<option value="">All Specializations</option>';
            
            specializations.forEach(spec => {
                const option = document.createElement('option');
                option.value = spec;
                option.textContent = spec;
                specializationFilter.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading specializations:', error);
        }
    }

    // Display doctors in the grid
    function displayDoctors() {
        if (!doctorsGrid) return;
        
        doctorsGrid.innerHTML = '';
        
        const startIndex = 0;
        const endIndex = currentPage * doctorsPerPage;
        const doctorsToShow = filteredDoctors.slice(startIndex, endIndex);
        
        if (doctorsToShow.length === 0) {
            showNoResults();
            return;
        }
        
        doctorsToShow.forEach(doctor => {
            const doctorCard = createDoctorCard(doctor);
            doctorsGrid.appendChild(doctorCard);
        });
        
        // Show load more button if there are more doctors
        if (endIndex < filteredDoctors.length) {
            loadMoreContainer.style.display = 'block';
        } else {
            loadMoreContainer.style.display = 'none';
        }
    }

    // Create doctor card element
    function createDoctorCard(doctor) {
        const card = document.createElement('div');
        card.className = 'doctor-card';
        
        card.innerHTML = `
            <div class="doctor-image">
                <i class="fas fa-user-md"></i>
            </div>
            <h3 class="doctor-name">${doctor.name}</h3>
            <p class="doctor-specialization">${doctor.specialization}</p>
            <p class="doctor-education">${doctor.education}</p>
            <p class="doctor-experience">${doctor.experience} years experience</p>
            <div class="doctor-actions">
                <button class="btn btn-primary btn-small" onclick="bookWithDoctor(${doctor.id})">
                    <i class="fas fa-calendar-plus"></i> Book Appointment
                </button>
            </div>
        `;
        
        return card;
    }

    // Book appointment with specific doctor
    function bookWithDoctor(doctorId) {
        window.location.href = `book.html?doctor_id=${doctorId}`;
    }

    // Setup event listeners
    function setupEventListeners() {
        // Search functionality
        if (searchInput) {
            searchInput.addEventListener('input', debounce(filterDoctors, 300));
        }
        
        // Specialization filter
        if (specializationFilter) {
            specializationFilter.addEventListener('change', filterDoctors);
        }
        
        // Clear filters
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', clearFilters);
        }
        
        // Load more button
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', loadMoreDoctors);
        }
    }

    // Filter doctors based on search and specialization
    function filterDoctors() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const selectedSpecialization = specializationFilter.value;
        
        filteredDoctors = allDoctors.filter(doctor => {
            const matchesSearch = !searchTerm || 
                doctor.name.toLowerCase().includes(searchTerm) ||
                doctor.specialization.toLowerCase().includes(searchTerm) ||
                doctor.education.toLowerCase().includes(searchTerm);
            
            const matchesSpecialization = !selectedSpecialization || 
                doctor.specialization === selectedSpecialization;
            
            return matchesSearch && matchesSpecialization;
        });
        
        currentPage = 1;
        displayDoctors();
        updateLoadMoreButton();
    }

    // Clear all filters
    function clearFilters() {
        searchInput.value = '';
        specializationFilter.value = '';
        filteredDoctors = [...allDoctors];
        currentPage = 1;
        displayDoctors();
        updateLoadMoreButton();
    }

    // Load more doctors
    function loadMoreDoctors() {
        if (isLoading) return;
        
        currentPage++;
        displayDoctors();
        updateLoadMoreButton();
    }

    // Update load more button visibility
    function updateLoadMoreButton() {
        if (!loadMoreContainer) return;
        
        const endIndex = currentPage * doctorsPerPage;
        if (endIndex >= filteredDoctors.length) {
            loadMoreContainer.style.display = 'none';
        } else {
            loadMoreContainer.style.display = 'block';
        }
    }

    // Show no results message
    function showNoResults() {
        doctorsGrid.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search"></i>
                <h3>No doctors found</h3>
                <p>Try adjusting your search criteria or clear the filters</p>
                <button class="btn btn-outline" onclick="clearFilters()">Clear Filters</button>
            </div>
        `;
        loadMoreContainer.style.display = 'none';
    }

    // Utility functions
    function showLoading(container) {
        if (!container) return;
        
        container.innerHTML = `
            <div class="loading">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Loading doctors...</p>
            </div>
        `;
    }

    function showError(container, message) {
        if (!container) return;
        
        container.innerHTML = `
            <div class="loading">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
            </div>
        `;
    }

    // Debounce function for search
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

    // Add CSS for additional styles
    const additionalStyles = `
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
        
        .search-section {
            background: #f8fafc;
            padding: 2rem 0;
        }
        
        .search-container {
            display: flex;
            gap: 1rem;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .search-box {
            flex: 1;
            min-width: 300px;
            position: relative;
        }
        
        .search-box i {
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            color: #6b7280;
        }
        
        .search-box input {
            width: 100%;
            padding: 0.75rem 1rem 0.75rem 3rem;
            border: 2px solid #e5e7eb;
            border-radius: 25px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        .search-box input:focus {
            outline: none;
            border-color: #2563eb;
        }
        
        .filter-container {
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        
        .filter-container select {
            padding: 0.75rem 1rem;
            border: 2px solid #e5e7eb;
            border-radius: 25px;
            font-size: 1rem;
            background: white;
            min-width: 200px;
        }
        
        .doctors-section {
            padding: 4rem 0;
        }
        
        .doctors-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .doctor-card {
            background: white;
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .doctor-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        
        .doctor-actions {
            margin-top: 1.5rem;
        }
        
        .btn-small {
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
        }
        
        .load-more-container {
            text-align: center;
            margin-top: 2rem;
        }
        
        .no-results {
            text-align: center;
            padding: 3rem;
            color: #6b7280;
        }
        
        .no-results i {
            font-size: 4rem;
            margin-bottom: 1rem;
            color: #d1d5db;
        }
        
        .no-results h3 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #374151;
        }
        
        .cta-section {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            text-align: center;
            padding: 4rem 0;
        }
        
        .cta-content h2 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }
        
        .cta-content p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        
        @media (max-width: 768px) {
            .search-container {
                flex-direction: column;
                align-items: stretch;
            }
            
            .search-box {
                min-width: auto;
            }
            
            .filter-container {
                justify-content: center;
            }
            
            .doctors-grid {
                grid-template-columns: 1fr;
            }
            
            .page-header h1 {
                font-size: 2rem;
            }
        }
    `;

    // Add the additional styles to the page
    const styleSheet = document.createElement('style');
    styleSheet.textContent = additionalStyles;
    document.head.appendChild(styleSheet);

    // Make functions globally available
    window.bookWithDoctor = bookWithDoctor;
    window.clearFilters = clearFilters;

})();