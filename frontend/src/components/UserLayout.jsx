import React from 'react';
import { Outlet, NavLink as RouterNavLink } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Container, Button, Box, Paper, Stack, useTheme } from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';

const navLinks = [
  { label: 'Hỏi-Đáp', to: '/' },
  { label: 'Tài liệu', to: '/documents' },
  { label: 'Câu hỏi phổ biến', to: '/popular-questions' },
  { label: 'Đăng nhập', to: '/login' }
];

const activeLinkStyle = {
  background: 'linear-gradient(90deg, #1976d2 60%, #42a5f5 100%)',
  color: 'white',
  borderRadius: 20,
  boxShadow: '0 2px 8px rgba(25, 118, 210, 0.15)',
  fontWeight: 700,
};

const UserLayout = () => {
  const theme = useTheme();

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* AppBar nâng cấp */}
      <AppBar position="static" elevation={3} sx={{ bgcolor: 'white', color: 'primary.main', borderBottom: `2px solid ${theme.palette.primary.light}` }}>
        <Container maxWidth="lg">
          <Toolbar sx={{ py: 1 }}>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ flexGrow: 1 }}>
              <SchoolIcon fontSize="large" color="primary" />
              <Typography variant="h5" sx={{ fontWeight: 'bold', letterSpacing: 1 }}>
                TDTU Q&A
              </Typography>
            </Stack>
            <Stack direction="row" spacing={1}>
              {navLinks.map(link => (
                <Button
                  key={link.to}
                  component={RouterNavLink}
                  to={link.to}
                  style={({ isActive }) => isActive ? activeLinkStyle : undefined}
                  sx={{
                    px: 2.5,
                    py: 1,
                    borderRadius: 20,
                    fontWeight: 600,
                    color: 'primary.main',
                    transition: 'all 0.2s',
                    '&:hover': {
                      background: 'rgba(25, 118, 210, 0.08)',
                      color: 'primary.dark',
                      boxShadow: '0 2px 8px rgba(25, 118, 210, 0.10)'
                    }
                  }}
                >
                  {link.label}
                </Button>
              ))}
            </Stack>
          </Toolbar>
        </Container>
      </AppBar>

      {/* Main content với shadow và bo góc */}
      <Box component="main" sx={{ flexGrow: 1, py: { xs: 2, md: 4 }, bgcolor: 'background.default' }}>
        <Container maxWidth="md">
          <Paper elevation={4} sx={{ borderRadius: 5, p: { xs: 2, md: 4 }, minHeight: '60vh', boxShadow: '0 8px 32px 0 rgba(25,118,210,0.08)' }}>
            <Outlet />
          </Paper>
        </Container>
      </Box>

      {/* Footer nâng cấp */}
      <Box component="footer" sx={{
        bgcolor: 'primary.main',
        color: 'white',
        py: 3,
        mt: 'auto',
        boxShadow: '0 -2px 16px 0 rgba(25,118,210,0.10)'
      }}>
        <Container maxWidth="lg">
          <Typography variant="body2" align="center" sx={{ opacity: 0.95 }}>
            © {new Date().getFullYear()} - Đồ án chuyên ngành Công nghệ thông tin - TDTU
          </Typography>
        </Container>
      </Box>
    </Box>
  );
};

export default UserLayout;