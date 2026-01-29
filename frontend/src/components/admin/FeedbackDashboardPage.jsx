import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
    Box, Grid, Paper, Typography, CircularProgress, Alert, 
    TableContainer, Table, TableHead, TableRow, TableCell, 
    TableBody, Chip, TablePagination, Button 
} from '@mui/material';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import ArticleIcon from '@mui/icons-material/Article'; 
import GroupIcon from '@mui/icons-material/Group';
import VisibilityIcon from '@mui/icons-material/Visibility';

import useUserAuth from '../../hooks/useUserAuth';
import { calculateDashboardMetrics, updateManagerAnswer } from '../../api/adminApi'; 
import ManagerAnswerModal from './ManagerAnswerModal'; 
import DashboardMetricCard from './DashboardMetricCard'; 

const FeedbackDashboardPage = () => {
    const { user: currentUser } = useUserAuth();
    const isManager = currentUser?.role === 'Admin' || currentUser?.is_faculty_manager;
    
    const [metrics, setMetrics] = useState({ 
        totalQuestions: 0, 
        totalLikes: 0, 
        totalDislikes: 0,
        unansweredDislikes: 0, 
        satisfactionRate: 0, 
        totalUsers: 0, 
    });
    
    const [feedbackList, setFeedbackList] = useState([]);
    const [totalFeedback, setTotalFeedback] = useState(0);
    
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);

    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [successMsg, setSuccessMsg] = useState(null);
    
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [currentFeedback, setCurrentFeedback] = useState(null);

    const loadData = useCallback(async () => {
        if (!isManager || !currentUser) return;

        setIsLoading(true);
        setError(null);
        setSuccessMsg(null);
        let facultyScope = undefined;
        if (currentUser.role === 'Admin') {
            facultyScope = ''; 
        } else if (currentUser.is_faculty_manager) {
            facultyScope = currentUser.department; 
        }
                
        try {
            const data = await calculateDashboardMetrics(facultyScope);
            setMetrics(data); 
            setFeedbackList(data.dislikeRecords);
            setTotalFeedback(data.dislikeRecords.length);
            setPage(0); 

        } catch (err) {
            console.error("Error loading dashboard data:", err);
            
            let errorMessage = "Không thể tải dữ liệu Dashboard. Đảm bảo bạn có quyền truy cập API /qa/all.";
            if (err.response) {
                if (err.response.status === 422) {
                    errorMessage = "Lỗi 422: Tham số truy vấn không hợp lệ. Vui lòng kiểm tra lại cleanParams trong adminApi.js.";
                } else if (err.response.data?.details) {
                    errorMessage = err.response.data.details;
                }
            } else {
                 errorMessage = err.message;
            }
            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    }, [currentUser, isManager]);

    useEffect(() => {
        if (currentUser) {
            loadData(); 
        }
    }, [currentUser, loadData]); 
    
    const displayedFeedback = useMemo(() => {
        const start = page * rowsPerPage;
        const end = start + rowsPerPage;
        return feedbackList.slice(start, end);
    }, [feedbackList, page, rowsPerPage]);


    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0); 
    };

    const handleOpenProcess = (item) => {
        setCurrentFeedback(item);
        setIsModalOpen(true);
    };
    
    const handleSaveAnswer = async (qaId, answer) => {
        try {
            await updateManagerAnswer(qaId, answer);
            setIsModalOpen(false);
            setSuccessMsg("Đã cập nhật câu trả lời thành công! Dữ liệu đang được tải lại.");
            
            await loadData(); 
            
        } catch (err) {
            console.error("Error updating manager answer:", err);
            setError("Lỗi khi cập nhật câu trả lời: " + (err.response?.data?.details || err.message));
        }
    };
    
    if (!isManager) {
        return <Alert severity="error">Bạn không có quyền truy cập trang này.</Alert>;
    }
    
    if (isLoading) {
        return <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}><CircularProgress /></Box>;
    }

    return (
        <Box sx={{ p: { xs: 1, md: 3 } }}>
            <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main', mb: 3 }}>
                Thống kê và Phản hồi
            </Typography>

            {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
            {successMsg && <Alert severity="success" sx={{ mb: 3 }}>{successMsg}</Alert>}
            
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <DashboardMetricCard 
                    title="Tổng số câu hỏi" 
                    value={metrics.totalQuestions.toLocaleString('vi-VN')} 
                    icon={<ArticleIcon />} 
                    color="#1976d2" 
                />
                <DashboardMetricCard 
                    title="Tỷ lệ hài lòng" 
                    value={`${metrics.satisfactionRate}%`} 
                    icon={<CheckIcon />} 
                    color="#2e7d32" 
                    subtitle={`${metrics.totalLikes} Like / ${metrics.totalDislikes} Dislike`}
                />
                <DashboardMetricCard 
                    title="Cần xử lý (Dislike)" 
                    value={metrics.unansweredDislikes.toLocaleString('vi-VN')} 
                    icon={<CloseIcon />} 
                    color="#d32f2f"
                    tooltip="Số câu hỏi Dislike chưa có câu trả lời của Quản lý."
                />
                {currentUser.role === 'Admin' && (
                    <DashboardMetricCard 
                        title="Tổng số người dùng" 
                        value={metrics.totalUsers.toLocaleString('vi-VN')} 
                        icon={<GroupIcon />} 
                        color="#f57c00" 
                    />
                )}
            </Grid>
            

            <Typography variant="h5" sx={{ fontWeight: 600, color: 'text.primary', mb: 2 }}>
                Phản hồi tiêu cực
            </Typography>

            <TableContainer component={Paper} elevation={1} sx={{ borderRadius: 4, boxShadow: '0 4px 16px 0 rgba(0,0,0,0.06)' }}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell><b>Câu hỏi</b></TableCell>
                            <TableCell><b>Khoa/MSSV</b></TableCell>
                            <TableCell><b>Trạng thái</b></TableCell>
                            <TableCell align="right"><b>Hành động</b></TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {displayedFeedback.map((item) => {
                            const isAnswered = item.managerAnswer && item.managerAnswer.trim() !== '';
                            return (
                                <TableRow key={item.id} hover>
                                    <TableCell>
                                        <Typography variant="body2" fontWeight={600} sx={{ maxWidth: 400 }} noWrap>{item.question}</Typography>
                                        <Typography variant="caption" color="text.secondary">{new Date(new Date(item.createdAt).getTime() + 7 * 60 * 60 * 1000).toLocaleString('vi-VN')}</Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Typography variant="body2">{item.studentFaculty}</Typography>
                                        <Typography variant="caption" color="text.secondary">{item.studentId}</Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Chip 
                                            label={isAnswered ? 'Đã xử lý' : 'Cần xử lý'}
                                            color={isAnswered ? 'success' : 'error'}
                                            size="small"
                                        />
                                    </TableCell>
                                    <TableCell align="right">
                                        <Button 
                                            variant="contained" 
                                            size="small" 
                                            startIcon={<VisibilityIcon />}
                                            onClick={() => handleOpenProcess(item)}
                                            color={isAnswered ? 'info' : 'error'}
                                        >
                                            {isAnswered ? 'Xem / Sửa' : 'Xử lý'}
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            );
                        })}
                        {displayedFeedback.length === 0 && !isLoading && (
                            <TableRow><TableCell colSpan={4} align="center" sx={{ py: 4 }}>
                                {totalFeedback > 0 ? 'Đang tải trang...' : 'Không có phản hồi tiêu cực cần xử lý.'}
                            </TableCell></TableRow>
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
            
            <TablePagination
                component="div"
                count={totalFeedback}
                page={page}
                onPageChange={handleChangePage}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={handleChangeRowsPerPage}
                rowsPerPageOptions={[10, 25, 50, 100]}
                labelRowsPerPage="Số hàng mỗi trang:"
                labelDisplayedRows={({ from, to, count }) => `${from}-${to} trên ${count}`}
            />
            
            <ManagerAnswerModal
                open={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                qaRecord={currentFeedback}
                onSave={handleSaveAnswer}
            />

        </Box>
    );
};

export default FeedbackDashboardPage;