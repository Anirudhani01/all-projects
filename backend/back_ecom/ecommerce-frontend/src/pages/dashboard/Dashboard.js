import React from 'react';
import {
  CubeIcon,
  TagIcon,
  ShoppingCartIcon,
  UsersIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

const Dashboard = () => {

  const stats = [
    {
      name: 'Products',
      value: '0',
      icon: CubeIcon,
      color: 'bg-blue-500'
    },
    {
      name: 'Categories',
      value: '0',
      icon: TagIcon,
      color: 'bg-green-500'
    },
    {
      name: 'Orders',
      value: '0',
      icon: ShoppingCartIcon,
      color: 'bg-yellow-500'
    },
    {
      name: 'Users',
      value: '0',
      icon: UsersIcon,
      color: 'bg-purple-500'
    },
    {
      name: 'Analytics',
      value: 'Available',
      icon: ChartBarIcon,
      color: 'bg-indigo-500'
    }
  ];



  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome to E-Commerce Management System!
            </h1>
            <p className="text-gray-600 mt-2">
              Manage your products, categories, orders, and analytics from one central dashboard.
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-bold">⚡</span>
            </div>
            <span className="text-sm font-medium text-blue-600">Ready to Manage</span>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          
          return (
            <div
              key={stat.name}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
            >
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.color}`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>



      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => window.location.href = '/products'}
            className="flex items-center justify-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <CubeIcon className="h-6 w-6 text-blue-600 mr-2" />
            <span>Add Product</span>
          </button>
          
          <button
            onClick={() => window.location.href = '/categories'}
            className="flex items-center justify-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <TagIcon className="h-6 w-6 text-green-600 mr-2" />
            <span>Manage Categories</span>
          </button>
          
          <button
            onClick={() => window.location.href = '/analytics'}
            className="flex items-center justify-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <ChartBarIcon className="h-6 w-6 text-indigo-600 mr-2" />
            <span>View Analytics</span>
          </button>
        </div>
      </div>

      {/* System Status */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">System Status</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-gray-600">Application Status</span>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              Running
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-600">Access Level</span>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              Public
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-600">Database Connection</span>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              Connected
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
