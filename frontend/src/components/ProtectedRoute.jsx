import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import useUserAuth from '../hooks/useUserAuth'; 
import { CircularProgress, Box } from '@mui/material';

const ProtectedRoute = () => {
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

    // 1. Check Authentication
    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    const isAdminOrManager = user && (user.role === 'Admin' || user.is_faculty_manager === true);
    
    if (isAdminOrManager) {
        // Nếu là Admin, chuyển hướng ra khỏi khu vực Student và đến Admin Dashboard
        return <Navigate to="/admin/dashboard" replace />;
    }

    // 3. Nếu là Student, cho phép truy cập User Route
    return <Outlet />;
};

export default ProtectedRoute;