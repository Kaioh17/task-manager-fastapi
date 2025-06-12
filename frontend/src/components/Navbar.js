import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null; // Don't show navbar if not authenticated
  }

  return (
    <nav className="bg-indigo-600 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/dashboard" className="flex-shrink-0">
              <h1 className="text-white text-xl font-bold">Task Manager</h1>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link
              to="/dashboard"
              className="text-white hover:text-indigo-200 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Dashboard
            </Link>
            <Link
              to="/tasks"
              className="text-white hover:text-indigo-200 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Tasks
            </Link>
            <Link
              to="/users"
              className="text-white hover:text-indigo-200 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Users
            </Link>
            <Link
              to="/organizations"
              className="text-white hover:text-indigo-200 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Organizations
            </Link>
            <Link
              to="/assignments"
              className="text-white hover:text-indigo-200 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Assignments
            </Link>
            <Link
              to="/audit-logs"
              className="text-white hover:text-indigo-200 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Audit Logs
            </Link>
            
            {/* User Menu */}
            <div className="relative">
              <div className="flex items-center space-x-4">
                <span className="text-white text-sm">
                  Welcome, {user?.email}
                </span>
                <button
                  onClick={handleLogout}
                  className="bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-800 transition-colors"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="text-white hover:text-indigo-200 focus:outline-none focus:text-indigo-200 p-2"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {isOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {isOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-indigo-700">
            <Link
              to="/dashboard"
              className="text-white hover:text-indigo-200 block px-3 py-2 rounded-md text-base font-medium"
              onClick={() => setIsOpen(false)}
            >
              Dashboard
            </Link>
            <Link
              to="/tasks"
              className="text-white hover:text-indigo-200 block px-3 py-2 rounded-md text-base font-medium"
              onClick={() => setIsOpen(false)}
            >
              Tasks
            </Link>
            <Link
              to="/users"
              className="text-white hover:text-indigo-200 block px-3 py-2 rounded-md text-base font-medium"
              onClick={() => setIsOpen(false)}
            >
              Users
            </Link>
            <Link
              to="/organizations"
              className="text-white hover:text-indigo-200 block px-3 py-2 rounded-md text-base font-medium"
              onClick={() => setIsOpen(false)}
            >
              Organizations
            </Link>
            <Link
              to="/assignments"
              className="text-white hover:text-indigo-200 block px-3 py-2 rounded-md text-base font-medium"
              onClick={() => setIsOpen(false)}
            >
              Assignments
            </Link>
            <Link
              to="/audit-logs"
              className="text-white hover:text-indigo-200 block px-3 py-2 rounded-md text-base font-medium"
              onClick={() => setIsOpen(false)}
            >
              Audit Logs
            </Link>
            <div className="border-t border-indigo-500 pt-4">
              <div className="flex items-center px-3">
                <span className="text-white text-sm">Welcome, {user?.email}</span>
              </div>
              <button
                onClick={handleLogout}
                className="mt-2 w-full text-left text-white hover:text-indigo-200 block px-3 py-2 rounded-md text-base font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;