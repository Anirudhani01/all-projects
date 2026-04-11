import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const authAPI = {
  login: (credentials) => api.post('/api/v1/auth/login', credentials),
  register: (userData) => api.post('/api/v1/auth/register', userData),
  refresh: (refreshToken) => api.post('/api/v1/auth/refresh', { refresh_token: refreshToken }),
  logout: () => api.post('/api/v1/auth/logout'),
  me: () => api.get('/api/v1/auth/me'),
};

export const userAPI = {
  getProfile: () => api.get('/api/v1/users/me'),
  updateProfile: (userData) => api.put('/api/v1/users/me', userData),
  getUser: (userId) => api.get(`/api/v1/users/${userId}`),
};

export const creditLimitAPI = {
  getCreditLimit: () => api.get('/api/v1/credit-limits/me'),
  applyCreditLimit: (applicationData) => api.post('/api/v1/credit-limits/apply', applicationData),
  updateCreditLimit: (limitId, updateData) => api.put(`/api/v1/credit-limits/${limitId}`, updateData),
};

export const transactionAPI = {
  getTransactions: (params) => api.get('/api/v1/transactions', { params }),
  getTransaction: (transactionId) => api.get(`/api/v1/transactions/${transactionId}`),
  createTransaction: (transactionData) => api.post('/api/v1/transactions', transactionData),
  updateTransaction: (transactionId, updateData) => api.put(`/api/v1/transactions/${transactionId}`, updateData),
};

export const merchantAPI = {
  getMerchants: (params) => api.get('/api/v1/merchants', { params }),
  getMerchant: (merchantId) => api.get(`/api/v1/merchants/${merchantId}`),
  registerMerchant: (merchantData) => api.post('/api/v1/merchants', merchantData),
};

export default api;
