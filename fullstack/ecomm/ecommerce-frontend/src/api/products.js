import axios from 'axios'
import { config } from '../config/env.js'

const API_URL = config.API_URL

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
})

export const getProducts = async (filters = {}) => {
  try {
    const params = new URLSearchParams()
    
    if (filters.category) params.append('category', filters.category)
    if (filters.size) params.append('size', filters.size)
    if (filters.price_min) params.append('price_min', filters.price_min)
    if (filters.price_max) params.append('price_max', filters.price_max)
    if (filters.is_featured) params.append('is_featured', filters.is_featured)
    
    const response = await api.get(`/api/v1/products?${params.toString()}`)
    return response.data
  } catch (error) {
    console.error('Error fetching products:', error)
    throw error
  }
}

export const getProductById = async (id) => {
  try {
    const response = await api.get(`/api/v1/products/${id}`)
    return response.data
  } catch (error) {
    console.error('Error fetching product:', error)
    throw error
  }
}

export const searchProducts = async (query) => {
  try {
    const response = await api.get(`/api/v1/products/search?q=${encodeURIComponent(query)}`)
    return response.data
  } catch (error) {
    console.error('Error searching products:', error)
    throw error
  }
}

export const getFeaturedProducts = async () => {
  try {
    const response = await api.get('/api/v1/products?is_featured=true&limit=6')
    return response.data
  } catch (error) {
    console.error('Error fetching featured products:', error)
    throw error
  }
}
