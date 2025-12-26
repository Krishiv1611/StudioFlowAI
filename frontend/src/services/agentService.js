import api from './api';

export const agentService = {
    runAgent: async (input, modelProvider = 'gemini') => {
        const response = await api.post('/agent/run', { input, model_provider: modelProvider });
        return response.data; // Returns { thread_id, next_step, values }
    },

    getStatus: async (threadId) => {
        const response = await api.get(`/agent/status/${threadId}`);
        return response.data;
    },

    approveDraft: async (threadId, action) => {
        // action is 'approve' or 'reject'
        const response = await api.post(`/agent/approve/${threadId}`, { action });
        return response.data;
    },

    chatWithGuru: async (input, history = []) => {
        const response = await api.post('/agent/chat', { input, chat_history: history });
        return response.data;
    }
};
