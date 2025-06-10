import axios from 'axios';
const API_URL = 'http://localhost:8000';

export const getOrgs = async () => {
  const res = await axios.get(`${API_URL}/org`);
  return res.data;
};

export const createOrg = async (org) => {
  const res = await axios.post(`${API_URL}/org`, org);
  return res.data;
};
