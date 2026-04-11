import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  CubeIcon,
  TagIcon,
  ShoppingCartIcon,
  UsersIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

const AdminLayout = () => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon, current: location.pathname === '/' },
    { name: 'Products', href: '/products', icon: CubeIcon, current: location.pathname === '/products' },
    { name: 'Categories', href: '/categories', icon: TagIcon, current: location.pathname === '/categories' },
    { name: 'Orders', href: '/orders', icon: ShoppingCartIcon, current: location.pathname === '/orders' },
    { name: 'Users', href: '/users', icon: UsersIcon, current: location.pathname === '/users' },
    { name: 'Analytics', href: '/analytics', icon: ChartBarIcon, current: location.pathname === '/analytics' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex">
        {/* Sidebar */}
        <div className="w-64 bg-white shadow-sm min-h-screen border-r border-gray-200">
          {/* Header */}
          <div className="p-6 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-blue-600">E-Commerce Admin Portal</h1>
            <div className="mt-2 text-sm text-gray-600">
              Welcome to the management system
            </div>
          </div>
          
          {/* Navigation */}
          <nav className="mt-6 px-3">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center px-3 py-2 text-sm font-medium rounded-md mb-1 transition-colors ${
                    item.current
                      ? 'bg-blue-100 text-blue-700 border-r-2 border-blue-700'
                      : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  <Icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
          

        </div>
        
        {/* Main Content */}
        <div className="flex-1 p-8">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default AdminLayout;
