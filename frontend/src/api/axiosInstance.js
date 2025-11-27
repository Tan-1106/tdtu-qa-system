import axios from 'axios';

const baseURL = import.meta?.env?.VITE_API_BASE || '/api';

// Tạo một instance của Axios
const axiosInstance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Thêm một interceptor để tự động đính kèm token vào mỗi request
axiosInstance.interceptors.request.use(
  (config) => {
    // Kiểm tra xem có phải là browser không
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('accessToken');
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