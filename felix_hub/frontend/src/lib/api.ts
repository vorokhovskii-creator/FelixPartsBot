import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add mechanic token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('mechanic_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('mechanic_token');
      localStorage.removeItem('mechanic');
      window.location.href = '/mechanic/login';
    }
    return Promise.reject(error);
  }
);

export default api;
