import axios from 'axios';

const BACKEND_URL = import.meta?.env?.VITE_BACKEND_URL || 'http://localhost:8000';
const baseURL = `${BACKEND_URL}/api`;
// Tạo một instance của Axios
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
        // Lưu ý: Đảm bảo key này khớp với key bạn đang sử dụng ('accessToken' hoặc 'access_token')
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
        // Nếu không có refresh token, báo lỗi để buộc đăng nhập lại
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
        throw error; // Re-throw để thông báo thất bại
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
        
        // 1. Kiểm tra lỗi 401 Unauthorized (Access Token hết hạn) và chưa thử lại
        if (error.response && error.response.status === 401 && !originalRequest._retry) {
            
            // Thiết lập cờ để không bị lặp vô hạn
            originalRequest._retry = true;
            
            if (isRefreshing) {
                // Nếu đã có quá trình refresh đang chạy, thêm request vào hàng đợi
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
                // Thực hiện refresh token
                const newAccessToken = await refreshAccessToken();
                
                // Cập nhật token cho request ban đầu
                originalRequest.headers['Authorization'] = 'Bearer ' + newAccessToken;
                
                // Xử lý các request trong hàng đợi
                processQueue(null, newAccessToken);
                
                // Thử lại request ban đầu
                return axiosInstance(originalRequest);

            } catch (err) {
                // Refresh thất bại, xóa token và ném lỗi
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
    // Kiểm tra xem có phải là browser không
    if (typeof window !== 'undefined') {
    //   const token = localStorage.getItem('accessToken');
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