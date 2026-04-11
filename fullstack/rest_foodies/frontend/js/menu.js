// Menu Management Module
class MenuManager {
    static currentCategory = null;
    static currentSubCategory = null;
    static searchTerm = '';

    static async loadMenu() {
        try {
            app.showLoading('menu-items-grid');
            
            // Load categories first
            await this.loadCategories();
            
            // Load menu items
            await this.loadMenuItems();
            
            app.hideLoading('menu-items-grid');
        } catch (error) {
            app.showError('Failed to load menu', error);
            app.hideLoading('menu-items-grid');
        }
    }

    static async loadCategories() {
        try {
            const categories = await api.getMenuCategories();
            this.renderCategories(categories);
        } catch (error) {
            app.showError('Failed to load categories', error);
        }
    }

    static renderCategories(categories) {
        const container = document.getElementById('category-filters');
        if (!container) return;

        let html = '<div class="list-group list-group-flush">';
        
        // Add "All Categories" option
        html += `
            <div class="list-group-item category-filter active" onclick="MenuManager.filterByCategory(null)">
                <i class="bi bi-list-ul"></i> All Categories
            </div>
        `;

        // Render main categories
        Object.keys(categories).forEach(mainCategory => {
            const subCategories = categories[mainCategory];
            
            html += `
                <div class="list-group-item">
                    <div class="category-filter" onclick="MenuManager.filterByCategory('${mainCategory}')">
                        <i class="bi bi-folder"></i> ${this.capitalizeFirst(mainCategory)}
                    </div>
                    ${subCategories.length > 1 ? `
                        <div class="ms-3 mt-2">
                            ${subCategories.map(subCat => `
                                <div class="category-filter sub-category" onclick="MenuManager.filterBySubcategory('${mainCategory}', '${subCat}')">
                                    <i class="bi bi-chevron-right"></i> ${this.capitalizeFirst(subCat)}
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            `;
        });

        html += '</div>';
        container.innerHTML = html;
    }

    static async loadMenuItems() {
        try {
            let menuItems;
            
            if (this.currentSubCategory) {
                menuItems = await api.getMenuBySubcategory(this.currentCategory, this.currentSubCategory);
            } else if (this.currentCategory) {
                menuItems = await api.getMenuByCategory(this.currentCategory);
            } else if (this.searchTerm) {
                menuItems = await api.getMenu(this.searchTerm);
            } else {
                menuItems = await api.getMenu();
            }

            this.renderMenuItems(menuItems);
        } catch (error) {
            app.showError('Failed to load menu items', error);
        }
    }

    static renderMenuItems(menuItems) {
        const grid = document.getElementById('menu-items-grid');
        if (!grid) return;

        if (menuItems.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-search"></i>
                    <h5>No menu items found</h5>
                    <p>Try adjusting your search or category filter</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = '';

        menuItems.forEach(item => {
            const itemCard = this.createMenuItemCard(item);
            grid.appendChild(itemCard);
        });
    }

    static createMenuItemCard(item) {
        const col = document.createElement('div');
        col.className = 'col-md-4 col-sm-6 mb-3';
        
        const outOfStockClass = item.is_out_of_stock ? 'out-of-stock' : '';
        const outOfStockBadge = item.is_out_of_stock ? '<span class="badge bg-danger ms-2">Out of Stock</span>' : '';

        col.innerHTML = `
            <div class="card menu-item-card ${outOfStockClass}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="card-title mb-0">${item.name}</h6>
                        ${outOfStockBadge}
                    </div>
                    
                    <p class="card-text text-muted small">${item.description || 'No description available'}</p>
                    
                    <div class="menu-item-category mb-2">
                        <i class="bi bi-tag"></i> ${this.capitalizeFirst(item.main_category)} - ${this.capitalizeFirst(item.sub_category)}
                    </div>
                    
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="menu-item-price">${app.formatCurrency(item.price)}</div>
                        <div class="btn-group btn-group-sm">
                            ${!item.is_out_of_stock ? `
                                <button class="btn btn-outline-primary" onclick="MenuManager.addToOrder(${item.id})">
                                    <i class="bi bi-plus"></i> Add
                                </button>
                            ` : ''}
                            <button class="btn btn-outline-secondary" onclick="MenuManager.toggleOutOfStock(${item.id})">
                                <i class="bi bi-x-circle"></i> ${item.is_out_of_stock ? 'In Stock' : 'Out of Stock'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        return col;
    }

    static async filterByCategory(category) {
        this.currentCategory = category;
        this.currentSubCategory = null;
        
        // Update active state
        document.querySelectorAll('.category-filter').forEach(filter => {
            filter.classList.remove('active');
        });
        event.target.closest('.category-filter').classList.add('active');
        
        await this.loadMenuItems();
    }

    static async filterBySubcategory(mainCategory, subCategory) {
        this.currentCategory = mainCategory;
        this.currentSubCategory = subCategory;
        
        // Update active state
        document.querySelectorAll('.category-filter').forEach(filter => {
            filter.classList.remove('active');
        });
        event.target.closest('.category-filter').classList.add('active');
        
        await this.loadMenuItems();
    }

    static async searchMenu(searchTerm) {
        this.searchTerm = searchTerm;
        this.currentCategory = null;
        this.currentSubCategory = null;
        
        // Clear category filters
        document.querySelectorAll('.category-filter').forEach(filter => {
            filter.classList.remove('active');
        });
        
        await this.loadMenuItems();
    }

    static async addToOrder(menuItemId) {
        if (!app.currentOrder) {
            app.showError('Please open a table order first');
            return;
        }

        try {
            await TablesManager.addItemToOrder(menuItemId, 1);
        } catch (error) {
            app.showError('Failed to add item to order', error);
        }
    }

    static async toggleOutOfStock(menuItemId) {
        try {
            // Get current menu items to find the item
            const menuItems = await api.getMenu();
            const item = menuItems.find(item => item.id === menuItemId);
            
            if (!item) {
                app.showError('Menu item not found');
                return;
            }

            // Toggle the out-of-stock status
            const newIds = item.is_out_of_stock ? [] : [menuItemId];
            await api.toggleOutOfStock(newIds);
            
            // Reload menu items
            await this.loadMenuItems();
            
            app.showSuccess(`Item ${item.is_out_of_stock ? 'restored to stock' : 'marked as out of stock'}`);
        } catch (error) {
            app.showError('Failed to toggle out-of-stock status', error);
        }
    }

    static capitalizeFirst(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1).replace(/-/g, ' ');
    }

    static getMenuStats(menuItems) {
        const stats = {
            total: menuItems.length,
            inStock: 0,
            outOfStock: 0,
            categories: {}
        };

        menuItems.forEach(item => {
            if (item.is_out_of_stock) {
                stats.outOfStock++;
            } else {
                stats.inStock++;
            }

            if (!stats.categories[item.main_category]) {
                stats.categories[item.main_category] = 0;
            }
            stats.categories[item.main_category]++;
        });

        return stats;
    }

    static renderMenuStats(menuItems) {
        const stats = this.getMenuStats(menuItems);
        
        return `
            <div class="row mb-3">
                <div class="col-md-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body text-center">
                            <h5>Total Items</h5>
                            <h3>${stats.total}</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body text-center">
                            <h5>In Stock</h5>
                            <h3>${stats.inStock}</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-danger text-white">
                        <div class="card-body text-center">
                            <h5>Out of Stock</h5>
                            <h3>${stats.outOfStock}</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body text-center">
                            <h5>Categories</h5>
                            <h3>${Object.keys(stats.categories).length}</h3>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
}

// Export for global access
window.MenuManager = MenuManager;
