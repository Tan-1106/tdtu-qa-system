import React, { useState, useEffect } from 'react';
import {
    Box, Button, Typography, Table, TableBody, TableCell, TableContainer,
    TableHead, TableRow, Paper, IconButton, Chip, TablePagination, CircularProgress, 
    Alert, Grid, FormControl, Select, MenuItem, Stack, Dialog, DialogTitle,
    DialogContent, DialogActions, TextField, Tooltip
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import SchoolIcon from '@mui/icons-material/School';
import AddCircleIcon from '@mui/icons-material/AddCircle';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';

import {
    getPopularQuestions, generatePopularQuestions, 
    togglePopularQuestionDisplay, assignFacultyScope, updatePopularQuestion
} from '../../api/statisticalApi';
import { getFaculties } from '../../api/adminApi'; 
import useUserAuth from '../../hooks/useUserAuth';

const AssignFacultyDialog = ({ open, onClose, question, onSave, faculties }) => {
    const [selectedFaculty, setSelectedFaculty] = useState(question?.summary?.faculty_scope || '');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        setSelectedFaculty(question?.summary?.faculty_scope || '');
        setError(null);
    }, [question, open]);

    const handleSave = async () => {
        if (!question) return;
        setLoading(true);
        setError(null);
        try {
            await assignFacultyScope(question.id, selectedFaculty);
            onSave();
        } catch (err) {
            console.error(err);
            const errorMessage = err.response?.data?.details || 
                                err.response?.data?.message || 
                                'Lỗi khi chỉ định khoa.';
            
            setError(typeof errorMessage === 'object' ? JSON.stringify(errorMessage) : errorMessage);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
            <DialogTitle>Chỉ định Phạm vi Khoa</DialogTitle>
            <DialogContent dividers>
                {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
                <Typography variant="body1" sx={{ mb: 2 }}>
                    Câu hỏi: {question?.question}
                </Typography>
                <FormControl fullWidth margin="dense">
                    <Select
                        value={selectedFaculty}
                        onChange={(e) => setSelectedFaculty(e.target.value)}
                        displayEmpty
                        disabled={loading}
                    >
                        <MenuItem value="">
                            <em>Toàn trường</em>
                        </MenuItem>
                        {faculties.map((faculty) => (
                            <MenuItem key={faculty} value={faculty}>{faculty}</MenuItem>
                        ))}
                    </Select>
                </FormControl>
            </DialogContent>
            <DialogActions sx={{ px: 3, pb: 2 }}>
                <Button 
                    onClick={onClose} 
                    disabled={loading}
                    variant="outlined" 
                    color="inherit"
                    sx={{ borderRadius: 2 }}
                >
                    Hủy
                </Button>
                <Button 
                    onClick={handleSave} 
                    color="info" 
                    variant="contained" 
                    disabled={loading} 
                    startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SchoolIcon />}
                    sx={{ 
                        borderRadius: 2,
                        boxShadow: '0 4px 12px 0 rgba(2, 136, 209, 0.3)',
                        px: 4
                    }}
                >
                    Xác nhận
                </Button>
            </DialogActions>
        </Dialog>
    );
};

