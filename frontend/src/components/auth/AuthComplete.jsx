import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Box, CircularProgress, Paper, Alert, Typography, Button } from '@mui/material'; 
import SchoolIcon from '@mui/icons-material/School';
import axiosInstance, { setTokens } from '../../axiosInstance'; 

const extractError = (error, defaultMessage) => {
    if (error.response?.data?.details) {
        return error.response.data.details; 
    }
    return error.message || defaultMessage || 'Lỗi không xác định.';
};

const AuthComplete = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const didRunRef = useRef(false);
  const [isProcessing, setIsProcessing] = useState(true); 

  useEffect(() => {
    if (didRunRef.current) return; 
    didRunRef.current = true;
    const state = searchParams.get('state');
    const code = searchParams.get('code');
    const savedState = localStorage.getItem('elit_oauth_state');

    if (!state || !code || !savedState || savedState !== state) {
      setError('Phiên đăng nhập không hợp lệ. Vui lòng thử lại.');
      setIsProcessing(false);
      return;
    }

    const run = async () => {
      setIsProcessing(true);
      try {
        const resp = await axiosInstance.post('/auth/verify', { code });
        const tokens = resp.data?.details?.tokens; 
        const userData = resp.data?.details?.user;

        if (tokens && tokens.access_token && tokens.refresh_token) {
          setTokens({ 
                access_token: tokens.access_token, 
                refresh_token: tokens.refresh_token 
            }); 
        } else {
            throw new Error("Missing tokens in server response.");
        }

        if (userData) {
            // Lưu thông tin cơ bản
            localStorage.setItem('currentUser', JSON.stringify({
                name: userData.name,
                uid: userData._id,
                studentId: userData.sub,
                role: userData.role,
                faculty: userData.faculty,
                is_faculty_manager: userData.is_faculty_manager,
            }));
        }

        localStorage.removeItem('elit_oauth_state');
        navigate('/role-dispatch'); 

      } catch (e) {
        let finalError = extractError(e, 'Bạn đã bị từ chối cấp quyền hoặc có sự cố xảy ra.'); 
        if (finalError.includes("User is banned")) {
            finalError = "Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị viên.";
        } else if (finalError.includes("Permission denied")) {
            finalError = "Bạn không có quyền truy cập hệ thống.";
        }
        setError(finalError);
      } finally {
        setIsProcessing(false);
      }
    };
    run();
  }, [searchParams, navigate]);

  return (
      <Box 
            sx={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                minHeight: '100vh', 
                // Sử dụng màu nền giống trang Login
                background: 'linear-gradient(180deg, #f0f7ff 0%, #e8f0fe 100%)', 
            }}
        >
            <Paper 
                elevation={12} 
                sx={{ 
                    p: { xs: 4, md: 6 }, 
                    maxWidth: 450, 
                    width: '100%', 
                    borderRadius: 4, 
                    textAlign: 'center',
                    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
                }}
            >
                {/* 💡 HIỂN THỊ LỖI */}
                {error ? (
                    <Box>
                        <Typography variant="h5" color="error" fontWeight={700} sx={{ mb: 2 }}>
                            Xác thực thất bại
                        </Typography>
                        <Alert severity="error" sx={{ mb: 3, textAlign: 'left', fontWeight: 500 }}>
                            {error}
                        </Alert>
                        <Button 
                            variant="contained" 
                            color="primary" 
                            onClick={() => navigate('/login')}
                            sx={{ mt: 1, borderRadius: '12px', fontWeight: 600 }}
                        >
                            Quay lại trang Đăng nhập
                        </Button>
                    </Box>
                ) : (
                    // 💡 GIAO DIỆN LOADING
                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                        <CircularProgress color="primary" size={60} thickness={4} sx={{ mb: 2 }} />
                        <Typography variant="h6" color="primary.dark" fontWeight={700}>
                            Đang xử lý đăng nhập...
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                            Vui lòng chờ trong giây lát.
                        </Typography>
                        <SchoolIcon sx={{ fontSize: 40, color: 'primary.light', mt: 3 }} />
                    </Box>
                )}
            </Paper>
        </Box>
  );
};

export default AuthComplete;