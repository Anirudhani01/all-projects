import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { toast } from 'react-toastify'
import FilterSidebar from '../components/FilterSidebar'
import TestImageCard from '../components/TestImageCard'
import { getProducts, searchProducts } from '../api/products'

const Products = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [products, setProducts] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [hasMore, setHasMore] = useState(true)
  const [page, setPage] = useState(1)
  
  const [filters, setFilters] = useState({
    size: '',
    color: '',
    price_min: '',
    price_max: '',
    material: ''
  })

  const searchQuery = searchParams.get('search') || ''

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setIsLoading(true)
        setError(null)
        setPage(1)
        
        // For demo purposes, using mock data since backend isn't available
        const mockProducts = generateMockProducts(20)
        setProducts(mockProducts)
        setHasMore(mockProducts.length === 20)
        
        // Uncomment when backend is available:
        // let productsData
        // if (searchQuery) {
        //   productsData = await searchProducts(searchQuery)
        // } else {
        //   productsData = await getProducts({ ...filters, page: 1 })
        // }
        // setProducts(productsData.products || productsData)
        // setHasMore(productsData.hasMore || false)
        
      } catch (err) {
        console.error('Error fetching products:', err)
        setError('Failed to load products')
        toast.error('Failed to load products')
      } finally {
        setIsLoading(false)
      }
    }

    fetchProducts()
  }, [filters, searchQuery])

  const generateMockProducts = (count) => {
    const names = [
      'Floral Summer Dress',
      'Elegant White Blouse', 
      'Classic Denim Jacket',
      'Maxi Evening Dress',
      'Professional Pencil Skirt',
      'Cozy Knit Sweater',
      'Casual T-Shirt',
      'Formal Blazer',
      'Summer Shorts',
      'Winter Coat'
    ]
    
    const mockProducts = []
    
    for (let i = 0; i < count; i++) {
      const imageIndex = i % 3 // Use our 3 new images
      const imagePaths = [
        '/images/products/perky-girl-stylish-glasses-stares-amazement-walking-pink-wall-brunette-culottes-orange-blouse-posing-with-red-handbag.jpg',
        '/images/products/portrait-young-stylish-girl-model-casual-summer-clothes-brown-hat-with-natural-makeup-glasses-isolated.jpg',
        '/images/products/smiling-lady-model-short-blue-dress-hat-barfoot-white.jpg'
      ]
      
      mockProducts.push({
        id: i + 1,
        name: names[i % names.length],
        price: Math.floor(Math.random() * 150) + 29.99,
        image: imagePaths[imageIndex],
        size: ['XS', 'S', 'M', 'L', 'XL', 'XXL'][Math.floor(Math.random() * 6)],
        color: ['black', 'white', 'red', 'blue', 'green', 'pink', 'purple', 'yellow'][Math.floor(Math.random() * 8)],
        material: ['cotton', 'polyester', 'silk', 'wool', 'linen', 'denim'][Math.floor(Math.random() * 6)]
      })
    }
    
    return mockProducts
  }

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters)
  }

  const handleClearFilters = () => {
    setFilters({
      size: '',
      color: '',
      price_min: '',
      price_max: '',
      material: ''
    })
  }

  const handleLoadMore = async () => {
    try {
      setPage(prev => prev + 1)
      
      // For demo purposes, generating more mock products
      const moreProducts = generateMockProducts(20)
      setProducts(prev => [...prev, ...moreProducts])
      setHasMore(moreProducts.length === 20)
      
      // Uncomment when backend is available:
      // const nextPageProducts = await getProducts({ ...filters, page: page + 1 })
      // setProducts(prev => [...prev, ...(nextPageProducts.products || nextPageProducts)])
      // setHasMore(nextPageProducts.hasMore || false)
      
    } catch (err) {
      console.error('Error loading more products:', err)
      toast.error('Failed to load more products')
    }
  }

  const filteredProducts = products.filter(product => {
    if (filters.size && product.size !== filters.size) return false
    if (filters.color && product.color !== filters.color) return false
    if (filters.material && product.material !== filters.material) return false
    if (filters.price_min && product.price < parseFloat(filters.price_min)) return false
    if (filters.price_max && product.price > parseFloat(filters.price_max)) return false
    return true
  })

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Something went wrong
          </h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {searchQuery ? `Search Results for "${searchQuery}"` : 'All Products'}
          </h1>
          <p className="text-gray-600">
            {filteredProducts.length} products found
          </p>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filter Sidebar */}
          <div className="lg:w-64 flex-shrink-0">
            <FilterSidebar
              filters={filters}
              onFilterChange={handleFilterChange}
              onClearFilters={handleClearFilters}
            />
          </div>

          {/* Products Grid */}
          <div className="flex-1">
            {isLoading && page === 1 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {[...Array(6)].map((_, index) => (
                  <div key={index} className="animate-pulse">
                    <div className="bg-gray-200 aspect-square rounded-lg mb-4"></div>
                    <div className="h-4 bg-gray-200 rounded mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  </div>
                ))}
              </div>
            ) : filteredProducts.length > 0 ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {filteredProducts.map((product) => (
                    <TestImageCard key={product.id} product={product} />
                  ))}
                </div>

                {/* Load More Button */}
                {hasMore && (
                  <div className="text-center mt-12">
                    <button
                      onClick={handleLoadMore}
                      className="btn-primary text-lg px-8 py-3"
                    >
                      Load More Products
                    </button>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-16">
                <div className="text-gray-400 mb-4">
                  <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No products found
                </h3>
                <p className="text-gray-600 mb-6">
                  Try adjusting your filters or search terms
                </p>
                <button
                  onClick={handleClearFilters}
                  className="btn-primary"
                >
                  Clear Filters
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Products
