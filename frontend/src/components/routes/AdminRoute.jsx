// src/components/AdminRoute.jsx (Tạo file này)

import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import useUserAuth from '../../hooks/useUserAuth'; 
import LoadingScreen from '../LoadingScreen.jsx';

const AdminRoute = () => {
    const { user, isAuthenticated, isLoadingUser } = useUserAuth();

    if (isLoadingUser) {
        return <LoadingScreen />;
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    const isAuthorized = user?.role === 'Admin' || user?.is_faculty_manager;

    if (isAuthorized) {
        return <Outlet />;
    }
    
    return <Navigate to="/" replace />; 
};

export default AdminRoute;