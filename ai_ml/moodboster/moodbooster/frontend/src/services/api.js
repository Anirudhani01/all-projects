import axios from 'axios';

// API base URL - update this to match your backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`Response from ${response.config.url}:`, response.status);
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'Server error';
      return Promise.reject(new Error(message));
    } else if (error.request) {
      // Request was made but no response received
      return Promise.reject(new Error('Network error. Please check your connection.'));
    } else {
      // Something else happened
      return Promise.reject(new Error('An unexpected error occurred.'));
    }
  }
);

// API endpoints
export const moodAPI = {
  // Basic mood analysis
  analyzeMood: async (text) => {
    try {
      const response = await api.post('/api/v1/mood/analyze', { text });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  },

  // Enriched mood analysis
  getEnrichedMood: async (text) => {
    try {
      const response = await api.post('/api/v1/mood/analyze/enriched', { text });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  },

  // Complete analysis (Input + Middle + Decision + Output)
  getCompleteAnalysis: async (text) => {
    try {
      const response = await api.post('/api/v1/mood/complete-analysis', { text });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  },

  // Get mood insights
  getMoodInsights: async (userId) => {
    try {
      const response = await api.post('/api/v1/mood/insights', { user_id: userId });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  },

  // Quick booster
  getQuickBooster: async (mood) => {
    try {
      const response = await api.post('/api/v1/mood/quick-booster', { mood });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  }
};

export const diaryAPI = {
  // Create diary entry
  createEntry: async (entryData) => {
    try {
      const response = await api.post('/api/v1/diary/entries', entryData);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  },

  // Get diary entries
  getEntries: async (userId, page = 1, limit = 10) => {
    try {
      const response = await api.get(`/api/v1/diary/entries?user_id=${userId}&page=${page}&limit=${limit}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  },

  // Get single entry
  getEntry: async (entryId) => {
    try {
      const response = await api.get(`/api/v1/diary/entries/${entryId}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  },

  // Update entry
  updateEntry: async (entryId, entryData) => {
    try {
      const response = await api.put(`/api/v1/diary/entries/${entryId}`, entryData);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  },

  // Delete entry
  deleteEntry: async (entryId) => {
    try {
      await api.delete(`/api/v1/diary/entries/${entryId}`);
      return {
        success: true
      };
    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  }
};

export const externalAPI = {
  // Get music recommendations
  getMusic: async (mood, limit = 5) => {
    try {
      const response = await api.post('/api/v1/external/content/music', null, {
        params: { mood, limit }
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  },

  // Get video recommendations
  getVideos: async (mood, maxResults = 5) => {
    try {
      const response = await api.post('/api/v1/external/content/videos', null, {
        params: { mood, maxResults }
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  },

  // Get quotes
  getQuotes: async (mood, count = 3) => {
    try {
      const response = await api.post('/api/v1/external/content/quotes', null, {
        params: { mood, count }
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  },

  // Get unified content
  getUnifiedContent: async (mood, contentTypes, maxResults = 3) => {
    try {
      const response = await api.post('/api/v1/external/content/unified', {
        mood,
        content_types: contentTypes,
        max_results_per_type: maxResults
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  },

  // Health check
  checkHealth: async () => {
    try {
      const response = await api.get('/api/v1/external/health');
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  }
};

export const analyticsAPI = {
  // Get mood analytics
  getMoodAnalytics: async (userId, period = 'week') => {
    try {
      const response = await api.get(`/api/v1/analytics/mood?user_id=${userId}&period=${period}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  },

  // Get mood trends
  getMoodTrends: async (userId, days = 30) => {
    try {
      const response = await api.get(`/api/v1/analytics/trends?user_id=${userId}&days=${days}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  }
};

export default api;
