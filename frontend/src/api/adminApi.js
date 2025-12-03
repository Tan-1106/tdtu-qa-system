import axiosInstance from '../axiosInstance';

// **********************************************
// 2.1.1 Lấy danh sách tất cả người dùng (Có phân trang)
// **********************************************
export const getUsersList = async (page = 1, limit = 10) => {
    try {
        const response = await axiosInstance.get(`/users`, {
            params: { page, limit }
        });
        if (response.data.status_code === 200) {
            // Trả về details chứa users, total, total_pages, current_page
            return response.data.details; 
        }
        throw new Error(response.data.message || 'Failed to fetch user list.');
    } catch (error) {
        throw error;
    }
};

// **********************************************
// 2.1.2 Lấy danh sách các role
// **********************************************
export const getRoles = async () => {
    try {
        const response = await axiosInstance.get(`/users/roles`);
        if (response.data.status_code === 200) {
            return response.data.details.roles;
        }
        throw new Error(response.data.message || 'Failed to fetch roles.');
    } catch (error) {
        throw error;
    }
};

// **********************************************
// 2.1.3 Lấy danh sách các khoa
// **********************************************
export const getFaculties = async () => {
    try {
        const response = await axiosInstance.get(`/users/faculties`);
        if (response.data.status_code === 200) {
            return response.data.details.faculties;
        }
        throw new Error(response.data.message || 'Failed to fetch faculties.');
    } catch (error) {
        throw error;
    }
};

// **********************************************
// 2.1.4 - 2.1.6 Phân quyền
// **********************************************
// Phân quyền Admin
export const assignAdminRole = async (userId) => {
    return await axiosInstance.post(`/users/${userId}/assign-admin`);
};

// Phân quyền Faculty Manager
export const assignFacultyManagerRole = async (userId, faculty) => {
    return await axiosInstance.post(`/users/${userId}/assign-faculty-manager`, { faculty });
};

// Phân quyền Student
export const assignStudentRole = async (userId, faculty) => {
    return await axiosInstance.post(`/users/${userId}/assign-student`, { faculty });
};

// **********************************************
// 2.1.7 & 2.1.8 Chặn/Bỏ chặn
// **********************************************
export const banUser = async (userId) => {
    return await axiosInstance.patch(`/users/${userId}/ban`);
};

export const unbanUser = async (userId) => {
    return await axiosInstance.patch(`/users/${userId}/unban`);
};