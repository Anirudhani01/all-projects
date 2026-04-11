# Women's Fashion E-Commerce Frontend

A modern, responsive e-commerce website built with React.js and Tailwind CSS, designed specifically for women's clothing.

## Features

- **Landing Page**: Hero banner with featured products
- **Product Browsing**: Grid view with filters and search functionality
- **Wishlist**: Client-side wishlist stored in localStorage
- **Responsive Design**: Optimized for desktop and mobile devices
- **Modern UI**: Clean, feminine aesthetic with smooth animations

## Tech Stack

- **Frontend**: React.js 18
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **Routing**: React Router DOM
- **HTTP Client**: Axios
- **Notifications**: React Toastify
- **Deployment**: Vercel (planned)

## Current Status

🎉 **Major Milestone Achieved!** 

We have successfully completed **Phases 1-3** of the e-commerce website development:
- ✅ **Phase 1**: Complete project setup with Vite, React, Tailwind CSS
- ✅ **Phase 2**: All components and pages implemented
- ✅ **Phase 3**: Responsive design and styling complete
- 🔄 **Phase 4**: Testing framework setup (in progress)
- 🚀 **Phase 5**: Deployment configuration ready

The application is now fully functional with:
- Beautiful, responsive landing page
- Product browsing with advanced filters
- Client-side wishlist functionality
- Modern, feminine aesthetic design
- Mobile-first responsive layout

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env.local` file with your backend API URL:
   ```
   VITE_API_URL=https://your-backend.com
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
src/
├── components/     # Reusable UI components
├── pages/         # Page components
├── api/           # API utilities
├── utils/         # Helper functions
└── assets/        # Static assets
```

## API Endpoints

The frontend expects the following backend API endpoints:

- `GET /api/v1/products` - Get products with filters
- `GET /api/v1/products/{id}` - Get product by ID
- `GET /api/v1/products/search?q={query}` - Search products

## Development Phases

This project follows a phase-wise development approach:

1. **Phase 1**: Project scaffolding and setup ✅
2. **Phase 2**: Component development ✅
3. **Phase 3**: Styling and responsiveness ✅
4. **Phase 4**: Testing (in progress)
5. **Phase 5**: Deployment (ready)

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Ensure responsive design works on all devices
4. Test wishlist functionality thoroughly

## License

MIT License
