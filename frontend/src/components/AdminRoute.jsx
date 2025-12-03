// src/components/AdminRoute.jsx (Tạo file này)

import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import useUserAuth from '../hooks/useUserAuth'; 
import { CircularProgress, Box } from '@mui/material';

const AdminRoute = () => {
    const { user, isAuthenticated, isLoadingUser } = useUserAuth();

    // 1. Loading
    if (isLoadingUser) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
                <CircularProgress />
            </Box>
        );
    }

    // Định nghĩa các vai trò có quyền truy cập
    const allowedRoles = ['Admin', 'Faculty Manager']; 
    const isAuthorized = user && allowedRoles.includes(user.role);

    // 2. Check Authentication
    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    // 3. Check Authorization (Vai trò)
    if (isAuthorized) {
        return <Outlet />;
    }
    
    // Nếu đã đăng nhập nhưng không đủ quyền, chuyển hướng về trang chat chính
    return <Navigate to="/" replace />; 
};

export default AdminRoute;