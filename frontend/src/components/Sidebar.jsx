import React, { useState } from 'react';
import { Box, Button, Typography, IconButton, Avatar, Stack, Divider, useTheme } from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';
import CloseIcon from '@mui/icons-material/Close'; 
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import FolderOpenOutlinedIcon from '@mui/icons-material/FolderOpenOutlined';
import HelpOutlineOutlinedIcon from '@mui/icons-material/HelpOutlineOutlined';
import LogoutIcon from '@mui/icons-material/Logout';
import { NavLink as RouterNavLink, useNavigate } from 'react-router-dom'; 
import useUserAuth from '../hooks/useUserAuth';

const initialHistory = [
  { id: 'chat-1', title: 'Hỏi về quy chế học vụ', date: '2025-10-01' },
  { id: 'chat-2', title: 'Yêu cầu phúc khảo điểm', date: '2025-10-05' },
  { id: 'chat-3', title: 'Thông tin về học bổng', date: '2025-10-10' },
];

const sidebarWidth = '280px';

const Sidebar = ({ isSidebarOpen, toggleSidebar, activeChatId, setActiveChatId }) => {
    const theme = useTheme();
    const navigate = useNavigate();
    const { user, handleLogout } = useUserAuth();

    const [history] = useState(initialHistory); 

    const handleNewChat = () => {
        if (window.location.pathname !== '/') {
            navigate('/'); 
        }

        setActiveChatId(null); 
        
        if (window.innerWidth < theme.breakpoints.values.md) {
          toggleSidebar();
        }
    };

    const handleLoadChat = (chatId) => {
        if (window.location.pathname !== '/') {
            navigate('/'); 
        }

        if (activeChatId !== chatId) {
            setActiveChatId(chatId); 
        }
        
        if (window.innerWidth < theme.breakpoints.values.md) {
          toggleSidebar();
        }
    };
    
    const defaultUser = { name: 'Đang tải...', studentId: '...', department: '...', avatar: '?' };
    const currentUser = user || defaultUser;

    return (
        <Box sx={{
            width: sidebarWidth,
            background: 'linear-gradient(180deg, #1976d2 60%, #42a5f5 100%)',
            color: 'white',
            p: 1.5,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            borderRight: '1px solid #104e8c',
            position: 'fixed',
            top: 0,
            bottom: 0,
            left: 0,
            zIndex: 100,
            transform: isSidebarOpen ? 'translateX(0)' : 'translateX(-100%)',
            transition: 'transform 0.3s ease-in-out',
            display: { xs: isSidebarOpen ? 'flex' : 'none', md: 'flex' }
        }}>
            
            <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
                <Stack 
                    direction="row" 
                    alignItems="center" 
                    justifyContent="space-between" 
                    spacing={1} 
                    sx={{ mb: 2, p: 0.5 }}
                >
                    <Stack direction="row" alignItems="center" spacing={1}>
                        <SchoolIcon fontSize="large" sx={{ color: 'white' }} />
                        <Typography variant="h6" fontWeight={700}>TDTU Q&A</Typography>
                    </Stack>
                    <IconButton 
                        onClick={toggleSidebar} 
                        sx={{ color: 'white', display: { md: 'none' } }} 
                    >
                        <CloseIcon />
                    </IconButton>
                </Stack>

                <Button
                    fullWidth
                    startIcon={<AddCircleOutlineIcon />}
                    onClick={handleNewChat} 
                    variant={activeChatId === null ? 'contained' : 'outlined'} 
                    sx={{ 
                        mb: 3, 
                        borderColor: 'rgba(255,255,255,0.4)', 
                        color: activeChatId === null ? 'primary.dark' : 'white',
                        bgcolor: activeChatId === null ? 'white' : 'transparent',
                        justifyContent: 'flex-start',
                        borderRadius: '10px',
                        height: '50px',
                        '&:hover': { 
                            borderColor: 'white', 
                            bgcolor: activeChatId === null ? 'white' : 'rgba(255,255,255,0.1)' 
                        } 
                    }}
                >
                    Cuộc trò chuyện mới
                </Button>
                
                <Divider sx={{ mb: 2, borderColor: '#104e8c' }} /> 
                
                <Typography variant="subtitle2" sx={{ opacity: 0.7, mb: 1, textTransform: 'uppercase' }}>
                    Điều hướng
                </Typography>
                <Box>
                    {[
                        { path: '/documents', label: 'Tài liệu', icon: <FolderOpenOutlinedIcon /> }, 
                        { path: '/popular-questions', label: 'Câu hỏi phổ biến', icon: <HelpOutlineOutlinedIcon /> }
                    ].map((item) => (
                        <Button
                            key={item.path}
                            fullWidth
                            component={RouterNavLink}
                            to={item.path}
                            startIcon={item.icon}
                            sx={{ 
                                justifyContent: 'flex-start', 
                                color: 'white', 
                                mb: 1, 
                                borderRadius: '10px',
                                '&.active': { background: theme.palette.primary.main, color: 'white' },
                                '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } ,
                            }}
                        >
                            {item.label}
                        </Button>
                    ))}
                </Box>

                <Divider sx={{ my: 2, borderColor: '#104e8c' }} />
                
                <Typography variant="subtitle2" sx={{ opacity: 0.7, mb: 1, textTransform: 'uppercase' }}>
                    Lịch sử
                </Typography>
                <Box>
                    {history.map((chat) => (
                        <Button 
                            key={chat.id}
                            fullWidth
                            variant={chat.id === activeChatId ? 'contained' : 'text'}
                            onClick={() => handleLoadChat(chat.id)} 
                            sx={{ 
                                justifyContent: 'flex-start', 
                                mb: 0.5,
                                color: 'rgba(255,255,255,0.8)',
                                bgcolor: chat.id === activeChatId ? theme.palette.primary.main : 'transparent', // Nền active màu primary.main
                                borderRadius: '10px',
                                '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' },
                                whiteSpace: 'nowrap',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                            }}
                        >
                            {chat.title}
                        </Button>
                    ))}
                </Box>
            </Box>
            
            <Box sx={{ borderTop: '1px solid #104e8c', pt: 1 }}>
                <Stack direction="row" alignItems="center" spacing={1} sx={{ p: 1, borderRadius: '10px', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } }}>
                    <Avatar sx={{ bgcolor: 'secondary.main', color: 'white', width: 32, height: 32, fontSize: '14px', fontWeight: 700 }}>
                        {currentUser.avatar}
                    </Avatar>
                    
                    <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                        <Typography variant="body2" fontWeight={600} noWrap>{currentUser.name}</Typography>
                        <Typography variant="caption" sx={{ opacity: 0.7, display: 'block' }} noWrap>{currentUser.studentId}</Typography>
                        <Typography variant="caption" sx={{ opacity: 0.7, display: 'block' }} noWrap>{currentUser.department}</Typography>
                    </Box>
                    
                    <IconButton onClick={handleLogout} sx={{ color: 'white' }} title="Đăng xuất">
                        <LogoutIcon />
                    </IconButton>
                </Stack>
            </Box>
        </Box>
    );
};

export default Sidebar;