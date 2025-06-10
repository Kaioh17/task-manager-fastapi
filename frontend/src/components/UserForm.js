import React, { useState, useEffect } from 'react';
import { User, Building, Mail, Lock, UserCheck, AlertCircle, CheckCircle } from 'lucide-react';
import { createUser, getOrganizations } from '../api/user';

const UserForm = ({ onSuccess, onError }) => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    user_email: '',
    user_password: '',
    confirm_password: '',
    user_role: 'user',
    org_id: '',
    org_name: '',
    org_description: ''
  });

  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (formData.user_role === 'user') {
      fetchOrganizations();
    }
  }, [formData.user_role]);

  const fetchOrganizations = async () => {
    try {
      const orgs = await getOrganizations();
      setOrganizations(orgs);
    } catch (error) {
      console.error('Error fetching organizations:', error);
      setOrganizations([]);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Required fields validation
    if (!formData.first_name.trim()) newErrors.first_name = 'First name is required';
    if (!formData.last_name.trim()) newErrors.last_name = 'Last name is required';
    if (!formData.user_email.trim()) newErrors.user_email = 'Email is required';
    if (!formData.user_password) newErrors.user_password = 'Password is required';
    if (!formData.confirm_password) newErrors.confirm_password = 'Please confirm your password';

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (formData.user_email && !emailRegex.test(formData.user_email)) {
      newErrors.user_email = 'Please enter a valid email address';
    }

    // Password validation
    if (formData.user_password && formData.user_password.length < 6) {
      newErrors.user_password = 'Password must be at least 6 characters long';
    }

    // Confirm password validation
    if (formData.user_password !== formData.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match';
    }

    // Role-specific validation
    if (formData.user_role === 'user') {
      if (!formData.org_id) newErrors.org_id = 'Please select an organization';
    } else if (formData.user_role === 'admin') {
      if (!formData.org_name.trim()) newErrors.org_name = 'Organization name is required';
      if (!formData.org_description.trim()) newErrors.org_description = 'Organization description is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const userData = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        user_email: formData.user_email,
        user_password: formData.user_password,
        user_role: formData.user_role,
        ...(formData.user_role === 'admin' 
          ? {
              org_name: formData.org_name,
              org_description: formData.org_description
            }
          : {
              org_id: parseInt(formData.org_id)
            }
        )
      };

      const result = await createUser(userData);
      
      const successMessage = `${formData.user_role === 'admin' ? 'Admin' : 'User'} account created successfully!`;
      setMessage({ type: 'success', text: successMessage });
      
      // Reset form
      setFormData({
        first_name: '',
        last_name: '',
        user_email: '',
        user_password: '',
        confirm_password: '',
        user_role: 'user',
        org_id: '',
        org_name: '',
        org_description: ''
      });

      // Call success callback if provided
      if (onSuccess) {
        onSuccess(result, successMessage);
      }

    } catch (error) {
      const errorMessage = error.message || 'Failed to create account. Please try again.';
      setMessage({ type: 'error', text: errorMessage });
      
      // Call error callback if provided
      if (onError) {
        onError(error, errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = (role) => {
    setFormData(prev => ({
      ...prev,
      user_role: role,
      org_id: '',
      org_name: '',
      org_description: ''
    }));
    setErrors({});
    setMessage({ type: '', text: '' });
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl p-8">
      <div className="text-center mb-8">
        <div className="mx-auto w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mb-4">
          <UserCheck className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Account</h1>
        <p className="text-gray-600">Join our platform as a user or create your organization</p>
      </div>

      {message.text && (
        <div className={`mb-6 p-4 rounded-lg flex items-center gap-3 ${
          message.type === 'success' 
            ? 'bg-green-50 text-green-800 border border-green-200' 
            : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          {message.type === 'success' ? (
            <CheckCircle className="w-5 h-5 flex-shrink-0" />
          ) : (
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      <div className="space-y-6">
        {/* Role Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Account Type
          </label>
          <div className="grid grid-cols-2 gap-4">
            <button
              type="button"
              onClick={() => handleRoleChange('user')}
              className={`p-4 rounded-lg border-2 transition-all ${
                formData.user_role === 'user'
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <User className="w-6 h-6 mx-auto mb-2" />
              <div className="font-medium">Regular User</div>
              <div className="text-sm text-gray-500">Join existing organization</div>
            </button>
            <button
              type="button"
              onClick={() => handleRoleChange('admin')}
              className={`p-4 rounded-lg border-2 transition-all ${
                formData.user_role === 'admin'
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <Building className="w-6 h-6 mx-auto mb-2" />
              <div className="font-medium">Admin</div>
              <div className="text-sm text-gray-500">Create new organization</div>
            </button>
          </div>
        </div>

        {/* Personal Information */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              First Name *
            </label>
            <input
              type="text"
              name="first_name"
              value={formData.first_name}
              onChange={handleInputChange}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.first_name ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Enter your first name"
            />
            {errors.first_name && (
              <p className="mt-1 text-sm text-red-600">{errors.first_name}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Last Name *
            </label>
            <input
              type="text"
              name="last_name"
              value={formData.last_name}
              onChange={handleInputChange}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.last_name ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Enter your last name"
            />
            {errors.last_name && (
              <p className="mt-1 text-sm text-red-600">{errors.last_name}</p>
            )}
          </div>
        </div>

        {/* Email */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Email Address *
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="email"
              name="user_email"
              value={formData.user_email}
              onChange={handleInputChange}
              className={`w-full pl-12 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.user_email ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Enter your email address"
            />
          </div>
          {errors.user_email && (
            <p className="mt-1 text-sm text-red-600">{errors.user_email}</p>
          )}
        </div>

        {/* Password */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password *
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="password"
                name="user_password"
                value={formData.user_password}
                onChange={handleInputChange}
                className={`w-full pl-12 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.user_password ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Enter password"
              />
            </div>
            {errors.user_password && (
              <p className="mt-1 text-sm text-red-600">{errors.user_password}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Confirm Password *
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleInputChange}
                className={`w-full pl-12 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.confirm_password ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Confirm password"
              />
            </div>
            {errors.confirm_password && (
              <p className="mt-1 text-sm text-red-600">{errors.confirm_password}</p>
            )}
          </div>
        </div>

        {/* Organization Selection (for regular users) */}
        {formData.user_role === 'user' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Organization *
            </label>
            <select
              name="org_id"
              value={formData.org_id}
              onChange={handleInputChange}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.org_id ? 'border-red-300' : 'border-gray-300'
              }`}
            >
              <option value="">Choose an organization</option>
              {organizations.map((org) => (
                <option key={org.org_id} value={org.org_id}>
                  {org.org_name}
                </option>
              ))}
            </select>
            {errors.org_id && (
              <p className="mt-1 text-sm text-red-600">{errors.org_id}</p>
            )}
          </div>
        )}

        {/* Organization Creation (for admins) */}
        {formData.user_role === 'admin' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Organization Name *
              </label>
              <input
                type="text"
                name="org_name"
                value={formData.org_name}
                onChange={handleInputChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.org_name ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Enter organization name"
              />
              {errors.org_name && (
                <p className="mt-1 text-sm text-red-600">{errors.org_name}</p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Organization Description *
              </label>
              <textarea
                name="org_description"
                value={formData.org_description}
                onChange={handleInputChange}
                rows={3}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.org_description ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Describe your organization"
              />
              {errors.org_description && (
                <p className="mt-1 text-sm text-red-600">{errors.org_description}</p>
              )}
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="button"
          onClick={handleSubmit}
          disabled={loading}
          className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 text-white py-3 px-6 rounded-lg font-medium hover:from-blue-600 hover:to-indigo-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <div className="flex items-center justify-center gap-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              Creating Account...
            </div>
          ) : (
            `Create ${formData.user_role === 'admin' ? 'Admin' : 'User'} Account`
          )}
        </button>
      </div>

      <div className="mt-8 text-center">
        <p className="text-gray-600">
          Already have an account?{' '}
          <a href="/login" className="text-blue-600 hover:text-blue-700 font-medium">
            Sign in here
          </a>
        </p>
      </div>
    </div>
  );
};

export default UserForm;