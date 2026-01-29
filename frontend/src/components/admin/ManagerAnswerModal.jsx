import React, { useState, useEffect } from 'react';
import { 
    Dialog, DialogTitle, DialogContent, DialogActions, 
    Button, TextField, Typography, Box, Divider, CircularProgress, Grid, Chip
} from '@mui/material';

const ManagerAnswerModal = ({ open, onClose, qaRecord, onSave }) => {
    const [answer, setAnswer] = useState('');
    const [isSaving, setIsSaving] = useState(false);

    useEffect(() => {
        if (qaRecord) {
            setAnswer(qaRecord.managerAnswer || ''); 
        }
    }, [qaRecord, open]);

    const handleSave = async () => {
        if (!qaRecord || !answer.trim()) return;
        setIsSaving(true);
        await onSave(qaRecord.id, answer.trim());
        setIsSaving(false);
    };

    if (!qaRecord) return null;
    
    const isAnswered = qaRecord.managerAnswer && qaRecord.managerAnswer.trim() !== '';

    return (
        <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
            <DialogTitle sx={{ bgcolor: isAnswered ? '#e8f5e9' : '#ffebee' }}>
                {isAnswered ? 'Xem / Sửa Phản hồi đã xử lý' : 'Xử lý Phản hồi Tiêu cực (Dislike)'}
            </DialogTitle>
            <Divider />
            <DialogContent>
                <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                        <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>Thông tin User:</Typography>
                        <Typography variant="caption" display="block">MSSV: {qaRecord.studentId}</Typography>
                        <Typography variant="caption" display="block">Khoa: {qaRecord.studentFaculty}</Typography>
                        <Typography variant="caption" display="block">Thời điểm: {new Date(new Date(qaRecord.createdAt).getTime() + 7 * 60 * 60 * 1000).toLocaleString('vi-VN')}</Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                         <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>Trạng thái:</Typography>
                         <Chip label={`Feedback: ${qaRecord.feedback}`} color="error" size="small" sx={{ mr: 1 }} />
                         <Chip label={isAnswered ? 'Đã xử lý' : 'Cần xử lý'} color={isAnswered ? 'success' : 'warning'} size="small" />
                    </Grid>
                </Grid>
                <Divider sx={{ my: 2 }} />

                <Typography variant="body1" sx={{ fontWeight: 600, mb: 1 }}>Câu hỏi:</Typography>
                <Box sx={{ p: 1.5, mb: 2, bgcolor: '#e3f2fd', borderRadius: 2 }}>
                    <Typography>{qaRecord.question}</Typography>
                </Box>
                
                <Typography variant="body1" sx={{ fontWeight: 600, mb: 1 }}>Câu trả lời BOT (Gốc):</Typography>
                <Box sx={{ p: 1.5, mb: 3, bgcolor: '#fff3e0', borderRadius: 2, borderLeft: '3px solid orange' }}>
                    <Typography>{qaRecord.botAnswer || 'Không có câu trả lời từ BOT.'}</Typography>
                </Box>

                <Typography variant="body1" sx={{ fontWeight: 600, mb: 1 }}>Câu trả lời của quản lý</Typography>
                <TextField
                    fullWidth
                    multiline
                    rows={8}
                    label="Nhập câu trả lời"
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    variant="outlined"
                    sx={{ mb: 2 }}
                />
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} disabled={isSaving}>Hủy</Button>
                <Button 
                    onClick={handleSave} 
                    color={isAnswered ? 'primary' : 'error'} 
                    variant="contained" 
                    disabled={isSaving || !answer.trim()}
                    startIcon={isSaving && <CircularProgress size={20} color="inherit" />}
                >
                    {isSaving ? 'Đang lưu...' : 'Lưu và Cập nhật'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default ManagerAnswerModal;