import axiosInstance from './axiosInstance';

const BASE_URL = '/qa';

export const sendQuery = async (question) => {
    try {
        const response = await axiosInstance.post(`${BASE_URL}/ask`, {
            question: question
        });

        if (response.data.status_code === 200) {
            return response.data.details; 
        }
        throw new Error(response.data.message || 'Failed to get bot response.');
    } catch (error) {
        throw error;
    }
};

export const getChatHistory = async (page = 1, limit = 100) => {
    try {
        const response = await axiosInstance.get(`${BASE_URL}/history`, {
            params: { page, limit }
        });
        if (response.data.status_code === 200) {
            return response.data.details.questions; 
        }
        throw new Error(response.data.message || 'Failed to load chat history.');
    } catch (error) {
        throw error;
    }
};

export const sendFeedback = async (qa_record_id, feedbackType) => {
    try {
        const response = await axiosInstance.post(`${BASE_URL}/feedback/${qa_record_id}`, {
            feedback: feedbackType 
        });
        
        if (response.data.status_code === 200) {
            return true;
        }
        throw new Error(response.data.message || 'Failed to send feedback.');
    } catch (error) {
        throw error;
    }
};