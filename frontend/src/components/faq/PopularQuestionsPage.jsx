// pages/user/PopularQuestionsPage.js
import React, { useState, useEffect, useCallback } from 'react';
import { 
    Box, Typography, CircularProgress, Alert, Accordion, 
    AccordionSummary, AccordionDetails, useTheme, Stack, 
    TablePagination, IconButton 
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import HelpOutlineOutlinedIcon from '@mui/icons-material/HelpOutlineOutlined';
import { useOutletContext } from 'react-router-dom';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';

import { getPopularQuestionsForUser } from '../../api/statisticalApi'; 
import useUserAuth from '../../hooks/useUserAuth';


const PopularQuestionsPage = () => {
    const theme = useTheme();
    const { user: currentUser } = useUserAuth(); 
    
    // Lấy context từ UserLayout (dùng để mở/đóng Sidebar)
    const context = useOutletContext();
    const { isSidebarOpen = true, toggleSidebar = () => {} } = context || {};
    
    const [questions, setQuestions] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    
    const [page, setPage] = useState(0); 
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [totalQuestions, setTotalQuestions] = useState(0);

    const fetchQuestions = useCallback(async (currentPage, limit) => {
        if (!currentUser) return;
        
        setIsLoading(true);
        setError(null);

        try {
            // Sử dụng hàm getPopularQuestionsForUser, backend tự động lọc is_display=true và faculty
            const data = await getPopularQuestionsForUser(currentPage + 1, limit);
            
            // Backend trả về: { popular_questions: [...], total: N, ... }
            setQuestions(data.popular_questions || []);
            setTotalQuestions(data.total || 0);

        } catch (err) {
            console.error("Error fetching popular questions:", err);
            setError("Không thể tải danh sách câu hỏi phổ biến. Vui lòng thử lại.");
            setQuestions([]);
        } finally {
            setIsLoading(false);
        }
    }, [currentUser]);

    useEffect(() => {
        if (currentUser) {
            fetchQuestions(page, rowsPerPage);
        }
    }, [fetchQuestions, page, rowsPerPage]);


    const handlePageChange = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0); 
    };
    
    // --- Render Component ---
    
    return (
        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* Thanh tiêu đề (cho màn hình lớn) */}
            <Box sx={{ 
                p: 2, 
                bgcolor: 'white', 
                display: { xs: 'none', md: 'flex' }, 
                alignItems: 'center', 
                gap: 1.5, 
                borderBottom: '1px solid #e3e3e3',
                position: 'sticky', 
                top: 0,
                zIndex: 10,
                flexShrink: 0 
            }}>
                <IconButton 
                    size="large" 
                    onClick={toggleSidebar} 
                    sx={{ color: 'text.primary' }}
                >
                    {isSidebarOpen ? <CloseIcon /> : <MenuIcon />}
                </IconButton>
                <Typography variant="h6" sx={{ fontWeight: 600, flexGrow: 1, color: 'primary.main' }}>
                    Câu hỏi Phổ biến
                </Typography>
            </Box>
            
            {/* Nội dung chính */}
            <Box sx={{ p: { xs: 1, md: 3 }, overflowY: 'auto', flexGrow: 1 }}>
                
                <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 3 }}>
                    <HelpOutlineOutlinedIcon sx={{ color: theme.palette.primary.main }} />
                    <Typography variant="h5" sx={{ fontWeight: 700, color: 'text.primary' }}>
                        Các Câu Hỏi Thường Gặp
                    </Typography>
                </Stack>
                
                {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
                
                {isLoading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
                        <CircularProgress />
                        <Typography sx={{ ml: 2 }}>Đang tải câu hỏi...</Typography>
                    </Box>
                ) : questions.length === 0 ? (
                    <Alert severity="info">
                        Hiện tại không có câu hỏi phổ biến nào được hiển thị cho phạm vi của bạn.
                    </Alert>
                ) : (
                    <>
                        {/* Danh sách Accordion */}
                        {questions.map((item, index) => (
                            <Accordion 
                                key={item.id || index} // Dùng item.id (tên mới) hoặc item._id (tên cũ)
                                sx={{ mb: 1, boxShadow: '0 2px 8px rgba(0,0,0,0.05)', borderRadius: '8px !important' }}
                            >
                                <AccordionSummary
                                    expandIcon={<ExpandMoreIcon />}
                                    sx={{ 
                                        bgcolor: 'white', 
                                        borderBottom: 1, 
                                        borderColor: 'divider',
                                        '&.Mui-expanded': { minHeight: 48 },
                                        '.MuiAccordionSummary-content': { margin: '12px 0' },
                                    }}
                                >
                                    <Typography fontWeight={600} color="primary.main">
                                        {index + 1 + page * rowsPerPage}. {item.question}
                                    </Typography>
                                </AccordionSummary>
                                <AccordionDetails sx={{ bgcolor: '#f5f5f5', borderTop: '1px solid #eee' }}>
                                    {/* Câu trả lời */}
                                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                                        {item.answer || 'Chưa có câu trả lời.'}
                                    </Typography>
                                    
                                    {/* Thông tin phạm vi (tùy chọn) */}
                                    <Box sx={{ mt: 2, pt: 1, borderTop: '1px dashed #ddd' }}>
                                        <Typography variant="caption" color="text.secondary">
                                            Phạm vi: {item.summary?.faculty_scope || 'Toàn trường'}
                                        </Typography>
                                    </Box>
                                </AccordionDetails>
                            </Accordion>
                        ))}

                        {/* Phân trang */}
                        <TablePagination
                            component="div"
                            count={totalQuestions}
                            page={page}
                            onPageChange={handlePageChange}
                            rowsPerPage={rowsPerPage}
                            onRowsPerPageChange={handleChangeRowsPerPage}
                            rowsPerPageOptions={[10, 25, 50]}
                            labelRowsPerPage="Số hàng mỗi trang:"
                            labelDisplayedRows={({ from, to, count }) =>
                                `${from}-${to} trên ${count}`
                            }
                        />
                    </>
                )}
            </Box>
        </Box>
    );
};

export default PopularQuestionsPage;