import axios from 'axios';

// Backend API service client
const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

export const jiraApi = {
    getConnectionStatus: (connectionId) => api.get(`/connection/${connectionId}`),
    saveConnection: (connectionId) => api.post('/connection', { connectionId }),
    getProjects: (connectionId) => api.get(`/projects/${connectionId}`),
    getIssues: (connectionId, params) => api.get(`/issues/${connectionId}`, { params }),
    getIssueTypes: (connectionId, projectId) => api.get(`/issue-types/${connectionId}/${projectId}`),
    createIssue: (connectionId, data) => api.post(`/issues/${connectionId}`, data),
};

export default api;
