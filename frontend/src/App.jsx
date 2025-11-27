// src/App.jsx
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// Layouts
import UserLayout from './components/UserLayout.jsx';
import AdminLayout from './components/admin/AdminLayout.jsx';

// Auth Pages
import LoginPage from './components/auth/LoginPage.jsx';
import AuthComplete from './components/auth/AuthComplete.jsx';

// User Pages
import ChatPage from './components/ChatPage.jsx';
import DocumentListPage from './components/documents/DocumentListPage.jsx';
import PopularQuestionsPage from './components/faq/PopularQuestionsPage.jsx';

// Admin Pages
import DocumentManagementPage from './components/admin/DocumentManagementPage.jsx';
import FeedbackDashboardPage from './components/admin/FeedbackDashboardPage.jsx';
import UserManagementPage from './components/admin/UserManagementPage.jsx';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* === CÁC TRANG CỦA NGƯỜI DÙNG === */}
        <Route element={<UserLayout />}>
          <Route path="/" element={<ChatPage />} />
          <Route path="/documents" element={<DocumentListPage />} />
          <Route path="/popular-questions" element={<PopularQuestionsPage />} />
        </Route>

        {/* === CÁC TRANG XÁC THỰC === */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/auth-complete" element={<AuthComplete />} />

        {/* === CÁC TRANG CỦA ADMIN === */}
        <Route path="/admin" element={<AdminLayout />}>
          <Route path="dashboard" element={<FeedbackDashboardPage />} />
          <Route path="documents" element={<DocumentManagementPage />} />
          <Route path="users" element={<UserManagementPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;