import axiosInstance from './axiosInstance'; 

const BASE_URL = '/documents';

export const getGeneralDocuments = async (params = {}) => {
    try {
        const response = await axiosInstance.get(`${BASE_URL}/general`, {
            params: {
                ...params, 
                page: params.page || 1,     
                limit: params.limit || 10,
            }
        });
        if (response.data.status_code === 200) {
            return response.data.details;
        }
        throw new Error(response.data.message || 'Failed to fetch general documents.');
    } catch (error) {
        throw error;
    }
};

export const getFacultyDocuments = async (params = {}) => {
    try {
        const response = await axiosInstance.get(`${BASE_URL}/faculty`, {
            params: {
                page: 1,
                limit: 10,
                ...params,
            }
        });
        if (response.data.status_code === 200) {
            return response.data.details;
        }
        throw new Error(response.data.message || 'Failed to fetch faculty documents.');
    } catch (error) {
        throw error;
    }
};

export const getAllDepartments = async () => {
    try {
        const response = await axiosInstance.get(`/documents/departments`);
        if (response.data.status_code === 200) {
            return response.data.details; 
        }
        throw new Error(response.data.message || 'Failed to fetch departments.');
    } catch (error) {
        throw error;
    }
};

export const getDocTypes = async () => {
    try {
        const response = await axiosInstance.get(`${BASE_URL}/doc-types`);
        if (response.data.status_code === 200) {
            return response.data.details; 
        }
        throw new Error(response.data.message || 'Failed to fetch document types.');
    } catch (error) {
        throw error;
    }
};


export const uploadDocument = async (formData, isAppendix = false) => {
    const endpoint = isAppendix ? `${BASE_URL}/upload-appendix` : `${BASE_URL}/upload`;
    try {
        const response = await axiosInstance.post(endpoint, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        if (response.data.status_code === 201) {
            return response.data.details;
        }
        throw new Error(response.data.message || 'Failed to upload document.');
    } catch (error) {
        throw error;
    }
};


export const updateDocument = async (docId, updateData) => {
    const response = await axiosInstance.patch(`${BASE_URL}/${docId}`, updateData);
    if (response.data.status_code === 200) {
        return response.data.details;
    }
    throw new Error(response.data.message || 'Failed to update document.');
};


export const deleteDocument = async (docId) => {
    const response = await axiosInstance.delete(`${BASE_URL}/${docId}`);
    if (response.data.status_code === 200) {
        return response.data.message;
    }
    throw new Error(response.data.message || 'Failed to delete document.');
};

export const getDocumentFileBlob = async (docId) => {
    try {
        const response = await axiosInstance.get(`/documents/view/${docId}`, {
            responseType: 'blob', 
        });
        
        return response.data;
    } catch (error) {
        throw error;
    }
};


import { getFaculties } from './adminApi';
export { getFaculties };

export const getChunksByDocumentId = async (docId, page = 1, limit = 10) => {
    try {
        const response = await axiosInstance.get(`/document-chunks/${docId}`, {
            params: { page, limit }
        });
        if (response.data.status_code === 200) {
            // Cấu trúc response: { document_id, document_chunks: { '0': { ... }, '1': { ... } }, total, total_pages, current_page }
            return response.data.details;
        }
        throw new Error(response.data.message || 'Failed to fetch document chunks.');
    } catch (error) {
        throw error;
    }
};


export const addPotentialQuestionToChunk = async (docId, chunkIndex, question) => {
    const response = await axiosInstance.post(
        `/document-chunks/${docId}/chunks/${chunkIndex}/potential-questions`, 
        { question }
    );
    if (response.data.status_code === 200) {
        return response.data.details; 
    }
    throw new Error(response.data.message || 'Failed to add potential question.');
};

export const deletePotentialQuestionFromChunk = async (docId, chunkIndex, questionIndex) => {
    const response = await axiosInstance.delete(
        `/document-chunks/${docId}/chunks/${chunkIndex}/potential-questions/${questionIndex}`
    );
    if (response.data.status_code === 200) {
        return response.data.message;
    }
    throw new Error(response.data.message || 'Failed to delete potential question.');
};