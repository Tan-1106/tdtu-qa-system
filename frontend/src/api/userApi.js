import axiosInstance from '../axiosInstance'; 
import { clearTokens } from '../axiosInstance'; 

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


export const logoutUser = () => {
    clearTokens();
    // Thêm logic chuyển hướng hoặc làm mới trang
    // Ví dụ: window.location.href = '/login'; 
};