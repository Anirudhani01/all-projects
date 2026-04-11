// Tables Management Module
class TablesManager {
    static currentSearchResults = [];
    static selectedTable = null;

    static async loadTables() {
        try {
            console.log('TablesManager.loadTables() called');
            app.showLoading('tables-grid');
            
            console.log('Calling api.getTables()...');
            const tables = await api.getTables();
            console.log('Tables received:', tables);
            
            console.log('Rendering tables...');
            this.renderTables(tables);
            
            app.hideLoading('tables-grid');
            console.log('Tables loaded successfully');
        } catch (error) {
            console.error('Error in loadTables:', error);
            app.showError('Failed to load tables', error);
            app.hideLoading('tables-grid');
        }
    }

    static renderTables(tables) {
        const grid = document.getElementById('tables-grid');
        if (!grid) return;

        grid.innerHTML = '';

        tables.forEach(table => {
            const tableCard = this.createTableCard(table);
            grid.appendChild(tableCard);
        });
    }

    static createTableCard(table) {
        const col = document.createElement('div');
        col.className = 'col-lg-4 col-md-6 col-sm-6 mb-4';
        
        const statusClass = this.getStatusClass(table.status);
        const statusIcon = this.getStatusIcon(table.status);
        const itemCount = table.items.length;
        const totalAmount = table.total_amount;

        col.innerHTML = `
            <div class="card table-card ${statusClass}">
                <div class="card-header p-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="table-number-small">Table ${table.table_number}</div>
                        <div class="table-status-small ${statusClass}">
                            <i class="bi ${statusIcon}"></i> ${table.status.toUpperCase()}
                        </div>
                    </div>
                </div>
                <div class="card-body p-2">
                    <!-- Order Info -->
                    <div class="order-info mb-2">
                        ${itemCount > 0 ? `
                            <div class="table-items">
                                <i class="bi bi-list-ul"></i> ${itemCount} item${itemCount > 1 ? 's' : ''}
                            </div>
                            <div class="table-total">
                                ${app.formatCurrency(totalAmount)}
                            </div>
                        ` : `
                            <div class="table-items text-muted">
                                <i class="bi bi-dash-circle"></i> No items
                            </div>
                        `}
                    </div>
                    
                    <!-- Search Section -->
                    <div class="table-search-section">
                        <div class="input-group input-group-sm mb-2">
                            <input type="text" 
                                   class="form-control table-search-input" 
                                   id="search-table-${table.table_number}"
                                   placeholder="Search items..."
                                   onclick="event.stopPropagation()">
                            <button class="btn btn-outline-secondary btn-sm" 
                                    type="button" 
                                    onclick="event.stopPropagation(); TablesManager.clearTableSearch(${table.table_number})">
                                <i class="bi bi-x"></i>
                            </button>
                        </div>
                        <div class="table-search-results" 
                             id="search-results-${table.table_number}" 
                             style="display: none;">
                            <!-- Search results will appear here -->
                        </div>
                    </div>
                    
                    <!-- Action Buttons -->
                    <div class="mt-2">
                        <button class="btn btn-primary btn-sm w-100" 
                                onclick="event.stopPropagation(); TablesManager.openTableOrder(${table.table_number})">
                            <i class="bi bi-eye"></i> View Order
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Setup search functionality for this table
        setTimeout(() => {
            this.setupTableSearchListener(table.table_number);
        }, 100);

        return col;
    }

    static getStatusClass(status) {
        switch (status) {
            case 'idle':
                return 'idle';
            case 'open':
                return 'open';
            case 'paid':
                return 'paid';
            default:
                return '';
        }
    }

    static getStatusIcon(status) {
        switch (status) {
            case 'idle':
                return 'bi-circle';
            case 'open':
                return 'bi-clock';
            case 'paid':
                return 'bi-check-circle';
            default:
                return 'bi-question-circle';
        }
    }

    static async openTableOrder(tableNumber) {
        try {
            const order = await api.openOrGetOrder(tableNumber);
            this.showOrderModal(order);
        } catch (error) {
            app.showError('Failed to open table order', error);
        }
    }

    static showOrderModal(order) {
        // Set current order in app
        app.setCurrentOrder(order);

        // Update modal content
        const modalTableNumber = document.getElementById('modal-table-number');
        const orderItemsList = document.getElementById('order-items-list');
        const orderTotal = document.getElementById('order-total');
        const payOrderBtn = document.getElementById('pay-order-btn');

        if (modalTableNumber) modalTableNumber.textContent = order.table_number;
        if (orderTotal) orderTotal.textContent = order.total_amount.toFixed(2);

        // Render order items
        if (orderItemsList) {
            orderItemsList.innerHTML = this.renderOrderItems(order.items);
        }

        // Show/hide pay button based on order status
        if (payOrderBtn) {
            if (order.status === 'open' && order.items.length > 0) {
                payOrderBtn.style.display = 'block';
            } else {
                payOrderBtn.style.display = 'none';
            }
        }

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('tableOrderModal'));
        modal.show();
    }

    static renderOrderItems(items) {
        if (items.length === 0) {
            return `
                <div class="text-center text-muted py-4">
                    <i class="bi bi-inbox" style="font-size: 3rem;"></i>
                    <p class="mt-2">No items in this order</p>
                </div>
            `;
        }

        return items.map(item => `
            <div class="order-item">
                <div class="row align-items-center">
                    <div class="col">
                        <div class="order-item-name">${item.name_snapshot}</div>
                        <div class="order-item-price">${app.formatCurrency(item.price_snapshot)} each</div>
                    </div>
                    <div class="col-auto">
                        <div class="quantity-controls d-flex align-items-center">
                            <button class="btn btn-sm btn-outline-secondary me-2" 
                                    onclick="TablesManager.updateOrderItemQuantity(${item.id}, ${item.quantity - 1})"
                                    ${item.quantity <= 1 ? 'disabled' : ''}>
                                <i class="bi bi-dash"></i>
                            </button>
                            <span class="order-item-quantity mx-2">${item.quantity}</span>
                            <button class="btn btn-sm btn-outline-secondary ms-2" 
                                    onclick="TablesManager.updateOrderItemQuantity(${item.id}, ${item.quantity + 1})">
                                <i class="bi bi-plus"></i>
                            </button>
                        </div>
                    </div>
                    <div class="col-auto">
                        <div class="order-item-price">${app.formatCurrency(item.price_snapshot * item.quantity)}</div>
                    </div>
                    <div class="col-auto">
                        <button class="btn btn-sm btn-outline-danger" 
                                onclick="TablesManager.removeOrderItem(${item.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    static async addItemToOrder(menuItemId, quantity = 1) {
        if (!app.currentOrder) {
            app.showError('No active order');
            return;
        }

        try {
            const updatedOrder = await api.addOrderItem(app.currentOrder.id, menuItemId, quantity);
            
            // Update current order
            app.setCurrentOrder(updatedOrder);
            
            // Refresh order modal
            this.showOrderModal(updatedOrder);
            
            // Refresh tables grid
            await this.loadTables();
            
            app.showSuccess('Item added to order');
        } catch (error) {
            app.showError('Failed to add item to order', error);
        }
    }

