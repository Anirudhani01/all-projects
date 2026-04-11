// Environment configuration
// In production, these would be set via environment variables
export const config = {
  API_URL: 'https://your-backend.com',
  // Add other configuration values here
}

// For development, you can override these values
if (import.meta.env.DEV) {
  config.API_URL = 'http://localhost:8000' // Example local backend URL
}
