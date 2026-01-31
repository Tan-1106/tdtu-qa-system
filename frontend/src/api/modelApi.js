import axiosInstance from './axiosInstance';

const BASE_URL = '/model/api-keys';
const AVAILABLE_MODELS_URL = '/model/available-models';

export const createApiKey = async (data) => {
    const response = await axiosInstance.post(BASE_URL, data);
    if (response.data.status_code === 201) {
        return response.data.details;
    }
    throw new Error(response.data.message || 'Failed to create API key.');
};

export const getApiKeysList = async (params = { page: 1, limit: 10 }) => {
    try {
        const response = await axiosInstance.get(BASE_URL, {
            params: params 
        });
        if (response.data.status_code === 200) {
            return response.data.details;
        }
        throw new Error(response.data.message || 'Failed to fetch API keys list.');
    } catch (error) {
        throw error;
    }
};

export const updateApiKeyInfo = async (keyId, updateData) => {
    const response = await axiosInstance.patch(`${BASE_URL}/${keyId}`, updateData);
    if (response.data.status_code === 200) {
        return response.data.details;
    }
    throw new Error(response.data.message || 'Failed to update API key information.');
};

export const deleteApiKey = async (keyId) => {
    const response = await axiosInstance.delete(`${BASE_URL}/${keyId}`);
    if (response.data.status_code === 200) {
        return response.data.message;
    }
    throw new Error(response.data.message || 'Failed to delete API key.');
};

export const toggleApiKeyUsage = async (keyId) => {
    const response = await axiosInstance.post(`${BASE_URL}/${keyId}/toggle-usage`);
    if (response.data.status_code === 200) {
        return response.data.details; 
    }
    throw new Error(response.data.message || 'Failed to toggle API key usage status.');
};

export const addModelToApiKey = async (keyId, usingModel, inputTokenPrice, outputTokenPrice) => {
    const response = await axiosInstance.post(`${BASE_URL}/${keyId}/add-model`, { 
        using_model: usingModel,
        input_token_price: inputTokenPrice,
        output_token_price: outputTokenPrice
    });
    if (response.data.status_code === 200) {
        return response.data.details;
    }
    throw new Error(response.data.message || 'Failed to add model to API key.');
};

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