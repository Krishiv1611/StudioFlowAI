import api from './api';

export const authService = {
    login: async (email, password) => {
        const response = await api.post('/auth/login', { username: email, password });
        if (response.data.access_token) {
            localStorage.setItem('token', response.data.access_token);
        }
        return response.data;
    },

    signup: async (email, password, full_name) => {
        const response = await api.post('/users/', { email, password, full_name });
        return response.data;
    },

    logout: () => {
        localStorage.removeItem('token');
        window.location.href = '/login';
    },

    getCurrentUser: async () => {
        const response = await api.get('/users/me');
        return response.data;
    }
};
