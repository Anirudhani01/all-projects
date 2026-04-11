const API_BASE_URL = 'http://localhost:8000/api/v1';

class ProductService {
    // Get all products with filters and pagination
    async getProducts(params = {}) {
        try {
            const queryParams = new URLSearchParams();
            
            if (params.page) queryParams.append('page', params.page);
            if (params.limit) queryParams.append('limit', params.limit);
            if (params.search) queryParams.append('search', params.search);
            if (params.category) queryParams.append('category', params.category);
            if (params.minPrice) queryParams.append('min_price', params.minPrice);
            if (params.maxPrice) queryParams.append('max_price', params.maxPrice);
            if (params.sortBy) queryParams.append('sort_by', params.sortBy);
            if (params.sortOrder) queryParams.append('sort_order', params.sortOrder);

            const url = `${API_BASE_URL}/products?${queryParams.toString()}`;
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching products:', error);
            throw error;
        }
    }

    // Get product by ID
    async getProduct(id) {
        try {
            const response = await fetch(`${API_BASE_URL}/products/${id}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching product:', error);
            throw error;
        }
    }

    // Create new product
    async createProduct(productData) {
        try {
            const response = await fetch(`${API_BASE_URL}/products/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(productData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to create product');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error creating product:', error);
            throw error;
        }
    }

    // Update product
    async updateProduct(id, productData) {
        try {
            const response = await fetch(`${API_BASE_URL}/products/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(productData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to update product');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error updating product:', error);
            throw error;
        }
    }

    // Delete product
    async deleteProduct(id) {
        try {
            const response = await fetch(`${API_BASE_URL}/products/${id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to delete product');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error deleting product:', error);
            throw error;
        }
    }

    // Get filter options (categories, materials, sizes, colors)
    async getFilterOptions() {
        try {
            const response = await fetch(`${API_BASE_URL}/products/filter-options`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching filter options:', error);
            throw error;
        }
    }

    // Upload product image
    async uploadImage(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${API_BASE_URL}/products/upload-image`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to upload image');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error uploading image:', error);
            throw error;
        }
    }

    // Get product statistics
    async getProductStats() {
        try {
            const response = await fetch(`${API_BASE_URL}/products/stats`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching product stats:', error);
            throw error;
        }
    }
}

export default new ProductService();
