import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
    Box, Typography, CircularProgress, Alert, Accordion, 
    AccordionSummary, AccordionDetails, useTheme, Stack, 
    TablePagination, IconButton, TextField, InputAdornment, Paper
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import HelpOutlineOutlinedIcon from '@mui/icons-material/HelpOutlineOutlined';
import SearchIcon from '@mui/icons-material/Search';
import { useOutletContext } from 'react-router-dom';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
import SchoolIcon from '@mui/icons-material/School';

import { getPopularQuestionsForUser } from '../../api/statisticalApi'; 
import useUserAuth from '../../hooks/useUserAuth';

const PopularQuestionsPage = () => {
    const theme = useTheme();
    const { user: currentUser } = useUserAuth(); 
    const context = useOutletContext();
    const { isSidebarOpen = true, toggleSidebar = () => {} } = context || {};
    
    const [questions, setQuestions] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState(''); 
    
    const [page, setPage] = useState(0); 
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [totalQuestions, setTotalQuestions] = useState(0);

    const fetchQuestions = useCallback(async (currentPage, limit) => {
        if (!currentUser) return;
        setIsLoading(true);
        setError(null);
        try {
            const data = await getPopularQuestionsForUser(currentPage + 1, limit);
            setQuestions(data.popular_questions || []);
            setTotalQuestions(data.total || 0);
        } catch (err) {
            setError("Không thể tải danh sách câu hỏi. Vui lòng thử lại.");
        } finally {
            setIsLoading(false);
        }
    }, [currentUser]);

    useEffect(() => {
        if (currentUser) fetchQuestions(page, rowsPerPage);
    }, [fetchQuestions, page, rowsPerPage]);

    // Lọc nhanh câu hỏi dựa trên searchTerm
    const filteredQuestions = useMemo(() => {
        return questions.filter(q => 
            q.question.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }, [questions, searchTerm]);

    return (
        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', height: '100%', bgcolor: '#f8f9fa' }}>
            {/* Desktop Header */}
            <Box sx={{ 
                p: 2, bgcolor: 'white', display: { xs: 'none', md: 'flex' }, 
                alignItems: 'center', borderBottom: '1px solid #e3e3e3',
                position: 'sticky', top: 0, zIndex: 10 
            }}>
                <IconButton onClick={toggleSidebar} sx={{ mr: 2 }}>
                    {isSidebarOpen ? <CloseIcon /> : <MenuIcon />}
                </IconButton>
                <Typography variant="h6" fontWeight={700} color="primary">
                    Các câu hỏi phổ biến
                </Typography>
            </Box>
            
            <Box sx={{ p: { xs: 2, md: 4 }, overflowY: 'auto', flexGrow: 1, maxWidth: '1000px', mx: 'auto', width: '100%', scrollbarGutter: 'stable' }}>
                {/* Hero Section */}
                <Box sx={{ mb: 4, textAlign: 'center' }}>
                    <Typography variant="h4" fontWeight={800} gutterBottom sx={{ color: '#1a237e' }}>
                        Bạn cần hỗ trợ điều gì?
                    </Typography>
                    <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                        Tổng hợp những thắc mắc thường gặp từ sinh viên TDTU
                    </Typography>
                    
                    {/* Search Bar */}
                    <TextField
                        fullWidth
                        placeholder="Tìm nhanh nội dung câu hỏi..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        variant="outlined"
                        InputProps={{
                            startAdornment: (
                                <InputAdornment position="start">
                                    <SearchIcon color="primary" />
                                </InputAdornment>
                            ),
                            sx: { borderRadius: '12px', bgcolor: 'white', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }
                        }}
                    />
                </Box>
                
                {error && <Alert severity="error" sx={{ mb: 3, borderRadius: '10px' }}>{error}</Alert>}
                
                {isLoading ? (
                    <Stack alignItems="center" sx={{ py: 10 }}>
                        <CircularProgress size={50} thickness={4} />
                        <Typography sx={{ mt: 2, fontWeight: 500, opacity: 0.7 }}>Đang tra cứu dữ liệu...</Typography>
                    </Stack>
                ) : filteredQuestions.length === 0 ? (
                    <Paper sx={{ p: 5, textAlign: 'center', borderRadius: '15px' }}>
                        <HelpOutlineOutlinedIcon sx={{ fontSize: 60, color: '#ccc', mb: 2 }} />
                        <Typography variant="h6" color="text.secondary">
                            Không tìm thấy câu hỏi nào phù hợp.
                        </Typography>
                    </Paper>
                ) : (
                    <>
                        {filteredQuestions.map((item, index) => (
                            <Accordion 
                                key={item.id || index}
                                disableGutters
                                elevation={0}
                                sx={{ 
                                    mb: 2, 
                                    borderRadius: '12px !important',
                                    border: '1px solid #e0e0e0',
                                    '&:before': { display: 'none' },
                                    overflow: 'hidden',
                                    transition: 'all 0.3s ease',
                                    '&:hover': { boxShadow: '0 6px 15px rgba(0,0,0,0.08)', borderColor: theme.palette.primary.main }
                                }}
                            >
                                <AccordionSummary
                                    expandIcon={<ExpandMoreIcon color="primary" />}
                                    sx={{ 
                                        px: 3, py: 1,
                                        '&.Mui-expanded': { bgcolor: 'rgba(25, 118, 210, 0.04)' }
                                    }}
                                >
                                    <Stack direction="row" spacing={2} alignItems="center">
                                        <Box sx={{ 
                                            width: 32, height: 32, minWidth: 32, flexShrink: 0, bgcolor: 'primary.light', 
                                            borderRadius: '50%', display: 'flex', alignItems: 'center', 
                                            justifyContent: 'center', color: 'white', fontWeight: 700, fontSize: '0.8rem'
                                        }}>
                                            {index + 1 + page * rowsPerPage}
                                        </Box>
                                        <Typography fontWeight={600} sx={{ fontSize: '1.05rem' }}>
                                            {item.question}
                                        </Typography>
                                    </Stack>
                                </AccordionSummary>
                                <AccordionDetails sx={{ px: 3, pb: 3, pt: 2, bgcolor: '#fafafa' }}>
                                    <Box sx={{ pl: 6 }}>
                                        <Typography 
                                            variant="body1" 
                                            sx={{ 
                                                whiteSpace: 'pre-wrap', 
                                                wordBreak: 'break-word',
                                                color: 'text.primary',
                                                lineHeight: 1.6 
                                            }}
                                        >
                                            {item.answer || 'Chưa có câu trả lời.'}
                                        </Typography>
                                        
                                        <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 3, opacity: 0.8 }}>
                                            <SchoolIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                                            <Typography variant="caption" fontWeight={600} color="text.secondary">
                                                Phạm vi áp dụng: {item.summary?.faculty_scope || 'Toàn trường'}
                                            </Typography>
                                        </Stack>
                                    </Box>
                                </AccordionDetails>
                            </Accordion>
                        ))}

                        <TablePagination
                            component="div"
                            count={totalQuestions}
                            page={page}
                            onPageChange={(e, p) => setPage(p)}
                            rowsPerPage={rowsPerPage}
                            onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value, 10)); setPage(0); }}
                            rowsPerPageOptions={[10, 20]}
                            labelRowsPerPage="Hiển thị:"
                            sx={{ mt: 2 }}
                        />
                    </>
                )}
            </Box>
        </Box>
    );
};

export default PopularQuestionsPage;