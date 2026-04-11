// Admin Blog Management JavaScript

// DOM Elements
const blogTable = document.getElementById('blog-table');
const addBlogForm = document.getElementById('add-blog-form');
const blogForm = document.getElementById('blog-form');
const searchInput = document.getElementById('search-input');
const categoryFilter = document.getElementById('category-filter');
const statusFilter = document.getElementById('status-filter');
const editModal = document.getElementById('edit-modal');
const editBlogForm = document.getElementById('edit-blog-form');

// State
let blogPosts = [];
let currentPage = 1;
let totalPages = 1;
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
    
    // Load blog posts
    loadBlogPosts();
    
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
    // Add blog form
    if (blogForm) {
        blogForm.addEventListener('submit', handleAddBlog);
    }
    
    // Edit blog form
    if (editBlogForm) {
        editBlogForm.addEventListener('submit', handleEditBlog);
    }
    
    // Filter changes
    searchInput.addEventListener('input', debounce(applyFilters, 300));
    categoryFilter.addEventListener('change', applyFilters);
    statusFilter.addEventListener('change', applyFilters);
}

// Load blog posts from API
async function loadBlogPosts() {
    try {
        showLoading(blogTable);
        
        const response = await AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/blog/`);
        if (!response) return;
        
        const data = await response.json();
        blogPosts = data.posts || [];
        
        displayBlogPosts(blogPosts);
        updatePagination();
        
    } catch (error) {
        console.error('Error loading blog posts:', error);
        showError(blogTable, 'Failed to load blog posts');
    }
}

// Display blog posts in table
function displayBlogPosts(postsList) {
    const tbody = blogTable.querySelector('tbody');
    
    if (postsList.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="loading">
                    <i class="fas fa-blog"></i>
                    No blog posts found
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = postsList.map(post => `
        <tr>
            <td>
                <div class="blog-info">
                    <div class="blog-title">${post.title}</div>
                    <div class="blog-excerpt">${post.content.length > 100 ? 
                        post.content.substring(0, 100) + '...' : 
                        post.content}</div>
                </div>
            </td>
            <td>
                <span class="category-badge">${post.category || 'General'}</span>
            </td>
            <td>
                <span class="status-badge ${post.is_published ? 'active' : 'inactive'}">
                    ${post.is_published ? 'Published' : 'Draft'}
                </span>
            </td>
            <td>
                <div class="date-info">
                    ${formatDate(post.created_at)}
                </div>
            </td>
            <td>
                <div class="date-info">
                    ${post.updated_at ? formatDate(post.updated_at) : 'Never'}
                </div>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-outline btn-sm" onclick="editBlogPost(${post.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-warning btn-sm" onclick="togglePublishStatus(${post.id})" title="${post.is_published ? 'Unpublish' : 'Publish'}">
                        <i class="fas fa-${post.is_published ? 'eye-slash' : 'eye'}"></i>
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteBlogPost(${post.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Show add blog form
function showAddBlogForm() {
    addBlogForm.style.display = 'block';
    blogForm.reset();
    addBlogForm.scrollIntoView({ behavior: 'smooth' });
}

// Cancel add blog
function cancelAddBlog() {
    addBlogForm.style.display = 'none';
    blogForm.reset();
}

// Handle add blog form submission
async function handleAddBlog(event) {
    event.preventDefault();
    
    const formData = new FormData(blogForm);
    const blogData = {
        title: formData.get('title'),
        content: formData.get('content'),
        category: formData.get('category'),
        featured_image: formData.get('featured_image') || null,
        is_published: formData.get('is_published') === 'true'
    };
    
    try {
        const response = await AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/blog/`, {
            method: 'POST',
            body: JSON.stringify(blogData)
        });
        
        if (!response) return;
        
        if (response.ok) {
            AdminAuth.showNotification('Blog post added successfully!', 'success');
            blogForm.reset();
            addBlogForm.style.display = 'none';
            loadBlogPosts();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to add blog post');
        }
        
    } catch (error) {
        console.error('Error adding blog post:', error);
        AdminAuth.showNotification(error.message || 'Failed to add blog post', 'error');
    }
}

// Edit blog post
function editBlogPost(postId) {
    const post = blogPosts.find(p => p.id === postId);
    if (!post) {
        AdminAuth.showNotification('Blog post not found', 'error');
        return;
    }
    
    currentEditId = postId;
    
    // Populate form
    document.getElementById('edit-blog-id').value = post.id;
    document.getElementById('edit-blog-title').value = post.title;
    document.getElementById('edit-blog-content').value = post.content;
    document.getElementById('edit-blog-category').value = post.category || '';
    document.getElementById('edit-blog-image').value = post.featured_image || '';
    document.getElementById('edit-blog-published').value = post.is_published.toString();
    
    // Show modal
    editModal.style.display = 'flex';
}

// Close edit modal
function closeEditModal() {
    editModal.style.display = 'none';
    currentEditId = null;
    editBlogForm.reset();
}

// Save blog edit
async function saveBlogEdit() {
    if (!currentEditId) {
        AdminAuth.showNotification('No blog post selected for editing', 'error');
        return;
    }
    
    const formData = new FormData(editBlogForm);
    const blogData = {
        title: formData.get('title'),
        content: formData.get('content'),
        category: formData.get('category'),
        featured_image: formData.get('featured_image') || null,
        is_published: formData.get('is_published') === 'true'
    };
    
    try {
        const response = await AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/blog/${currentEditId}`, {
            method: 'PUT',
            body: JSON.stringify(blogData)
        });
        
        if (!response) return;
        
        if (response.ok) {
            AdminAuth.showNotification('Blog post updated successfully!', 'success');
            closeEditModal();
            loadBlogPosts();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to update blog post');
        }
        
    } catch (error) {
        console.error('Error updating blog post:', error);
        AdminAuth.showNotification(error.message || 'Failed to update blog post', 'error');
    }
}

// Toggle publish status
async function togglePublishStatus(postId) {
    const post = blogPosts.find(p => p.id === postId);
    if (!post) {
        AdminAuth.showNotification('Blog post not found', 'error');
        return;
    }
    
    const newStatus = !post.is_published;
    const action = newStatus ? 'publish' : 'unpublish';
    
    if (!confirm(`Are you sure you want to ${action} this blog post?`)) {
        return;
    }
    
    try {
        const response = await AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/blog/${postId}`, {
            method: 'PUT',
            body: JSON.stringify({ is_published: newStatus })
        });
        
        if (!response) return;
        
        if (response.ok) {
            AdminAuth.showNotification(`Blog post ${action}ed successfully!`, 'success');
            loadBlogPosts();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to ${action} blog post`);
        }
        
    } catch (error) {
        console.error(`Error ${action}ing blog post:`, error);
        AdminAuth.showNotification(error.message || `Failed to ${action} blog post`, 'error');
    }
}

// Delete blog post
async function deleteBlogPost(postId) {
    if (!confirm('Are you sure you want to delete this blog post? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await AdminAuth.apiRequest(`${AdminAuth.API_BASE_URL}/admin/blog/${postId}`, {
            method: 'DELETE'
        });
        
        if (!response) return;
        
        if (response.ok) {
            AdminAuth.showNotification('Blog post deleted successfully!', 'success');
            loadBlogPosts();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to delete blog post');
        }
        
    } catch (error) {
        console.error('Error deleting blog post:', error);
        AdminAuth.showNotification(error.message || 'Failed to delete blog post', 'error');
    }
}

// Apply filters
function applyFilters() {
    const searchTerm = searchInput.value.toLowerCase();
    const category = categoryFilter.value;
    const status = statusFilter.value;
    
    let filteredPosts = [...blogPosts];
    
    // Filter by search term
    if (searchTerm) {
        filteredPosts = filteredPosts.filter(post => 
            (post.title && post.title.toLowerCase().includes(searchTerm)) ||
            (post.content && post.content.toLowerCase().includes(searchTerm))
        );
    }
    
    // Filter by category
    if (category) {
        filteredPosts = filteredPosts.filter(post => 
            post.category && post.category.toLowerCase() === category.toLowerCase()
        );
    }
    
    // Filter by status
    if (status) {
        const isPublished = status === 'published';
        filteredPosts = filteredPosts.filter(post => 
            post.is_published === isPublished
        );
    }
    
    displayBlogPosts(filteredPosts);
}

// Clear all filters
function clearFilters() {
    searchInput.value = '';
    categoryFilter.value = '';
    statusFilter.value = '';
    displayBlogPosts(blogPosts);
}

// Refresh blog posts
function refreshBlogPosts() {
    loadBlogPosts();
    AdminAuth.showNotification('Blog posts refreshed', 'success');
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
        loadBlogPosts();
    }
}

// Next page
function nextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        loadBlogPosts();
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

function showLoading(container) {
    if (!container) return;
    
    const tbody = container.querySelector('tbody');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    Loading blog posts...
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

// Add CSS for additional blog management styles
const additionalStyles = `
    .blog-info {
        max-width: 300px;
    }
    
    .blog-title {
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }
    
    .blog-excerpt {
        font-size: 0.9rem;
        color: #6b7280;
        line-height: 1.4;
    }
    
    .category-badge {
        background: #dbeafe;
        color: #1e40af;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .date-info {
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
    
    .form-container {
        margin-bottom: 2rem;
    }
    
    .modal {
        max-width: 800px;
    }
    
    .modal-body {
        max-height: 70vh;
        overflow-y: auto;
    }
    
    .form-group textarea {
        resize: vertical;
        min-height: 200px;
    }
    
    @media (max-width: 768px) {
        .blog-info {
            max-width: 200px;
        }
        
        .blog-title {
            font-size: 0.9rem;
        }
        
        .blog-excerpt {
            font-size: 0.8rem;
        }
    }
`;

// Add the additional styles to the page
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);
