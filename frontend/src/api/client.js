import axios from 'axios';

export const BASE = import.meta.env.VITE_API_URL || '/api';

export const tokens = {
  get access() { return localStorage.getItem('access'); },
  get refresh() { return localStorage.getItem('refresh'); },
  set(access, refresh) {
    localStorage.setItem('access', access);
    if (refresh) localStorage.setItem('refresh', refresh);
  },
  clear() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('user');
  },
};

export const api = axios.create({ baseURL: BASE });

api.interceptors.request.use((config) => {
  if (tokens.access && !config.skipAuth) {
    config.headers.Authorization = `Bearer ${tokens.access}`;
  }
  return config;
});

let refreshing = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const isAuthCall = original && original.url && original.url.includes('/auth/');
    if (error.response && error.response.status === 401 && original && !original._retry && tokens.refresh && !isAuthCall) {
      original._retry = true;
      try {
        refreshing = refreshing || axios.post(`${BASE}/auth/refresh/`, { refresh: tokens.refresh }).finally(() => { refreshing = null; });
        const { data } = await refreshing;
        tokens.set(data.access, data.refresh);
        original.headers.Authorization = `Bearer ${data.access}`;
        return api(original);
      } catch (refreshError) {
        tokens.clear();
        window.dispatchEvent(new Event('auth:logout'));
        // Public pages should still load when the login has expired.
        if ((original.method || 'get').toLowerCase() === 'get') {
          original.skipAuth = true;
          if (original.headers && original.headers.delete) original.headers.delete('Authorization');
          return api(original);
        }
      }
    }
    return Promise.reject(error);
  }
);
