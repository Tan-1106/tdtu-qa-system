import React, { useCallback, useMemo } from 'react';
import { Box, Paper, Typography, Button, Alert, styled } from '@mui/material';
import LoginIcon from '@mui/icons-material/Login';
import SchoolIcon from '@mui/icons-material/School';

// Environment Variables
const ELIT_BASE_URL = import.meta.env.VITE_ELIT_BASE_URL;
const CLIENT_ID = import.meta.env.VITE_ELIT_CLIENT_ID;
const CALLBACK_URL = import.meta.env.VITE_ELIT_CALLBACK_URL || `${window.location.origin}/auth-complete`;
const SCOPE = import.meta.env.VITE_ELIT_SCOPE || 'openid profile email';


// Custom styled component for the modern button
const GradientButton = styled(Button)(({ theme }) => ({
    background: 'linear-gradient(135deg, #1976d2 30%, #42a5f5 90%)',
    color: '#fff',
    padding: '12px 24px',
    fontWeight: 600,
    fontSize: '1rem',
    borderRadius: '12px',
    boxShadow: '0 4px 12px rgba(25, 118, 210, 0.4)',
    transition: 'transform 0.2s, box-shadow 0.2s',
    '&:hover': {
        transform: 'translateY(-2px)',
        boxShadow: '0 6px 16px rgba(25, 118, 210, 0.6)',
        background: 'linear-gradient(135deg, #1565c0 30%, #1976d2 90%)',
    },
}));


// Generate random state (hex)
function generateState(bytes = 16) {
    const arr = new Uint8Array(bytes);
    window.crypto.getRandomValues(arr);
    return Array.from(arr).map(b => b.toString(16).padStart(2, '0')).join('');
}


// Login Page Component
const LoginPage = () => {
  // Check for missing configuration
    const missingConfig = useMemo(() => {
        const missing = [];
        if (!ELIT_BASE_URL) missing.push('VITE_ELIT_BASE_URL');
        if (!CLIENT_ID) missing.push('VITE_ELIT_CLIENT_ID');
        return missing;
    }, []);

  // Handle ELIT Login
    const handleElitLogin = useCallback(() => {
        if (missingConfig.length) return;
        const state = generateState();
        localStorage.setItem('elit_oauth_state', state);
        const scopeParam = SCOPE.trim().replace(/\s+/g, '+');
        const authorizeUrl = `${ELIT_BASE_URL}/oauth2/v1/authorize?client_id=${encodeURIComponent(CLIENT_ID)}&redirect_uri=${encodeURIComponent(CALLBACK_URL)}&response_type=code&scope=${scopeParam}&state=${encodeURIComponent(state)}`;
    window.location.href = authorizeUrl;
    }, [missingConfig]);

    return (
        <Box 
            sx={{
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                minHeight: '100vh', 
                px: 2,
                // Background Gradient
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
                {/* School Icon/Logo */}
                <SchoolIcon sx={{ 
                    fontSize: 60, 
                    color: 'primary.main', 
                    mb: 1.5,
                    p: 1,
                    borderRadius: '50%',
                    bgcolor: 'rgba(25, 118, 210, 0.1)'
                }} />

                <Box mb={4}>
                    <Typography variant="h4" fontWeight={700} color="primary.dark" gutterBottom>
                        Hệ thống hỏi đáp cho sinh viên TDTU
                    </Typography>
                    <Typography variant="subtitle1" color="text.secondary">
                        Đăng nhập để tiếp tục sử dụng hệ thống
                    </Typography>
                </Box>

                {missingConfig.length > 0 && (
                    <Alert severity="error" sx={{ mb: 3 }}>
                        Thiếu cấu hình môi trường: {missingConfig.join(', ')}.
                    </Alert>
                )}

                <GradientButton
                    fullWidth
                    size="large"
                    startIcon={<LoginIcon />}
                    onClick={handleElitLogin}
                    disabled={missingConfig.length > 0}
                >
                    Đăng nhập bằng TDTU Account
                </GradientButton>

                <Box mt={3} p={1}>
                    <Alert 
                        severity="info" 
                        variant="standard" 
                        sx={{ bgcolor: 'rgba(25, 118, 210, 0.05)', borderRadius: 2 }}
                    >
                        Vui lòng sử dụng tài khoản Google được cấp bởi Trường Đại học Tôn Đức Thắng.
                    </Alert>
                </Box>
            </Paper>
        </Box>
    );
};

export default LoginPage;