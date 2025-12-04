import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Box, Typography } from '@mui/material'; 
import Sidebar from './Sidebar'; 
import MenuIcon from '@mui/icons-material/Menu';
import IconButton from '@mui/material/IconButton';

const sidebarWidth = '280px';
// Dữ liệu mẫu ban đầu cho lịch sử
const initialChatId = 'chat-1';

const UserLayout = () => {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    // Nâng cấp state activeChatId lên đây
    const [activeChatId, setActiveChatId] = useState(initialChatId); 

    const toggleSidebar = () => {
        setIsSidebarOpen(prev => !prev);
    };

    // Giá trị Context được truyền cho Outlet (sử dụng cho ChatPage và các trang khác)
    const contextValue = { 
        isSidebarOpen, 
        toggleSidebar,
        activeChatId,
        setActiveChatId
    };

    return (
        <Box sx={{ 
            display: 'flex',
            height: '100vh', 
            width: '100%',
            bgcolor: '#f7fafd'
        }}>
            
            {/* Sidebar (Cố định vị trí) */}
            <Sidebar 
                isSidebarOpen={isSidebarOpen} 
                toggleSidebar={toggleSidebar}
                activeChatId={activeChatId}
                setActiveChatId={setActiveChatId} 
            />

            {/* Overlay cho Mobile khi Sidebar mở */}
            {isSidebarOpen && (
                <Box
                    onClick={toggleSidebar}
                    sx={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        bgcolor: 'rgba(0, 0, 0, 0.5)',
                        zIndex: 90,
                        display: { xs: 'block', md: 'none' }
                    }}
                />
            )}

            {/* Khu vực Nội dung Chính (Outlet) */}
            <Box 
                component="main" 
                sx={{ 
                    flexGrow: 1, 
                    display: 'flex',
                    flexDirection: 'column',
                    height: '100%', 
                    ml: { xs: 0, md: isSidebarOpen ? sidebarWidth : 0 },
                    transition: 'margin-left 0.3s ease-in-out',
                    width: '100%',
                }}
            > 
                {/* Header cho Mobile (chỉ hiện nút Menu) */}
                <Box sx={{ 
                    p: 1, 
                    bgcolor: 'white', 
                    display: { xs: 'flex', md: 'none' },
                    alignItems: 'center', 
                    borderBottom: '1px solid #e3e3e3',
                    position: 'sticky', 
                    top: 0,
                    zIndex: 10 
                }}>
                    <IconButton size="large" onClick={toggleSidebar} sx={{ color: 'text.primary' }}>
                        <MenuIcon />
                    </IconButton>
                    <Typography variant="h6" sx={{ fontWeight: 600, ml: 1 }}>TDTU Q&A</Typography>
                </Box>
                
                {/* Outlet sẽ render ChatPage, DocumentListPage, PopularQuestionsPage */}
                <Outlet context={contextValue} /> 
            </Box>
        </Box>
    );
}

export default UserLayout;