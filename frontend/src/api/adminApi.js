import axiosInstance from '../axiosInstance';

export const getUsersList = async (page = 1, limit = 10) => {
    try {
        const response = await axiosInstance.get(`/users`, {
            params: { page, limit }
        });
        if (response.data.status_code === 200) {
            return response.data.details; 
        }
        throw new Error(response.data.message || 'Failed to fetch user list.');
    } catch (error) {
        throw error;
    }
};

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

export const assignAdminRole = async (userId) => {
    return await axiosInstance.post(`/users/${userId}/assign-admin`);
};

export const assignFacultyManagerRole = async (userId, faculty) => {
    return await axiosInstance.post(`/users/${userId}/assign-faculty-manager`, { faculty });
};

export const assignStudentRole = async (userId, faculty) => {
    return await axiosInstance.post(`/users/${userId}/assign-student`, { faculty });
};


export const banUser = async (userId) => {
    return await axiosInstance.patch(`/users/${userId}/ban`);
};

export const unbanUser = async (userId) => {
    return await axiosInstance.patch(`/users/${userId}/unban`);
};


export const getStudentsList = async (page = 1, limit = 10) => {
    try {
        const response = await axiosInstance.get(`/users/students`, { 
            params: { page, limit }
        });
        if (response.data.status_code === 200) {
            return {
                users: response.data.details.students, 
                total: response.data.details.total,
                total_pages: response.data.details.total_pages,
                current_page: response.data.details.current_page,
            };
        }
        throw new Error(response.data.message || 'Failed to fetch student list.');
    } catch (error) {
        throw error;
    }
};

export const banStudent = async (userId) => {
    return await axiosInstance.patch(`/users/students/${userId}/ban`); 
};

export const unbanStudent = async (userId) => {
    return await axiosInstance.patch(`/users/students/${userId}/unban`); 
};