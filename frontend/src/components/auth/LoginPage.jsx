import React, { useCallback, useMemo } from 'react';
import { Box, Paper, Typography, Button, Alert } from '@mui/material';
import LoginIcon from '@mui/icons-material/Login';


// Environment Variables
const ELIT_BASE_URL = import.meta.env.VITE_ELIT_BASE_URL;
const CLIENT_ID = import.meta.env.VITE_ELIT_CLIENT_ID;
const CALLBACK_URL = import.meta.env.VITE_ELIT_CALLBACK_URL || `${window.location.origin}/auth-complete`;
const SCOPE = import.meta.env.VITE_ELIT_SCOPE || 'openid profile email';


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
		<Box display="flex" justifyContent="center" alignItems="center" minHeight="70vh" px={2}>
			<Paper elevation={4} sx={{ p: 5, maxWidth: 420, width: '100%', borderRadius: 4 }}>
				<Box mb={3} textAlign="center">
					<Typography variant="h5" fontWeight={600} gutterBottom>
						Hệ thống hỏi đáp dành cho sinh viên TDTU
					</Typography>
					<Typography variant="body2" color="text.secondary">
						Đăng nhập để sử dụng
					</Typography>
				</Box>

				<Button
					fullWidth
					size="large"
					variant="contained"
					color="primary"
					startIcon={<LoginIcon />}
					onClick={handleElitLogin}
					disabled={missingConfig.length > 0}
				>
					{missingConfig.length ? 'Thiếu cấu hình ENV' : 'Đăng nhập bằng Google'}
				</Button>

				<Box mt={2}>
					<Alert severity="info" variant="outlined">
						Ghi chú: Sinh viên chỉ có thể đăng nhập bằng tài khoản Google với Email do Trường cung cấp
					</Alert>
				</Box>
			</Paper>
		</Box>
	);
};

export default LoginPage;