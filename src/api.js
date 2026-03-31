// Triggering redeploy for env var injection
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'https://snacko-backend.onrender.com';

const api = axios.create({
    baseURL: API_BASE,
    headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request if available
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;
