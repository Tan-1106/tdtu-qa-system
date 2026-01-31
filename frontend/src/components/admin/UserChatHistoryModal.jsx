import React, { useState, useEffect } from 'react';
import {
    Dialog, DialogTitle, DialogContent, IconButton, Typography, 
    Box, CircularProgress, Pagination, Divider, Paper, Stack, TextField,
    Accordion, AccordionSummary, AccordionDetails, Chip, InputAdornment
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SearchIcon from '@mui/icons-material/Search';
import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutline';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import ReactMarkdown from 'react-markdown';
import { getUserChatHistory } from '../../api/adminApi';

const UserChatHistoryModal = ({ open, onClose, user }) => {
    const [data, setData] = useState({ questions: [], total_pages: 1 });
    const [loading, setLoading] = useState(false);
    const [page, setPage] = useState(1);
    const [searchQuery, setSearchQuery] = useState('');
    const [expandedId, setExpandedId] = useState(null);

    useEffect(() => {
        if (open && user?.id) {
            fetchHistory(1);
        }
    }, [open, user]);

    const fetchHistory = async (p) => {
        setLoading(true);
        try {
            const res = await getUserChatHistory(user.id, p, 15); // Tăng lên 15 chat/trang
            setData(res);
            setPage(p);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const filteredQuestions = data.questions.filter(item => 
        item.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (item.answer && item.answer.toLowerCase().includes(searchQuery.toLowerCase()))
    );

    const formatDate = (dateString) => {
        const date = new Date(new Date(dateString).getTime() + 7 * 60 * 60 * 1000);
        return date.toLocaleString('vi-VN', { 
            day: '2-digit', 
            month: '2-digit', 
            year: 'numeric',
            hour: '2-digit', 
            minute: '2-digit' 
        });
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle sx={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                bgcolor: 'primary.main', 
                color: 'white',
                pb: 2
            }}>
                <Box>
                    <Typography variant="h6">Lịch sử chat: {user?.fullName}</Typography>
                    <Typography variant="caption" sx={{ opacity: 0.9 }}>
                        Tổng số: {data.total || 0} cuộc hội thoại
                    </Typography>
                </Box>
                <IconButton onClick={onClose} sx={{ color: 'white' }}><CloseIcon /></IconButton>
            </DialogTitle>

            <Box sx={{ px: 3, pt: 2, pb: 1, bgcolor: '#f5f5f5', borderBottom: '1px solid #e0e0e0' }}>
                <TextField
                    fullWidth
                    size="small"
                    placeholder="Tìm kiếm trong lịch sử chat..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <SearchIcon />
                            </InputAdornment>
                        ),
                    }}
                    sx={{ bgcolor: 'white' }}
                />
            </Box>

            <DialogContent sx={{ p: 0, bgcolor: '#fafafa', minHeight: '500px', maxHeight: '600px' }}>
                {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
                        <CircularProgress />
                    </Box>
                ) : filteredQuestions.length > 0 ? (
                    <Box sx={{ p: 2 }}>
                        {filteredQuestions.map((item, index) => (
                            <Accordion 
                                key={item._id}
                                expanded={expandedId === item._id}
                                onChange={() => setExpandedId(expandedId === item._id ? null : item._id)}
                                sx={{ 
                                    mb: 1.5,
                                    '&:before': { display: 'none' },
                                    boxShadow: '0 2px 4px rgba(0,0,0,0.08)',
                                    borderRadius: '8px !important',
                                    overflow: 'hidden'
                                }}
                            >
                                <AccordionSummary 
                                    expandIcon={<ExpandMoreIcon />}
                                    sx={{ 
                                        bgcolor: 'white',
                                        '&:hover': { bgcolor: '#f5f5f5' },
                                        borderLeft: item.manager_answer ? '4px solid #f44336' : '4px solid #2196f3'
                                    }}
                                >
                                    <Box sx={{ width: '100%', pr: 2 }}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                            <ChatBubbleOutlineIcon sx={{ fontSize: 18, color: 'primary.main' }} />
                                            <Typography 
                                                variant="body2" 
                                                sx={{ 
                                                    fontWeight: 500,
                                                    flex: 1,
                                                    overflow: 'hidden',
                                                    textOverflow: 'ellipsis',
                                                    whiteSpace: 'nowrap'
                                                }}
                                            >
                                                {item.question}
                                            </Typography>
                                        </Box>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                                            <Chip 
                                                icon={<AccessTimeIcon />}
                                                label={formatDate(item.created_at)}
                                                size="small"
                                                sx={{ fontSize: '0.7rem', height: 22 }}
                                            />
                                            {item.feedback === 'Like' && (
                                                <Chip label="👍 Like" size="small" color="success" sx={{ fontSize: '0.7rem', height: 22 }} />
                                            )}
                                            {item.feedback === 'Dislike' && (
                                                <Chip label="👎 Dislike" size="small" color="error" sx={{ fontSize: '0.7rem', height: 22 }} />
                                            )}
                                            {item.manager_answer && (
                                                <Chip label="✏️ Đã sửa" size="small" color="warning" sx={{ fontSize: '0.7rem', height: 22 }} />
                                            )}
                                        </Box>
                                    </Box>
                                </AccordionSummary>
                                <AccordionDetails sx={{ bgcolor: '#f9f9f9', p: 2 }}>
                                    <Stack spacing={2}>
                                        {/* Câu hỏi */}
                                        <Paper sx={{ p: 2, bgcolor: '#e3f2fd', borderLeft: '3px solid #2196f3' }}>
                                            <Typography variant="caption" sx={{ fontWeight: 'bold', color: 'primary.main', display: 'block', mb: 1 }}>
                                                Câu hỏi:
                                            </Typography>
                                            <Typography variant="body2">{item.question}</Typography>
                                        </Paper>

                                        {/* Câu trả lời của bot */}
                                        <Paper sx={{ p: 2, bgcolor: 'white', border: '1px solid #e0e0e0' }}>
                                            <Typography variant="caption" sx={{ fontWeight: 'bold', color: 'text.secondary', display: 'block', mb: 1 }}>
                                                Trả lời của Chatbot:
                                            </Typography>
                                            <Box component="div" sx={{ 
                                                '& p': { margin: 0, marginBottom: '8px' },
                                                '& ul, & ol': { marginLeft: '20px', marginTop: '4px', marginBottom: '8px' },
                                                '& li': { marginBottom: '4px' }
                                            }}>
                                                <ReactMarkdown
                                                    components={{
                                                        p: ({node, ...props}) => <Typography variant="body2" component="p" {...props} />,
                                                        strong: ({node, ...props}) => <strong style={{ fontWeight: 700 }} {...props} />,
                                                        a: ({node, ...props}) => <a style={{ color: '#1976d2' }} {...props} target="_blank" rel="noopener noreferrer" />,
                                                    }}
                                                >
                                                    {(item.answer || "Đang trả lời...").replace(/\/n/g, '\n')}
                                                </ReactMarkdown>
                                            </Box>
                                        </Paper>

                                        {/* Câu trả lời của quản trị viên */}
                                        {item.manager_answer && (
                                            <Paper sx={{ p: 2, bgcolor: '#fff3e0', borderLeft: '3px solid #ff9800' }}>
                                                <Typography variant="caption" sx={{ fontWeight: 'bold', color: '#f57c00', display: 'block', mb: 1 }}>
                                                    ✏️ Quản trị viên đã sửa:
                                                </Typography>
                                                <Box component="div" sx={{ 
                                                    '& p': { margin: 0, marginBottom: '8px' },
                                                    '& ul, & ol': { marginLeft: '20px', marginTop: '4px', marginBottom: '8px' }
                                                }}>
                                                    <ReactMarkdown
                                                        components={{
                                                            p: ({node, ...props}) => <Typography variant="body2" component="p" {...props} />,
                                                            strong: ({node, ...props}) => <strong style={{ fontWeight: 700 }} {...props} />,
                                                            a: ({node, ...props}) => <a style={{ color: '#1976d2' }} {...props} target="_blank" rel="noopener noreferrer" />,
                                                        }}
                                                    >
                                                        {item.manager_answer.replace(/\/n/g, '\n')}
                                                    </ReactMarkdown>
                                                </Box>
                                            </Paper>
                                        )}
                                    </Stack>
                                </AccordionDetails>
                            </Accordion>
                        ))}
                    </Box>
                ) : (
                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '400px' }}>
                        <ChatBubbleOutlineIcon sx={{ fontSize: 60, color: 'text.disabled', mb: 2 }} />
                        <Typography color="text.secondary">
                            {searchQuery ? 'Không tìm thấy kết quả phù hợp' : 'Không có dữ liệu hội thoại'}
                        </Typography>
                    </Box>
                )}
            </DialogContent>

            {data.total_pages > 1 && (
                <Box sx={{ p: 2, display: 'flex', justifyContent: 'center', bgcolor: '#f5f5f5', borderTop: '1px solid #e0e0e0' }}>
                    <Pagination 
                        count={data.total_pages} 
                        page={page} 
                        onChange={(e, p) => fetchHistory(p)} 
                        color="primary" 
                        showFirstButton 
                        showLastButton
                    />
                </Box>
            )}
        </Dialog>
    );
};

export default UserChatHistoryModal;