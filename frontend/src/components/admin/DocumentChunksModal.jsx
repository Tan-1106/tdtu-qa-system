import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
    Dialog, DialogTitle, DialogContent, DialogActions, Button, 
    Box, Typography, CircularProgress, Alert, 
    Table, TableBody, TableCell, TableContainer, TableHead, 
    TableRow, Paper, TablePagination, Chip, IconButton, TextField, Stack, Divider
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import CloseIcon from '@mui/icons-material/Close';
import DescriptionIcon from '@mui/icons-material/Description';
import KeyIcon from '@mui/icons-material/Key';
import { 
    getChunksByDocumentId, 
    addPotentialQuestionToChunk, 
    deletePotentialQuestionFromChunk 
} from '../../api/documentApi'; 

export const extractError = (error, defaultMessage = 'Lỗi không xác định.') => {
    return error.response?.data?.details || error.message || defaultMessage;
};

const formatChunksData = (documentChunksObj) => {
    if (!documentChunksObj || typeof documentChunksObj !== 'object') return [];
    
    return Object.entries(documentChunksObj).map(([key, value]) => ({
        index: parseInt(key, 10),
        text: value.text,
        potential_questions: value.potential_questions || [],
        embedding_ids: value.embedding_ids || []
    })).sort((a, b) => a.index - b.index); 
};

