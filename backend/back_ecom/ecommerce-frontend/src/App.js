import React from 'react';
import { Routes, Route } from 'react-router-dom';
import AdminLayout from './layouts/AdminLayout';
import Dashboard from './pages/dashboard/Dashboard';
import Products from './pages/products/Products';
import Categories from './pages/categories/Categories';
import Orders from './pages/orders/Orders';
import Users from './pages/users/Users';
import Analytics from './pages/analytics/Analytics';

function App() {
  return (
    <div className="App">
      <Routes>
        {/* All routes are now public and accessible */}
        <Route path="/" element={<AdminLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="products" element={<Products />} />
          <Route path="categories" element={<Categories />} />
          <Route path="orders" element={<Orders />} />
          <Route path="users" element={<Users />} />
          <Route path="analytics" element={<Analytics />} />
        </Route>
      </Routes>
    </div>
  );
}

export default App;
