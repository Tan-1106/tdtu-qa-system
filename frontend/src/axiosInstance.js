import axios from 'axios';

const BACKEND_URL = import.meta?.env?.VITE_BACKEND_URL || 'http://localhost:8000';
const baseURL = `${BACKEND_URL}/api`;
const axiosInstance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Hàm để lấy Refresh Token
export const getRefreshToken = () => {
    if (typeof window !== 'undefined') {
        return localStorage.getItem('refreshToken');
    }
    return null;
};

// Hàm để lấy Access Token
export const getAccessToken = () => {
    if (typeof window !== 'undefined') {
        return localStorage.getItem('accessToken'); 
    }
    return null;
};

// Hàm để lưu cả hai token
export const setTokens = ({ access_token, refresh_token }) => {
    if (typeof window !== 'undefined') {
        localStorage.setItem('accessToken', access_token);
        localStorage.setItem('refreshToken', refresh_token);
    }
};

// Hàm xóa token (để đăng xuất hoặc khi refresh token hết hạn)
export const clearTokens = () => {
    if (typeof window !== 'undefined') {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
    }
    // TODO: Thêm logic chuyển hướng người dùng về trang đăng nhập ở đây nếu cần thiết
    // Ví dụ: window.location.href = '/login'; 
};


const refreshAccessToken = async () => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
        clearTokens();
        return Promise.reject(new Error("No refresh token available. Forced logout."));
    }

    try {
        const response = await axios.post(`${baseURL}/auth/refresh`, {
            refresh_token: refreshToken
        });
        
        if (response.data.status_code === 200 && response.data.details) {
            setTokens(response.data.details);
            return response.data.details.access_token;
        } else {
            clearTokens();
            throw new Error(response.data.message || "Token refresh failed.");
        }
    } catch (error) {
        console.error("Token refresh failed:", error);
        clearTokens(); 
        throw error;
    }
};


let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        
        if (error.response && error.response.status === 401 && !originalRequest._retry) {
            
            originalRequest._retry = true;
            
            if (isRefreshing) {
                return new Promise(function(resolve, reject) {
                    failedQueue.push({ resolve, reject });
                }).then(token => {
                    originalRequest.headers['Authorization'] = 'Bearer ' + token;
                    return axiosInstance(originalRequest);
                }).catch(err => {
                    return Promise.reject(err);
                });
            }

            isRefreshing = true;

            try {
                const newAccessToken = await refreshAccessToken();
                originalRequest.headers['Authorization'] = 'Bearer ' + newAccessToken;
                processQueue(null, newAccessToken);
                return axiosInstance(originalRequest);
            } catch (err) {
                processQueue(err, null);
                return Promise.reject(err);
                
            } finally {
                isRefreshing = false;
            }
        }
        
        return Promise.reject(error);
    }
);

// Thêm một interceptor để tự động đính kèm token vào mỗi request
axiosInstance.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
        const token = getAccessToken();
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default axiosInstance;