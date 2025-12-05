import axiosInstance from '../axiosInstance';

const BASE_URL = '/model/api-keys';
const AVAILABLE_MODELS_URL = '/model/available-models';

// --- CRUD Operations ---

// 3.1.1 Thêm 1 API Key
export const createApiKey = async (data) => {
    const response = await axiosInstance.post(BASE_URL, data);
    if (response.data.status_code === 201) {
        return response.data.details;
    }
    throw new Error(response.data.message || 'Failed to create API key.');
};

// 3.1.2 Lấy danh sách tất cả API Keys (Có phân trang)
export const getApiKeysList = async (page = 1, limit = 10) => {
    const response = await axiosInstance.get(BASE_URL, {
        params: { page, limit }
    });
    if (response.data.status_code === 200) {
        // Backend trả về details chứa api_keys, total, total_pages, current_page
        return response.data.details;
    }
    throw new Error(response.data.message || 'Failed to fetch API keys list.');
};

// 3.1.5 Cập nhật thông tin cơ bản của một API key
export const updateApiKeyInfo = async (keyId, updateData) => {
    const response = await axiosInstance.patch(`${BASE_URL}/${keyId}`, updateData);
    if (response.data.status_code === 200) {
        return response.data.details;
    }
    throw new Error(response.data.message || 'Failed to update API key information.');
};

// 3.1.6 Xóa một API Key
export const deleteApiKey = async (keyId) => {
    const response = await axiosInstance.delete(`${BASE_URL}/${keyId}`);
    if (response.data.status_code === 200) {
        return response.data.message;
    }
    throw new Error(response.data.message || 'Failed to delete API key.');
};


// --- Action Operations ---

// Toggle API Key Usage Status
// 3.1.7 Bật/Tắt sử dụng API Key
export const toggleApiKeyUsage = async (keyId) => {
    const response = await axiosInstance.post(`${BASE_URL}/${keyId}/toggle-usage`);
    if (response.data.status_code === 200) {
        return response.data.details; // Trả về API Key đã được cập nhật
    }
    throw new Error(response.data.message || 'Failed to toggle API key usage status.');
};

// 3.1.8 Thêm hoặc thay đổi model sử dụng cho API Key
export const addModelToApiKey = async (keyId, usingModel) => {
    const response = await axiosInstance.post(`${BASE_URL}/${keyId}/add-model`, { using_model: usingModel });
    if (response.data.status_code === 200) {
        return response.data.details; // Trả về API Key đã được cập nhật
    }
    throw new Error(response.data.message || 'Failed to add model to API key.');
};

// 3.1.9 Lấy tất cả các model có sẵn (cần key và provider)
export const getAvailableModels = async (apiKey, provider) => {
    const response = await axiosInstance.post(AVAILABLE_MODELS_URL, { 
        api_key: apiKey, 
        provider: provider 
    });
    if (response.data.status_code === 200) {
        return response.data.details.models || [];
    }
    throw new Error(response.data.message || 'Failed to fetch available models.');
};