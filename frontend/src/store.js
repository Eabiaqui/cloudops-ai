/**Zustand store for auth + tenant state.*/

import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  token: localStorage.getItem('token'),
  tenantId: localStorage.getItem('tenantId'),
  userId: localStorage.getItem('userId'),
  apiKey: localStorage.getItem('apiKey'),

  login: (token, tenantId, userId, apiKey) => {
    localStorage.setItem('token', token);
    localStorage.setItem('tenantId', tenantId);
    localStorage.setItem('userId', userId);
    if (apiKey) localStorage.setItem('apiKey', apiKey);
    set({ token, tenantId, userId, apiKey });
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('tenantId');
    localStorage.removeItem('userId');
    localStorage.removeItem('apiKey');
    set({ token: null, tenantId: null, userId: null, apiKey: null });
  },

  isAuthenticated: () => !!localStorage.getItem('token'),
}));
