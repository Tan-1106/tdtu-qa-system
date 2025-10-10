import React, { useState } from 'react';
import { Box, Typography, TextField, Button, Grid, Link as MuiLink, Paper, Avatar } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import AuthLayout from './AuthLayout.jsx';

const RegisterPage = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    if (password !== confirmPassword) {
      alert("Mật khẩu xác nhận không khớp!");
      return;
    }
    const formData = { fullName, email, password };
    console.log('Register form submitted:', formData);
    alert('Đã gửi thông tin đăng ký! Mở Console (F12) để xem dữ liệu.');
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
            sx={{
              '& .MuiOutlinedInput-root': { borderRadius: 3 }
            }}
          />
          <TextField 
            margin="normal" 
            required 
            fullWidth 
            id="email" 
            label="Địa chỉ Email" 
            name="email" 
            value={email} 
            onChange={(e) => setEmail(e.target.value)} 
            sx={{
              '& .MuiOutlinedInput-root': { borderRadius: 3 }
            }}
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
            sx={{
              '& .MuiOutlinedInput-root': { borderRadius: 3 }
            }}
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
            sx={{
              '& .MuiOutlinedInput-root': { borderRadius: 3 }
            }}
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