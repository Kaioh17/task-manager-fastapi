import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_data');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  login: async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  createUser: async (userData) => {
    const response = await api.post('/user/create/user', userData);
    return response.data;
  },

  createAdmin: async (adminData) => {
    const response = await api.post('/user/create/admin', adminData);
    return response.data;
  },
};

// User API calls
export const userAPI = {
  getAllUsers: async () => {
    const response = await api.get('/user/');
    return response.data;
  },

  getUsersByOrg: async (orgId) => {
    const response = await api.get(`/user/organization/${orgId}`);
    return response.data;
  },

  deleteUser: async (password) => {
    const response = await api.post('/user/delete', { user_password: password });
    return response.data;
  },
};

// Task API calls
export const taskAPI = {
  createTask: async (taskData) => {
    const response = await api.post('/task/create', taskData);
    return response.data;
  },

  getAllTasks: async () => {
    const response = await api.get('/task/');
    return response.data;
  },
};

// Organization API calls
export const orgAPI = {
  createOrg: async (orgData) => {
    const response = await api.post('/org/create', orgData);
    return response.data;
  },

  getAllOrgs: async () => {
    const response = await api.get('/org/');
    return response.data;
  },
};

export default api;