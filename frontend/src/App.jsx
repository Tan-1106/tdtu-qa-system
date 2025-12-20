import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';

import UserLayout from './components/UserLayout.jsx';
import AdminLayout from './components/admin/AdminLayout.jsx';

import LoginPage from './components/auth/LoginPage.jsx';
import AuthComplete from './components/auth/AuthComplete.jsx';

import ChatPage from './components/ChatPage.jsx';
import DocumentListPage from './components/documents/DocumentListPage.jsx';
import PopularQuestionsPage from './components/faq/PopularQuestionsPage.jsx';

import DocumentManagementPage from './components/admin/DocumentManagementPage.jsx';
import PopularQuestionManagementPage from './components/admin/PopularQuestionManagementPage.jsx';
import FeedbackDashboardPage from './components/admin/FeedbackDashboardPage.jsx';
import UserManagementPage from './components/admin/UserManagementPage.jsx';
import ModelManagementPage from './components/admin/ModelManagementPage.jsx'; 

import ProtectedRoute from './components/routes/ProtectedRoute.jsx'; 
import AdminRoute from './components/routes/AdminRoute.jsx'; 
import useUserAuth from './hooks/useUserAuth'; 

const RoleRedirector = () => {
    const { user, isLoadingUser, isAuthenticated } = useUserAuth();

    if (isLoadingUser) {
        return <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}><CircularProgress /></Box>;
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    // Nếu là Admin hoặc Faculty Manager, chuyển hướng đến trang Admin
    if (user?.role === 'Admin' || user?.is_faculty_manager === true) {
        return <Navigate to="/admin/dashboard" replace />;
    }

    // Nếu là Student chuyển hướng đến trang chat chính
    return <Navigate to="/" replace />; 
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/auth-complete" element={<AuthComplete />} />

        <Route path="/role-dispatch" element={<RoleRedirector />} />

        <Route element={<ProtectedRoute />}>
            <Route element={<UserLayout />}>
                <Route index element={<ChatPage />} />
                <Route path="documents" element={<DocumentListPage />} />
                <Route path="popular-questions" element={<PopularQuestionsPage />} />
            </Route>
        </Route>

        <Route element={<AdminRoute />}>
            <Route path="/admin" element={<AdminLayout />}>
                <Route index element={<Navigate to="dashboard" replace />} />
                <Route path="dashboard" element={<FeedbackDashboardPage />} /> 
                <Route path="popular-questions" element={<PopularQuestionManagementPage />} /> 
                <Route path="documents" element={<DocumentManagementPage />} />
                <Route path="users" element={<UserManagementPage />} />
                <Route path="models" element={<ModelManagementPage />} />
            </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;