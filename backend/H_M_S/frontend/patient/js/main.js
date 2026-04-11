// Main JavaScript for Hospital Management System

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// DOM Elements
const navMenu = document.querySelector('.nav-menu');
const hamburger = document.querySelector('.hamburger');
const blogGrid = document.getElementById('blog-grid');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    
    // Only load doctors if we're on a page that has a doctors grid
    const doctorsGrid = document.getElementById('doctors-grid');
    if (doctorsGrid) {
        loadDoctors();
    }
    
    // Only load blog posts if we're on a page that has a blog grid
    if (blogGrid) {
        loadBlogPosts();
    }
    
    initializeScrollEffects();
});

// Navigation functionality
function initializeNavigation() {
    // Mobile menu toggle
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            hamburger.classList.toggle('active');
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                // Close mobile menu if open
                navMenu.classList.remove('active');
                hamburger.classList.remove('active');
            }
        });
    });

    // Active navigation highlighting
    window.addEventListener('scroll', function() {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav-link');
        
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (scrollY >= (sectionTop - 200)) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
}

// Load doctors from API
async function loadDoctors() {
    const doctorsGrid = document.getElementById('doctors-grid');
    if (!doctorsGrid) return;
    
    try {
        showLoading(doctorsGrid);
        
        const response = await fetch(`${API_BASE_URL}/doctors/?limit=3`);
        if (!response.ok) {
            throw new Error('Failed to fetch doctors');
        }
        
        const data = await response.json();
        displayDoctors(data.doctors);
    } catch (error) {
        console.error('Error loading doctors:', error);
        showError(doctorsGrid, 'Failed to load doctors. Please try again later.');
    }
}

// Display doctors in the grid
function displayDoctors(doctors) {
    const doctorsGrid = document.getElementById('doctors-grid');
    if (!doctorsGrid) return;
    
    doctorsGrid.innerHTML = '';
    
    doctors.forEach(doctor => {
        const doctorCard = createDoctorCard(doctor);
        doctorsGrid.appendChild(doctorCard);
    });
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
    `;
    
    // Add click event to book appointment
    card.addEventListener('click', function() {
        window.location.href = `book.html?doctor_id=${doctor.id}`;
    });
    
    return card;
}

// Load blog posts from API
async function loadBlogPosts() {
    try {
        showLoading(blogGrid);
        
        const response = await fetch(`${API_BASE_URL}/blog/?limit=3`);
        if (!response.ok) {
            throw new Error('Failed to fetch blog posts');
        }
        
        const data = await response.json();
        displayBlogPosts(data.posts);
    } catch (error) {
        console.error('Error loading blog posts:', error);
        if (blogGrid) {
            showError(blogGrid, 'Failed to load articles. Please try again later.');
        }
    }
}

// Display blog posts in the grid
function displayBlogPosts(posts) {
    if (!blogGrid) {
        console.log('Blog grid not found, skipping blog posts display');
        return;
    }
    
    blogGrid.innerHTML = '';
    
    posts.forEach(post => {
        const blogCard = createBlogCard(post);
        blogGrid.appendChild(blogCard);
    });
}

// Create blog card element
function createBlogCard(post) {
    const card = document.createElement('div');
    card.className = 'blog-card';
    
    // Truncate content for preview
    const excerpt = post.content.length > 150 ? 
        post.content.substring(0, 150) + '...' : 
        post.content;
    
    card.innerHTML = `
        <div class="blog-image">
            <i class="fas fa-newspaper"></i>
        </div>
        <div class="blog-content">
            <p class="blog-category">${post.category || 'General'}</p>
            <h3 class="blog-title">${post.title}</h3>
            <p class="blog-excerpt">${excerpt}</p>
            <div class="blog-meta">
                <span><i class="fas fa-calendar"></i> ${formatDate(post.created_at)}</span>
                <span><i class="fas fa-eye"></i> Read More</span>
            </div>
        </div>
    `;
    
    // Add click event to view full article
    card.addEventListener('click', function() {
        window.location.href = `blog.html#post-${post.id}`;
    });
    
    return card;
}

// Initialize scroll effects
function initializeScrollEffects() {
    // Add scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.doctor-card, .blog-card, .stat').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// Utility functions
function showLoading(container) {
    if (!container) return;
    
    container.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Loading...</p>
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

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Form validation utilities
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^[\+]?[1-9][\d]{0,15}$/;
    return re.test(phone.replace(/\s/g, ''));
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 5000);
}

// Export functions for use in other scripts
window.HMS = {
    showNotification,
    validateEmail,
    validatePhone,
    API_BASE_URL
};
