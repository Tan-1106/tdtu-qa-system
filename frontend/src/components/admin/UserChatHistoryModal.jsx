import React, { useState, useEffect } from 'react';
import {
    Dialog, DialogTitle, DialogContent, IconButton, Typography, 
    Box, CircularProgress, Pagination, Divider, Paper, Stack
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { getUserChatHistory } from '../../api/adminApi';

const UserChatHistoryModal = ({ open, onClose, user }) => {
    const [data, setData] = useState({ questions: [], total_pages: 1 });
    const [loading, setLoading] = useState(false);
    const [page, setPage] = useState(1);

    useEffect(() => {
        if (open && user?.id) {
            fetchHistory(1);
        }
    }, [open, user]);

    const fetchHistory = async (p) => {
        setLoading(true);
        try {
            const res = await getUserChatHistory(user.id, p, 1); 
            setData(res);
            setPage(p);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', bgcolor: 'primary.main', color: 'white' }}>
                <Typography variant="h6">Lịch sử chat: {user?.fullName}</Typography>
                <IconButton onClick={onClose} sx={{ color: 'white' }}><CloseIcon /></IconButton>
            </DialogTitle>

            <DialogContent sx={{ p: 2, bgcolor: '#f0f2f5', minHeight: '400px' }}>
                {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 5 }}><CircularProgress /></Box>
                ) : data.questions.length > 0 ? (
                    <Stack spacing={2} sx={{ mt: 1 }}>
                        {data.questions.map((item) => (
                            <Box key={item._id}>
                                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
                                    <Paper sx={{ p: 1.5, bgcolor: '#0084ff', color: 'white', maxWidth: '80%', borderRadius: '18px 18px 0 18px' }}>
                                        <Typography variant="body2">{item.question}</Typography>
                                    </Paper>
                                </Box>
                                <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 1 }}>
                                    <Paper sx={{ p: 1.5, bgcolor: 'white', maxWidth: '80%', borderRadius: '18px 18px 18px 0', border: '1px solid #ddd' }}>
                                        <Typography variant="body2" sx={{ fontWeight: 'bold', color: 'primary.main', mb: 0.5 }}>Chatbot:</Typography>
                                        <Typography variant="body2">{item.answer || "Đang trả lời..."}</Typography>
                                        {item.manager_answer && (
                                            <>
                                                <Divider sx={{ my: 1 }} />
                                                <Typography variant="caption" color="error" sx={{ fontWeight: 'bold' }}>Quản trị viên đã sửa:</Typography>
                                                <Typography variant="body2" sx={{ fontStyle: 'italic' }}>{item.manager_answer}</Typography>
                                            </>
                                        )}
                                    </Paper>
                                </Box>
                                <Typography variant="caption" sx={{ display: 'block', textAlign: 'center', color: 'text.secondary', mb: 2 }}>
                                    {new Date(new Date(item.created_at).getTime() + 7 * 60 * 60 * 1000).toLocaleString('vi-VN')}
                                </Typography>
                            </Box>
                        ))}
                    </Stack>
                ) : (
                    <Typography sx={{ textAlign: 'center', mt: 5 }}>Không có dữ liệu hội thoại.</Typography>
                )}
            </DialogContent>

            <Box sx={{ p: 2, display: 'flex', justifyContent: 'center', bgcolor: '#f0f2f5' }}>
                <Pagination 
                    count={data.total_pages} 
                    page={page} 
                    onChange={(e, p) => fetchHistory(p)} 
                    color="primary" 
                    size="small"
                />
            </Box>
        </Dialog>
    );
};

export default UserChatHistoryModal;