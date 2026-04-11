// Admin Authentication JavaScript

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// DOM Elements
const loginForm = document.getElementById('login-form');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const loginBtn = document.querySelector('.login-btn');
const btnText = document.querySelector('.btn-text');
const btnLoading = document.querySelector('.btn-loading');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Only auto-redirect if we're on the login page
    if (window.location.pathname.includes('login.html')) {
        console.log('Login page loaded, redirecting to dashboard...');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);
    }
    
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Clear session button
    const clearSessionBtn = document.getElementById('clear-session-btn');
    if (clearSessionBtn) {
        clearSessionBtn.addEventListener('click', clearSession);
    }
    
    // Go to dashboard button
    const goToDashboardBtn = document.getElementById('go-to-dashboard-btn');
    if (goToDashboardBtn) {
        goToDashboardBtn.addEventListener('click', goToDashboard);
    }
    
    // Enter key support
    document.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && loginForm) {
            handleLogin(e);
        }
    });
}

// Handle login form submission
async function handleLogin(event) {
    event.preventDefault();
    
    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    
    if (!username || !password) {
        showNotification('Please enter both username and password', 'error');
        return;
    }
    
    try {
        setLoadingState(true);
        
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Login failed');
        }
        
        const data = await response.json();
        
        // Store token and user info
        localStorage.setItem('admin_token', data.access_token);
        localStorage.setItem('admin_user', JSON.stringify(data.user));
        
        showNotification('Login successful! Redirecting...', 'success');
        
        // Redirect to dashboard
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);
        
    } catch (error) {
        console.error('Login error:', error);
        showNotification(error.message || 'Login failed. Please try again.', 'error');
    } finally {
        setLoadingState(false);
    }
}

// Toggle password visibility
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleBtn = document.querySelector('.password-toggle i');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleBtn.classList.remove('fa-eye');
        toggleBtn.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        toggleBtn.classList.remove('fa-eye-slash');
        toggleBtn.classList.add('fa-eye');
    }
}

// Set loading state
function setLoadingState(loading) {
    if (loading) {
        loginBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline-flex';
    } else {
        loginBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
}

// Check if user is logged in
function isLoggedIn() {
    const token = localStorage.getItem('admin_token');
    const user = localStorage.getItem('admin_user');
    return !!(token && user);
}

// Get current user
function getCurrentUser() {
    const userStr = localStorage.getItem('admin_user');
    return userStr ? JSON.parse(userStr) : null;
}

// Get auth token
function getAuthToken() {
    return localStorage.getItem('admin_token');
}

// Clear session function
function clearSession() {
    // Clear all stored authentication data
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
    
    // Show confirmation message
    showNotification('Session cleared! You can now login fresh.', 'success');
    
    // Hide the "Go to Dashboard" button
    const goToDashboardBtn = document.getElementById('go-to-dashboard-btn');
    if (goToDashboardBtn) {
        goToDashboardBtn.style.display = 'none';
    }
    
    // Optional: Clear form fields
    if (usernameInput) usernameInput.value = '';
    if (passwordInput) passwordInput.value = '';
    
    // Focus on username field
    if (usernameInput) usernameInput.focus();
}

// Go to dashboard function
function goToDashboard() {
    window.location.href = 'dashboard.html';
}

// Logout function (disabled - just refresh dashboard)
function logout() {
    // Since authentication is disabled, just refresh the dashboard
    window.location.reload();
}

// Make API request with auth
async function apiRequest(url, options = {}) {
    const token = getAuthToken();
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...options.headers
        }
    };
    
    const response = await fetch(url, { ...defaultOptions, ...options });
    
    // If unauthorized, redirect to login
    if (response.status === 401) {
        logout();
        return null;
    }
    
    return response;
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Hide notification after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Export functions for use in other scripts
window.AdminAuth = {
    API_BASE_URL,
    isLoggedIn,
    getCurrentUser,
    getAuthToken,
    logout,
    apiRequest,
    showNotification
};
