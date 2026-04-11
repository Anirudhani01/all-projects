// Main Application Controller
class RestaurantApp {
    constructor() {
        this.currentPage = 'tables';
        this.currentOrder = null;
        this.init();
    }

    init() {
        console.log('Initializing RestaurantApp...');
        this.setupEventListeners();
        this.updateCurrentTime();
        console.log('Loading initial page...');
        this.loadCurrentPage();
        
        // Update time every second
        setInterval(() => this.updateCurrentTime(), 1000);
        
        // Auto-refresh data every 30 seconds
        setInterval(() => this.refreshCurrentPage(), 30000);
        console.log('RestaurantApp initialized successfully');
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigateToPage(e.target.closest('[data-page]').dataset.page);
            });
        });

        // Search functionality
        const menuSearch = document.getElementById('menu-search');
        if (menuSearch) {
            menuSearch.addEventListener('input', (e) => {
                this.handleMenuSearch(e.target.value);
            });
        }

        // Payment modal events
        const payOrderBtn = document.getElementById('pay-order-btn');
        if (payOrderBtn) {
            payOrderBtn.addEventListener('click', () => {
                this.showPaymentModal();
            });
        }

        const confirmPaymentBtn = document.getElementById('confirm-payment-btn');
        if (confirmPaymentBtn) {
            confirmPaymentBtn.addEventListener('click', () => {
                this.processPayment();
            });
        }

        // Modal cleanup on hidden events
        const paymentModal = document.getElementById('paymentModal');
        if (paymentModal) {
            paymentModal.addEventListener('hidden.bs.modal', () => {
                this.cleanupModals();
            });
        }

        const orderModal = document.getElementById('tableOrderModal');
        if (orderModal) {
            orderModal.addEventListener('hidden.bs.modal', () => {
                this.cleanupModals();
            });
        }
    }

    navigateToPage(page) {
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-page="${page}"]`).classList.add('active');

        // Hide all pages
        document.querySelectorAll('.page-content').forEach(pageEl => {
            pageEl.classList.add('d-none');
        });

        // Show target page
        document.getElementById(`${page}-page`).classList.remove('d-none');

        // Load page data
        this.currentPage = page;
        this.loadCurrentPage();
    }

    async loadCurrentPage() {
        try {
            console.log('Loading current page:', this.currentPage);
            switch (this.currentPage) {
                case 'tables':
                    console.log('Loading tables page...');
                    await TablesManager.loadTables();
                    break;
                case 'menu':
                    console.log('Loading menu page...');
                    await MenuManager.loadMenu();
                    break;
                case 'orders':
                    console.log('Loading orders page...');
                    await OrdersManager.loadOrders();
                    break;
                case 'admin':
                    console.log('Loading admin page...');
                    await AdminManager.loadDashboard();
                    break;
            }
            console.log('Page loaded successfully');
        } catch (error) {
            console.error('Error loading page:', error);
            this.showError('Failed to load page data', error);
        }
    }

    async refreshCurrentPage() {
        await this.loadCurrentPage();
    }

    updateCurrentTime() {
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            const now = new Date();
            timeElement.textContent = now.toLocaleTimeString();
        }
    }

    async handleMenuSearch(searchTerm) {
        try {
            await MenuManager.searchMenu(searchTerm);
        } catch (error) {
            this.showError('Search failed', error);
        }
    }

    showPaymentModal() {
        if (!this.currentOrder) return;

        const paymentTotal = document.getElementById('payment-total');
        if (paymentTotal) {
            paymentTotal.textContent = this.currentOrder.total_amount.toFixed(2);
        }

        const paymentModal = new bootstrap.Modal(document.getElementById('paymentModal'));
        paymentModal.show();
    }

    async processPayment() {
        if (!this.currentOrder) return;

        const paymentMethod = document.getElementById('payment-method').value;
        
        try {
            // Show loading state
            const confirmBtn = document.getElementById('confirm-payment-btn');
            const originalText = confirmBtn.innerHTML;
            confirmBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Processing...';
            confirmBtn.disabled = true;
            
            await api.payOrder(this.currentOrder.id, paymentMethod);
            
            // Close payment modal first
            const paymentModal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
            if (paymentModal) {
                paymentModal.hide();
            } else {
                // Fallback: manually hide the modal
                const paymentModalEl = document.getElementById('paymentModal');
                if (paymentModalEl) {
                    paymentModalEl.classList.remove('show');
                    paymentModalEl.style.display = 'none';
                }
            }
            
            // Close order modal
            const orderModal = bootstrap.Modal.getInstance(document.getElementById('tableOrderModal'));
            if (orderModal) {
                orderModal.hide();
            } else {
                // Fallback: manually hide the modal
                const orderModalEl = document.getElementById('tableOrderModal');
                if (orderModalEl) {
                    orderModalEl.classList.remove('show');
                    orderModalEl.style.display = 'none';
                }
            }
            
            // Clear current order
            this.currentOrder = null;
            
            // Clean up any modal artifacts
            this.cleanupModals();
            
            // Refresh tables after a short delay to ensure modals are closed
            setTimeout(async () => {
                try {
                    await TablesManager.loadTables();
                    this.showSuccess('Payment processed successfully!');
                } catch (refreshError) {
                    console.error('Error refreshing tables:', refreshError);
                    this.showError('Payment successful but failed to refresh tables');
                }
            }, 300);
            
        } catch (error) {
            this.showError('Payment failed', error);
        } finally {
            // Reset button state
            const confirmBtn = document.getElementById('confirm-payment-btn');
            if (confirmBtn) {
                confirmBtn.innerHTML = '<i class="bi bi-check-circle"></i> Confirm Payment';
                confirmBtn.disabled = false;
            }
        }
    }

    setCurrentOrder(order) {
        this.currentOrder = order;
    }

    cleanupModals() {
        // Remove any lingering modal backdrops
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());
        
        // Remove modal-open class from body
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        
        // Ensure all modals are properly hidden
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.classList.remove('show');
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
        });
    }

    // Utility methods for showing messages
    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showError(message, error = null) {
        console.error('Error:', error);
        this.showAlert(message, 'danger');
    }

    showInfo(message) {
        this.showAlert(message, 'info');
    }

    showAlert(message, type) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());

        // Create new alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // Loading state management
    showLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = '<div class="loading"></div>';
        }
    }

    hideLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element && element.querySelector('.loading')) {
            element.innerHTML = '';
        }
    }

    // Format currency
    formatCurrency(amount) {
        return `₹${parseFloat(amount).toFixed(2)}`;
    }

    // Format date
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString();
    }

    // Debounce function for search
    debounce(func, wait) {
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
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded - Creating RestaurantApp instance...');
    try {
        window.app = new RestaurantApp();
        console.log('RestaurantApp instance created successfully:', window.app);
    } catch (error) {
        console.error('Error creating RestaurantApp instance:', error);
    }
});

// Global utility functions
window.utils = {
    formatCurrency: (amount) => `₹${parseFloat(amount).toFixed(2)}`,
    formatDate: (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleString();
    },
    debounce: (func, wait) => {
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
};
