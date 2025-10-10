import React from 'react';
import { Box, Container } from '@mui/material';

const AuthLayout = ({ children }) => {
  return (
    <Box
      sx={{
        minHeight: 'calc(100vh - 128px)', 
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
      }}
    >
      <Container component="main" maxWidth="xs">
        {children}
      </Container>
    </Box>
  );
};

export default AuthLayout;