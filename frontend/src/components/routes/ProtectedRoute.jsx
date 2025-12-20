import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import useUserAuth from '../../hooks/useUserAuth'; 
import LoadingScreen from '../LoadingScreen.jsx';

const ProtectedRoute = () => {
    const { user, isAuthenticated, isLoadingUser } = useUserAuth();

    if (isLoadingUser) {
        return <LoadingScreen />;
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    if (user?.role === 'Admin' || user?.is_faculty_manager) {
        return <Navigate to="/admin/dashboard" replace />;
    }

    return <Outlet />;
};

export default ProtectedRoute;