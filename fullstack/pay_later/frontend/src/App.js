import React from 'react';
import { Routes, Route } from 'react-router-dom';
import './styles/App.css';

// Import pages (to be created)
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Transactions from './pages/Transactions';
import Profile from './pages/Profile';
import CreditLimits from './pages/CreditLimits';
import Admin from './pages/Admin';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/transactions" element={<Transactions />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/credit-limits" element={<CreditLimits />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/" element={<Login />} />
      </Routes>
    </div>
  );
}

export default App;
