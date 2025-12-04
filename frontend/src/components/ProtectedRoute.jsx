import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import useUserAuth from '../hooks/useUserAuth'; 
import { CircularProgress, Box } from '@mui/material';

const ProtectedRoute = () => {
    const { user, isAuthenticated, isLoadingUser } = useUserAuth();

    // Hiển thị Loading trong khi fetch trạng thái user
    if (isLoadingUser) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
                <CircularProgress />
            </Box>
        );
    }

    // 1. Check Authentication
    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    // 2. 💡 FIX: Access Control - Chặn Admin truy cập khu vực User
    const isAdminOrManager = user && (user.role === 'Admin' || user.role === 'Faculty Manager');
    
    if (isAdminOrManager) {
        // Nếu là Admin, chuyển hướng ra khỏi khu vực Student và đến Admin Dashboard
        return <Navigate to="/admin/dashboard" replace />;
    }

    // 3. Nếu là Student, cho phép truy cập User Route
    return <Outlet />;
};

export default ProtectedRoute;