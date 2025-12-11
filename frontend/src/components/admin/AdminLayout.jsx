import React, { useState } from 'react';
import { Outlet, NavLink as RouterNavLink } from 'react-router-dom';
import {
    Box, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText,
    AppBar, Toolbar, Typography, CssBaseline, Button, Divider, Stack,
    IconButton, useMediaQuery
} from '@mui/material';

import ArticleIcon from '@mui/icons-material/Article';
import FeedbackIcon from '@mui/icons-material/Feedback';
import GroupIcon from '@mui/icons-material/Group';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';
import DnsIcon from '@mui/icons-material/Dns';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';

import tdtuLogo from '../../assets/logo_tdtu.png';
import useUserAuth from '../../hooks/useUserAuth';

const drawerWidth = 240;
const collapsedDrawerWidth = 70;

const activeLinkStyle = {
    background: 'rgba(255,255,255,0.15)',
    color: 'white',
    borderRadius: 3,
    '& .MuiListItemIcon-root': { color: 'white' }
};

const AdminLayout = () => {
    const [open, setOpen] = useState(true);
    const [mobileOpen, setMobileOpen] = useState(false);
    const isMobile = useMediaQuery('(max-width: 899px)');
    const isDesktop = !isMobile;

    const handleDrawerToggle = () => {
        if (isMobile) setMobileOpen(!mobileOpen);
        else setOpen(!open);
    };

    const currentDrawerWidth = isDesktop ? (open ? drawerWidth : collapsedDrawerWidth) : drawerWidth;

    const { user: currentUser, isLoadingUser, handleLogout } = useUserAuth();
    if (isLoadingUser || !currentUser) return null;

    const isAdmin = currentUser?.role === "Admin";
    const isFacultyManager = currentUser?.is_faculty_manager;

    const sidebarTitle = isAdmin ? "TDTU Admin" : isFacultyManager ? "TDTU Manager" : "Quản trị";
    const departmentName = !isAdmin ? (currentUser?.faculty || currentUser?.department) : null;

    const menuItems = [
        { text: "Thống kê & Phản hồi", to: "/admin/dashboard", icon: <FeedbackIcon /> },
        { text: "Quản lý Tài liệu", to: "/admin/documents", icon: <ArticleIcon /> },
        { text: "Quản lý Người dùng", to: "/admin/users", icon: <GroupIcon /> },
        ...(isAdmin ? [{ text: "Quản lý Model & API", to: "/admin/models", icon: <DnsIcon /> }] : [])
    ];

    const drawerContent = (
        <Box sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
            <Toolbar
                sx={{
                    flexDirection: "column",
                    gap: 1,
                    py: 1.2,
                    minHeight: 70,
                }}
            >
                <Stack
                    direction="row"
                    alignItems="center"
                    spacing={1}
                    sx={{
                        opacity: isMobile ? 1 : open ? 1 : 0,
                        transition: "opacity .25s ease",
                        justifyContent: "center",
                        width: "100%",
                    }}
                >
                    <Box
                        component="img"
                        src={tdtuLogo}
                        alt="TDTU Logo"
                        sx={{
                            height: 40,
                            borderRadius: 1.5,
                            boxShadow: "0 3px 10px rgba(0,0,0,0.20)",
                        }}
                    />

                    <Typography
                        variant="h6"
                        sx={{
                            fontWeight: 700,
                            whiteSpace: "nowrap",
                        }}
                    >
                        {sidebarTitle}
                    </Typography>
                </Stack>

                {departmentName && open && (
                    <Typography variant="caption" sx={{ opacity: 0.85, textAlign: "center" }}>
                        {departmentName}
                    </Typography>
                )}
            </Toolbar>

            <Divider sx={{ opacity: 0.4 }} />

            <List sx={{ mt: 1 }}>
                {menuItems.map(item => (
                    <ListItem key={item.text} disablePadding>
                        <ListItemButton
                            component={RouterNavLink}
                            to={item.to}
                            sx={({ isActive }) => ({
                                mx: 1,
                                mb: 0.5,
                                color: "white",
                                borderRadius: 3,
                                minHeight: 48,
                                transition: "all .25s ease",
                                justifyContent: open ? "initial" : "center",
                                '&:hover': {
                                    background: "rgba(255,255,255,0.10)",
                                    transform: "translateX(4px)",
                                },
                                ...(isActive ? activeLinkStyle : {})
                            })}
                        >
                            <ListItemIcon sx={{ color: "inherit", minWidth: 36 }}>
                                {item.icon}
                            </ListItemIcon>

                            <ListItemText
                                primary={item.text}
                                sx={{
                                    opacity: open ? 1 : 0,
                                    transition: "opacity .25s ease"
                                }}
                            />
                        </ListItemButton>
                    </ListItem>
                ))}
            </List>
        </Box>
    );

    return (
        <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "background.default" }}>
            <CssBaseline />

            {/* APP BAR */}
            <AppBar
                position="fixed"
                elevation={1}
                sx={{
                    bgcolor: "white",
                    color: "primary.main",
                    borderBottom: "1px solid #e0e0e0",
                    zIndex: theme => theme.zIndex.drawer + 1,
                    ...(isDesktop && {
                        width: `calc(100% - ${currentDrawerWidth}px)`,
                        ml: `${currentDrawerWidth}px`,
                        transition: "all .3s ease",
                    })
                }}
            >
                <Toolbar sx={{ minHeight: 65 }}>
                    <IconButton color="inherit" onClick={handleDrawerToggle} sx={{ mr: 2 }}>
                        {isDesktop && open ? <ChevronLeftIcon /> : <MenuIcon />}
                    </IconButton>

                    <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 700 }}>
                        Trang Quản Trị Hệ Thống Hỏi-Đáp TDTU
                    </Typography>

                    <Button
                        onClick={handleLogout}
                        startIcon={<ExitToAppIcon />}
                        sx={{
                            fontWeight: 600,
                            px: 2.5,
                            py: 1,
                            color: "white",
                            background: "linear-gradient(90deg, #1976d2, #42a5f5)",
                            '&:hover': { background: "linear-gradient(90deg, #1565c0, #1976d2)" }
                        }}
                    >
                        Đăng xuất
                    </Button>
                </Toolbar>
            </AppBar>

            {/* DRAWER MOBILE */}
            {isMobile && (
                <Drawer
                    variant="temporary"
                    open={mobileOpen}
                    onClose={() => setMobileOpen(false)}
                    ModalProps={{ keepMounted: true }}
                    sx={{
                        '& .MuiDrawer-paper': {
                            width: drawerWidth,
                            background: 'linear-gradient(180deg,#1976d2,#42a5f5)',
                            color: 'white',
                            backdropFilter: "blur(6px)"
                        }
                    }}
                >
                    {drawerContent}
                </Drawer>
            )}

            {/* DRAWER DESKTOP */}
            {isDesktop && (
                <Drawer
                    variant="permanent"
                    sx={{
                        width: currentDrawerWidth,
                        flexShrink: 0,
                        '& .MuiDrawer-paper': {
                            width: currentDrawerWidth,
                            background: 'linear-gradient(180deg,#1976d2,#42a5f5)',
                            color: 'white',
                            transition: "width .3s ease",
                            backdropFilter: "blur(6px)"
                        }
                    }}
                    open={open}
                >
                    {drawerContent}
                </Drawer>
            )}

            <Box component="main" sx={{ flexGrow: 1, p: { xs: 2, md: 4 } }}>
                <Toolbar />
                <Outlet />
            </Box>
        </Box>
    );
};

export default AdminLayout;
