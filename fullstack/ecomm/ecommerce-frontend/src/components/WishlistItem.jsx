import { useState } from 'react'
import { toast } from 'react-toastify'
import { removeFromWishlist } from '../utils/wishlist'

const WishlistItem = ({ product, onRemove }) => {
  const [isLoading, setIsLoading] = useState(false)
  const [imageError, setImageError] = useState(false)

  const handleRemove = async () => {
    setIsLoading(true)
    try {
      await removeFromWishlist(product.id)
      onRemove(product.id)
      toast.success('Removed from wishlist')
    } catch (error) {
      toast.error('Failed to remove from wishlist')
    } finally {
      setIsLoading(false)
    }
  }

  const handleImageError = () => {
    setImageError(true)
  }

  return (
    <div className="flex items-center space-x-4 p-4 bg-white rounded-lg shadow-sm border border-gray-100">
      {/* Product Image */}
      <div className="flex-shrink-0">
        {!imageError && product.image ? (
          <img
            src={product.image}
            alt={product.name}
            className="w-20 h-20 object-cover rounded-lg"
            onError={handleImageError}
          />
        ) : (
          <div className="w-20 h-20 bg-gray-100 rounded-lg flex items-center justify-center">
            <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
            </svg>
          </div>
        )}
      </div>

      {/* Product Info */}
      <div className="flex-1 p-6 flex flex-col justify-between">
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            {product.name}
          </h3>
          
          <div className="flex flex-wrap gap-2 mb-4">
            {product.size && (
              <span className="px-3 py-1 bg-primary-100 text-primary-800 text-sm rounded-full">
                Size: {product.size}
              </span>
            )}
            {product.color && (
              <span className="px-3 py-1 bg-primary-100 text-primary-800 text-sm rounded-full">
                Color: {product.color}
              </span>
            )}
            {product.material && (
              <span className="px-3 py-1 bg-primary-100 text-primary-800 text-sm rounded-full">
                {product.material}
              </span>
            )}
          </div>

          <p className="text-gray-600 mb-4 line-clamp-3">
            {product.description || 'No description available for this product.'}
          </p>
        </div>

        {/* Price and Actions */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <span className="text-2xl font-bold text-primary-600">
              ${product.price}
            </span>
            {product.originalPrice && product.originalPrice > product.price && (
              <span className="text-lg text-gray-500 line-through">
                ${product.originalPrice}
              </span>
            )}
          </div>

          <div className="flex space-x-3">
            <button className="btn-primary">
              Add to Cart
            </button>
            <button
              onClick={handleRemove}
              disabled={isLoading}
              className="btn-secondary text-red-600 hover:bg-red-100 hover:text-red-700"
            >
              {isLoading ? (
                <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              ) : (
                'Remove'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default WishlistItem
