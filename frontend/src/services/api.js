import axios from 'axios';
import { API_BASE } from './constants';

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${API_BASE}/upload-csv`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  
  return response.data;
};

export const getEnrichmentProgress = async () => {
  const response = await axios.get(`${API_BASE}/enrichment-progress`);
  return response.data;
};

export const getSuggestions = async (mission) => {
  const response = await axios.post(`${API_BASE}/get-suggestions`, { mission });
  return response.data;
};

export const generateMessage = async (messageData) => {
  const response = await axios.post(`${API_BASE}/generate-message`, messageData);
  return response.data;
};