const DocumentChunksModal = ({ open, onClose, document }) => {
    const [chunksData, setChunksData] = useState([]);
    const [totalChunks, setTotalChunks] = useState(0);
    const [page, setPage] = useState(0); 
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [successMsg, setSuccessMsg] = useState(null);
    const [newQuestionInput, setNewQuestionInput] = useState({}); 
    const [isActionLoading, setIsActionLoading] = useState(false); 

    const documentId = document?._id || document?.id;
    const documentName = document?.file_name || 'Tài liệu không tên';

    useEffect(() => {
        if (!open) {
            setChunksData([]);
            setTotalChunks(0);
            setPage(0);
            setError(null);
            setSuccessMsg(null);
            setNewQuestionInput({});
        } else if (documentId) {
            fetchChunks();
        }
    }, [open, documentId]);

    const fetchChunks = useCallback(async (targetPage = page, targetLimit = rowsPerPage) => {
        if (!documentId) return;
        setIsLoading(true);
        try {
            const result = await getChunksByDocumentId(documentId, targetPage + 1, targetLimit);
            const formattedChunks = formatChunksData(result.document_chunks);
            setChunksData(formattedChunks);
            setTotalChunks(result.total);
            setPage(result.current_page - 1); 
        } catch (err) {
            setError(extractError(err, 'Lỗi khi tải danh sách chunks.'));
        } finally {
            setIsLoading(false);
        }
    }, [documentId, page, rowsPerPage]);

    useEffect(() => {
        if (open && documentId && !isLoading) {
            fetchChunks();
        }
    }, [page, rowsPerPage, fetchChunks]);
    
    const handleChangePage = (event, newPage) => setPage(newPage);
    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0); 
    };
    
    const handleAddQuestion = async (chunkIndex) => {
        const question = newQuestionInput[chunkIndex]?.trim();
        if (!question) return;
        setIsActionLoading(true);
        try {
            await addPotentialQuestionToChunk(documentId, chunkIndex, question); 
            setNewQuestionInput(prev => ({ ...prev, [chunkIndex]: '' }));
            await fetchChunks(); 
        } catch (err) {
            setError(extractError(err, `Lỗi khi thêm câu hỏi.`));
        } finally {
            setIsActionLoading(false);
        }
    };

    const handleDeleteQuestion = async (chunkIndex, questionIndex, questionText) => {
        if (!window.confirm(`Xóa câu hỏi này?`)) return;
        setIsActionLoading(true);
        try {
            await deletePotentialQuestionFromChunk(documentId, chunkIndex, questionIndex); 
            await fetchChunks();
        } catch (err) {
            setError(extractError(err, `Lỗi khi xóa câu hỏi.`));
        } finally {
            setIsActionLoading(false);
        }
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="xl" fullWidth scroll="paper">
            <DialogTitle sx={{ 
                m: 0, p: 2, bgcolor: 'primary.main', color: 'white',
                display: 'flex', justifyContent: 'space-between', alignItems: 'center'
            }}>
                <Typography variant="h6" fontWeight={700}>CHI TIẾT DỮ LIỆU TRÍCH XUẤT (CHUNKS)</Typography>
                <IconButton onClick={onClose} sx={{ color: 'white' }}><CloseIcon /></IconButton>
            </DialogTitle>

            <DialogContent dividers sx={{ bgcolor: '#f8f9fa', p: 3 }}>
                <Paper elevation={0} sx={{ p: 2, mb: 3, borderRadius: 2, border: '1px dashed #1976d2', bgcolor: '#e3f2fd' }}>
                    <Stack spacing={1}>
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                            <DescriptionIcon color="primary" sx={{ mt: 0.3 }} />
                            <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#1565c0', lineHeight: 1.3 }}>
                                {documentName}
                            </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <KeyIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                            <Typography variant="caption" sx={{ fontFamily: 'monospace', color: 'text.secondary', bgcolor: 'white', px: 1, borderRadius: 1 }}>
                                ID: {documentId}
                            </Typography>
                        </Box>
                    </Stack>
                </Paper>

                {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
                
                <TableContainer component={Paper} elevation={3} sx={{ borderRadius: 2, position: 'relative' }}>
                    {isLoading && (
                        <Box sx={{ position: 'absolute', zIndex: 10, width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', bgcolor: 'rgba(255,255,255,0.7)' }}>
                            <CircularProgress />
                        </Box>
                    )}
                    <Table>
                        <TableHead sx={{ bgcolor: '#2c3e50' }}>
                            <TableRow>
                                <TableCell sx={{ width: '60px', color: 'white', fontWeight: 700 }}></TableCell>
                                <TableCell sx={{ width: '60%', color: 'white', fontWeight: 700 }}>Nội dung đoạn văn (Text Chunk)</TableCell>
                                <TableCell sx={{ color: 'white', fontWeight: 700 }}>Câu hỏi huấn luyện AI</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {chunksData.map((chunk) => (
                                <TableRow key={chunk.index} sx={{ '&:nth-of-type(odd)': { bgcolor: '#ffffff' }, '&:nth-of-type(even)': { bgcolor: '#fcfcfc' } }}>
                                    <TableCell sx={{ verticalAlign: 'top', fontWeight: 700 }}>
                                        <Chip label={chunk.index} size="small" color="primary" variant="outlined" />
                                    </TableCell>
                                    <TableCell sx={{ verticalAlign: 'top' }}>
                                        <Box sx={{ 
                                            height: 'auto', 
                                            minHeight: '100px', 
                                            pr: 1,
                                            fontSize: '0.95rem',
                                            lineHeight: 1.6,
                                            color: '#34495e',
                                            whiteSpace: 'pre-wrap', 
                                        }}>
                                            {chunk.text}
                                        </Box>
                                    </TableCell>
                                    <TableCell sx={{ verticalAlign: 'top', bgcolor: '#fdfefe' }}>
                                        <Stack spacing={1.5}>
                                            {chunk.potential_questions.map((question, qIndex) => (
                                                <Box key={qIndex} sx={{ 
                                                    display: 'flex', gap: 1, p: 1.5, borderRadius: 1.5, 
                                                    bgcolor: 'white', border: '1px solid #e0e0e0',
                                                    boxShadow: '0 2px 4px rgba(0,0,0,0.03)',
                                                    '&:hover': { borderColor: 'primary.light' }
                                                }}>
                                                    <Typography variant="body2" sx={{ flexGrow: 1, color: '#2c3e50' }}>
                                                        <b style={{ color: '#1976d2' }}>Q{qIndex + 1}:</b> {question}
                                                    </Typography>
                                                    <IconButton size="small" onClick={() => handleDeleteQuestion(chunk.index, qIndex, question)} color="error" sx={{ p: 0.5 }}>
                                                        <DeleteIcon fontSize="small" />
                                                    </IconButton>
                                                </Box>
                                            ))}
                                            
                                            <Box sx={{ mt: 1, p: 1.5, borderRadius: 1.5, border: '1px dashed #95a5a6' }}>
                                                <TextField
                                                    fullWidth multiline rows={2} variant="standard"
                                                    placeholder="Thêm câu hỏi tiềm năng cho đoạn văn này..."
                                                    value={newQuestionInput[chunk.index] || ''}
                                                    onChange={(e) => setNewQuestionInput({...newQuestionInput, [chunk.index]: e.target.value})}
                                                    InputProps={{ disableUnderline: true, sx: { fontSize: '0.875rem' } }}
                                                />
                                                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                                                    <Button 
                                                        size="small" variant="contained" startIcon={<AddIcon />}
                                                        disabled={!newQuestionInput[chunk.index]?.trim() || isActionLoading}
                                                        onClick={() => handleAddQuestion(chunk.index)}
                                                    >
                                                        Thêm câu hỏi
                                                    </Button>
                                                </Box>
                                            </Box>
                                        </Stack>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>

                <TablePagination
                    component="div"
                    count={totalChunks}
                    page={page}
                    onPageChange={handleChangePage}
                    rowsPerPage={rowsPerPage}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                    rowsPerPageOptions={[5, 10, 20]}
                    labelRowsPerPage="Số dòng:"
                    sx={{ mt: 1 }}
                />
            </DialogContent>
            <DialogActions sx={{ p: 2, bgcolor: '#f1f2f6' }}>
                <Button onClick={onClose} variant="outlined" color="inherit">Đóng cửa sổ</Button>
            </DialogActions>
        </Dialog>
    );
};

export default DocumentChunksModal;