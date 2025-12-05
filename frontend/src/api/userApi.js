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
        clearTokens();
        throw error; 
    }
};


export const logoutUser = async () => {
    try {
        const response = await axiosInstance.post('/users/logout');
        
        if (response.data.status_code === 200) {
            console.log("Logout API call successful.");
        } else {
            console.error("Logout API call returned non-200 status:", response.data.message);
        }
    } catch (error) {
        console.error("Error during logout API call:", error);
    } finally {
        clearTokens();
    }
};