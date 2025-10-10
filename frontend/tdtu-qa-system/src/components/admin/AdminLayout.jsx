import React from 'react';
import { Outlet, NavLink as RouterNavLink, useNavigate } from 'react-router-dom';
import {
  Box, Drawer, List, ListItem, ListItemButton, ListItemIcon,
  ListItemText, AppBar, Toolbar, Typography, CssBaseline, Button, Divider
} from '@mui/material';
import ArticleIcon from '@mui/icons-material/Article';
import FeedbackIcon from '@mui/icons-material/Feedback';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';
import tdtuLogo from '../../assets/logo_tdtu.png';

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
  const navigate = useNavigate();

  const handleLogout = () => {
    console.log('Admin logged out');
    navigate('/');
  };

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
            onClick={handleLogout}
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
        <Toolbar sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', py: 3 }}>
          <Box
            component="img"
            src={tdtuLogo}
            alt="TDTU Logo"
            sx={{ height: 44, mr: 1.5, borderRadius: 2, boxShadow: '0 2px 8px 0 rgba(25,118,210,0.10)' }}
          />
          <Typography variant="h6" sx={{ fontWeight: 'bold', letterSpacing: 1 }}>
            TDTU Admin
          </Typography>
        </Toolbar>
        <Divider sx={{ bgcolor: 'rgba(255, 255, 255, 0.15)', mb: 1 }} />
        <List sx={{ mt: 2 }}>
          <ListItem disablePadding>
            <ListItemButton
              component={RouterNavLink}
              to="/admin/dashboard"
              sx={({ isActive }) => ({
                color: 'white',
                borderRadius: 3,
                mx: 1,
                my: 0.5,
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
                color: 'white',
                borderRadius: 3,
                mx: 1,
                my: 0.5,
                '&:hover': { background: 'rgba(255,255,255,0.10)' },
                ...(isActive ? activeLinkStyle : {}),
              })}
            >
              <ListItemIcon sx={{ color: 'inherit', minWidth: 38 }}><ArticleIcon /></ListItemIcon>
              <ListItemText primary="Quản lý Tài liệu" sx={{ fontWeight: 600 }} />
            </ListItemButton>
          </ListItem>
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