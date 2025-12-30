import axiosInstance from './axiosInstance';

export const getUsersList = async (params = { page: 1, limit: 10 }) => {
    try {
        const response = await axiosInstance.get(`/users`, {
            params: params 
        });
        if (response.data.status_code === 200) {
            const details = response.data.details;
            if (details.students && !details.users) {
                return {
                    users: details.students,
                    total: details.total,
                    total_pages: details.total_pages,
                    current_page: details.current_page,
                };
            }
            return details; 
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

export const assignTeacherRole = async (userId, faculty) => {
    return await axiosInstance.post(`/users/${userId}/assign-teacher`, { faculty });
};

export const assignStudentRole = async (userId, faculty) => {
    return await axiosInstance.post(`/users/${userId}/assign-student`, { faculty });
};

export const assignFacultyManagerPermission = async (userId, faculty) => {
    return await axiosInstance.post(`/users/${userId}/assign-faculty-manager`, { faculty });
};

export const revokeFacultyManagerPermission = async (userId) => {
    return await axiosInstance.post(`/users/${userId}/revoke-permissions`);
};

export const banUser = async (userId) => {
    return await axiosInstance.patch(`/users/${userId}/ban`);
};

export const unbanUser = async (userId) => {
    return await axiosInstance.patch(`/users/${userId}/unban`);
};


export const getStudentsList = async (params = { page: 1, limit: 10 }) => {
    try {
        const response = await axiosInstance.get(`/users/students`, { 
            params: params 
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


const QA_BASE_URL = '/qa';
const cleanParams = (rawParams) => {
    return Object.keys(rawParams).reduce((acc, key) => {
        const value = rawParams[key];
        if (value !== undefined && value !== null) {
            
            if (typeof value === 'string' && value.trim() === '') {
                return acc; 
            }
            acc[key] = value;
        }
        return acc;
    }, {});
};

export const getFeedbackList = async (rawParams = {}) => {
    
    const cleanQueryParams = cleanParams(rawParams);

    cleanQueryParams.page = cleanQueryParams.page || 1;
    cleanQueryParams.limit = cleanQueryParams.limit || 100; 

    try {
        const response = await axiosInstance.get(`${QA_BASE_URL}/all`, { 
            params: cleanQueryParams 
        });
        if (response.data.status_code === 200) {
            return response.data.details; 
        }
        throw new Error(response.data.message || 'Failed to fetch question records.');
    } catch (error) {
        throw error;
    }
};


export const updateManagerAnswer = async (qaId, managerAnswer) => {
    try {
        const response = await axiosInstance.post(`${QA_BASE_URL}/${qaId}/reply`, { 
            manager_answer: managerAnswer 
        });
        if (response.data.status_code === 200) {
            return response.data.details;
        }
        throw new Error(response.data.message || 'Failed to update manager answer.');
    } catch (error) {
        throw error;
    }
};


export const calculateDashboardMetrics = async (userFaculty) => {
    const filter = {};
    if (userFaculty) {
        filter.faculty = userFaculty; 
    }
    
    let allRecords = [];
    let totalUsers = 0;

    try {
        const [allRecordsResponse, usersResponse] = await Promise.all([
            getFeedbackList({ 
                ...filter,
                limit: 100, 
                page: 1 
            }), 
            
            getUsersList({ page: 1, limit: 1 })
        ]);
        
        allRecords = allRecordsResponse.questions || [];
        totalUsers = usersResponse.total || 0; 

    } catch (error) {
        console.error("Lỗi khi tải dữ liệu Dashboard metrics:", error);
    }
    
    const totalQuestions = allRecords.length;
    let totalLikes = 0;
    let totalDislikes = 0;
    let unansweredDislikes = 0;
    let dislikeRecords = []; 

    allRecords.forEach(record => {
        if (record.feedback === 'Like') {
            totalLikes++;
        } else if (record.feedback === 'Dislike') {
            totalDislikes++;

            const isAnswered = record.manager_answer && record.manager_answer.trim() !== '';
            
            if (!isAnswered) {
                unansweredDislikes++;
            }
            
            dislikeRecords.push({
                id: record._id,
                question: record.question,
                botAnswer: record.answer,
                managerAnswer: record.manager_answer,
                feedback: record.feedback,
                createdAt: record.created_at,
                studentFaculty: record.user_faculty || 'N/A', 
                studentId: record.user_sub || 'N/A', 
            });
        }
    });

    const satisfactionRate = (totalLikes + totalDislikes) > 0 
        ? ((totalLikes / (totalLikes + totalDislikes)) * 100).toFixed(2) 
        : 0;
        
    return {
        totalQuestions,
        totalLikes,
        totalDislikes,
        unansweredDislikes,
        satisfactionRate: parseFloat(satisfactionRate),
        dislikeRecords,
        totalUsers
    };
};

export const getUserChatHistory = async (userId, page = 1, limit = 10) => {
    try {
        const response = await axiosInstance.get(`${QA_BASE_URL}/${userId}/history`, {
            params: { page, limit }
        });
        if (response.data.status_code === 200) {
            return response.data.details; 
        }
        throw new Error(response.data.message || 'Không thể tải lịch sử chat.');
    } catch (error) {
        console.error("Lỗi khi gọi API getUserChatHistory:", error);
        throw error;
    }
};