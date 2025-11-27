import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Box, CircularProgress, Paper, Alert } from '@mui/material';
import axiosInstance from '../../api/axiosInstance';

const AuthComplete = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const didRunRef = useRef(false);

  useEffect(() => {
    if (didRunRef.current) return; // Prevent double-run in React StrictMode
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
        const details = resp.data?.details || {};

        // Store tokens & user
        if (details.access_token) {
          localStorage.setItem('accessToken', details.access_token);
        }
        
        localStorage.setItem('currentUser', JSON.stringify({
          uid: details.uid,
          username: details.username,
          name: details.name,
          email: details.email,
          image: details.image,
          nickname: details.nickname,
          given_name: details.given_name,
          family_name: details.family_name,
          email_verified: details.email_verified,
          role: 'User',
        }));

        localStorage.removeItem('elit_oauth_state');
        navigate('/');
      } catch (e) {
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