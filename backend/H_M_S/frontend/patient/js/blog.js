// Blog page JavaScript

// DOM Elements
const blogGrid = document.getElementById('blog-grid');
const searchInput = document.getElementById('search-input');
const filterBtns = document.querySelectorAll('.filter-btn');
const loadMoreBtn = document.getElementById('load-more-btn');
const loadMoreContainer = document.getElementById('load-more-container');

// State
let allPosts = [];
let filteredPosts = [];
let currentPage = 1;
let isLoading = false;
const postsPerPage = 6;

// Initialize the blog page
document.addEventListener('DOMContentLoaded', function() {
    loadBlogPosts();
    setupEventListeners();
});

// Load blog posts from API
async function loadBlogPosts() {
    try {
        showLoading(blogGrid);
        isLoading = true;
        
        const response = await fetch(`${HMS.API_BASE_URL}/blog/`);
        if (!response.ok) {
            throw new Error('Failed to fetch blog posts');
        }
        
        const data = await response.json();
        allPosts = data.posts;
        filteredPosts = [...allPosts];
        
        displayBlogPosts();
        updateLoadMoreButton();
    } catch (error) {
        console.error('Error loading blog posts:', error);
        showError(blogGrid, 'Failed to load articles. Please try again later.');
    } finally {
        isLoading = false;
    }
}

// Display blog posts in the grid
function displayBlogPosts() {
    if (!blogGrid) return;
    
    blogGrid.innerHTML = '';
    
    const startIndex = 0;
    const endIndex = currentPage * postsPerPage;
    const postsToShow = filteredPosts.slice(startIndex, endIndex);
    
    if (postsToShow.length === 0) {
        showNoResults();
        return;
    }
    
    postsToShow.forEach(post => {
        const blogCard = createBlogCard(post);
        blogGrid.appendChild(blogCard);
    });
    
    // Show load more button if there are more posts
    if (endIndex < filteredPosts.length) {
        loadMoreContainer.style.display = 'block';
    } else {
        loadMoreContainer.style.display = 'none';
    }
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
        viewFullArticle(post);
    });
    
    return card;
}

// View full article (modal or new page)
function viewFullArticle(post) {
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'article-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>${post.title}</h2>
                <button class="close-btn">&times;</button>
            </div>
            <div class="modal-body">
                <div class="article-meta">
                    <span class="article-category">${post.category || 'General'}</span>
                    <span class="article-date">${formatDate(post.created_at)}</span>
                </div>
                <div class="article-content">
                    ${post.content}
                </div>
            </div>
        </div>
    `;
    
    // Add modal styles
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    `;
    
    const modalContent = modal.querySelector('.modal-content');
    modalContent.style.cssText = `
        background: white;
        border-radius: 10px;
        max-width: 800px;
        max-height: 80vh;
        overflow-y: auto;
        position: relative;
    `;
    
    const modalHeader = modal.querySelector('.modal-header');
    modalHeader.style.cssText = `
        padding: 2rem 2rem 1rem;
        border-bottom: 1px solid #e5e7eb;
        display: flex;
        justify-content: space-between;
        align-items: center;
    `;
    
    const modalBody = modal.querySelector('.modal-body');
    modalBody.style.cssText = `
        padding: 2rem;
    `;
    
    const closeBtn = modal.querySelector('.close-btn');
    closeBtn.style.cssText = `
        background: none;
        border: none;
        font-size: 2rem;
        cursor: pointer;
        color: #6b7280;
    `;
    
    // Add close functionality
    closeBtn.addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
    
    document.body.appendChild(modal);
}

// Setup event listeners
function setupEventListeners() {
    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterPosts, 300));
    }
    
    // Category filters
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            filterBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            
            filterPosts();
        });
    });
    
    // Load more button
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', loadMorePosts);
    }
}

// Filter posts based on search and category
function filterPosts() {
    const searchTerm = searchInput.value.toLowerCase().trim();
    const activeFilter = document.querySelector('.filter-btn.active');
    const selectedCategory = activeFilter ? activeFilter.dataset.category : '';
    
    filteredPosts = allPosts.filter(post => {
        const matchesSearch = !searchTerm || 
            post.title.toLowerCase().includes(searchTerm) ||
            post.content.toLowerCase().includes(searchTerm) ||
            (post.category && post.category.toLowerCase().includes(searchTerm));
        
        const matchesCategory = !selectedCategory || 
            post.category === selectedCategory;
        
        return matchesSearch && matchesCategory;
    });
    
    currentPage = 1;
    displayBlogPosts();
    updateLoadMoreButton();
}

// Load more posts
function loadMorePosts() {
    if (isLoading) return;
    
    currentPage++;
    displayBlogPosts();
    updateLoadMoreButton();
}

// Update load more button visibility
function updateLoadMoreButton() {
    if (!loadMoreContainer) return;
    
    const endIndex = currentPage * postsPerPage;
    if (endIndex >= filteredPosts.length) {
        loadMoreContainer.style.display = 'none';
    } else {
        loadMoreContainer.style.display = 'block';
    }
}

// Show no results message
function showNoResults() {
    blogGrid.innerHTML = `
        <div class="no-results">
            <i class="fas fa-search"></i>
            <h3>No articles found</h3>
            <p>Try adjusting your search criteria or category filter</p>
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
            <p>Loading articles...</p>
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

// Add CSS for blog page
const blogStyles = `
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
    
    .filter-section {
        background: #f8fafc;
        padding: 2rem 0;
    }
    
    .filter-container {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        align-items: center;
    }
    
    .search-box {
        position: relative;
        max-width: 400px;
        width: 100%;
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
    
    .category-filters {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .filter-btn {
        padding: 0.5rem 1.5rem;
        border: 2px solid #e5e7eb;
        border-radius: 25px;
        background: white;
        color: #6b7280;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    
    .filter-btn:hover,
    .filter-btn.active {
        border-color: #2563eb;
        background: #2563eb;
        color: white;
    }
    
    .blog-section {
        padding: 4rem 0;
    }
    
    .blog-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 2rem;
        margin-bottom: 3rem;
    }
    
    .blog-card {
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
    }
    
    .blog-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    
    .blog-image {
        width: 100%;
        height: 200px;
        background: #e5e7eb;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        color: #9ca3af;
    }
    
    .blog-content {
        padding: 1.5rem;
    }
    
    .blog-category {
        color: #2563eb;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .blog-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #1f2937;
        line-height: 1.4;
    }
    
    .blog-excerpt {
        color: #6b7280;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    .blog-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.9rem;
        color: #9ca3af;
    }
    
    .load-more-container {
        text-align: center;
        margin-top: 2rem;
    }
    
    .no-results {
        text-align: center;
        padding: 3rem;
        color: #6b7280;
        grid-column: 1 / -1;
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
    
    .article-meta {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
        font-size: 0.9rem;
        color: #6b7280;
    }
    
    .article-category {
        background: #2563eb;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-weight: 500;
    }
    
    .article-content {
        line-height: 1.7;
        color: #374151;
    }
    
    @media (max-width: 768px) {
        .page-header h1 {
            font-size: 2rem;
        }
        
        .blog-grid {
            grid-template-columns: 1fr;
        }
        
        .category-filters {
            flex-direction: column;
            align-items: center;
        }
        
        .filter-btn {
            width: 200px;
        }
    }
`;

// Add the blog styles to the page
const blogStyleSheet = document.createElement('style');
blogStyleSheet.textContent = blogStyles;
document.head.appendChild(blogStyleSheet);
