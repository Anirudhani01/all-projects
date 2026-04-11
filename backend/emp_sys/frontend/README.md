# Employee Management System - Frontend

A modern React-based frontend for the Employee Management System with dark theme and JWT authentication.

## Features (Updated)

- Dark and Minimal White Theme: Switchable, modern UI
- JWT Authentication: Secure login/logout with token storage
- Responsive Design: Works on all devices
- Employee Dashboard: Paginated, searchable, filterable employee list
- Add/Edit Employee: Modal forms with validation
- Delete Employee: Confirmation dialog
- Image Upload: Employee photo upload and preview
- Statistics Cards: Key employee metrics
- Search Bar: Real-time search and filtering
- Pagination Controls: Configurable page size
- Status Badges: Color-coded for employee attributes
- Error Handling: User-friendly error messages
- CORS: Integrated with backend
- Robust Responsive Design: Layout, text, and buttons remain visually consistent at any zoom or window size using rem/clamp units, fluid containers, and responsive tables/buttons.

## Technical Changes (Summary)
- Created React-based frontend (later converted to standalone HTML/JS/CSS)
- Implemented login and dashboard pages
- Added modal forms for add/edit employee
- Added image upload and preview
- Added statistics and search features
- Added responsive and minimal UI/UX
- Integrated with backend API endpoints
- Implemented robust responsive web design with rem/clamp units, fluid containers, flexible buttons, and responsive tables.

## Tech Stack

- **React 18**: Modern React with hooks
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **CSS3**: Custom styling with CSS variables and animations
- **Responsive Design**: Mobile-first approach

## Setup Instructions

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

## Usage

### Login

1. Use the demo credentials:
   - **Username**: `admin`
   - **Password**: `admin123`

2. Click "Sign In" to access the dashboard

### Dashboard Features

- **Statistics Cards**: View total employees, gender distribution, and average age
- **Search**: Search employees by name using the search bar
- **Pagination**: Navigate through employee data with configurable page sizes
- **Responsive Table**: View all employee details in a responsive table
- **Status Badges**: Color-coded badges for payment tiers, gender, and status

## API Integration

The frontend integrates with all backend endpoints:

- `POST /auth/login` - User authentication
- `GET /me` - Get current user info
- `GET /employees/` - Get paginated employee list
- `GET /employees/search/` - Search employees by name

## Design Features

### Dark Theme
- Primary background: `#0a0a0a`
- Secondary background: `#1a1a1a`
- Accent colors: Purple gradient (`#6366f1` to `#4f46e5`)
- Text colors: White and gray shades

### Animations
- Smooth hover effects on cards and buttons
- Loading spinners
- Fade-in animations
- Gradient text effects

### Responsive Design
- Mobile-first approach
- Breakpoints at 480px, 768px, and 1024px
- Flexible grid layouts
- Responsive table with horizontal scroll

## File Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Login.js
│   │   ├── Login.css
│   │   ├── EmployeeDashboard.js
│   │   └── EmployeeDashboard.css
│   ├── context/
│   │   └── AuthContext.js
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── index.css
├── package.json
└── README.md
```

## Customization

### Colors
Modify the CSS variables in `src/index.css`:

```css
:root {
  --bg-primary: #0a0a0a;
  --bg-secondary: #1a1a1a;
  --accent-primary: #6366f1;
  --accent-secondary: #4f46e5;
  /* ... other variables */
}
```

### API Configuration
The frontend is configured to proxy requests to `http://localhost:8000`. To change this:

1. Update the `proxy` field in `package.json`
2. Or modify the base URL in API calls

## Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Adding New Features

1. Create new components in `src/components/`
2. Add corresponding CSS files
3. Update routing in `App.js` if needed
4. Test responsiveness across different screen sizes

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Lazy loading for better performance
- Optimized CSS with CSS variables
- Efficient pagination to handle large datasets
- Responsive images and icons

## Security

- JWT tokens stored in localStorage
- Automatic token validation
- Protected routes
- Secure API communication

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure backend has CORS configured
2. **API Connection**: Verify backend is running on port 8000
3. **Authentication**: Check if admin user exists in database

### Development Tips

- Use browser dev tools to inspect network requests
- Check console for JavaScript errors
- Test on different screen sizes
- Verify API responses match expected format

## Contributing

1. Follow the existing code style
2. Test on multiple devices
3. Ensure responsive design works
4. Update documentation as needed

## License

This project is part of the Employee Management System.
