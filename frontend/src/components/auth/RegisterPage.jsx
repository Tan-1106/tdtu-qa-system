import React, { useState } from 'react';
import { Box, Typography, TextField, Button, Grid, Link as MuiLink, Paper, Avatar, Alert } from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom'; // Thêm useNavigate
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import AuthLayout from './AuthLayout.jsx';
import axiosInstance from '../../api/axiosInstance'; // Import axiosInstance

const RegisterPage = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  // Thêm state cho lỗi và thành công
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');

    if (password !== confirmPassword) {
      setError("Mật khẩu xác nhận không khớp!");
      return;
    }

    try {
      // Gọi API đăng ký
      await axiosInstance.post('/auth/register', {
        full_name: fullName,
        email: email,
        password: password,
      });

      setSuccess('Đăng ký thành công! Đang chuyển đến trang đăng nhập...');
      // Chuyển hướng đến trang đăng nhập sau 2 giây
      setTimeout(() => {
        navigate('/login');
      }, 2000);

    } catch (err) {
      // Hiển thị lỗi từ backend
      const errorMessage = err.response?.data?.message || 'Đã có lỗi xảy ra. Vui lòng thử lại.';
      setError(errorMessage);
    }
  };

  return (
    <AuthLayout>
      <Paper 
        elevation={8}
        sx={{
          p: { xs: 3, md: 5 },
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          borderRadius: 5,
          boxShadow: '0 8px 32px 0 rgba(25,118,210,0.10)'
        }}
      >
        <Avatar sx={{ m: 1, bgcolor: 'primary.main', width: 56, height: 56 }}>
          <LockOutlinedIcon fontSize="large" />
        </Avatar>
        <Typography component="h1" variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
          Đăng ký
        </Typography>

        {/* Hiển thị thông báo */}
        {error && <Alert severity="error" sx={{ width: '100%', mt: 2, borderRadius: 3 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ width: '100%', mt: 2, borderRadius: 3 }}>{success}</Alert>}

        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2, width: '100%' }}>
          <TextField 
            margin="normal" 
            required 
            fullWidth 
            id="fullName" 
            label="Họ và Tên" 
            name="fullName" 
            autoFocus 
            value={fullName} 
            onChange={(e) => setFullName(e.target.value)} 
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
          />
          <TextField 
            margin="normal" 
            required 
            fullWidth 
            id="email" 
            label="Địa chỉ Email" 
            name="email" 
            type="email"
            value={email} 
            onChange={(e) => setEmail(e.target.value)} 
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
          />
          <TextField 
            margin="normal" 
            required 
            fullWidth 
            name="password" 
            label="Mật khẩu" 
            type="password" 
            id="password" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)} 
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
          />
          <TextField 
            margin="normal" 
            required 
            fullWidth 
            name="confirmPassword" 
            label="Xác nhận Mật khẩu" 
            type="password" 
            id="confirmPassword" 
            value={confirmPassword} 
            onChange={(e) => setConfirmPassword(e.target.value)} 
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{
              mt: 3, mb: 2, py: 1.5, borderRadius: 3, fontWeight: 700,
              fontSize: '1.1rem',
              boxShadow: '0 2px 8px 0 rgba(25,118,210,0.10)',
              background: 'linear-gradient(90deg, #1976d2 60%, #42a5f5 100%)',
              transition: '0.2s',
              '&:hover': {
                background: 'linear-gradient(90deg, #1565c0 60%, #1976d2 100%)'
              }
            }}
          >
            Đăng ký
          </Button>
          <Grid container justifyContent="flex-end">
            <Grid item>
              <MuiLink component={RouterLink} to="/login" variant="body2" sx={{ fontWeight: 500 }}>
                Đã có tài khoản? Đăng nhập
              </MuiLink>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    </AuthLayout>
  );
};

export default RegisterPage;