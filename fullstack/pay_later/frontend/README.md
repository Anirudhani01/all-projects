# Pay-Later Frontend

React frontend for the Pay-Later application.

## Features

- React 18 with modern hooks
- Redux Toolkit for state management
- React Router for navigation
- Axios for API communication
- Responsive design
- Modern CSS with utility classes

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Copy environment file:
```bash
cp env.example .env
```

3. Update `.env` with your configuration.

### Running the Application

```bash
# Development
npm start

# Build for production
npm run build

# Run tests
npm test

# Lint code
npm run lint
```

## Project Structure

```
frontend/
├── public/             # Static assets
├── src/
│   ├── components/     # Reusable components
│   │   ├── common/     # Common UI components
│   │   ├── layout/     # Layout components
│   │   └── features/   # Feature-specific components
│   ├── pages/          # Page components
│   ├── services/       # API services
│   ├── store/          # Redux store and slices
│   ├── utils/          # Utility functions
│   └── styles/         # CSS styles
├── package.json        # Dependencies and scripts
└── README.md          # This file
```

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App
- `npm run lint` - Lint code
- `npm run lint:fix` - Fix linting issues

## Environment Variables

Key environment variables:
- `REACT_APP_API_BASE_URL`: Backend API URL
- `REACT_APP_API_VERSION`: API version
- `REACT_APP_NAME`: Application name
- `REACT_APP_ENVIRONMENT`: Environment (development/production)

## Pages

- `/login` - User login
- `/register` - User registration
- `/dashboard` - Main dashboard
- `/transactions` - Transaction history
- `/profile` - User profile
- `/credit-limits` - Credit limit management
- `/admin` - Admin panel

## State Management

The application uses Redux Toolkit for state management with the following slices:

- `auth` - Authentication state
- `user` - User profile state
- `transactions` - Transaction state
- `creditLimits` - Credit limit state

## API Integration

The frontend communicates with the backend through the API service (`src/services/api.js`) which provides:

- Centralized API configuration
- Request/response interceptors
- Error handling
- Authentication token management

## Styling

The application uses custom CSS with utility classes for:
- Layout and spacing
- Forms and buttons
- Cards and alerts
- Responsive design

## Development

### Code Quality

- ESLint for code linting
- Prettier for code formatting
- React Testing Library for testing

### Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Follow the existing code style
2. Write tests for new components
3. Update documentation
4. Ensure all tests pass
5. Test on multiple browsers
