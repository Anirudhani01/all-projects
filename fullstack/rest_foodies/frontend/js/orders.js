// Orders Management Module
class OrdersManager {
    static async loadOrders() {
        try {
            app.showLoading('orders-list');
            
            // Load all orders (both open and paid)
            const orders = await api.getAdminOrders();
            this.renderOrders(orders);
            
            app.hideLoading('orders-list');
        } catch (error) {
            app.showError('Failed to load orders', error);
            app.hideLoading('orders-list');
        }
    }

    static renderOrders(orders) {
        const container = document.getElementById('orders-list');
        if (!container) return;

        if (orders.length === 0) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="empty-state">
                        <i class="bi bi-receipt"></i>
                        <h5>No orders found</h5>
                        <p>Orders will appear here once they are created</p>
                    </div>
                </div>
            `;
            return;
        }

        container.innerHTML = '';

        // Group orders by status
        const openOrders = orders.filter(order => order.status === 'open');
        const paidOrders = orders.filter(order => order.status === 'paid');

        // Render open orders
        if (openOrders.length > 0) {
            container.innerHTML += `
                <div class="col-12 mb-4">
                    <h4><i class="bi bi-clock text-warning"></i> Open Orders (${openOrders.length})</h4>
                    <div class="row">
                        ${openOrders.map(order => this.createOrderCard(order)).join('')}
                    </div>
                </div>
            `;
        }

        // Render paid orders
        if (paidOrders.length > 0) {
            container.innerHTML += `
                <div class="col-12">
                    <h4><i class="bi bi-check-circle text-success"></i> Paid Orders (${paidOrders.length})</h4>
                    <div class="row">
                        ${paidOrders.map(order => this.createOrderCard(order)).join('')}
                    </div>
                </div>
            `;
        }
    }

    static createOrderCard(order) {
        const statusClass = this.getStatusClass(order.status);
        const statusIcon = this.getStatusIcon(order.status);
        const paymentMethod = order.payment_method ? this.capitalizeFirst(order.payment_method) : 'N/A';
        const openedAt = app.formatDate(order.opened_at);
        const paidAt = order.paid_at ? app.formatDate(order.paid_at) : 'Not paid';

        return `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card order-card ${statusClass}">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="bi bi-table"></i> Table ${order.table_number}
                        </h6>
                        <span class="badge ${statusClass}">
                            <i class="bi ${statusIcon}"></i> ${order.status.toUpperCase()}
                        </span>
                    </div>
                    <div class="card-body">
                        <div class="order-info mb-3">
                            <div class="row">
                                <div class="col-6">
                                    <small class="text-muted">Opened:</small><br>
                                    <strong>${openedAt}</strong>
                                </div>
                                <div class="col-6">
                                    <small class="text-muted">Paid:</small><br>
                                    <strong>${paidAt}</strong>
                                </div>
                            </div>
                            <div class="row mt-2">
                                <div class="col-6">
                                    <small class="text-muted">Payment:</small><br>
                                    <strong>${paymentMethod}</strong>
                                </div>
                                <div class="col-6">
                                    <small class="text-muted">Items:</small><br>
                                    <strong>${order.items.length}</strong>
                                </div>
                            </div>
                        </div>
                        
                        <div class="order-items mb-3">
                            <h6><i class="bi bi-list-ul"></i> Order Items</h6>
                            ${this.renderOrderItemsList(order.items)}
                        </div>
                        
                        <div class="order-total text-end">
                            <h5 class="text-success">Total: ${app.formatCurrency(order.total_amount)}</h5>
                        </div>
                        
                        <div class="order-actions mt-3">
                            ${order.status === 'open' ? `
                                <button class="btn btn-sm btn-success me-2" onclick="OrdersManager.payOrder(${order.id})">
                                    <i class="bi bi-credit-card"></i> Pay Order
                                </button>
                                <button class="btn btn-sm btn-primary" onclick="OrdersManager.viewOrder(${order.id})">
                                    <i class="bi bi-eye"></i> View Details
                                </button>
                            ` : `
                                <button class="btn btn-sm btn-secondary" onclick="OrdersManager.viewOrder(${order.id})">
                                    <i class="bi bi-eye"></i> View Details
                                </button>
                            `}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    static renderOrderItemsList(items) {
        if (items.length === 0) {
            return '<p class="text-muted small">No items in this order</p>';
        }

        return `
            <div class="order-items-list">
                ${items.map(item => `
                    <div class="order-item-small">
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="order-item-name">${item.name_snapshot}</span>
                            <span class="order-item-quantity">${item.quantity}</span>
                        </div>
                        <div class="text-muted small">
                            ${app.formatCurrency(item.price_snapshot)} each
                        </div>
                    </div>
                `).join('')}
            </div>
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

    static async viewOrder(orderId) {
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
                    <i class="bi bi-receipt"></i> Order Details - Table ${order.table_number}
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Order ID:</strong> #${order.id}<br>
                        <strong>Status:</strong> 
                        <span class="badge ${this.getStatusClass(order.status)}">
                            ${order.status.toUpperCase()}
                        </span>
                    </div>
                    <div class="col-md-6">
                        <strong>Opened:</strong> ${app.formatDate(order.opened_at)}<br>
                        ${order.paid_at ? `<strong>Paid:</strong> ${app.formatDate(order.paid_at)}` : ''}
                    </div>
                </div>
                
                <div class="order-items-details">
                    <h6><i class="bi bi-list-ul"></i> Order Items</h6>
                    ${this.renderDetailedOrderItems(order.items)}
                </div>
                
                <div class="order-summary mt-3">
                    <div class="row">
                        <div class="col-md-6">
                            <strong>Payment Method:</strong> ${order.payment_method ? this.capitalizeFirst(order.payment_method) : 'Not specified'}
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
                    <button type="button" class="btn btn-success" onclick="OrdersManager.payOrder(${order.id})">
                        <i class="bi bi-credit-card"></i> Pay Order
                    </button>
                ` : ''}
            </div>
        `;

        // Create and show modal
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'orderDetailsModal';
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

    static getOrderStats(orders) {
        const stats = {
            total: orders.length,
            open: 0,
            paid: 0,
            totalRevenue: 0,
            cashPayments: 0,
            onlinePayments: 0
        };

        orders.forEach(order => {
            if (order.status === 'open') {
                stats.open++;
            } else if (order.status === 'paid') {
                stats.paid++;
                stats.totalRevenue += order.total_amount;
                
                if (order.payment_method === 'cash') {
                    stats.cashPayments += order.total_amount;
                } else if (order.payment_method === 'online') {
                    stats.onlinePayments += order.total_amount;
                }
            }
        });

        return stats;
    }

    static renderOrderStats(orders) {
        const stats = this.getOrderStats(orders);
        
        return `
            <div class="row mb-3">
                <div class="col-md-2">
                    <div class="card bg-primary text-white">
                        <div class="card-body text-center">
                            <h6>Total Orders</h6>
                            <h4>${stats.total}</h4>
                        </div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="card bg-warning text-dark">
                        <div class="card-body text-center">
                            <h6>Open Orders</h6>
                            <h4>${stats.open}</h4>
                        </div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="card bg-success text-white">
                        <div class="card-body text-center">
                            <h6>Paid Orders</h6>
                            <h4>${stats.paid}</h4>
                        </div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="card bg-info text-white">
                        <div class="card-body text-center">
                            <h6>Total Revenue</h6>
                            <h4>${app.formatCurrency(stats.totalRevenue)}</h4>
                        </div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="card bg-secondary text-white">
                        <div class="card-body text-center">
                            <h6>Cash Payments</h6>
                            <h4>${app.formatCurrency(stats.cashPayments)}</h4>
                        </div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="card bg-dark text-white">
                        <div class="card-body text-center">
                            <h6>Online Payments</h6>
                            <h4>${app.formatCurrency(stats.onlinePayments)}</h4>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
}

// Export for global access
window.OrdersManager = OrdersManager;
