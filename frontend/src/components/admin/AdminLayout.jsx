import React from 'react';
import { Outlet, NavLink as RouterNavLink, useNavigate } from 'react-router-dom';
import {
  Box, Drawer, List, ListItem, ListItemButton, ListItemIcon,
  ListItemText, AppBar, Toolbar, Typography, CssBaseline, Button, Divider, Stack
} from '@mui/material';
import ArticleIcon from '@mui/icons-material/Article';
import FeedbackIcon from '@mui/icons-material/Feedback';
import GroupIcon from '@mui/icons-material/Group'; 
import ExitToAppIcon from '@mui/icons-material/ExitToApp';
import DnsIcon from '@mui/icons-material/Dns'; // 💡 Icon mới cho Model/API Key
import tdtuLogo from '../../assets/logo_tdtu.png'; 
import useUserAuth from '../../hooks/useUserAuth'; 

const drawerWidth = 240;

const activeLinkStyle = {
  background: 'linear-gradient(90deg, #1976d2 60%, #42a5f5 100%)',
  color: 'white',
  borderRadius: 3,
  boxShadow: '0 2px 8px rgba(25, 118, 210, 0.10)',
  '& .MuiListItemIcon-root': {
    color: 'white',
  },
};

const AdminLayout = () => {
  // 💡 1. LẤY THÔNG TIN NGƯỜI DÙNG
  const { user: currentUser, isLoadingUser, handleLogout } = useUserAuth(); 
  
  // 💡 2. LOGIC TÍNH TOÁN VAI TRÒ
  const isAdmin = currentUser?.role === 'Admin';
  const isFacultyManager = currentUser?.role === 'Faculty Manager';
  
  const sidebarTitle = isAdmin 
    ? "TDTU Admin" 
    : (isFacultyManager ? "TDTU Manager" : "Quản trị"); 
  
  const departmentName = isFacultyManager ? currentUser?.department : null;


  const handleAdminLogout = () => {
    console.log('Admin initiating logout and reload...');
    handleLogout(); 
  };
    
  // Xử lý Loading (Đảm bảo user đã tải xong)
  if (isLoadingUser) {
    // Để tránh lỗi trắng màn hình, AdminRoute/ProtectedRoute đã xử lý loading. 
    return null; 
  }
  
  // Trường hợp user không có quyền (đã được lọc qua AdminRoute)
  if (!currentUser) return null;


  return (
    <Box sx={{ display: 'flex', bgcolor: 'background.default', minHeight: '100vh' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        elevation={2}
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          width: `calc(100% - ${drawerWidth}px)`,
          ml: `${drawerWidth}px`,
          bgcolor: 'white',
          color: 'primary.main',
          borderBottom: '2px solid #e3e3e3',
          boxShadow: '0 2px 8px 0 rgba(25,118,210,0.08)'
        }}
      >
        <Toolbar>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, fontWeight: 'bold', letterSpacing: 1 }}>
            Trang Quản Trị Hệ Thống Hỏi-Đáp TDTU
          </Typography>
          <Button
            color="primary"
            onClick={handleAdminLogout}
            startIcon={<ExitToAppIcon />}
            sx={{
              fontWeight: 600,
              borderRadius: 3,
              px: 2.5,
              py: 1,
              background: 'linear-gradient(90deg, #1976d2 60%, #42a5f5 100%)',
              color: 'white',
              boxShadow: '0 2px 8px 0 rgba(25,118,210,0.10)',
              '&:hover': {
                background: 'linear-gradient(90deg, #1565c0 60%, #1976d2 100%)',
                color: 'white'
              }
            }}
          >
            Đăng xuất
          </Button>
        </Toolbar>
      </AppBar>
      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            background: 'linear-gradient(180deg, #1976d2 60%, #42a5f5 100%)',
            color: 'white',
            borderRight: 'none',
            boxShadow: '4px 0 16px 0 rgba(25,118,210,0.08)',
            height: '100vh',
          },
        }}
        variant="permanent"
        anchor="left"
      >
        <Toolbar sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', py: 3, flexDirection: 'column' }}>
          
          {/* LOGO và TÊN VAI TRÒ */}
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: departmentName ? 0.5 : 1.5 }}>
            <Box
              component="img"
              src={tdtuLogo}
              alt="TDTU Logo"
              sx={{ height: 44, mr: 1.5, borderRadius: 2, boxShadow: '0 2px 8px 0 rgba(25,118,210,0.10)' }}
            />
            <Typography variant="h6" sx={{ fontWeight: 'bold', letterSpacing: 1, whiteSpace: 'nowrap' }}>
              {sidebarTitle} {/* Hiển thị TDTU Admin / TDTU Manager */}
            </Typography>
          </Stack>
          
          {/* TÊN KHOA (CHỈ KHI LÀ MANAGER) */}
          {departmentName && (
              <Typography variant="caption" sx={{ opacity: 0.9, mt: 0, textAlign: 'center', maxWidth: '90%' }} noWrap>
                  {departmentName}
              </Typography>
          )}

        </Toolbar>
        <Divider sx={{ bgcolor: 'rgba(255, 255, 255, 0.15)', mb: 1 }} />
        <List sx={{ mt: 2 }}>
          <ListItem disablePadding>
            <ListItemButton
              component={RouterNavLink}
              to="/admin/dashboard"
              sx={({ isActive }) => ({
                color: 'white', borderRadius: 3, mx: 1, my: 0.5,
                '&:hover': { background: 'rgba(255,255,255,0.10)' },
                ...(isActive ? activeLinkStyle : {}),
              })}
            >
              <ListItemIcon sx={{ color: 'inherit', minWidth: 38 }}><FeedbackIcon /></ListItemIcon>
              <ListItemText primary="Thống kê & Phản hồi" sx={{ fontWeight: 600 }} />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton
              component={RouterNavLink}
              to="/admin/documents"
              sx={({ isActive }) => ({
                color: 'white', borderRadius: 3, mx: 1, my: 0.5,
                '&:hover': { background: 'rgba(255,255,255,0.10)' },
                ...(isActive ? activeLinkStyle : {}),
              })}
            >
              <ListItemIcon sx={{ color: 'inherit', minWidth: 38 }}><ArticleIcon /></ListItemIcon>
              <ListItemText primary="Quản lý Tài liệu" sx={{ fontWeight: 600 }} />
            </ListItemButton>
          </ListItem>

          <ListItem disablePadding>
            <ListItemButton
              component={RouterNavLink}
              to="/admin/users"
              sx={({ isActive }) => ({
                color: 'white', borderRadius: 3, mx: 1, my: 0.5,
                '&:hover': { background: 'rgba(255,255,255,0.10)' },
                ...(isActive ? activeLinkStyle : {}),
              })}
            >
              <ListItemIcon sx={{ color: 'inherit', minWidth: 38 }}><GroupIcon /></ListItemIcon>
              <ListItemText primary="Quản lý Người dùng" sx={{ fontWeight: 600 }} />
            </ListItemButton>
          </ListItem>
          
          {/* 💡 CHỈ HIỂN THỊ CHO ADMIN */}
          {isAdmin && (
              <ListItem disablePadding>
                  <ListItemButton
                      component={RouterNavLink}
                      to="/admin/models"
                      sx={({ isActive }) => ({
                          color: 'white', borderRadius: 3, mx: 1, my: 0.5,
                          '&:hover': { background: 'rgba(255,255,255,0.10)' },
                          ...(isActive ? activeLinkStyle : {}),
                      })}
                  >
                      <ListItemIcon sx={{ color: 'inherit', minWidth: 38 }}><DnsIcon /></ListItemIcon>
                      <ListItemText primary="Quản lý Model & API" sx={{ fontWeight: 600 }} />
                  </ListItemButton>
              </ListItem>
          )}

        </List>
      </Drawer>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: { xs: 2, md: 4 },
          width: `calc(100% - ${drawerWidth}px)`,
          minHeight: '100vh',
          bgcolor: 'background.default'
        }}
      >
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
};

export default AdminLayout;