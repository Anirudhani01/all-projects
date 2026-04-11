import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'react-toastify'
import WishlistItem from '../components/WishlistItem'
import { getProductById } from '../api/products'
import { getWishlist } from '../utils/wishlist'

const Wishlist = () => {
  const [wishlistProducts, setWishlistProducts] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchWishlistProducts = async () => {
      try {
        setIsLoading(true)
        setError(null)
        
        const wishlistIds = getWishlist()
        
        if (wishlistIds.length === 0) {
          setWishlistProducts([])
          setIsLoading(false)
          return
        }

        // For demo purposes, using mock data since backend isn't available
        const mockProducts = generateMockWishlistProducts(wishlistIds)
        setWishlistProducts(mockProducts)
        
        // Uncomment when backend is available:
        // const products = await Promise.all(
        //   wishlistIds.map(id => getProductById(id))
        // )
        // setWishlistProducts(products)
        
      } catch (err) {
        console.error('Error fetching wishlist products:', err)
        setError('Failed to load wishlist products')
        toast.error('Failed to load wishlist products')
      } finally {
        setIsLoading(false)
      }
    }

    fetchWishlistProducts()
  }, [])

  const generateMockWishlistProducts = (ids) => {
    const names = [
      'Floral Summer Dress',
      'Elegant White Blouse', 
      'Classic Denim Jacket',
      'Maxi Evening Dress',
      'Professional Pencil Skirt',
      'Cozy Knit Sweater'
    ]
    
    const mockProducts = []
    
    ids.forEach((id, index) => {
      const imagePaths = [
        '/images/products/floral-dress.svg',
        '/images/products/white-blouse.svg',
        '/images/products/denim-jacket.svg',
        '/images/products/maxi-dress.svg',
        '/images/products/pencil-skirt.svg',
        '/images/products/knit-sweater.svg'
      ]
      
      mockProducts.push({
        id: id,
        name: names[index % names.length],
        price: Math.floor(Math.random() * 150) + 29.99,
        originalPrice: Math.random() > 0.7 ? Math.floor(Math.random() * 200) + 50 : null,
        image: imagePaths[index % imagePaths.length],
        size: ['XS', 'S', 'M', 'L', 'XL', 'XXL'][Math.floor(Math.random() * 6)],
        color: ['black', 'white', 'red', 'blue', 'green', 'pink', 'purple', 'yellow'][Math.floor(Math.random() * 8)],
        material: ['cotton', 'polyester', 'silk', 'wool', 'linen', 'denim'][Math.floor(Math.random() * 6)],
        description: "This is a beautiful product that you've added to your wishlist. It features high-quality materials and a timeless design that will complement any wardrobe."
      })
    })
    
    return mockProducts
  }

  const handleRemoveFromWishlist = (productId) => {
    setWishlistProducts(prev => prev.filter(product => product.id !== productId))
    toast.success('Product removed from wishlist')
  }

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
            My Wishlist
          </h1>
          <p className="text-gray-600">
            {wishlistProducts.length} item{wishlistProducts.length !== 1 ? 's' : ''} in your wishlist
          </p>
        </div>

        {isLoading ? (
          <div className="space-y-6">
            {[...Array(3)].map((_, index) => (
              <div key={index} className="animate-pulse">
                <div className="bg-white rounded-lg shadow-md p-6">
                  <div className="flex flex-col md:flex-row">
                    <div className="md:w-48 md:h-48 w-full h-48 bg-gray-200 rounded-lg mb-4 md:mb-0 md:mr-6"></div>
                    <div className="flex-1">
                      <div className="h-6 bg-gray-200 rounded mb-4"></div>
                      <div className="h-4 bg-gray-200 rounded mb-2 w-3/4"></div>
                      <div className="h-4 bg-gray-200 rounded mb-6 w-1/2"></div>
                      <div className="flex space-x-3">
                        <div className="h-10 bg-gray-200 rounded w-32"></div>
                        <div className="h-10 bg-gray-200 rounded w-24"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : wishlistProducts.length > 0 ? (
          <div className="space-y-6">
            {wishlistProducts.map((product) => (
              <WishlistItem
                key={product.id}
                product={product}
                onRemove={handleRemoveFromWishlist}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <div className="text-gray-400 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Your wishlist is empty
            </h3>
            <p className="text-gray-600 mb-6">
              Start adding products to your wishlist by browsing our collection
            </p>
            <Link
              to="/products"
              className="btn-primary"
            >
              Browse Products
            </Link>
          </div>
        )}

        {/* Call to Action */}
        {wishlistProducts.length > 0 && (
          <div className="mt-16 text-center">
            <div className="bg-white rounded-lg shadow-md p-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Ready to make your wishlist a reality?
              </h3>
              <p className="text-gray-600 mb-6">
                Add items to your cart and complete your purchase to bring these beautiful pieces home.
              </p>
              <Link
                to="/products"
                className="btn-primary text-lg px-8 py-3"
              >
                Continue Shopping
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Wishlist
