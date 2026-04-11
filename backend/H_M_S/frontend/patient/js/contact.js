// Contact page JavaScript

// DOM Elements
const contactForm = document.getElementById('contact-form');
const faqItems = document.querySelectorAll('.faq-item');

// Initialize the contact page
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    initializeFAQ();
});

// Setup event listeners
function setupEventListeners() {
    // Contact form submission
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactFormSubmission);
    }
    
    // Form validation
    document.querySelectorAll('input[required], textarea[required]').forEach(input => {
        input.addEventListener('blur', validateField);
    });
}

// Handle contact form submission
async function handleContactFormSubmission(event) {
    event.preventDefault();
    
    if (!validateForm()) {
        return;
    }
    
    try {
        // Show loading state
        const submitBtn = event.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        submitBtn.disabled = true;
        
        // Prepare form data
        const formData = new FormData(contactForm);
        const contactData = {
            name: formData.get('name'),
            email: formData.get('email'),
            phone: formData.get('phone') || null,
            subject: formData.get('subject') || null,
            message: formData.get('message')
        };
        
        // Submit contact message
        const response = await fetch(`${HMS.API_BASE_URL}/contact/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(contactData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to send message');
        }
        
        // Show success message
        HMS.showNotification('Message sent successfully! We will get back to you soon.', 'success');
        
        // Reset form
        contactForm.reset();
        
    } catch (error) {
        console.error('Error sending message:', error);
        HMS.showNotification(error.message || 'Failed to send message. Please try again.', 'error');
    } finally {
        // Reset button state
        const submitBtn = event.target.querySelector('button[type="submit"]');
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// Validate form
function validateForm() {
    const requiredFields = contactForm.querySelectorAll('input[required], textarea[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('error');
            isValid = false;
        } else {
            field.classList.remove('error');
        }
    });
    
    // Validate email
    const emailField = document.getElementById('contact-email');
    if (emailField.value && !HMS.validateEmail(emailField.value)) {
        emailField.classList.add('error');
        HMS.showNotification('Please enter a valid email address.', 'error');
        isValid = false;
    }
    
    // Validate phone if provided
    const phoneField = document.getElementById('contact-phone');
    if (phoneField.value && !HMS.validatePhone(phoneField.value)) {
        phoneField.classList.add('error');
        HMS.showNotification('Please enter a valid phone number.', 'error');
        isValid = false;
    }
    
    if (!isValid) {
        HMS.showNotification('Please fill in all required fields correctly.', 'error');
    }
    
    return isValid;
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
        return false;
    }
    
    if (field.type === 'tel' && value && !HMS.validatePhone(value)) {
        field.classList.add('error');
        return false;
    }
    
    return true;
}

// Initialize FAQ functionality
function initializeFAQ() {
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');
        const icon = item.querySelector('.faq-question i');
        
        // Initially hide all answers
        answer.style.display = 'none';
        
        question.addEventListener('click', function() {
            const isOpen = answer.style.display === 'block';
            
            // Close all other FAQ items
            faqItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.querySelector('.faq-answer').style.display = 'none';
                    otherItem.querySelector('.faq-question i').style.transform = 'rotate(0deg)';
                    otherItem.classList.remove('active');
                }
            });
            
            // Toggle current item
            if (isOpen) {
                answer.style.display = 'none';
                icon.style.transform = 'rotate(0deg)';
                item.classList.remove('active');
            } else {
                answer.style.display = 'block';
                icon.style.transform = 'rotate(180deg)';
                item.classList.add('active');
            }
        });
    });
}

// Add CSS for contact page
const contactStyles = `
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
    
    .contact-section {
        padding: 4rem 0;
    }
    
    .contact-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 4rem;
        max-width: 1000px;
        margin: 0 auto;
    }
    
    .contact-info h2 {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #1f2937;
    }
    
    .contact-info p {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    .contact-details {
        display: flex;
        flex-direction: column;
        gap: 2rem;
    }
    
    .contact-item {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .contact-icon {
        width: 50px;
        height: 50px;
        background: #2563eb;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        flex-shrink: 0;
    }
    
    .contact-text h3 {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #1f2937;
    }
    
    .contact-text p {
        color: #6b7280;
        margin-bottom: 0.25rem;
        font-size: 0.95rem;
    }
    
    .contact-form-container {
        background: white;
        border-radius: 10px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .contact-form h2 {
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
    .form-group textarea {
        width: 100%;
        padding: 0.75rem;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        font-size: 1rem;
        transition: border-color 0.3s ease;
        font-family: inherit;
    }
    
    .form-group input:focus,
    .form-group textarea:focus {
        outline: none;
        border-color: #2563eb;
    }
    
    .form-group input.error,
    .form-group textarea.error {
        border-color: #ef4444;
    }
    
    .form-group textarea {
        resize: vertical;
        min-height: 120px;
    }
    
    .map-section {
        background: #f8fafc;
        padding: 4rem 0;
    }
    
    .map-section h2 {
        text-align: center;
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 2rem;
        color: #1f2937;
    }
    
    .map-container {
        max-width: 800px;
        margin: 0 auto;
    }
    
    .map-placeholder {
        width: 100%;
        height: 400px;
        background: #e5e7eb;
        border-radius: 10px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #6b7280;
    }
    
    .map-placeholder i {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .map-placeholder p {
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .map-placeholder small {
        font-size: 0.9rem;
    }
    
    .faq-section {
        padding: 4rem 0;
    }
    
    .faq-section h2 {
        text-align: center;
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 3rem;
        color: #1f2937;
    }
    
    .faq-container {
        max-width: 800px;
        margin: 0 auto;
    }
    
    .faq-item {
        background: white;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        overflow: hidden;
        transition: box-shadow 0.3s ease;
    }
    
    .faq-item:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .faq-item.active {
        box-shadow: 0 4px 8px rgba(37, 99, 235, 0.2);
    }
    
    .faq-question {
        padding: 1.5rem;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #f8fafc;
        transition: background 0.3s ease;
    }
    
    .faq-item.active .faq-question {
        background: #2563eb;
        color: white;
    }
    
    .faq-question h3 {
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0;
    }
    
    .faq-question i {
        font-size: 1.2rem;
        transition: transform 0.3s ease;
    }
    
    .faq-answer {
        padding: 0 1.5rem 1.5rem;
        color: #6b7280;
        line-height: 1.6;
    }
    
    .faq-answer p {
        margin: 0;
    }
    
    @media (max-width: 768px) {
        .contact-container {
            grid-template-columns: 1fr;
            gap: 2rem;
        }
        
        .page-header h1 {
            font-size: 2rem;
        }
        
        .contact-details {
            gap: 1.5rem;
        }
        
        .contact-item {
            flex-direction: column;
            text-align: center;
        }
        
        .contact-icon {
            align-self: center;
        }
        
        .map-placeholder {
            height: 300px;
        }
        
        .faq-question {
            padding: 1rem;
        }
        
        .faq-answer {
            padding: 0 1rem 1rem;
        }
    }
`;

// Add the contact styles to the page
const contactStyleSheet = document.createElement('style');
contactStyleSheet.textContent = contactStyles;
document.head.appendChild(contactStyleSheet);
