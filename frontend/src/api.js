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
  // Auth — query params format
  signup: (email, password, tenantName) =>
    client.post('/api/v1/auth/signup', null, {
      params: { email, password, tenant_name: tenantName }
    }),
  login: (email, password) =>
    client.post('/api/v1/auth/login', null, {
      params: { email, password }
    }),

  // Alerts
  listAlerts: (skip = 0, limit = 100) =>
    client.get('/api/v1/alerts', { params: { skip, limit } }),
  getAlert: (alertId) =>
    client.get(`/api/v1/alerts/${alertId}`),
  updateAlert: (alertId, status) =>
    client.patch(`/api/v1/alerts/${alertId}`, null, {
      params: { alert_status: status }
    }),

  // Fallback: legacy endpoint
  recent: () =>
    client.get('/alerts/recent'),

  // API Keys
  generateApiKey: (description) =>
    client.post('/api/v1/api-keys', null, {
      params: { description }
    }),

  // Inventory & Security
  getInventory: () =>
    client.get('/api/v1/inventory'),
  exportInventory: (format = 'json') =>
    client.get('/api/v1/inventory/export', { params: { format } }),
  runSecurityScan: () =>
    client.post('/api/v1/security-scan'),

  // Health
  health: () =>
    client.get('/health'),
};

export default api;
