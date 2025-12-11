import axiosInstance from '../axiosInstance';

const BASE_URL = '/qa';

/**
 * Gửi câu hỏi mới và nhận câu trả lời từ LLM (Core RAG).
 * Endpoint: POST /qa/ask
 */
export const sendQuery = async (question) => {
    try {
        // Backend đang sử dụng POST /qa/ask với body là {question: string}
        const response = await axiosInstance.post(`${BASE_URL}/ask`, {
            question: question
        });

        if (response.data.status_code === 200) {
            // Controller trả về đối tượng 'answer' (có thể là chuỗi hoặc object {answer, qa_record_id})
            return response.data.details; 
        }
        throw new Error(response.data.message || 'Failed to get bot response.');
    } catch (error) {
        throw error;
    }
};

/**
 * Lấy lịch sử các phiên hỏi đáp của người dùng hiện tại.
 * Endpoint: GET /qa/history
 */
export const getChatHistory = async (page = 1, limit = 100) => {
    try {
        const response = await axiosInstance.get(`${BASE_URL}/history`, {
            params: { page, limit }
        });
        if (response.data.status_code === 200) {
            return response.data.details.questions; // <<< Trả về Array [questions]
        }
        throw new Error(response.data.message || 'Failed to load chat history.');
    } catch (error) {
        throw error;
    }
};

/**
 * Gửi feedback cho một câu trả lời cụ thể.
 * Endpoint: POST /qa/feedback/{qa_record_id}
 */
export const sendFeedback = async (qa_record_id, feedbackType) => {
    try {
        // Backend sử dụng POST với body {feedback: string}
        const response = await axiosInstance.post(`${BASE_URL}/feedback/${qa_record_id}`, {
            feedback: feedbackType // 'Like' hoặc 'Dislike'
        });
        
        if (response.data.status_code === 200) {
            return true;
        }
        throw new Error(response.data.message || 'Failed to send feedback.');
    } catch (error) {
        throw error;
    }
};