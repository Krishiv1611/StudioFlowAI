import api from './api';

export const postService = {
    createPost: async (postData) => {
        const response = await api.post('/posts/', postData);
        return response.data;
    },

    getAllPosts: async (status = null) => {
        const params = status ? { status } : {};
        const response = await api.get('/posts/', { params });
        return response.data;
    },

    updatePost: async (postId, updateData) => {
        const response = await api.patch(`/posts/${postId}`, updateData);
        return response.data;
    },

    deletePost: async (postId) => {
        await api.delete(`/posts/${postId}`);
    }
};
