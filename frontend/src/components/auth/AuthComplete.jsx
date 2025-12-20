import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Box, CircularProgress, Alert, Typography, Button } from '@mui/material'; 
import SchoolIcon from '@mui/icons-material/School';
import AuthLayout from './AuthLayout';
import axiosInstance, { setTokens } from '../../api/axiosInstance'; 

const extractError = (error, defaultMessage) => {
    return error.response?.data?.details || error.message || defaultMessage || 'Lỗi không xác định.';
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

        const verifyAuth = async () => {
            setIsProcessing(true);
            try {
                const resp = await axiosInstance.post('/auth/verify', { code });
                const { tokens, user: userData } = resp.data?.details || {};

                if (tokens?.access_token && tokens?.refresh_token) {
                    setTokens({ access_token: tokens.access_token, refresh_token: tokens.refresh_token }); 
                } else {
                    throw new Error("Missing tokens in server response.");
                }

                if (userData) {
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
                if (finalError.includes("User is banned")) finalError = "Tài khoản của bạn đã bị khóa.";
                setError(finalError);
            } finally {
                setIsProcessing(false);
            }
        };
        verifyAuth();
    }, [searchParams, navigate]);

    return (
        <AuthLayout>
            {error ? (
                <Box>
                    <Typography variant="h5" color="error" fontWeight={700} sx={{ mb: 2 }}>
                        Xác thực thất bại
                    </Typography>
                    <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>
                    <Button 
                        variant="contained" 
                        onClick={() => navigate('/login')}
                        sx={{ borderRadius: '12px', fontWeight: 600 }}
                    >
                        Quay lại trang Đăng nhập
                    </Button>
                </Box>
            ) : (
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <CircularProgress size={60} thickness={4} sx={{ mb: 2 }} />
                    <Typography variant="h6" color="primary.dark" fontWeight={700}>
                        Đang xử lý đăng nhập...
                    </Typography>
                    <SchoolIcon sx={{ fontSize: 40, color: 'primary.light', mt: 3 }} />
                </Box>
            )}
        </AuthLayout>
    );
};

export default AuthComplete;