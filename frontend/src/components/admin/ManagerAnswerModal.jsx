import React, { useState, useEffect } from 'react';
import { 
    Dialog, DialogTitle, DialogContent, DialogActions, 
    Button, TextField, Typography, Box, Divider, CircularProgress, Grid, Chip,
    Paper, Stack
} from '@mui/material';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import EditNoteIcon from '@mui/icons-material/EditNote';
import PersonIcon from '@mui/icons-material/Person';

// Function to remove markdown formatting (only bold and italic)
const cleanMarkdown = (text) => {
    if (!text) return text;
    
    // Remove bold (**text** or __text__)
    text = text.replace(/\*\*(.+?)\*\*/g, '$1');
    text = text.replace(/__(.+?)__/g, '$1');
    
    // Remove italic (*text* or _text_) - but be careful not to remove single asterisks used for other purposes
    text = text.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '$1');
    text = text.replace(/(?<!_)_(?!_)(.+?)(?<!_)_(?!_)/g, '$1');
    
    return text;
};

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
        <Dialog open={open} onClose={onClose} fullWidth maxWidth="lg">
            <DialogTitle sx={{ 
                bgcolor: isAnswered ? '#e8f5e9' : '#ffebee',
                display: 'flex',
                alignItems: 'center',
                gap: 1
            }}>
                <EditNoteIcon />
                {isAnswered ? 'Xem / Sửa Phản hồi đã xử lý' : 'Xử lý Phản hồi Tiêu cực (Dislike)'}
            </DialogTitle>
            <Divider />
            <DialogContent sx={{ bgcolor: '#fafafa' }}>
                {/* Thông tin User */}
                <Paper elevation={1} sx={{ p: 2, mb: 2, borderLeft: '4px solid #2196f3' }}>
                    <Stack direction="row" spacing={3} alignItems="center" flexWrap="wrap">
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <PersonIcon sx={{ color: 'primary.main' }} />
                            <Box>
                                <Typography variant="caption" color="text.secondary">MSSV</Typography>
                                <Typography variant="body2" fontWeight={600}>{qaRecord.studentId}</Typography>
                            </Box>
                        </Box>
                        <Box>
                            <Typography variant="caption" color="text.secondary">Khoa</Typography>
                            <Typography variant="body2" fontWeight={600}>{qaRecord.studentFaculty}</Typography>
                        </Box>
                        <Box>
                            <Typography variant="caption" color="text.secondary">Thời điểm</Typography>
                            <Typography variant="body2" fontWeight={600}>
                                {new Date(new Date(qaRecord.createdAt).getTime() + 7 * 60 * 60 * 1000).toLocaleString('vi-VN')}
                            </Typography>
                        </Box>
                        <Box sx={{ ml: 'auto' }}>
                            <Chip label={`Feedback: ${qaRecord.feedback}`} color="error" size="small" sx={{ mr: 1 }} />
                            <Chip label={isAnswered ? 'Đã xử lý' : 'Cần xử lý'} color={isAnswered ? 'success' : 'warning'} size="small" />
                        </Box>
                    </Stack>
                </Paper>

                {/* Câu hỏi */}
                <Paper elevation={1} sx={{ p: 2, mb: 2, bgcolor: '#e3f2fd', borderLeft: '4px solid #1976d2' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <QuestionAnswerIcon sx={{ color: 'primary.main' }} />
                        <Typography variant="subtitle1" fontWeight={600}>Câu hỏi của sinh viên</Typography>
                    </Box>
                    <Typography variant="body1">{qaRecord.question}</Typography>
                </Paper>
                
                {/* Câu trả lời BOT */}
                <Paper elevation={1} sx={{ p: 2, mb: 2, bgcolor: '#fff3e0', borderLeft: '4px solid #ff9800' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <SmartToyIcon sx={{ color: '#f57c00' }} />
                        <Typography variant="subtitle1" fontWeight={600}>Câu trả lời của Chatbot (Gốc)</Typography>
                    </Box>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                        {cleanMarkdown((qaRecord.botAnswer || 'Không có câu trả lời từ BOT.').replace(/\/n/g, '\n'))}
                    </Typography>
                </Paper>

                {/* Câu trả lời của Quản lý */}
                <Paper elevation={2} sx={{ borderLeft: '4px solid #4caf50' }}>
                    <Box sx={{ bgcolor: '#e8f5e9', px: 2, py: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <EditNoteIcon sx={{ color: '#2e7d32' }} />
                            <Typography variant="subtitle1" fontWeight={600}>Câu trả lời của Quản lý</Typography>
                        </Box>
                    </Box>
                    
                    <Box sx={{ p: 2, bgcolor: 'white' }}>
                        <TextField
                            fullWidth
                            multiline
                            rows={10}
                            placeholder="Nhập câu trả lời của bạn tại đây..."
                            value={answer}
                            onChange={(e) => setAnswer(e.target.value)}
                            variant="outlined"
                            sx={{ 
                                '& .MuiOutlinedInput-root': {
                                    fontFamily: 'monospace',
                                    fontSize: '0.9rem'
                                }
                            }}
                        />
                    </Box>
                </Paper>
            </DialogContent>
            <DialogActions sx={{ px: 3, py: 2, bgcolor: '#fafafa' }}>
                <Button onClick={onClose} disabled={isSaving} variant="outlined">
                    Hủy
                </Button>
                <Button 
                    onClick={handleSave} 
                    color={isAnswered ? 'primary' : 'error'} 
                    variant="contained" 
                    disabled={isSaving || !answer.trim()}
                    startIcon={isSaving ? <CircularProgress size={20} color="inherit" /> : <EditNoteIcon />}
                >
                    {isSaving ? 'Đang lưu...' : 'Lưu và Cập nhật'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default ManagerAnswerModal;
