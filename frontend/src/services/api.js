import axios from 'axios';
import { API_BASE } from './constants';
import { supabase } from './supabase';

// Create axios instance with auth interceptor
const apiClient = axios.create({
  baseURL: API_BASE,
});

// Add auth token to all requests
apiClient.interceptors.request.use(
  async (config) => {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, sign out user
      await supabase.auth.signOut();
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post('/upload-csv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  
  return response.data;
};

export const getEnrichmentProgress = async () => {
  const response = await axios.get(`${API_BASE}/enrichment-progress`); // Public endpoint
  return response.data;
};

export const getSuggestions = async (mission) => {
  const response = await apiClient.post('/get-suggestions', { mission });
  return response.data;
};

export const generateMessage = async (messageData) => {
  const response = await apiClient.post('/generate-message', messageData);
  return response.data;
};