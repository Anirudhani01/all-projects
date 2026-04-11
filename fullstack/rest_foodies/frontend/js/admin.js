// Admin Dashboard Module
class AdminManager {
    static async loadDashboard() {
        try {
            // Load metrics
            await this.loadMetrics();
            
            // Load recent orders
            await this.loadRecentOrders();
            
        } catch (error) {
            app.showError('Failed to load admin dashboard', error);
        }
    }

    static async loadMetrics() {
        try {
            const metrics = await api.getAdminMetrics();
            this.renderMetrics(metrics);
        } catch (error) {
            app.showError('Failed to load metrics', error);
        }
    }

    static renderMetrics(metrics) {
        // Update metric cards
        const totalRevenue = document.getElementById('total-revenue');
        const ordersPaid = document.getElementById('orders-paid');
        const itemsSold = document.getElementById('items-sold');
        const cashPayments = document.getElementById('cash-payments');

        if (totalRevenue) totalRevenue.textContent = app.formatCurrency(metrics.total_revenue);
        if (ordersPaid) ordersPaid.textContent = metrics.orders_paid;
        if (itemsSold) itemsSold.textContent = metrics.items_sold;
        if (cashPayments) cashPayments.textContent = app.formatCurrency(metrics.cash);
    }

    static async loadRecentOrders() {
        try {
            // Get recent orders (last 10)
            const orders = await api.getAdminOrders({ limit: 10 });
            this.renderRecentOrders(orders);
        } catch (error) {
            app.showError('Failed to load recent orders', error);
        }
    }

