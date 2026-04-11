import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'react-toastify'
import HeroBanner from '../components/HeroBanner'


import TestImageCard from '../components/TestImageCard'
import { getFeaturedProducts } from '../api/products'

const Home = () => {
  const [featuredProducts, setFeaturedProducts] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchFeaturedProducts = async () => {
      try {
        setIsLoading(true)
        setError(null)
        
        // Using the 3 new fashion model images
        const mockProducts = [
          {
            id: 1,
            name: "Floral Summer Dress",
            price: 89.99,
            image: `/images/products/perky-girl-stylish-glasses-stares-amazement-walking-pink-wall-brunette-culottes-orange-blouse-posing-with-red-handbag.jpg`,
            size: "M",
            color: "Blue"
          },
          {
            id: 2,
            name: "Elegant White Blouse",
            price: 59.99,
            image: `/images/products/portrait-young-stylish-girl-model-casual-summer-clothes-brown-hat-with-natural-makeup-glasses-isolated.jpg`,
            size: "S",
            color: "White"
          },
          {
            id: 3,
            name: "Classic Denim Jacket",
            price: 129.99,
            image: `/images/products/smiling-lady-model-short-blue-dress-hat-barfoot-white.jpg`,
            size: "L",
            color: "Blue"
          },
          {
            id: 4,
            name: "Maxi Evening Dress",
            price: 149.99,
            image: `/images/products/perky-girl-stylish-glasses-stares-amazement-walking-pink-wall-brunette-culottes-orange-blouse-posing-with-red-handbag.jpg`,
            size: "M",
            color: "Black"
          },
          {
            id: 5,
            name: "Professional Pencil Skirt",
            price: 79.99,
            image: `/images/products/portrait-young-stylish-girl-model-casual-summer-clothes-brown-hat-with-natural-makeup-glasses-isolated.jpg`,
            size: "S",
            color: "Gray"
          },
          {
            id: 6,
            name: "Cozy Knit Sweater",
            price: 99.99,
            image: `/images/products/smiling-lady-model-short-blue-dress-hat-barfoot-white.jpg`,
            size: "L",
            color: "Beige"
          }
        ]
        
        setFeaturedProducts(mockProducts)
        
        // Debug logging
        console.log('Home page - Featured products set:', mockProducts)
        console.log('First product image URL:', mockProducts[0]?.image)
        
        // Uncomment when backend is available:
        // const products = await getFeaturedProducts()
        // setFeaturedProducts(products)
        
      } catch (err) {
        console.error('Error fetching featured products:', err)
        setError('Failed to load featured products')
        toast.error('Failed to load featured products')
      } finally {
        setIsLoading(false)
      }
    }

    fetchFeaturedProducts()
  }, [])

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
            Try again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Banner */}
      <HeroBanner />
      
      {/* Featured Products Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Featured Products
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Discover our most popular and trending items. Each piece is carefully selected to bring you the latest in women's fashion.
            </p>
          </div>
          
          {isLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="bg-gray-200 aspect-square rounded-lg mb-4"></div>
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
                {featuredProducts.map((product) => (
                  <TestImageCard key={product.id} product={product} />
                ))}
              </div>
              
              <div className="text-center">
                <Link 
                  to="/products" 
                  className="btn-primary text-lg px-8 py-3"
                >
                  View All Products
                </Link>
              </div>
            </>
          )}
        </div>
      </section>
    </div>
  )
}

export default Home
