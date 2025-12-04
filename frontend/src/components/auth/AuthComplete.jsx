import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Box, CircularProgress, Paper, Alert } from '@mui/material';
// Cần import setTokens nếu bạn đã export nó từ axiosInstance.js
import axiosInstance, { setTokens } from '../../axiosInstance'; // Đảm bảo đã import setTokens

const AuthComplete = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const didRunRef = useRef(false);

  useEffect(() => {
    if (didRunRef.current) return; 
    didRunRef.current = true;
    const state = searchParams.get('state');
    const code = searchParams.get('code');
    const savedState = localStorage.getItem('elit_oauth_state');

    if (!state || !code || !savedState || savedState !== state) {
      setError('Phiên đăng nhập không hợp lệ. Vui lòng thử lại.');
      return;
    }

    // Exchange code for tokens via backend
    const run = async () => {
      try {
        const resp = await axiosInstance.post('/auth/verify', { code });
        
        // Backend trả về: resp.data.details = { user: {...}, tokens: {...} }
        const tokens = resp.data?.details?.tokens; 
        const userData = resp.data?.details?.user;

        // 1. Store tokens & user
        if (tokens && tokens.access_token && tokens.refresh_token) {
          // ✅ SỬ DỤNG setTokens để lưu đồng bộ cả hai
          setTokens({ 
                access_token: tokens.access_token, 
                refresh_token: tokens.refresh_token 
            }); 
        } else {
            // Trường hợp backend không trả tokens (mặc dù Status 200, nhưng data thiếu)
            throw new Error("Missing tokens in server response.");
        }
        
        // 2. Lưu thông tin người dùng (Optional, nếu bạn không muốn gọi /auth/me ngay)
        // Lưu ý: Dữ liệu bạn lưu ở đây khác với dữ liệu /auth/me
        if (userData) {
            localStorage.setItem('currentUser', JSON.stringify({
                // Trích xuất các trường từ userData (user._id, user.name, user.email, user.role, user.faculty)
                // Lưu ý: user.sub (MSSV) và user.faculty (Khoa) là quan trọng nhất
                name: userData.name,
                uid: userData._id,
                studentId: userData.sub,
                role: userData.role,
                faculty: userData.faculty,
            }));
        }


        localStorage.removeItem('elit_oauth_state');
        navigate('/role-dispatch'); 
      } catch (e) {
        // Xử lý lỗi nếu việc gọi /auth/verify thất bại
        const msg = e.response?.data?.details || e.response?.data?.message || 'Không trao đổi được token với ELIT.';
        setError(msg);
      }
    };
    run();
  }, [searchParams, navigate]);

  return (
    <Box display="flex" alignItems="center" justifyContent="center" minHeight="60vh">
      <Paper sx={{ p: 4, borderRadius: 3, minWidth: 360, textAlign: 'center' }}>
        {!error ? (
          <CircularProgress />
        ) : (
          <Alert severity="error">{error}</Alert>
        )}
      </Paper>
    </Box>
  );
};

export default AuthComplete;