const EditQuestionDialog = ({ open, onClose, question, onSave }) => {
    const [editedQuestion, setEditedQuestion] = useState(question?.question || '');
    const [editedAnswer, setEditedAnswer] = useState(question?.answer || '');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        setEditedQuestion(question?.question || '');
        setEditedAnswer(question?.answer || '');
        setError(null);
    }, [question, open]);
    
    const isSaveDisabled = loading || (
        editedQuestion.trim() === (question?.question || '').trim() && 
        editedAnswer.trim() === (question?.answer || '').trim()
    );

    const handleSave = async () => {
        if (!question) return;
        setLoading(true);
        setError(null);
        
        const updateData = {};
        if (editedQuestion.trim() !== (question.question || '').trim()) {
            updateData.question = editedQuestion.trim();
        }
        if (editedAnswer.trim() !== (question.answer || '').trim()) {
            updateData.answer = editedAnswer.trim();
        }
        
        if (Object.keys(updateData).length === 0) {
            onClose(); 
            return;
        }

        try {
            await updatePopularQuestion(question.id, updateData);
            onSave();
        } catch (err) {
            const errorMessage = err.response?.data?.details || err.message || 'Lỗi khi cập nhật câu hỏi.';
            setError(errorMessage);
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
            <DialogTitle sx={{ bgcolor: 'primary.main', color: 'white', mb: 2 }}>
                <Stack direction="row" alignItems="center" spacing={1}>
                    <Typography variant="h6">Chỉnh sửa câu hỏi và câu trả lời</Typography>
                </Stack>
            </DialogTitle>
            <DialogContent dividers>
                {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
                
                <TextField
                    label="Câu hỏi"
                    fullWidth
                    margin="dense"
                    variant="outlined"
                    value={editedQuestion}
                    onChange={(e) => setEditedQuestion(e.target.value)}
                    multiline
                    rows={2}
                    disabled={loading}
                    sx={{ mb: 2 }}
                />
                <TextField
                    label="Câu trả lời"
                    fullWidth
                    margin="dense"
                    variant="outlined"
                    value={editedAnswer}
                    onChange={(e) => setEditedAnswer(e.target.value)}
                    multiline
                    minRows={15}
                    maxRows={25}
                    disabled={loading}
                    sx={{ 
                        mb: 2,
                        '& .MuiInputBase-root': {
                            lineHeight: 1.5, 
                            fontSize: '0.95rem' 
                        }
                    }}
                />
            </DialogContent>
            <DialogActions sx={{ px: 3, pb: 2 }}>
                <Button onClick={onClose} color="inherit">Hủy bỏ</Button>
                <Button 
                    onClick={handleSave} 
                    color="primary" 
                    variant="contained" 
                    disabled={isSaveDisabled}
                    sx={{ 
                        borderRadius: 2,
                        px: 4,
                        '&.Mui-disabled': { bgcolor: 'action.disabledBackground' }
                    }}
                >
                    Lưu thay đổi
                </Button>
            </DialogActions>
        </Dialog>
    );
};


const GeneratePopularQuestionsDialog = ({ open, onClose, onGenerate }) => {
    const [periodType, setPeriodType] = useState('Monthly'); 
    const [n, setN] = useState(10); 
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (open) {
            setPeriodType('Monthly');
            setN(10);
            setError(null);
        }
    }, [open]);

    const handleGenerate = async () => {
        if (n <= 0) {
            setError('N phải là một số nguyên dương.');
            return;
        }

        setLoading(true);
        setError(null);
        
        try {
            await onGenerate(periodType, n);
            onClose(); 
        } catch (err) {
            const errorMessage = err.response?.data?.details || err.message || 'Lỗi khi tạo câu hỏi phổ biến.';
            setError(errorMessage);
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const isGenerateDisabled = loading || n <= 0;

    return (
        <Dialog open={open} onClose={onClose} fullWidth maxWidth="xs">
            <DialogTitle>Thống kê các câu hỏi phổ biến</DialogTitle>
            <DialogContent dividers>
                {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Chọn chu kỳ thống kê và số lượng câu hỏi phổ biến hàng đầu (N) để tạo mới.
                </Typography>

                <FormControl fullWidth margin="dense" sx={{ mb: 2 }}>
                    <Typography variant="caption" display="block" sx={{ color: 'text.secondary', mb: 0.5 }}>
                        Chu kỳ thống kê
                    </Typography>
                    <Select
                        value={periodType}
                        onChange={(e) => setPeriodType(e.target.value)}
                        disabled={loading}
                        size="small"
                    >
                        <MenuItem value="Weekly">Theo Tuần</MenuItem>
                        <MenuItem value="Monthly">Theo Tháng</MenuItem>
                        <MenuItem value="Yearly">Theo Năm</MenuItem>
                    </Select>
                </FormControl>

                <TextField
                    label="Số lượng câu hỏi hàng đầu (N)"
                    fullWidth
                    margin="dense"
                    variant="outlined"
                    type="number"
                    value={n}
                    onChange={(e) => setN(parseInt(e.target.value) || 0)}
                    disabled={loading}
                    size="small"
                    inputProps={{ min: 1, max: 100 }}
                />
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} disabled={loading}>Hủy</Button>
                <Button 
                    onClick={handleGenerate} 
                    color="primary" 
                    disabled={isGenerateDisabled} 
                    startIcon={loading && <CircularProgress size={20} />}
                >
                    {loading ? 'Đang tạo...' : 'Tạo mới'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

const PopularQuestionManagementPage = () => {
    const { user: currentUser } = useUserAuth();
    const isAdmin = currentUser?.role === 'Admin';
    const isFacultyManager = currentUser?.is_faculty_manager;
    const canManage = isAdmin || isFacultyManager; 

    const [questions, setQuestions] = useState([]);
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [totalQuestions, setTotalQuestions] = useState(0);
    
    const [isDisplayFilter, setIsDisplayFilter] = useState('true'); 
    const [facultyFilter, setFacultyFilter] = useState('');
    const [availableFaculties, setAvailableFaculties] = useState([]);

    const [isInitialLoading, setIsInitialLoading] = useState(true);
    const [isRefetching, setIsRefetching] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);

    const [isAssignFacultyOpen, setIsAssignFacultyOpen] = useState(false);
    const [isEditQuestionOpen, setIsEditQuestionOpen] = useState(false);
    const [selectedQuestion, setSelectedQuestion] = useState(null);
    const [isGenerateDialogOpen, setIsGenerateDialogOpen] = useState(false);
    

    const fetchFilterOptions = async () => {
        try {
            const faculties = await getFaculties();
            setAvailableFaculties(faculties);
        } catch (err) {
            console.error("Error fetching filter options:", err);
        }
    };
    
    const fetchQuestions = async (currentPage, limit, isDisplay, faculty, isInitialLoad) => {
        if (isInitialLoad) {
            setIsInitialLoading(true);
        } else {
            setIsRefetching(true);
        }
        setError(null);
        setSuccessMessage(null);
        
        let displayFilter = undefined;
        if (isDisplay === 'true') {
            displayFilter = true;
        } else if (isDisplay === 'false') {
            displayFilter = false;
        } 

        const params = {
            page: currentPage + 1,
            limit: limit,
            is_display: displayFilter, 
            faculty: isAdmin ? faculty : undefined, 
        };
        
        try {
            const data = await getPopularQuestions(params);
            
            setQuestions(data.popular_questions.map(q => ({
                ...q,
                id: q._id || q.id || 'temp-' + Math.random(),                
                faculty_scope: q.summary?.faculty_scope,
                created_at: q.created_at,
                updated_at: q.updated_at
            })));
            setTotalQuestions(data.total);
        } catch (err) {
            console.error("Error fetching popular questions:", err);
            let errorMessage = (err.response?.data?.details || err.message) || 'Lỗi không xác định khi tải danh sách.';
            setError(errorMessage);
        } finally {
            if (isInitialLoad) {
                setIsInitialLoading(false);
            } else {
                setIsRefetching(false);
            }
        }
    };

    const loadQuestionsWithFilters = (resetPage = true, isInitialLoad = false) => {
        const targetPage = resetPage ? 0 : page;
        fetchQuestions(
            targetPage, 
            rowsPerPage, 
            isDisplayFilter, 
            facultyFilter, 
            isInitialLoad
        );
        
        if (resetPage && page !== 0) {
            setPage(0);
        }
    };

    useEffect(() => {
        if (currentUser) {
            if (isAdmin) {
                fetchFilterOptions();
            }

            loadQuestionsWithFilters(true, true);
        }
    }, [currentUser]);

    useEffect(() => {
        if (!isInitialLoading) {
            loadQuestionsWithFilters(true);
        }
    }, [isDisplayFilter, facultyFilter, rowsPerPage]);

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
        fetchQuestions(newPage, rowsPerPage, isDisplayFilter, facultyFilter, false);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0); 
    };
    
    const handleGenerate = async (periodType, n) => { 
        if (!isAdmin) {
            setError('Bạn không có quyền thực hiện chức năng này.');
            return;
        }
        setIsGenerating(true);
        setError(null);
        setSuccessMessage(null);

        try {
            await generatePopularQuestions(periodType, n);
            setSuccessMessage(`Đã tạo thành công ${n} câu hỏi phổ biến hàng đầu trong ${periodType.toLowerCase()}.`);
            
            if (isDisplayFilter !== 'false') {
                 setIsDisplayFilter('false'); 
            } else {
                 loadQuestionsWithFilters(true);
            }
        } catch (err) {
            const errorMessage = err.response?.data?.details || err.message || 'Lỗi khi tạo câu hỏi phổ biến.';
            setError(errorMessage);
            console.error(err);
            throw err; 
        } finally {
            setIsGenerating(false);
        }
    };
    
    const handleToggleDisplay = async (questionId) => {
        if (!canManage) {
            setError('Bạn không có quyền thay đổi trạng thái hiển thị.');
            return;
        }
        setError(null);
        setSuccessMessage(null);
        
        try {
            const updated = await togglePopularQuestionDisplay(questionId);
            setSuccessMessage(`Đã ${updated.is_display ? 'hiển thị' : 'ẩn'} câu hỏi thành công.`);
            loadQuestionsWithFilters(false); 
        } catch (err) {
            const errorMessage = err.response?.data?.details || err.message || 'Lỗi khi chuyển đổi trạng thái hiển thị.';
            setError(errorMessage);
            console.error(err);
        }
    };
    
    const handleOpenAssignFaculty = (question) => {
        if (!isAdmin) {
            setError('Bạn không có quyền chỉ định phạm vi khoa.');
            return;
        }
        setSelectedQuestion(question);
        setIsAssignFacultyOpen(true);
    };

    const handleAssignFacultySave = () => {
        setIsAssignFacultyOpen(false);
        setSuccessMessage('Đã chỉ định phạm vi khoa thành công.');
        loadQuestionsWithFilters(false);
    };

    const handleOpenEditQuestion = (question) => {
        if (!canManage) {
            setError('You do not have permission to edit this question.');
            return;
        }
        if (isFacultyManager && question.summary.faculty_scope !== currentUser.department) {
             setError('You are only allowed to edit questions within the scope of your department.');
             return;
        }
        setSelectedQuestion(question);
        setIsEditQuestionOpen(true);
    };

    const handleEditQuestionSave = () => {
        setIsEditQuestionOpen(false);
        setSuccessMessage('Đã cập nhật câu hỏi/trả lời thành công.');
        loadQuestionsWithFilters(false);
    };


    if (isInitialLoading || !currentUser) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
                <CircularProgress />
                <Typography sx={{ ml: 2 }}>Đang tải dữ liệu câu hỏi phổ biến...</Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ p: { xs: 1, md: 3 } }}>
            {error && <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>{error}</Alert>}
            {successMessage && <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccessMessage(null)}>{successMessage}</Alert>}
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main' }}>
                    Quản lý các câu hỏi phổ biến
                </Typography>
                
                {isAdmin && (
                    <Button 
                        variant="contained" 
                        startIcon={<AutoFixHighIcon />}
                        onClick={() => setIsGenerateDialogOpen(true)}
                        disabled={isGenerating}
                    >
                        {isGenerating ? 'Đang tạo...' : 'Tạo mới (Thống kê)'}
                    </Button>
                )}
            </Box>
            
            <Paper elevation={1} sx={{ p: 2, mb: 3, borderRadius: 3, borderLeft: '5px solid #1976d2' }}>
                <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 700, color: 'primary.main' }}>Bộ lọc</Typography>
                <Grid container spacing={2} alignItems="flex-end">
                    
                    <Grid item xs={12} sm={6} md={isAdmin ? 4 : 6}> 
                        <Typography variant="caption" display="block" sx={{ color: 'text.secondary', mb: 0.5 }}>
                            Trạng thái hiển thị
                        </Typography>
                        <FormControl fullWidth size="small" variant="outlined">
                            <Select
                                value={isDisplayFilter}
                                onChange={(e) => setIsDisplayFilter(e.target.value)} 
                                disabled={!canManage} 
                            >
                                <MenuItem key="true" value="true">Đang hiển thị</MenuItem>
                                
                                {canManage && (
                                    <MenuItem key="false" value="false">Đã ẩn</MenuItem>
                                )}
                            </Select>
                        </FormControl>
                    </Grid>
                    
                    {isAdmin && (
                        <Grid item xs={12} sm={6} md={4}>
                            <Typography variant="caption" display="block" sx={{ color: 'text.secondary', mb: 0.5 }}>
                                Phạm vi Khoa
                            </Typography>
                            <FormControl fullWidth size="small" variant="outlined">
                                <Select
                                    value={facultyFilter}
                                    displayEmpty
                                    onChange={(e) => setFacultyFilter(e.target.value)}
                                >
                                    <MenuItem value="">
                                        <em>Tất cả</em>
                                    </MenuItem>
                                    {availableFaculties.map((faculty) => (
                                        <MenuItem key={faculty} value={faculty}>{faculty}</MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        </Grid>
                    )}
                </Grid>
            </Paper>

            <TableContainer 
                component={Paper} 
                sx={{ 
                    borderRadius: 4, 
                    boxShadow: '0 4px 16px 0 rgba(25,118,210,0.06)',
                    position: 'relative', 
                }}
            >
                {isRefetching && (
                    <Box 
                        sx={{
                            position: 'absolute',
                            top: 0, left: 0, right: 0, bottom: 0,
                            bgcolor: 'rgba(255, 255, 255, 0.7)', 
                            zIndex: 1000, 
                            display: 'flex',
                            justifyContent: 'center',
                            alignItems: 'center',
                            borderRadius: 4,
                        }}
                    >
                        <CircularProgress size={40} />
                    </Box>
                )}
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell><b>Câu hỏi</b></TableCell>
                            <TableCell align="center"><b>Lượt hỏi</b></TableCell>
                            <TableCell><b>Phạm vi Khoa</b></TableCell>
                            <TableCell align="center"><b>Hiển thị</b></TableCell>
                            <TableCell align="right"><b>Hành động</b></TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {questions.map((q) => (
                            <TableRow key={q.id} hover>
                                <TableCell sx={{ maxWidth: 300, wordBreak: 'break-word' }}>
                                    <Tooltip title={q.question} arrow>
                                        <Typography variant="body2" noWrap>{q.question}</Typography>
                                    </Tooltip>
                                </TableCell>
                                <TableCell align="center">
                                    <Chip 
                                        label={q.summary?.count || 0} 
                                        size="small"
                                        sx={{ fontWeight: 600, borderRadius: 1.5 }}
                                    />
                                </TableCell>
                                <TableCell>
                                    <Stack direction="row" spacing={0.5} alignItems="center">
                                        <SchoolIcon fontSize="small" color={q.faculty_scope ? 'primary' : 'inherit'} />
                                        <Typography variant="body2">
                                            {q.faculty_scope || 'Toàn trường'}
                                        </Typography>
                                    </Stack>
                                </TableCell>
                                <TableCell align="center">
                                    <Chip
                                        label={q.is_display ? 'Đang hiển thị' : 'Đã ẩn'}
                                        color={q.is_display ? 'success' : 'error'}
                                        variant={q.is_display ? 'outlined' : 'filled'}
                                        sx={{ fontWeight: 500, borderRadius: 2 }} 
                                    />
                                </TableCell>
                                <TableCell align="right">
                                    <Tooltip title="Chỉnh sửa Câu hỏi/Trả lời">
                                        <IconButton onClick={() => handleOpenEditQuestion(q)} color="primary" disabled={!canManage}>
                                            <EditIcon />
                                        </IconButton>
                                    </Tooltip>
                                    {isAdmin && (
                                        <Tooltip title="Chỉ định Khoa">
                                            <IconButton onClick={() => handleOpenAssignFaculty(q)} sx={{ color: 'info.main' }}>
                                                <AddCircleIcon />
                                            </IconButton>
                                        </Tooltip>
                                    )}
                                    <Tooltip title={q.is_display ? 'Ẩn câu hỏi' : 'Hiển thị câu hỏi'}>
                                        <IconButton 
                                            onClick={() => handleToggleDisplay(q.id)} 
                                            sx={{ color: q.is_display ? 'error.main' : 'success.main' }}
                                            disabled={!canManage}
                                        >
                                            {q.is_display ? <VisibilityOffIcon /> : <VisibilityIcon />}
                                        </IconButton>
                                    </Tooltip>
                                </TableCell>
                            </TableRow>
                        ))}
                        {questions.length === 0 && !isInitialLoading && ( 
                            <TableRow>
                                <TableCell colSpan={5} align="center" sx={{ color: 'text.secondary', py: 4 }}>
                                    Không có câu hỏi phổ biến nào được tìm thấy.
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
            
            <TablePagination
                component="div"
                count={totalQuestions}
                page={page}
                onPageChange={handleChangePage}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={handleChangeRowsPerPage}
                rowsPerPageOptions={[10, 25, 50]}
                labelRowsPerPage="Số hàng mỗi trang:"
                labelDisplayedRows={({ from, to, count }) =>
                    `${from}-${to} trên ${count}`
                }
            />
            {isAdmin && (
                <GeneratePopularQuestionsDialog
                    open={isGenerateDialogOpen}
                    onClose={() => setIsGenerateDialogOpen(false)}
                    onGenerate={handleGenerate}
                />
            )}
            {selectedQuestion && (
                <>
                    <AssignFacultyDialog
                        open={isAssignFacultyOpen}
                        onClose={() => setIsAssignFacultyOpen(false)}
                        question={selectedQuestion}
                        onSave={handleAssignFacultySave}
                        faculties={availableFaculties}
                    />
                    <EditQuestionDialog
                        open={isEditQuestionOpen}
                        onClose={() => setIsEditQuestionOpen(false)}
                        question={selectedQuestion}
                        onSave={handleEditQuestionSave}
                    />
                </>
            )}
        </Box>
    );
};

export default PopularQuestionManagementPage;