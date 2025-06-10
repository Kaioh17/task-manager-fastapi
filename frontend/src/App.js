import React, { useState } from 'react';
import UserForm from './components/UserForm';
import './App.css';

function App() {
  const [notification, setNotification] = useState({ show: false, message: '', type: '' });

  const handleUserCreationSuccess = (userData, message) => {
    console.log('User created successfully:', userData);
    setNotification({
      show: true,
      message: message,
      type: 'success'
    });

    // Auto-hide notification after 5 seconds
    setTimeout(() => {
      setNotification({ show: false, message: '', type: '' });
    }, 5000);

    // You can add additional logic here, such as:
    // - Redirecting to login page
    // - Automatically logging in the user
    // - Sending welcome email
    // - Analytics tracking
  };

  const handleUserCreationError = (error, message) => {
    console.error('User creation failed:', error);
    setNotification({
      show: true,
      message: message,
      type: 'error'
    });

    // Auto-hide notification after 5 seconds
    setTimeout(() => {
      setNotification({ show: false, message: '', type: '' });
    }, 5000);
  };

  const closeNotification = () => {
    setNotification({ show: false, message: '', type: '' });
  };

  return (
    <div className="App">
      {/* Global Notification */}
      {notification.show && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-md ${
          notification.type === 'success' 
            ? 'bg-green-100 border border-green-200 text-green-800' 
            : 'bg-red-100 border border-red-200 text-red-800'
        }`}>
          <div className="flex items-center justify-between">
            <span>{notification.message}</span>
            <button
              onClick={closeNotification}
              className="ml-4 text-gray-500 hover:text-gray-700"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Main Application Content */}
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <UserForm 
          onSuccess={handleUserCreationSuccess}
          onError={handleUserCreationError}
        />
      </div>

      {/* Footer */}
      <footer className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4">
        <div className="text-center text-sm text-gray-600">
          © 2025 Your Company Name. All rights reserved.
        </div>
      </footer>
    </div>
  );
}

export default App;