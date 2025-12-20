import axiosInstance from './axiosInstance'; 

const BASE_URL = '/documents';

/**
 * Lấy danh sách tài liệu chung (Phòng ban)
 * Dùng cho Admin (có thể lọc theo department) và Faculty Manager (chỉ thấy faculty của mình)
 */
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

/**
 * Lấy danh sách tài liệu Khoa (Faculty)
 * Dùng cho Admin (có thể lọc theo faculty) và Faculty Manager (chỉ thấy faculty của mình)
 */
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

/**
 * Upload tài liệu mới (PDF)
 * @param {FormData} formData - Chứa file, doc_type, file_url, department/faculty
 * @param {boolean} isAppendix - Xác định dùng endpoint upload hay upload-appendix
 */
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

/**
 * Cập nhật thông tin tài liệu
 * @param {string} docId 
 * @param {object} updateData - { file_name, doc_type, department, faculty, file_url }
 */
export const updateDocument = async (docId, updateData) => {
    const response = await axiosInstance.patch(`${BASE_URL}/${docId}`, updateData);
    if (response.data.status_code === 200) {
        return response.data.details;
    }
    throw new Error(response.data.message || 'Failed to update document.');
};

/**
 * Xóa tài liệu
 * @param {string} docId 
 */
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

// --- APIs CHO DOCUMENT CHUNKS ---

/**
 * Lấy danh sách document chunks của một tài liệu
 * @param {string} docId - ID của tài liệu
 * @param {number} page - Trang hiện tại (bắt đầu từ 1)
 * @param {number} limit - Số lượng chunk mỗi trang
 */
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

/**
 * Thêm một câu hỏi tiềm năng vào một chunk cụ thể
 * @param {string} docId - ID tài liệu
 * @param {number} chunkIndex - Index của chunk
 * @param {string} question - Nội dung câu hỏi mới
 */
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

/**
 * Xóa một câu hỏi tiềm năng khỏi một chunk cụ thể
 * @param {string} docId - ID tài liệu
 * @param {number} chunkIndex - Index của chunk
 * @param {number} questionIndex - Index của câu hỏi trong mảng potential_questions
 */
export const deletePotentialQuestionFromChunk = async (docId, chunkIndex, questionIndex) => {
    const response = await axiosInstance.delete(
        `/document-chunks/${docId}/chunks/${chunkIndex}/potential-questions/${questionIndex}`
    );
    if (response.data.status_code === 200) {
        return response.data.message;
    }
    throw new Error(response.data.message || 'Failed to delete potential question.');
};