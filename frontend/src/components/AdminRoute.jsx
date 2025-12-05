// src/components/AdminRoute.jsx (Tạo file này)

import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import useUserAuth from '../hooks/useUserAuth'; 
import { CircularProgress, Box } from '@mui/material';

const AdminRoute = () => {
    const { user, isAuthenticated, isLoadingUser } = useUserAuth();

    if (isLoadingUser) {
        return (
            <Box
                sx={{
                    position: "fixed",
                    inset: 0,
                    background: "rgba(255, 255, 255, 0.7)",
                    backdropFilter: "blur(4px)",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    zIndex: 9999,
                }}
            >
                <CircularProgress size={60} thickness={4} />
                <Box
                    sx={{
                        mt: 2,
                        fontSize: "1.1rem",
                        fontWeight: 500,
                        color: "#555",
                        animation: "fadeIn 1s ease-in-out infinite alternate"
                    }}
                >
                    Đang kiểm tra quyền truy cập...
                </Box>
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