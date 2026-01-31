import React, { useState, useEffect } from 'react';
import { 
    Dialog, DialogTitle, DialogContent, DialogActions, 
    Button, TextField, Typography, Box, Divider, CircularProgress, Grid, Chip,
    Tabs, Tab, Paper, Stack
} from '@mui/material';
import ReactMarkdown from 'react-markdown';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import EditNoteIcon from '@mui/icons-material/EditNote';
import VisibilityIcon from '@mui/icons-material/Visibility';
import PersonIcon from '@mui/icons-material/Person';

const ManagerAnswerModal = ({ open, onClose, qaRecord, onSave }) => {
    const [answer, setAnswer] = useState('');
    const [isSaving, setIsSaving] = useState(false);
    const [previewTab, setPreviewTab] = useState(0); // 0: Edit, 1: Preview

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
                    <Box component="div" sx={{ 
                        '& p': { margin: 0, marginBottom: '12px', lineHeight: 1.7 },
                        '& p:last-child': { marginBottom: 0 },
                        '& ul, & ol': { marginLeft: '24px', marginTop: '8px', marginBottom: '12px' },
                        '& li': { marginBottom: '6px', lineHeight: 1.6 },
                        '& strong': { fontWeight: 700, color: '#d84315' },
                        '& a': { color: '#1976d2', textDecoration: 'underline' }
                    }}>
                        <ReactMarkdown
                            components={{
                                p: ({node, ...props}) => <Typography variant="body2" component="p" {...props} />,
                                strong: ({node, ...props}) => <strong {...props} />,
                                a: ({node, ...props}) => <a {...props} target="_blank" rel="noopener noreferrer" />,
                                ul: ({node, ...props}) => <ul {...props} />,
                                ol: ({node, ...props}) => <ol {...props} />,
                                li: ({node, ...props}) => <li {...props} />,
                            }}
                        >
                            {(qaRecord.botAnswer || 'Không có câu trả lời từ BOT.').replace(/\/n/g, '\n')}
                        </ReactMarkdown>
                    </Box>
                </Paper>

                {/* Câu trả lời của Quản lý với Tab Preview */}
                <Paper elevation={2} sx={{ borderLeft: '4px solid #4caf50' }}>
                    <Box sx={{ bgcolor: '#e8f5e9', px: 2, pt: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <EditNoteIcon sx={{ color: '#2e7d32' }} />
                            <Typography variant="subtitle1" fontWeight={600}>Câu trả lời của Quản lý</Typography>
                        </Box>
                        <Tabs 
                            value={previewTab} 
                            onChange={(e, newValue) => setPreviewTab(newValue)}
                            sx={{ minHeight: 40 }}
                        >
                            <Tab 
                                icon={<EditNoteIcon />} 
                                iconPosition="start" 
                                label="Nhập liệu" 
                                sx={{ minHeight: 40, textTransform: 'none' }}
                            />
                            <Tab 
                                icon={<VisibilityIcon />} 
                                iconPosition="start" 
                                label="Xem trước" 
                                sx={{ minHeight: 40, textTransform: 'none' }}
                            />
                        </Tabs>
                    </Box>
                    
                    <Box sx={{ p: 2, bgcolor: 'white' }}>
                        {previewTab === 0 ? (
                            <Box>
                                <TextField
                                    fullWidth
                                    multiline
                                    rows={10}
                                    placeholder="Nhập câu trả lời của bạn tại đây... (Hỗ trợ Markdown)"
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
                                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                                    💡 Hỗ trợ Markdown: **in đậm**, *in nghiêng*, - danh sách, 1. danh sách số
                                </Typography>
                            </Box>
                        ) : (
                            <Box sx={{ 
                                minHeight: '280px',
                                p: 2,
                                bgcolor: '#f5f5f5',
                                borderRadius: 1,
                                border: '1px solid #e0e0e0'
                            }}>
                                {answer.trim() ? (
                                    <Box component="div" sx={{ 
                                        '& p': { margin: 0, marginBottom: '12px', lineHeight: 1.7 },
                                        '& p:last-child': { marginBottom: 0 },
                                        '& ul, & ol': { marginLeft: '24px', marginTop: '8px', marginBottom: '12px' },
                                        '& li': { marginBottom: '6px', lineHeight: 1.6 },
                                        '& strong': { fontWeight: 700 },
                                        '& a': { color: '#1976d2', textDecoration: 'underline' }
                                    }}>
                                        <ReactMarkdown
                                            components={{
                                                p: ({node, ...props}) => <Typography variant="body2" component="p" {...props} />,
                                                strong: ({node, ...props}) => <strong {...props} />,
                                                a: ({node, ...props}) => <a {...props} target="_blank" rel="noopener noreferrer" />,
                                                ul: ({node, ...props}) => <ul {...props} />,
                                                ol: ({node, ...props}) => <ol {...props} />,
                                                li: ({node, ...props}) => <li {...props} />,
                                            }}
                                        >
                                            {answer.replace(/\/n/g, '\n')}
                                        </ReactMarkdown>
                                    </Box>
                                ) : (
                                    <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                                        Chưa có nội dung để xem trước. Hãy nhập câu trả lời ở tab "Nhập liệu".
                                    </Typography>
                                )}
                            </Box>
                        )}
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
