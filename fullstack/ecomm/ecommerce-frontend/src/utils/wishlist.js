const WISHLIST_KEY = 'ecommerce_wishlist'

export const getWishlist = () => {
  try {
    const wishlist = localStorage.getItem(WISHLIST_KEY)
    return wishlist ? JSON.parse(wishlist) : []
  } catch (error) {
    console.error('Error reading wishlist from localStorage:', error)
    return []
  }
}

export const addToWishlist = (productId) => {
  try {
    const wishlist = getWishlist()
    if (!wishlist.includes(productId)) {
      const newWishlist = [...wishlist, productId]
      localStorage.setItem(WISHLIST_KEY, JSON.stringify(newWishlist))
      return true
    }
    return false
  } catch (error) {
    console.error('Error adding to wishlist:', error)
    return false
  }
}

export const removeFromWishlist = (productId) => {
  try {
    const wishlist = getWishlist()
    const newWishlist = wishlist.filter(id => id !== productId)
    localStorage.setItem(WISHLIST_KEY, JSON.stringify(newWishlist))
    return true
  } catch (error) {
    console.error('Error removing from wishlist:', error)
    return false
  }
}

export const isInWishlist = (productId) => {
  const wishlist = getWishlist()
  return wishlist.includes(productId)
}

export const clearWishlist = () => {
  try {
    localStorage.removeItem(WISHLIST_KEY)
    return true
  } catch (error) {
    console.error('Error clearing wishlist:', error)
    return false
  }
}
