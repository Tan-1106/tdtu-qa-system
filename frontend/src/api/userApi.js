// /api/userApi.js (Bạn cần tạo file này)

import axiosInstance from '../axiosInstance'; // Đảm bảo đường dẫn đúng
import { clearTokens } from '../axiosInstance'; // Hàm clearTokens đã được export từ axiosInstance.js

/**
 * Lấy thông tin người dùng hiện tại
 * API: GET {{base}}/auth/me
 */
export const getCurrentUser = async () => {
    try {
        const response = await axiosInstance.get('/auth/me');
        if (response.data.status_code === 200) {
            return response.data.details;
        } 
        throw new Error(response.data.message || "Failed to fetch user information.");
    } catch (error) {
        throw error; 
    }
};

/**
 * Hàm Đăng xuất
 */
export const logoutUser = () => {
    clearTokens();
    // Thêm logic chuyển hướng hoặc làm mới trang
    // Ví dụ: window.location.href = '/login'; 
};