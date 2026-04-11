# Restaurant Management System - Frontend

A modern, responsive web application for restaurant management built with vanilla HTML, CSS, and JavaScript. This frontend provides a complete interface for managing tables, orders, menu items, and restaurant analytics.

## 🚀 Features

### Phase 1 Implementation (Complete)

#### Table Management
- **12-Table Grid System**: 3x4 layout showing all restaurant tables
- **Real-time Status Updates**: Visual indicators for idle, open, and paid tables
- **Table Operations**: Click to view orders, open new orders
- **Order Summary**: Display item count and total amount per table

#### Menu Management
- **Category-based Display**: Organized by veg/non-veg/beverages with sub-categories
- **Search Functionality**: Real-time search across all menu items
- **Out-of-Stock Management**: Toggle item availability with visual indicators
- **Menu Operations**: Add items to orders, manage inventory

#### Order Management
- **Order Creation**: Add items to table orders with quantity selection
- **Order Viewing**: Detailed order display with item breakdown
- **Order Editing**: Modify quantities, remove items
- **Real-time Updates**: Automatic order total calculations

#### Payment Processing
- **Payment Methods**: Support for cash and online payments
- **Payment Confirmation**: Secure payment workflow with confirmation
- **Order Completion**: Automatic status updates after payment

#### Admin Dashboard
- **Analytics Overview**: Revenue, orders, and item statistics
- **Recent Orders**: Latest order activity with detailed view
- **Payment Analytics**: Cash vs online payment breakdown
- **Reporting**: Generate and export restaurant reports

#### User Experience
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Real-time Updates**: Auto-refresh data every 30 seconds
- **Loading States**: Visual feedback during data operations
- **Error Handling**: Comprehensive error messages and recovery
- **Modern UI**: Clean, intuitive interface with Bootstrap 5

## 🛠️ Technology Stack

- **Frontend Framework**: Vanilla HTML/CSS/JavaScript (No Node.js required)
- **UI Framework**: Bootstrap 5.3.0
- **Icons**: Bootstrap Icons 1.10.0
- **Architecture**: Modular JavaScript with ES6 classes
- **API Communication**: RESTful API calls to FastAPI backend
- **Responsive Design**: Mobile-first approach

## 📁 Project Structure

```
frontend/
├── index.html              # Main HTML file
├── css/
│   └── styles.css          # Custom CSS styles
├── js/
│   ├── api.js             # API service layer
│   ├── app.js             # Main application controller
│   ├── tables.js          # Tables management module
│   ├── menu.js            # Menu management module
│   ├── orders.js          # Orders management module
│   └── admin.js           # Admin dashboard module
└── README.md              # This file
```

## 🚀 Getting Started

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- FastAPI backend running on `http://localhost:8000`

### Installation
1. **Clone the repository** (if not already done)
2. **Start the backend server**:
   ```bash
   cd backend
   python main.py
   ```
3. **Open the frontend**:
   - Navigate to `frontend/index.html`
   - Open in your web browser
   - Or serve using a local server:
     ```bash
     cd frontend
     python -m http.server 8080
     # Then visit http://localhost:8080
     ```

## 📖 Usage Guide

### Table Management
1. **View Tables**: Navigate to the "Tables" tab to see all 12 tables
2. **Open Order**: Click on any table to open or view its order
3. **Add Items**: Use the menu to add items to the current order
4. **Process Payment**: Click "Pay Order" to complete the transaction

### Menu Management
1. **Browse Menu**: Navigate to the "Menu" tab to view all items
2. **Filter by Category**: Use the category sidebar to filter items
3. **Search Items**: Use the search bar to find specific items
4. **Manage Stock**: Toggle out-of-stock status for items

### Order Management
1. **View Orders**: Navigate to the "Orders" tab to see all orders
2. **Order Details**: Click on any order to view detailed information
3. **Process Payments**: Pay open orders directly from the orders list

### Admin Dashboard
1. **View Analytics**: Navigate to the "Admin" tab for system overview
2. **Monitor Metrics**: Check revenue, orders, and payment statistics
3. **Recent Activity**: View latest orders and their status
4. **Generate Reports**: Export restaurant data for analysis

## 🔧 Configuration

### Backend URL
The frontend is configured to connect to the backend at `http://localhost:8000`. To change this:

1. Open `frontend/js/api.js`
2. Modify the `baseURL` in the API constructor:
   ```javascript
   constructor() {
       this.baseURL = 'http://your-backend-url:port';
   }
   ```

### Auto-refresh Interval
The application automatically refreshes data every 30 seconds. To change this:

1. Open `frontend/js/app.js`
2. Modify the refresh interval in the `init()` method:
   ```javascript
   // Auto-refresh data every 30 seconds
   setInterval(() => this.refreshCurrentPage(), 30000); // Change 30000 to desired milliseconds
   ```

## 🎨 Customization

### Styling
- **Colors**: Modify CSS variables in `frontend/css/styles.css`
- **Layout**: Adjust Bootstrap classes in HTML files
- **Icons**: Replace Bootstrap Icons with custom icons

### Functionality
- **New Features**: Add new JavaScript modules following the existing pattern
- **API Integration**: Extend the API service layer in `api.js`
- **UI Components**: Create reusable components in separate modules

## 🔌 API Integration

The frontend integrates with the following backend endpoints:

### Menu Endpoints
- `GET /menu` - List all menu items
- `GET /menu/categories` - Get menu categories
- `PUT /menu/out-of-stock` - Toggle out-of-stock status

### Table Endpoints
- `GET /tables` - Get all table statuses
- `POST /tables/{num}/order` - Open order for table

### Order Endpoints
- `GET /orders/{id}` - Get order details
- `POST /orders/{id}/items` - Add item to order
- `PATCH /orders/{id}/items/{item_id}` - Update item quantity
- `DELETE /orders/{id}/items/{item_id}` - Remove item from order
- `POST /orders/{id}/pay` - Process payment

### Admin Endpoints
- `GET /admin/orders` - Get all orders with filters
- `GET /admin/metrics` - Get analytics data

## 🐛 Troubleshooting

### Common Issues

1. **Backend Connection Error**
   - Ensure the FastAPI backend is running on `http://localhost:8000`
   - Check browser console for CORS errors
   - Verify network connectivity

2. **Data Not Loading**
   - Check browser console for JavaScript errors
   - Verify API endpoints are accessible
   - Ensure database is properly seeded

3. **Payment Processing Issues**
   - Verify order has items before payment
   - Check payment method selection
   - Ensure order status is "open"

### Debug Mode
Enable debug logging by opening browser console (F12) to see detailed error messages and API calls.

## 📱 Browser Support

- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

## 🔄 Updates and Maintenance

### Auto-refresh
- Data refreshes automatically every 30 seconds
- Manual refresh available via browser refresh
- Real-time updates for critical operations

### Error Recovery
- Automatic retry for failed API calls
- Graceful degradation for network issues
- User-friendly error messages

## 📄 License

This frontend is part of the Restaurant Management System project.

## 🤝 Contributing

1. Follow the existing code structure and patterns
2. Test changes across different browsers
3. Ensure responsive design compatibility
4. Update documentation for new features

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review browser console for errors
3. Verify backend connectivity
4. Check API endpoint documentation

---

**Last Updated**: December 19, 2024
**Version**: 1.0.0
**Phase**: 1 Complete
