/** API client for backend communication. */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if present
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const api = {
  // Auth (Week 4 backend endpoints)
  signup: (email, password, tenantName) =>
    client.post('/api/v1/auth/signup', { email, password, tenant_name: tenantName }),
  login: (email, password) =>
    client.post('/api/v1/auth/login', { email, password }),

  // Alerts (Week 4 backend endpoints)
  listAlerts: (skip = 0, limit = 100) =>
    client.get('/api/v1/alerts', { params: { skip, limit } }),
  getAlert: (alertId) =>
    client.get(`/api/v1/alerts/${alertId}`),

  // Fallback: current public endpoint (Fase 1-6 backend)
  recent: () =>
    client.get('/alerts/recent'),

  // API Keys
  generateApiKey: (description) =>
    client.post('/api/v1/api-keys', { description }),

  // Health
  health: () =>
    client.get('/health'),
};

export default api;
