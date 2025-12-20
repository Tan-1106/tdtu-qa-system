import { Box, CircularProgress } from '@mui/material';

const LoadingScreen = ({ message = "Đang kiểm tra quyền truy cập..." }) => (
    <Box sx={{
        position: "fixed", inset: 0, background: "rgba(255, 255, 255, 0.7)",
        backdropFilter: "blur(4px)", display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center", zIndex: 9999,
    }}>
        <CircularProgress size={60} thickness={4} />
        <Box sx={{ mt: 2, fontSize: "1.1rem", fontWeight: 500, color: "#555" }}>
            {message}
        </Box>
    </Box>
);
export default LoadingScreen;