import api from './api';

export const vaultService = {
    updateKeys: async (keys) => {
        // keys: { openai_api_key: "...", ... }
        const response = await api.post('/vault/update', keys);
        return response.data;
    },

    getKeys: async () => {
        const response = await api.get('/vault/');
        return response.data;
    }
};
