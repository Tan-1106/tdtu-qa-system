import React from 'react';
import { Box, Paper } from '@mui/material';

const AuthLayout = ({ children }) => {
    return (
        <Box 
            sx={{
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                minHeight: '100vh', 
                px: 2,
                background: 'linear-gradient(180deg, #f0f7ff 0%, #e8f0fe 100%)', 
            }}
        >
            <Paper 
                elevation={12} 
                sx={{ 
                    p: { xs: 4, md: 6 }, 
                    maxWidth: 450, 
                    width: '100%', 
                    borderRadius: 4,
                    textAlign: 'center',
                    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
                }}
            >
                {children}
            </Paper>
        </Box>
    );
};

export default AuthLayout;