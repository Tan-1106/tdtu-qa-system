import axiosInstance from './axiosInstance';

const STATISTICAL_BASE_URL = '/statistics';

const cleanParams = (rawParams) => {
    return Object.keys(rawParams).reduce((acc, key) => {
        const value = rawParams[key];
        if (value !== undefined && value !== null && value !== '') {
            acc[key] = value;
        }
        return acc;
    }, {});
};

export const getPopularQuestions = async (rawParams = {}) => {
    const cleanQueryParams = cleanParams(rawParams);
    cleanQueryParams.page = cleanQueryParams.page || 1;
    cleanQueryParams.limit = cleanQueryParams.limit || 10;
    
    try {
        const response = await axiosInstance.get(`${STATISTICAL_BASE_URL}/popular-questions`, {
            params: cleanQueryParams
        });
        if (response.data.status_code === 200) {
            return response.data.details;
        }
        throw new Error(response.data.message || 'Failed to fetch popular questions.');
    } catch (error) {
        throw error;
    }
};


export const getPopularQuestionsForUser = async (page = 1, limit = 10) => {
    try {
        const response = await axiosInstance.get(`${STATISTICAL_BASE_URL}/popular-questions-student`, {
            params: {
                page: page,
                limit: limit,
            }
        });
        if (response.data.status_code === 200) {
            return response.data.details;
        }
        throw new Error(response.data.message || 'Failed to fetch popular questions for user.');
    } catch (error) {
        throw error;
    }
};

export const generatePopularQuestions = async (periodType, n) => {
    try {
        const response = await axiosInstance.get(`${STATISTICAL_BASE_URL}/generate-popular-questions`, {
            params: { period_type: periodType, n }
        });
        if (response.data.status_code === 200) {
            return response.data.details;
        }
        throw new Error(response.data.message || 'Failed to generate popular questions.');
    } catch (error) {
        throw error;
    }
};

export const togglePopularQuestionDisplay = async (questionId) => {
    try {
        const response = await axiosInstance.patch(`${STATISTICAL_BASE_URL}/popular-questions/${questionId}/toggle-display`);
        if (response.data.status_code === 200) {
            return response.data.details;
        }
        throw new Error(response.data.message || 'Failed to toggle display status.');
    } catch (error) {
        throw error;
    }
};

export const assignFacultyScope = async (questionId, faculty) => {
    try {
        const facultyData = faculty === null ? {} : { faculty: faculty };
        
        const response = await axiosInstance.patch(`${STATISTICAL_BASE_URL}/popular-questions/${questionId}/assign-faculty`, 
            facultyData
        );
        if (response.data.status_code === 200) {
            return response.data.details;
        }
        throw new Error(response.data.message || 'Failed to assign faculty scope.');
    } catch (error) {
        throw error;
    }
};

export const updatePopularQuestion = async (questionId, updateData) => {
    try {
        const response = await axiosInstance.patch(`${STATISTICAL_BASE_URL}/popular-questions/${questionId}/update`, updateData);
        if (response.data.status_code === 200) {
            return response.data.details;
        }
        throw new Error(response.data.message || 'Failed to update popular question.');
    } catch (error) {
        throw error;
    }
};