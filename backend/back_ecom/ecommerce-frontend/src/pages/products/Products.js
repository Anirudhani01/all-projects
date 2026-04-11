import React, { useState, useEffect, useCallback } from 'react';
import { 
  PlusIcon, 
  PencilIcon, 
  TrashIcon, 
  MagnifyingGlassIcon,
  FunnelIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import productService from '../../services/productService';

const Products = () => {
  // State management
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  const [materials, setMaterials] = useState([]);
  const [sizes, setSizes] = useState([]);
  const [colors, setColors] = useState([]);
  
  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  
  // Form states
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    originalPrice: '',
    discount: '',
    material: '',
    category: '',
    subcategory: '',
    tags: '',
    images: '',
    sizes: '',
    care: '',
    features: '',
    isFeatured: false
  });
  
  // Filter and pagination states
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    material: '',
    price_min: '',
    price_max: '',
    featured: ''
  });
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 12,
    total: 0
  });
  const [showFilters, setShowFilters] = useState(false);

  // Fetch products and filter options on component mount
  useEffect(() => {
    fetchProducts();
    fetchFilterOptions();
  }, []);

  // Fetch products from backend
  const fetchProducts = useCallback(async () => {
    try {
      setLoading(true);
      const params = {
        page: pagination.page,
        limit: pagination.limit,
        search: filters.search,
        category: filters.category,
        minPrice: filters.price_min,
        maxPrice: filters.price_max
      };
      
      const data = await productService.getProducts(params);
      if (data.success) {
        setProducts(data.data.items || []);
        setPagination(prev => ({
          ...prev,
          total: data.data.pagination?.total || 0
        }));
      }
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.limit, filters.search, filters.category, filters.price_min, filters.price_max]);

  // Fetch categories and other filter options
  const fetchFilterOptions = useCallback(async () => {
    try {
      const [categoriesRes, filterOptionsRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/categories/'),
        productService.getFilterOptions()
      ]);

      if (categoriesRes.ok) {
        const categoriesData = await categoriesRes.json();
        setCategories(categoriesData.data || []);
      }
      
      if (filterOptionsRes.success) {
        const { materials, sizes, colors } = filterOptionsRes.data;
        setMaterials(materials || []);
        setSizes(sizes || []);
        setColors(colors || []);
      }
    } catch (error) {
      console.error('Error fetching filter options:', error);
    }
  }, []);

  // Create product
  const createProduct = async (e) => {
    e.preventDefault();
    try {
      const productData = {
        ...formData,
        price: parseFloat(formData.price),
        originalPrice: formData.originalPrice ? parseFloat(formData.originalPrice) : null,
        discount: formData.discount ? parseFloat(formData.discount) : null,
        tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        images: formData.images.split(',').map(img => img.trim()).filter(img => img),
        sizes: formData.sizes.split(',').map(size => size.trim()).filter(size => size),
        features: formData.features ? formData.features.split(',').map(f => f.trim()).filter(f => f) : [],
        colors: [{ name: 'Default', hex: '#000000', image: formData.images.split(',')[0] || '' }]
      };

      const result = await productService.createProduct(productData);
      
      if (result.success) {
        setShowCreateModal(false);
        resetForm();
        fetchProducts();
        alert('Product created successfully!');
      } else {
        alert(`Error creating product: ${result.message}`);
      }
    } catch (error) {
      console.error('Error creating product:', error);
      alert('Error creating product');
    }
  };

  // Update product
  const updateProduct = async (e) => {
    e.preventDefault();
    try {
      const productData = {
        ...formData,
        price: parseFloat(formData.price),
        originalPrice: formData.originalPrice ? parseFloat(formData.originalPrice) : null,
        discount: formData.discount ? parseFloat(formData.discount) : null,
        tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        images: formData.images.split(',').map(img => img.trim()).filter(img => img),
        sizes: formData.sizes.split(',').map(size => size.trim()).filter(size => size),
        features: formData.features ? formData.features.split(',').map(f => f.trim()).filter(f => f) : []
      };

      const result = await productService.updateProduct(selectedProduct.id, productData);
      
      if (result.success) {
        setShowEditModal(false);
        resetForm();
        fetchProducts();
        alert('Product updated successfully!');
      } else {
        alert(`Error updating product: ${result.message}`);
      }
    } catch (error) {
      console.error('Error updating product:', error);
      alert('Error updating product');
    }
  };

  // Delete product
  const deleteProduct = async () => {
    try {
      const result = await productService.deleteProduct(selectedProduct.id);
      
      if (result.success) {
        setShowDeleteModal(false);
        fetchProducts();
        alert('Product deleted successfully!');
      } else {
        alert(`Error deleting product: ${result.message}`);
      }
    } catch (error) {
      console.error('Error deleting product:', error);
      alert('Error deleting product');
    }
  };

  // Edit product - populate form
  const handleEdit = (product) => {
    setSelectedProduct(product);
    setFormData({
      name: product.name || '',
      description: product.description || '',
      price: product.price?.toString() || '',
      originalPrice: product.originalPrice?.toString() || '',
      discount: product.discount?.toString() || '',
      material: product.material || '',
      category: product.category || '',
      subcategory: product.subcategory || '',
      tags: product.tags?.join(', ') || '',
      images: product.images?.join(', ') || '',
      sizes: product.sizes?.join(', ') || '',
      care: product.care || '',
      features: product.features?.join(', ') || '',
      isFeatured: product.isFeatured || false
    });
    setShowEditModal(true);
  };

  // Delete product confirmation
  const handleDelete = (product) => {
    setSelectedProduct(product);
    setShowDeleteModal(true);
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      price: '',
      originalPrice: '',
      discount: '',
      material: '',
      category: '',
      subcategory: '',
      tags: '',
      images: '',
      sizes: '',
      care: '',
      features: '',
      isFeatured: false
    });
  };

  // Handle filter changes
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPagination(prev => ({ ...prev, page: 1 })); // Reset to first page
  };

  // Apply filters
  const applyFilters = () => {
    fetchProducts();
  };

  // Clear filters
  const clearFilters = () => {
    setFilters({
      search: '',
      category: '',
      material: '',
      price_min: '',
      price_max: '',
      featured: ''
    });
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  // Pagination
  const handlePageChange = (newPage) => {
    setPagination(prev => ({ ...prev, page: newPage }));
  };

  // Effects
  useEffect(() => {
    fetchProducts();
    fetchFilterOptions();
  }, [pagination.page]);

  useEffect(() => {
    fetchProducts();
  }, [filters]);

  // Fetch products and filter options on component mount
  useEffect(() => {
    fetchProducts();
    fetchFilterOptions();
  }, []);





  // Show loading state
  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Loading Products...</h1>
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Products</h1>
          <p className="text-gray-600">Manage your product catalog</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <PlusIcon className="w-5 h-5" />
          Add Product
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="text-gray-600 hover:text-gray-900 flex items-center gap-2"
          >
            <FunnelIcon className="w-5 h-5" />
            {showFilters ? 'Hide' : 'Show'} Filters
          </button>
        </div>
        
        {showFilters && (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <input
              type="text"
              placeholder="Search products..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="input"
            />
            <select
              value={filters.category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
              className="input"
            >
              <option value="">All Categories</option>
              {categories.map(cat => (
                <option key={cat.id} value={cat.slug}>{cat.name}</option>
              ))}
            </select>
            <select
              value={filters.material}
              onChange={(e) => handleFilterChange('material', e.target.value)}
              className="input"
            >
              <option value="">All Materials</option>
              {materials.map(mat => (
                <option key={mat} value={mat}>{mat}</option>
              ))}
            </select>
            <input
              type="number"
              placeholder="Min Price"
              value={filters.price_min}
              onChange={(e) => handleFilterChange('price_min', e.target.value)}
              className="input"
            />
            <input
              type="number"
              placeholder="Max Price"
              value={filters.price_max}
              onChange={(e) => handleFilterChange('price_max', e.target.value)}
              className="input"
            />
            <select
              value={filters.featured}
              onChange={(e) => handleFilterChange('featured', e.target.value)}
              className="input"
            >
              <option value="">All Products</option>
              <option value="true">Featured Only</option>
              <option value="false">Non-Featured</option>
            </select>
          </div>
        )}
        
        <div className="flex gap-2 mt-4">
          <button
            onClick={applyFilters}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Apply Filters
          </button>
          <button
            onClick={clearFilters}
            className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Products List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading products...</p>
          </div>
        ) : products.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-gray-600">No products found</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="table-header">Image</th>
                    <th className="table-header">Name</th>
                    <th className="table-header">Category</th>
                    <th className="table-header">Price</th>
                    <th className="table-header">Stock</th>
                    <th className="table-header">Featured</th>
                    <th className="table-header">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {products.map((product) => (
                    <tr key={product.id} className="hover:bg-gray-50">
                      <td className="table-cell">
                        <img
                          src={product.images?.[0] || '/placeholder-product.jpg'}
                          alt={product.name}
                          className="w-16 h-16 object-cover rounded-lg"
                        />
                      </td>
                      <td className="table-cell">
                        <div>
                          <div className="font-medium text-gray-900">{product.name}</div>
                          <div className="text-sm text-gray-500">{product.material}</div>
                        </div>
                      </td>
                      <td className="table-cell">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {product.category}
                        </span>
                      </td>
                      <td className="table-cell">
                        <div className="text-sm text-gray-900">${product.price}</div>
                        {product.originalPrice && product.originalPrice > product.price && (
                          <div className="text-sm text-gray-500 line-through">
                            ${product.originalPrice}
                          </div>
                        )}
                      </td>
                      <td className="table-cell">
                        <span className="text-sm text-gray-900">
                          {product.availableSizes?.length || 0} sizes
                        </span>
                      </td>
                      <td className="table-cell">
                        {product.isFeatured ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            Featured
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            Regular
                          </span>
                        )}
                      </td>
                      <td className="table-cell">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleEdit(product)}
                            className="text-blue-600 hover:text-blue-900 p-1"
                            title="Edit"
                          >
                            <PencilIcon className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(product)}
                            className="text-red-600 hover:text-red-900 p-1"
                            title="Delete"
                          >
                            <TrashIcon className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {pagination.total > pagination.limit && (
              <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
                <div className="flex-1 flex justify-between sm:hidden">
                  <button
                    onClick={() => handlePageChange(pagination.page - 1)}
                    disabled={pagination.page === 1}
                    className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => handlePageChange(pagination.page + 1)}
                    disabled={pagination.page * pagination.limit >= pagination.total}
                    className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
                <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700">
                      Showing{' '}
                      <span className="font-medium">{(pagination.page - 1) * pagination.limit + 1}</span>
                      {' '}to{' '}
                      <span className="font-medium">
                        {Math.min(pagination.page * pagination.limit, pagination.total)}
                      </span>
                      {' '}of{' '}
                      <span className="font-medium">{pagination.total}</span>
                      {' '}results
                    </p>
                  </div>
                  <div>
                    <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                      {Array.from({ length: Math.ceil(pagination.total / pagination.limit) }, (_, i) => i + 1).map((page) => (
                        <button
                          key={page}
                          onClick={() => handlePageChange(page)}
                          className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                            page === pagination.page
                              ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                              : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                          }`}
                        >
                          {page}
                        </button>
                      ))}
                    </nav>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Create Product Modal */}
      {showCreateModal && (
        <ProductModal
          title="Create New Product"
          formData={formData}
          setFormData={setFormData}
          onSubmit={createProduct}
          onClose={() => setShowCreateModal(false)}
          categories={categories}
          materials={materials}
          sizes={sizes}
        />
      )}

      {/* Edit Product Modal */}
      {showEditModal && (
        <ProductModal
          title="Edit Product"
          formData={formData}
          setFormData={setFormData}
          onSubmit={updateProduct}
          onClose={() => setShowEditModal(false)}
          categories={categories}
          materials={materials}
          sizes={sizes}
          isEdit={true}
        />
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3 text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Delete Product</h3>
              <p className="text-sm text-gray-500 mb-6">
                Are you sure you want to delete "{selectedProduct?.name}"? This action cannot be undone.
              </p>
              <div className="flex justify-center space-x-4">
                <button
                  onClick={deleteProduct}
                  className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
                >
                  Delete
                </button>
                <button
                  onClick={() => setShowDeleteModal(false)}
                  className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Product Modal Component
const ProductModal = ({ 
  title, 
  formData, 
  setFormData, 
  onSubmit, 
  onClose, 
  categories, 
  materials, 
  sizes, 
  isEdit = false 
}) => {
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-2xl font-bold text-gray-900">{title}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        <form onSubmit={onSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Product Name *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="input"
                  placeholder="Enter product name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description *
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  required
                  rows={4}
                  className="input"
                  placeholder="Enter product description"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Price *
                  </label>
                  <input
                    type="number"
                    name="price"
                    value={formData.price}
                    onChange={handleChange}
                    required
                    step="0.01"
                    min="0"
                    className="input"
                    placeholder="0.00"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Original Price
                  </label>
                  <input
                    type="number"
                    name="originalPrice"
                    value={formData.originalPrice}
                    onChange={handleChange}
                    step="0.01"
                    min="0"
                    className="input"
                    placeholder="0.00"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Discount (%)
                </label>
                <input
                  type="number"
                  name="discount"
                  value={formData.discount}
                  onChange={handleChange}
                  min="0"
                  max="100"
                  className="input"
                  placeholder="0"
                />
              </div>
            </div>

            {/* Category and Details */}
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category *
                  </label>
                  <select
                    name="category"
                    value={formData.category}
                    onChange={handleChange}
                    required
                    className="input"
                  >
                    <option value="">Select Category</option>
                    {categories.map(cat => (
                      <option key={cat.id} value={cat.slug}>{cat.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Material *
                  </label>
                  <select
                    name="material"
                    value={formData.material}
                    onChange={handleChange}
                    required
                    className="input"
                  >
                    <option value="">Select Material</option>
                    {materials.map(mat => (
                      <option key={mat} value={mat}>{mat}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sizes *
                </label>
                <input
                  type="text"
                  name="sizes"
                  value={formData.sizes}
                  onChange={handleChange}
                  required
                  className="input"
                  placeholder="S, M, L, XL (comma separated)"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Images *
                </label>
                <input
                  type="text"
                  name="images"
                  value={formData.images}
                  onChange={handleChange}
                  required
                  className="input"
                  placeholder="https://example.com/image1.jpg, https://example.com/image2.jpg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tags
                </label>
                <input
                  type="text"
                  name="tags"
                  value={formData.tags}
                  onChange={handleChange}
                  className="input"
                  placeholder="tag1, tag2, tag3 (comma separated)"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Care Instructions
                </label>
                <textarea
                  name="care"
                  value={formData.care}
                  onChange={handleChange}
                  rows={2}
                  className="input"
                  placeholder="Enter care instructions"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Features
                </label>
                <input
                  type="text"
                  name="features"
                  value={formData.features}
                  onChange={handleChange}
                  className="input"
                  placeholder="feature1, feature2, feature3 (comma separated)"
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="isFeatured"
                  checked={formData.isFeatured}
                  onChange={handleChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-900">
                  Featured Product
                </label>
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              {isEdit ? 'Update Product' : 'Create Product'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Products;