    static renderRecentOrders(orders) {
        const container = document.getElementById('recent-orders');
        if (!container) return;

        if (orders.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-receipt"></i>
                    <h5>No orders yet</h5>
                    <p>Orders will appear here once they are created</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Order ID</th>
                            <th>Table</th>
                            <th>Status</th>
                            <th>Items</th>
                            <th>Total</th>
                            <th>Payment</th>
                            <th>Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${orders.map(order => this.createOrderRow(order)).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    static createOrderRow(order) {
        const statusClass = this.getStatusClass(order.status);
        const statusIcon = this.getStatusIcon(order.status);
        const paymentMethod = order.payment_method ? this.capitalizeFirst(order.payment_method) : 'N/A';
        const openedAt = app.formatDate(order.opened_at);

        return `
            <tr>
                <td><strong>#${order.id}</strong></td>
                <td>
                    <i class="bi bi-table"></i> Table ${order.table_number}
                </td>
                <td>
                    <span class="badge ${statusClass}">
                        <i class="bi ${statusIcon}"></i> ${order.status.toUpperCase()}
                    </span>
                </td>
                <td>
                    <span class="badge bg-secondary">${order.items.length} items</span>
                </td>
                <td>
                    <strong class="text-success">${app.formatCurrency(order.total_amount)}</strong>
                </td>
                <td>
                    <small class="text-muted">${paymentMethod}</small>
                </td>
                <td>
                    <small>${openedAt}</small>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="AdminManager.viewOrderDetails(${order.id})">
                            <i class="bi bi-eye"></i>
                        </button>
                        ${order.status === 'open' ? `
                            <button class="btn btn-outline-success" onclick="AdminManager.payOrder(${order.id})">
                                <i class="bi bi-credit-card"></i>
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `;
    }

    static getStatusClass(status) {
        switch (status) {
            case 'open':
                return 'bg-warning text-dark';
            case 'paid':
                return 'bg-success text-white';
            default:
                return 'bg-secondary text-white';
        }
    }

    static getStatusIcon(status) {
        switch (status) {
            case 'open':
                return 'bi-clock';
            case 'paid':
                return 'bi-check-circle';
            default:
                return 'bi-question-circle';
        }
    }

    static async viewOrderDetails(orderId) {
        try {
            const order = await api.getOrder(orderId);
            this.showOrderDetailsModal(order);
        } catch (error) {
            app.showError('Failed to load order details', error);
        }
    }

    static showOrderDetailsModal(order) {
        // Create modal content
        const modalContent = `
            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="bi bi-receipt"></i> Order #${order.id} - Table ${order.table_number}
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Order ID:</strong> #${order.id}<br>
                        <strong>Table:</strong> ${order.table_number}<br>
                        <strong>Status:</strong> 
                        <span class="badge ${this.getStatusClass(order.status)}">
                            ${order.status.toUpperCase()}
                        </span>
                    </div>
                    <div class="col-md-6">
                        <strong>Opened:</strong> ${app.formatDate(order.opened_at)}<br>
                        ${order.paid_at ? `<strong>Paid:</strong> ${app.formatDate(order.paid_at)}` : ''}<br>
                        <strong>Payment:</strong> ${order.payment_method ? this.capitalizeFirst(order.payment_method) : 'Not specified'}
                    </div>
                </div>
                
                <div class="order-items-details">
                    <h6><i class="bi bi-list-ul"></i> Order Items</h6>
                    ${this.renderDetailedOrderItems(order.items)}
                </div>
                
                <div class="order-summary mt-3">
                    <div class="row">
                        <div class="col-md-6">
                            <strong>Total Items:</strong> ${order.items.length}
                        </div>
                        <div class="col-md-6 text-end">
                            <h5 class="text-success">Total: ${app.formatCurrency(order.total_amount)}</h5>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                ${order.status === 'open' ? `
                    <button type="button" class="btn btn-success" onclick="AdminManager.payOrder(${order.id})">
                        <i class="bi bi-credit-card"></i> Pay Order
                    </button>
                ` : ''}
            </div>
        `;

        // Create and show modal
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'adminOrderDetailsModal';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    ${modalContent}
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Clean up modal after it's hidden
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    static renderDetailedOrderItems(items) {
        if (items.length === 0) {
            return '<p class="text-muted">No items in this order</p>';
        }

        return `
            <div class="table-responsive">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Item</th>
                            <th class="text-center">Quantity</th>
                            <th class="text-end">Price</th>
                            <th class="text-end">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${items.map(item => `
                            <tr>
                                <td>${item.name_snapshot}</td>
                                <td class="text-center">${item.quantity}</td>
                                <td class="text-end">${app.formatCurrency(item.price_snapshot)}</td>
                                <td class="text-end">${app.formatCurrency(item.price_snapshot * item.quantity)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    static async payOrder(orderId) {
        try {
            // Set current order for payment
            const order = await api.getOrder(orderId);
            app.setCurrentOrder(order);
            
            // Show payment modal
            app.showPaymentModal();
        } catch (error) {
            app.showError('Failed to process payment', error);
        }
    }

    static capitalizeFirst(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    static async generateReport() {
        try {
            // Get all orders for reporting
            const orders = await api.getAdminOrders();
            const metrics = await api.getAdminMetrics();
            
            this.showReportModal(orders, metrics);
        } catch (error) {
            app.showError('Failed to generate report', error);
        }
    }

    static showReportModal(orders, metrics) {
        const reportContent = this.generateReportContent(orders, metrics);
        
        const modalContent = `
            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="bi bi-file-earmark-text"></i> Restaurant Report
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                ${reportContent}
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button type="button" class="btn btn-primary" onclick="AdminManager.exportReport()">
                    <i class="bi bi-download"></i> Export Report
                </button>
            </div>
        `;

        // Create and show modal
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'reportModal';
        modal.innerHTML = `
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    ${modalContent}
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Clean up modal after it's hidden
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    static generateReportContent(orders, metrics) {
        const now = new Date();
        const dateStr = now.toLocaleDateString();
        const timeStr = now.toLocaleTimeString();

        // Calculate additional stats
        const openOrders = orders.filter(o => o.status === 'open');
        const paidOrders = orders.filter(o => o.status === 'paid');
        const totalItems = orders.reduce((sum, order) => sum + order.items.length, 0);

        return `
            <div class="report-header mb-4">
                <h4>Restaurant Management System Report</h4>
                <p class="text-muted">Generated on ${dateStr} at ${timeStr}</p>
            </div>

            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body text-center">
                            <h5>Total Revenue</h5>
                            <h3>${app.formatCurrency(metrics.total_revenue)}</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body text-center">
                            <h5>Paid Orders</h5>
                            <h3>${metrics.orders_paid}</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-warning text-dark">
                        <div class="card-body text-center">
                            <h5>Open Orders</h5>
                            <h3>${openOrders.length}</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body text-center">
                            <h5>Items Sold</h5>
                            <h3>${metrics.items_sold}</h3>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="bi bi-currency-dollar"></i> Payment Methods</h6>
                        </div>
                        <div class="card-body">
                            <div class="d-flex justify-content-between mb-2">
                                <span>Cash Payments:</span>
                                <strong>${app.formatCurrency(metrics.cash)}</strong>
                            </div>
                            <div class="d-flex justify-content-between mb-2">
                                <span>Online Payments:</span>
                                <strong>${app.formatCurrency(metrics.online)}</strong>
                            </div>
                            <div class="d-flex justify-content-between">
                                <span>Total:</span>
                                <strong>${app.formatCurrency(metrics.total_revenue)}</strong>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="bi bi-graph-up"></i> Order Statistics</h6>
                        </div>
                        <div class="card-body">
                            <div class="d-flex justify-content-between mb-2">
                                <span>Total Orders:</span>
                                <strong>${orders.length}</strong>
                            </div>
                            <div class="d-flex justify-content-between mb-2">
                                <span>Paid Orders:</span>
                                <strong>${paidOrders.length}</strong>
                            </div>
                            <div class="d-flex justify-content-between">
                                <span>Open Orders:</span>
                                <strong>${openOrders.length}</strong>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h6><i class="bi bi-list-ul"></i> Recent Orders</h6>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Order ID</th>
                                    <th>Table</th>
                                    <th>Status</th>
                                    <th>Items</th>
                                    <th>Total</th>
                                    <th>Payment</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${orders.slice(0, 10).map(order => `
                                    <tr>
                                        <td>#${order.id}</td>
                                        <td>Table ${order.table_number}</td>
                                        <td>
                                            <span class="badge ${this.getStatusClass(order.status)}">
                                                ${order.status.toUpperCase()}
                                            </span>
                                        </td>
                                        <td>${order.items.length}</td>
                                        <td>${app.formatCurrency(order.total_amount)}</td>
                                        <td>${order.payment_method ? this.capitalizeFirst(order.payment_method) : 'N/A'}</td>
                                        <td>${app.formatDate(order.opened_at)}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    }

    static exportReport() {
        // Create a simple text report for export
        const reportText = this.generateTextReport();
        
        // Create download link
        const blob = new Blob([reportText], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `restaurant-report-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        app.showSuccess('Report exported successfully!');
    }

    static async generateTextReport() {
        try {
            const orders = await api.getAdminOrders();
            const metrics = await api.getAdminMetrics();
            
            const now = new Date();
            const dateStr = now.toLocaleDateString();
            const timeStr = now.toLocaleTimeString();

            let report = `RESTAURANT MANAGEMENT SYSTEM REPORT\n`;
            report += `Generated on ${dateStr} at ${timeStr}\n`;
            report += `==========================================\n\n`;
            
            report += `SUMMARY:\n`;
            report += `- Total Revenue: ${app.formatCurrency(metrics.total_revenue)}\n`;
            report += `- Paid Orders: ${metrics.orders_paid}\n`;
            report += `- Items Sold: ${metrics.items_sold}\n`;
            report += `- Cash Payments: ${app.formatCurrency(metrics.cash)}\n`;
            report += `- Online Payments: ${app.formatCurrency(metrics.online)}\n\n`;
            
            report += `RECENT ORDERS:\n`;
            orders.slice(0, 10).forEach(order => {
                report += `- Order #${order.id}: Table ${order.table_number}, ${order.status}, ${app.formatCurrency(order.total_amount)}\n`;
            });
            
            return report;
        } catch (error) {
            return 'Error generating report: ' + error.message;
        }
    }
}

// Export for global access
window.AdminManager = AdminManager;
