import React, { useState } from 'react';
import { Outlet, NavLink as RouterNavLink } from 'react-router-dom';
import {
    Box, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText,
    AppBar, Toolbar, Typography, CssBaseline, Button, Divider, Stack,
    IconButton, useMediaQuery, CircularProgress
} from '@mui/material';

import ArticleIcon from '@mui/icons-material/Article';
import FeedbackIcon from '@mui/icons-material/Feedback';
import GroupIcon from '@mui/icons-material/Group';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';
import DnsIcon from '@mui/icons-material/Dns';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import QuizIcon from '@mui/icons-material/Quiz';

import tdtuLogo from '../../assets/logo_tdtu.png';
import useUserAuth from '../../hooks/useUserAuth';

const drawerWidth = 260;
const collapsedWidth = 70;

const AdminLayout = () => {
    const [open, setOpen] = useState(true);
    const [mobileOpen, setMobileOpen] = useState(false);
    const isMobile = useMediaQuery('(max-width: 899px)');
    const { user, isLoadingUser, handleLogout } = useUserAuth();

    if (isLoadingUser) return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
            <CircularProgress />
        </Box>
    );

    if (!user) return null;

    const isAdmin = user.role === "Admin";
    const sidebarTitle = isAdmin ? "TDTU Admin" : "TDTU Manager";

    const menuItems = [
        { text: "Thống kê & Phản hồi", to: "/admin/dashboard", icon: <FeedbackIcon /> },
        { text: "Câu hỏi phổ biến", to: "/admin/popular-questions", icon: <QuizIcon /> },
        { text: "Quản lý Tài liệu", to: "/admin/documents", icon: <ArticleIcon /> },
        { text: "Người dùng", to: "/admin/users", icon: <GroupIcon /> },
        ...(isAdmin ? [{ text: "Model & API", to: "/admin/models", icon: <DnsIcon /> }] : [])
    ];

    const drawerContent = (
        <Box sx={{ height: "100%", display: "flex", flexDirection: "column", bgcolor: 'primary.dark', color: 'white' }}>
            <Toolbar sx={{ flexDirection: "column", py: 2 }}>
                <Stack direction="row" spacing={2} alignItems="center" sx={{ width: '100%' }}>
                    <Box component="img" src={tdtuLogo} sx={{ height: 40, borderRadius: 1 }} />
                    {(open || isMobile) && <Typography variant="h6" fontWeight={700}>{sidebarTitle}</Typography>}
                </Stack>
                {open && !isAdmin && user.department && (
                    <Typography variant="caption" sx={{ mt: 1, opacity: 0.8 }}>{user.department}</Typography>
                )}
            </Toolbar>
            <Divider sx={{ bgcolor: 'rgba(255,255,255,0.12)' }} />
            <List sx={{ px: 1, mt: 1 }}>
                {menuItems.map((item) => (
                    <ListItem key={item.text} disablePadding>
                        <ListItemButton
                            component={RouterNavLink}
                            to={item.to}
                            sx={{
                                borderRadius: 2, mb: 0.5,
                                justifyContent: (open || isMobile) ? 'initial' : 'center',
                                '&:hover': { 
                                    bgcolor: 'rgba(255,255,255,0.08)',
                                    color: 'white', 
                                    '& .MuiListItemIcon-root': { color: 'white' }
                                },
                                '&.active': { bgcolor: 'rgba(255,255,255,0.2)', fontWeight: 700 }
                            }}
                        >
                            <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>{item.icon}</ListItemIcon>
                            {(open || isMobile) && <ListItemText primary={item.text} />}
                        </ListItemButton>
                    </ListItem>
                ))}
            </List>
        </Box>
    );

    return (
        <Box sx={{ display: "flex" }}>
            <CssBaseline />
            <AppBar
                position="fixed"
                elevation={0}
                sx={{
                    width: isMobile ? '100%' : `calc(100% - ${open ? drawerWidth : collapsedWidth}px)`,
                    ml: isMobile ? 0 : `${open ? drawerWidth : collapsedWidth}px`,
                    bgcolor: 'white', color: 'text.primary', borderBottom: '1px solid #eee',
                    transition: 'all 0.3s ease'
                }}
            >
                <Toolbar>
                    <IconButton onClick={() => isMobile ? setMobileOpen(true) : setOpen(!open)} sx={{ mr: 2 }}>
                        {open ? <ChevronLeftIcon /> : <MenuIcon />}
                    </IconButton>
                    <Typography 
                        variant="h6" 
                        noWrap 
                        sx={{ 
                            flexGrow: 1, 
                            fontWeight: 700, 
                            letterSpacing: '0.2px', 
                            fontSize: '1.15rem', 
                            color: 'primary.main',  
                            fontFamily: "'Roboto', sans-serif", 
                        }}
                    >
                        TRANG QUẢN TRỊ
                    </Typography>
                    <Button 
                        onClick={handleLogout}
                        variant="text"
                        startIcon={<ExitToAppIcon />}
                        sx={{
                            fontWeight: 700,
                            textTransform: 'none',
                            borderRadius: '12px',
                            color: 'error.main',
                            bgcolor: 'rgba(211, 47, 47, 0.05)',
                            px: 2,
                            '&:hover': {
                                bgcolor: 'rgba(211, 47, 47, 0.12)',
                                transform: 'scale(1.02)',
                            }
                        }}
                    >
                        Đăng xuất
                    </Button>
                </Toolbar>
            </AppBar>

            <Drawer
                variant={isMobile ? "temporary" : "permanent"}
                open={isMobile ? mobileOpen : open}
                onClose={() => setMobileOpen(false)}
                sx={{
                    width: open ? drawerWidth : collapsedWidth,
                    flexShrink: 0,
                    '& .MuiDrawer-paper': { 
                        width: isMobile ? drawerWidth : (open ? drawerWidth : collapsedWidth),
                        transition: 'width 0.3s ease', overflowX: 'hidden', border: 'none'
                    }
                }}
            >
                {drawerContent}
            </Drawer>

            <Box component="main" sx={{ flexGrow: 1, p: 3, bgcolor: '#f4f6f8', minHeight: '100vh' }}>
                <Toolbar />
                <Outlet />
            </Box>
        </Box>
    );
};

export default AdminLayout;