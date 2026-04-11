// Admin Contact Management JavaScript

// DOM Elements
const messagesTable = document.getElementById('messages-table');
const searchInput = document.getElementById('search-input');
const statusFilter = document.getElementById('status-filter');
const dateFrom = document.getElementById('date-from');
const dateTo = document.getElementById('date-to');
const messageModal = document.getElementById('message-modal');
const messageDetailsContent = document.getElementById('message-details-content');
const unreadCount = document.getElementById('unread-count');

// State
let messages = [];
let currentPage = 1;
let totalPages = 1;
let currentMessageId = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    if (!AdminAuth.isLoggedIn()) {
        window.location.href = '../login.html';
        return;
    }
    
    // Set user info
    setUserInfo();
    
    // Load messages
    loadMessages();
    
    // Setup event listeners
    setupEventListeners();
    
    // Auto-refresh every 30 seconds
    setInterval(loadMessages, 30000);
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
    // Filter changes
    searchInput.addEventListener('input', debounce(applyFilters, 300));
    statusFilter.addEventListener('change', applyFilters);
    dateFrom.addEventListener('change', applyFilters);
    dateTo.addEventListener('change', applyFilters);
}

// Load messages from API
async function loadMessages() {
    try {
        showLoading(messagesTable);
        
        const response = await AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/contact/`);
        if (!response) return;
        
        const data = await response.json();
        messages = data.messages || [];
        
        displayMessages(messages);
        updateUnreadCount();
        updatePagination();
        
    } catch (error) {
        console.error('Error loading messages:', error);
        showError(messagesTable, 'Failed to load messages');
    }
}

// Display messages in table
function displayMessages(messagesList) {
    const tbody = messagesTable.querySelector('tbody');
    
    if (messagesList.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="loading">
                    <i class="fas fa-envelope"></i>
                    No messages found
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = messagesList.map(message => `
        <tr class="${!message.is_read ? 'unread-message' : ''}">
            <td>
                <div class="sender-info">
                    <div class="sender-name">${message.name || 'N/A'}</div>
                    <div class="sender-email">${message.email || 'N/A'}</div>
                    ${message.phone ? `<div class="sender-phone">${message.phone}</div>` : ''}
                </div>
            </td>
            <td>
                <div class="message-subject">
                    ${message.subject || 'No Subject'}
                </div>
            </td>
            <td>
                <div class="message-preview">
                    ${message.message.length > 100 ? 
                        message.message.substring(0, 100) + '...' : 
                        message.message}
                </div>
            </td>
            <td>
                <span class="status-badge ${message.is_read ? 'active' : 'inactive'}">
                    ${message.is_read ? 'Read' : 'Unread'}
                </span>
            </td>
            <td>
                <div class="message-date">
                    ${formatDate(message.created_at)}
                </div>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-outline btn-sm" onclick="viewMessage(${message.id})" title="View">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-warning btn-sm" onclick="toggleReadStatus(${message.id})" title="${message.is_read ? 'Mark Unread' : 'Mark Read'}">
                        <i class="fas fa-${message.is_read ? 'envelope' : 'envelope-open'}"></i>
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteMessage(${message.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Apply filters
function applyFilters() {
    const searchTerm = searchInput.value.toLowerCase();
    const status = statusFilter.value;
    const fromDate = dateFrom.value;
    const toDate = dateTo.value;
    
    let filteredMessages = [...messages];
    
    // Filter by search term
    if (searchTerm) {
        filteredMessages = filteredMessages.filter(message => 
            (message.name && message.name.toLowerCase().includes(searchTerm)) ||
            (message.email && message.email.toLowerCase().includes(searchTerm)) ||
            (message.subject && message.subject.toLowerCase().includes(searchTerm)) ||
            (message.message && message.message.toLowerCase().includes(searchTerm))
        );
    }
    
    // Filter by status
    if (status) {
        const isRead = status === 'read';
        filteredMessages = filteredMessages.filter(message => 
            message.is_read === isRead
        );
    }
    
    // Filter by date range
    if (fromDate) {
        filteredMessages = filteredMessages.filter(message => 
            message.created_at && message.created_at >= fromDate
        );
    }
    
    if (toDate) {
        filteredMessages = filteredMessages.filter(message => 
            message.created_at && message.created_at <= toDate
        );
    }
    
    displayMessages(filteredMessages);
}

// Clear all filters
function clearFilters() {
    searchInput.value = '';
    statusFilter.value = '';
    dateFrom.value = '';
    dateTo.value = '';
    displayMessages(messages);
}

// View message details
function viewMessage(messageId) {
    const message = messages.find(m => m.id === messageId);
    if (!message) {
        AdminAuth.showNotification('Message not found', 'error');
        return;
    }
    
    currentMessageId = messageId;
    
    // Mark as read if unread
    if (!message.is_read) {
        markAsRead(messageId);
    }
    
    messageDetailsContent.innerHTML = `
        <div class="message-details">
            <div class="message-header">
                <div class="message-sender">
                    <h3>${message.name || 'N/A'}</h3>
                    <p class="sender-email">${message.email || 'N/A'}</p>
                    ${message.phone ? `<p class="sender-phone">${message.phone}</p>` : ''}
                </div>
                <div class="message-meta">
                    <div class="message-date">${formatDateTime(message.created_at)}</div>
                    <div class="message-status">
                        <span class="status-badge ${message.is_read ? 'active' : 'inactive'}">
                            ${message.is_read ? 'Read' : 'Unread'}
                        </span>
                    </div>
                </div>
            </div>
            
            <div class="message-content">
                <div class="message-subject">
                    <h4>Subject: ${message.subject || 'No Subject'}</h4>
                </div>
                <div class="message-body">
                    ${message.message.replace(/\n/g, '<br>')}
                </div>
            </div>
        </div>
    `;
    
    // Show modal
    messageModal.style.display = 'flex';
}

// Close message modal
function closeMessageModal() {
    messageModal.style.display = 'none';
    currentMessageId = null;
}

// Mark message as read
async function markAsRead(messageId) {
    try {
        const response = await AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/contact/${messageId}`, {
            method: 'PUT',
            body: JSON.stringify({ is_read: true })
        });
        
        if (response && response.ok) {
            // Update local state
            const message = messages.find(m => m.id === messageId);
            if (message) {
                message.is_read = true;
            }
            updateUnreadCount();
        }
        
    } catch (error) {
        console.error('Error marking message as read:', error);
    }
}

// Toggle read status
async function toggleReadStatus(messageId) {
    const message = messages.find(m => m.id === messageId);
    if (!message) {
        AdminAuth.showNotification('Message not found', 'error');
        return;
    }
    
    const newStatus = !message.is_read;
    const action = newStatus ? 'read' : 'unread';
    
    try {
        const response = await AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/contact/${messageId}`, {
            method: 'PUT',
            body: JSON.stringify({ is_read: newStatus })
        });
        
        if (!response) return;
        
        if (response.ok) {
            AdminAuth.showNotification(`Message marked as ${action}!`, 'success');
            message.is_read = newStatus;
            displayMessages(messages);
            updateUnreadCount();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to mark message as ${action}`);
        }
        
    } catch (error) {
        console.error(`Error marking message as ${action}:`, error);
        AdminAuth.showNotification(error.message || `Failed to mark message as ${action}`, 'error');
    }
}

// Mark all messages as read
async function markAllAsRead() {
    if (!confirm('Are you sure you want to mark all messages as read?')) {
        return;
    }
    
    try {
        const unreadMessages = messages.filter(m => !m.is_read);
        const promises = unreadMessages.map(message => 
            AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/contact/${message.id}`, {
                method: 'PUT',
                body: JSON.stringify({ is_read: true })
            })
        );
        
        await Promise.all(promises);
        
        // Update local state
        messages.forEach(message => {
            message.is_read = true;
        });
        
        AdminAuth.showNotification('All messages marked as read!', 'success');
        displayMessages(messages);
        updateUnreadCount();
        
    } catch (error) {
        console.error('Error marking all messages as read:', error);
        AdminAuth.showNotification('Failed to mark all messages as read', 'error');
    }
}

// Delete message
async function deleteMessage(messageId) {
    if (!confirm('Are you sure you want to delete this message? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/contact/${messageId}`, {
            method: 'DELETE'
        });
        
        if (!response) return;
        
        if (response.ok) {
            AdminAuth.showNotification('Message deleted successfully!', 'success');
            loadMessages();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to delete message');
        }
        
    } catch (error) {
        console.error('Error deleting message:', error);
        AdminAuth.showNotification(error.message || 'Failed to delete message', 'error');
    }
}

// Reply to message
function replyToMessage() {
    if (!currentMessageId) return;
    
    const message = messages.find(m => m.id === currentMessageId);
    if (!message) return;
    
    // Create mailto link
    const subject = `Re: ${message.subject || 'Your inquiry'}`;
    const body = `\n\n--- Original Message ---\nFrom: ${message.name}\nEmail: ${message.email}\nDate: ${formatDateTime(message.created_at)}\n\n${message.message}`;
    
    const mailtoLink = `mailto:${message.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    window.open(mailtoLink);
}

// Update unread count
function updateUnreadCount() {
    const unreadCount = messages.filter(m => !m.is_read).length;
    document.getElementById('unread-count').textContent = unreadCount;
}

// Refresh messages
function refreshMessages() {
    loadMessages();
    AdminAuth.showNotification('Messages refreshed', 'success');
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
        loadMessages();
    }
}

// Next page
function nextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        loadMessages();
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
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
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
                    Loading messages...
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

// Add CSS for additional contact management styles
const additionalStyles = `
    .unread-message {
        background-color: #fef3c7 !important;
        font-weight: 500;
    }
    
    .sender-info {
        text-align: left;
    }
    
    .sender-name {
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.25rem;
    }
    
    .sender-email {
        font-size: 0.9rem;
        color: #6b7280;
        margin-bottom: 0.25rem;
    }
    
    .sender-phone {
        font-size: 0.8rem;
        color: #9ca3af;
    }
    
    .message-subject {
        font-weight: 500;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .message-preview {
        font-size: 0.9rem;
        color: #6b7280;
        line-height: 1.4;
        max-width: 300px;
    }
    
    .message-date {
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
    
    .message-details {
        max-height: 60vh;
        overflow-y: auto;
    }
    
    .message-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .message-sender h3 {
        margin: 0 0 0.5rem 0;
        color: #1f2937;
        font-size: 1.3rem;
    }
    
    .sender-email,
    .sender-phone {
        margin: 0;
        color: #6b7280;
        font-size: 0.9rem;
    }
    
    .message-meta {
        text-align: right;
    }
    
    .message-date {
        font-size: 0.9rem;
        color: #6b7280;
        margin-bottom: 0.5rem;
    }
    
    .message-content {
        margin-top: 1rem;
    }
    
    .message-subject h4 {
        margin: 0 0 1rem 0;
        color: #1f2937;
        font-size: 1.1rem;
    }
    
    .message-body {
        background: #f9fafb;
        padding: 1.5rem;
        border-radius: 8px;
        line-height: 1.6;
        color: #374151;
        white-space: pre-wrap;
    }
    
    @media (max-width: 768px) {
        .message-header {
            flex-direction: column;
            gap: 1rem;
        }
        
        .message-meta {
            text-align: left;
        }
        
        .message-preview {
            max-width: 200px;
        }
    }
`;

// Add the additional styles to the page
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);