    static async updateOrderItemQuantity(itemId, newQuantity) {
        if (!app.currentOrder) {
            app.showError('No active order');
            return;
        }

        try {
            // If quantity becomes 0 or less, remove the item
            if (newQuantity <= 0) {
                await this.removeOrderItem(itemId);
                return;
            }

            const updatedOrder = await api.updateOrderItem(app.currentOrder.id, itemId, newQuantity);
            
            // Update current order
            app.setCurrentOrder(updatedOrder);
            
            // Refresh order modal
            this.showOrderModal(updatedOrder);
            
            // Refresh tables grid
            await this.loadTables();
            
            app.showSuccess('Order updated');
        } catch (error) {
            app.showError('Failed to update order', error);
        }
    }

    static async removeOrderItem(itemId) {
        if (!app.currentOrder) {
            app.showError('No active order');
            return;
        }

        try {
            const updatedOrder = await api.deleteOrderItem(app.currentOrder.id, itemId);
            
            // Update current order
            app.setCurrentOrder(updatedOrder);
            
            // Refresh order modal
            this.showOrderModal(updatedOrder);
            
            // Refresh tables grid
            await this.loadTables();
            
            app.showSuccess('Item removed from order');
        } catch (error) {
            app.showError('Failed to remove item from order', error);
        }
    }

    static getTableStatusSummary(tables) {
        const summary = {
            idle: 0,
            open: 0,
            paid: 0,
            total: tables.length
        };

        tables.forEach(table => {
            summary[table.status]++;
        });

        return summary;
    }

