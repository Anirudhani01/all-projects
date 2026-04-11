// API Service Layer for Restaurant Management System
class API {
    constructor() {
        this.baseURL = 'http://localhost:8000'; // FastAPI backend URL
        this.endpoints = {
            // Menu endpoints
            menu: '/menu',
            menuCategories: '/menu/categories',
            menuByCategory: (category) => `/menu/category/${category}`,
            menuBySubcategory: (mainCat, subCat) => `/menu/category/${mainCat}/${subCat}`,
            menuItem: (id) => `/menu/${id}`,
            toggleOutOfStock: '/menu/out-of-stock',
            
            // Table endpoints
            tables: '/tables',
            tableOrder: (tableNum) => `/tables/${tableNum}/order`,
            
            // Order endpoints
            order: (id) => `/orders/${id}`,
            addOrderItem: (orderId) => `/orders/${orderId}/items`,
            updateOrderItem: (orderId, itemId) => `/orders/${orderId}/items/${itemId}`,
            deleteOrderItem: (orderId, itemId) => `/orders/${orderId}/items/${itemId}`,
            payOrder: (orderId) => `/orders/${orderId}/pay`,
            
            // Admin endpoints
            adminOrders: '/admin/orders',
            adminMetrics: '/admin/metrics'
        };
    }

    // Generic request method
    async request(endpoint, options = {}) {
        const url = this.baseURL + endpoint;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        console.log('Making API request to:', url);
        console.log('Request config:', config);

        try {
            const response = await fetch(url, config);
            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                console.error('Response error data:', errorData);
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Response data:', data);
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            console.error('Error details:', {
                message: error.message,
                stack: error.stack,
                url: url,
                config: config
            });
            throw error;
        }
    }

    // GET request
    async get(endpoint, params = {}) {
        const url = new URL(this.baseURL + endpoint);
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== undefined) {
                url.searchParams.append(key, params[key]);
            }
        });
        
        return this.request(url.pathname + url.search);
    }

    // POST request
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // PUT request
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // PATCH request
    async patch(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }

    // DELETE request
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }

    // Menu API methods
    async getMenu(search = null) {
        return this.get(this.endpoints.menu, { search });
    }

    async searchMenu(searchTerm, category = null) {
        const params = {};
        if (searchTerm) params.search = searchTerm;
        if (category) params.category = category;
        return this.get(this.endpoints.menu, params);
    }

    async getMenuCategories() {
        return this.get(this.endpoints.menuCategories);
    }

    async getMenuByCategory(category) {
        return this.get(this.endpoints.menuByCategory(category));
    }

    async getMenuBySubcategory(mainCategory, subCategory) {
        return this.get(this.endpoints.menuBySubcategory(mainCategory, subCategory));
    }

    async getMenuItem(id) {
        return this.get(this.endpoints.menuItem(id));
    }

    async createMenuItem(data) {
        return this.post(this.endpoints.menu, data);
    }

    async updateMenuItem(id, data) {
        return this.put(this.endpoints.menuItem(id), data);
    }

    async deleteMenuItem(id) {
        return this.delete(this.endpoints.menuItem(id));
    }

    async toggleOutOfStock(ids) {
        return this.put(this.endpoints.toggleOutOfStock, { ids });
    }

    // Table API methods
    async getTables() {
        return this.get(this.endpoints.tables);
    }

    async openOrGetOrder(tableNumber) {
        return this.post(this.endpoints.tableOrder(tableNumber));
    }

    // Order API methods
    async getOrder(id) {
        return this.get(this.endpoints.order(id));
    }

    async addOrderItem(orderId, menuItemId, quantity) {
        return this.post(this.endpoints.addOrderItem(orderId), {
            menu_item_id: menuItemId,
            quantity: quantity
        });
    }

    async updateOrderItem(orderId, itemId, quantity) {
        return this.patch(this.endpoints.updateOrderItem(orderId, itemId), {
            quantity: quantity
        });
    }

    async deleteOrderItem(orderId, itemId) {
        return this.delete(this.endpoints.deleteOrderItem(orderId, itemId));
    }

    async payOrder(orderId, paymentMethod) {
        return this.post(this.endpoints.payOrder(orderId), {
            payment_method: paymentMethod
        });
    }

    // Admin API methods
    async getAdminOrders(filters = {}) {
        return this.get(this.endpoints.adminOrders, filters);
    }

    async getAdminMetrics() {
        return this.get(this.endpoints.adminMetrics);
    }
}

// Create global API instance
const api = new API();

// Export for use in other modules
window.api = api;
