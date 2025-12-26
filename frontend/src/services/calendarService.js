import api from './api';

export const calendarService = {
    getSchedule: async () => {
        // Assuming backend will have a calendar endpoint, or filtering posts by date
        // Based on user request, we need to utilize the backend feature.
        // Ideally: await api.get('/calendar/events');
        // If not implemented, we might fallback to filtered posts
        try {
            const response = await api.get('/calendar/events');
            return response.data;
        } catch (error) {
            console.warn("Calendar endpoint might not be ready, fetching posts instead.");
            const posts = await api.get('/posts/');
            return posts.data.filter(p => p.scheduled_for);
        }
    }
};