    static renderTableStatusSummary(tables) {
        const summary = this.getTableStatusSummary(tables);
        
        return `
            <div class="row mb-3">
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body text-center">
                            <h5>Idle Tables</h5>
                            <h3>${summary.idle}</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-warning text-white">
                        <div class="card-body text-center">
                            <h5>Open Orders</h5>
                            <h3>${summary.open}</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body text-center">
                            <h5>Paid Orders</h5>
                            <h3>${summary.paid}</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body text-center">
                            <h5>Total Tables</h5>
                            <h3>${summary.total}</h3>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Per-table search functionality
    static setupTableSearchListener(tableNumber) {
        const searchInput = document.getElementById(`search-table-${tableNumber}`);
        if (!searchInput) return;

        searchInput.addEventListener('input', app.debounce(() => {
            this.performTableSearch(tableNumber);
        }, 300));
    }

    static async performTableSearch(tableNumber) {
        const searchInput = document.getElementById(`search-table-${tableNumber}`);
        const resultsContainer = document.getElementById(`search-results-${tableNumber}`);
        
        if (!searchInput || !resultsContainer) {
            console.error('Search input or results container not found for table', tableNumber);
            return;
        }

        const searchTerm = searchInput.value.trim();
        console.log(`Searching for "${searchTerm}" in table ${tableNumber}`);

        if (!searchTerm) {
            resultsContainer.style.display = 'none';
            return;
        }

        try {
            const menuItems = await api.searchMenu(searchTerm);
            console.log(`Search results for "${searchTerm}":`, menuItems);
            this.renderTableSearchResults(tableNumber, menuItems);
        } catch (error) {
            console.error('Failed to search menu items:', error);
            resultsContainer.innerHTML = `
                <div class="alert alert-danger alert-sm">
                    <i class="bi bi-exclamation-triangle"></i> Search failed
                </div>
            `;
            resultsContainer.style.display = 'block';
        }
    }

    static renderTableSearchResults(tableNumber, menuItems) {
        const resultsContainer = document.getElementById(`search-results-${tableNumber}`);
        if (!resultsContainer) {
            console.error('Results container not found for table', tableNumber);
            return;
        }

        console.log(`Rendering ${menuItems.length} search results for table ${tableNumber}:`, menuItems);

        if (menuItems.length === 0) {
            resultsContainer.innerHTML = `
                <div class="alert alert-info alert-sm">
                    <i class="bi bi-info-circle"></i> No items found
                </div>
            `;
            resultsContainer.style.display = 'block';
            return;
        }

        const resultsHTML = menuItems.slice(0, 3).map(item => `
            <div class="table-search-item ${item.is_out_of_stock ? 'out-of-stock' : ''}" 
                 onclick="event.stopPropagation(); console.log('Clicked item:', ${item.id}); TablesManager.addItemToTable(${tableNumber}, ${item.id})"
                 style="cursor: pointer; padding: 8px; border-bottom: 1px solid #eee;">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="item-info">
                        <div class="item-name">${item.name}</div>
                        <div class="item-price">${app.formatCurrency(item.price)}</div>
                    </div>
                    <div class="item-action">
                        ${item.is_out_of_stock ? 
                            '<span class="badge bg-danger">Out</span>' :
                            '<i class="bi bi-plus-circle text-primary"></i>'
                        }
                    </div>
                </div>
            </div>
        `).join('');

        console.log('Generated HTML:', resultsHTML);
        resultsContainer.innerHTML = resultsHTML;
        resultsContainer.style.display = 'block';
    }

    static clearTableSearch(tableNumber) {
        const searchInput = document.getElementById(`search-table-${tableNumber}`);
        const resultsContainer = document.getElementById(`search-results-${tableNumber}`);
        
        if (searchInput) searchInput.value = '';
        if (resultsContainer) resultsContainer.style.display = 'none';
    }

    static async addItemToTable(tableNumber, menuItemId) {
        try {
            console.log(`Adding item ${menuItemId} to table ${tableNumber}`);
            
            // Open or get the order for this table first
            const order = await api.openOrGetOrder(tableNumber);
            console.log('Order created/retrieved:', order);
            
            // Add item to the order
            const updatedOrder = await api.addOrderItem(order.id, menuItemId, 1);
            console.log('Order updated:', updatedOrder);
            
            // Clear search and refresh tables
            this.clearTableSearch(tableNumber);
            await this.loadTables();
            
            app.showSuccess(`Item added to Table ${tableNumber}!`);
        } catch (error) {
            console.error('Error adding item to table:', error);
            app.showError('Failed to add item to table', error);
        }
    }
}

// Export for global access
window.TablesManager = TablesManager;
