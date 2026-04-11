# 🛍️ E-Commerce Management System

A modern, open e-commerce management system built with React and Tailwind CSS.

## 🚀 Features

- **Product Management**: Create, read, update, and delete products
- **Category Management**: Organize products by categories
- **Order Management**: Track and manage customer orders
- **User Management**: Manage user accounts and roles
- **Analytics Dashboard**: View business insights and statistics
- **Responsive Design**: Works on all devices

## 🛠️ Technology Stack

- **Frontend**: React 18, Tailwind CSS, Heroicons
- **Backend**: Python FastAPI, MongoDB
- **Authentication**: None (Open Access)

## 📱 Getting Started

### Prerequisites
- Node.js 16+ 
- npm or yarn
- Backend server running on `http://localhost:8000`

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm run dev
   ```

3. **Open your browser**:
   Navigate to `http://localhost:3000`

## 🎯 Available Routes

- `/` - Dashboard (Overview and statistics)
- `/products` - Product management (CRUD operations)
- `/categories` - Category management
- `/orders` - Order tracking and management
- `/users` - User management
- `/analytics` - Business analytics and reports

## 🔧 Development

### Project Structure
```
src/
├── components/     # Reusable UI components
├── layouts/        # Layout components
├── pages/          # Page components
├── services/       # API service layer
└── styles/         # CSS and styling
```

### Key Components
- **AdminLayout**: Main layout with sidebar navigation
- **Dashboard**: Overview page with statistics
- **Products**: Complete product management interface
- **Categories**: Category management system
- **Orders**: Order tracking and management
- **Users**: User management interface
- **Analytics**: Business intelligence dashboard

## 🎨 Styling

The application uses **Tailwind CSS** for styling with:
- Responsive design
- Modern UI components
- Consistent color scheme
- Interactive elements

## 📊 API Integration

All API calls are made to the backend at `http://localhost:8000/api/v1/`:
- Products: `/products`
- Categories: `/categories`
- Orders: `/orders`
- Users: `/users`
- Analytics: `/analytics`

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Serve Production Build
```bash
npm run preview
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

---

**🎉 Enjoy managing your e-commerce business with this powerful, open system!**
