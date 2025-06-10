import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const getUsers = async () => {
  const res = await axios.get(`${API_URL}/user`);
  return res.data;
};

export const getUserById = async (id) => {
  const res = await axios.get(`${API_URL}/user/${id}`);
  return res.data;
};

// Updated createUser function to handle both regular users and admins
export const createUser = async (userData) => {
  // Determine endpoint based on user role
  const endpoint = userData.user_role === 'admin' 
    ? `${API_URL}/user/create/admin` 
    : `${API_URL}/user/create/user`;
  
  const res = await axios.post(endpoint, userData);
  return res.data;
};

// Alternative approach: separate functions for clarity
export const createRegularUser = async (user) => {
  const res = await axios.post(`${API_URL}/user/create/user`, user);
  return res.data;
};

export const createAdminUser = async (admin) => {
  const res = await axios.post(`${API_URL}/user/create/admin`, admin);
  return res.data;
};


