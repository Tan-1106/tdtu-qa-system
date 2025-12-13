import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
    Dialog, DialogTitle, DialogContent, DialogActions, Button, 
    Box, Typography, CircularProgress, Alert, 
    Table, TableBody, TableCell, TableContainer, TableHead, 
    TableRow, Paper, TablePagination, Accordion, AccordionSummary, 
    AccordionDetails, Chip, IconButton, TextField, Stack 
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { 
    getChunksByDocumentId, 
    addPotentialQuestionToChunk, 
    deletePotentialQuestionFromChunk 
} from '../../api/documentApi'; 
import { extractError } from '../../utils/apiUtils';


// Hàm chuyển đổi object chunks thành mảng có key là index
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

    // Reset state khi modal đóng
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

    // Fetch chunks
    const fetchChunks = useCallback(async (targetPage = page, targetLimit = rowsPerPage) => {
        if (!documentId) return;

        setIsLoading(true);
        setError(null);
        setSuccessMsg(null);
        
        try {
            const result = await getChunksByDocumentId(documentId, targetPage + 1, targetLimit);
            
            const formattedChunks = formatChunksData(result.document_chunks);
            
            setChunksData(formattedChunks);
            setTotalChunks(result.total);
            setPage(result.current_page - 1); 
            
        } catch (err) {
            console.error("Error fetching document chunks:", err);
            setError(extractError(err, 'Lỗi khi tải danh sách chunks.'));
            setChunksData([]);
            setTotalChunks(0);
        } finally {
            setIsLoading(false);
        }
    }, [documentId, page, rowsPerPage]);

    // Re-fetch khi thay đổi trang/số dòng
    useEffect(() => {
        if (open && documentId && !isLoading) {
            fetchChunks();
        }
    }, [page, rowsPerPage, fetchChunks]);
    
    // Pagination Handlers
    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0); 
    };
    
    // --- Quản lý Câu hỏi Tiềm năng ---

    const handleNewQuestionChange = (chunkIndex, value) => {
        setNewQuestionInput(prev => ({ ...prev, [chunkIndex]: value }));
    };

    const handleAddQuestion = async (chunkIndex) => {
        const question = newQuestionInput[chunkIndex]?.trim();
        if (!question) {
            setError('Câu hỏi không được để trống.');
            return;
        }

        setIsActionLoading(true);
        setError(null);
        setSuccessMsg(null);
        
        try {
            await addPotentialQuestionToChunk(documentId, chunkIndex, question); 
            
            setNewQuestionInput(prev => ({ ...prev, [chunkIndex]: '' }));
            setSuccessMsg(`Đã thêm câu hỏi cho Chunk #${chunkIndex}. Đang tải lại danh sách...`);
            
            await fetchChunks(); 
            
        } catch (err) {
            console.error("Error adding potential question:", err);
            setError(extractError(err, `Thêm câu hỏi cho Chunk #${chunkIndex} thất bại.`));
        } finally {
            setIsActionLoading(false);
        }
    };
    const handleDeleteQuestion = async (chunkIndex, questionIndex, questionText) => {
        if (!window.confirm(`Bạn có chắc chắn muốn xóa câu hỏi "${questionText}" khỏi Chunk #${chunkIndex}? Thao tác này cũng xóa embedding liên quan.`)) {
            return;
        }

        setIsActionLoading(true);
        setError(null);
        setSuccessMsg(null);

        try {
            await deletePotentialQuestionFromChunk(documentId, chunkIndex, questionIndex); 
            
            setSuccessMsg(`Đã xóa câu hỏi #${questionIndex} khỏi Chunk #${chunkIndex}. Đang tải lại danh sách...`);
            
            await fetchChunks();

        } catch (err) {
            console.error("Error deleting potential question:", err);
            setError(extractError(err, `Xóa câu hỏi #${questionIndex} khỏi Chunk #${chunkIndex} thất bại.`));
        } finally {
            setIsActionLoading(false);
        }
    };

    // Render logic
    const chunksList = useMemo(() => formatChunksData(chunksData), [chunksData]);

    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="lg"
            fullWidth
        >
            <DialogTitle sx={{ bgcolor: 'primary.main', color: 'white' }}>
                Chi tiết Chunks và Câu hỏi Tiềm năng
            </DialogTitle>
            <DialogContent dividers sx={{ minHeight: 400, position: 'relative' }}>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    Tài liệu: {documentName} (ID: {documentId})
                </Typography>

                {error && <Alert severity="error" sx={{ my: 2 }}>{error}</Alert>}
                {successMsg && <Alert severity="success" sx={{ my: 2 }}>{successMsg}</Alert>}
                
                {isActionLoading && (
                    <Box sx={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, bgcolor: 'rgba(255, 255, 255, 0.7)', zIndex: 1000, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                        <CircularProgress size={60} />
                    </Box>
                )}
                
                {isLoading && chunksList.length === 0 ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
                        <CircularProgress />
                        <Typography sx={{ ml: 2 }}>Đang tải chunks...</Typography>
                    </Box>
                ) : (
                    <>
                        <TableContainer component={Paper} elevation={2} sx={{ mb: 2 }}>
                            <Table size="small">
                                <TableHead sx={{ bgcolor: 'grey.100' }}>
                                    <TableRow>
                                        <TableCell sx={{ width: '5%', fontWeight: 'bold' }}>#</TableCell>
                                        <TableCell sx={{ width: '40%', fontWeight: 'bold' }}>Đoạn văn bản (Text)</TableCell>
                                        <TableCell sx={{ width: '55%', fontWeight: 'bold' }}>Câu hỏi Tiềm năng ({totalChunks} Chunks)</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {chunksList.map((chunk) => (
                                        <TableRow key={chunk.index} hover>
                                            <TableCell sx={{ fontWeight: 600 }}>{chunk.index}</TableCell>
                                            <TableCell>
                                                <Typography 
                                                    variant="body2" 
                                                    sx={{ 
                                                        maxHeight: '150px', 
                                                        overflowY: 'auto', 
                                                        whiteSpace: 'pre-wrap' 
                                                    }}
                                                >
                                                    {chunk.text}
                                                </Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Stack spacing={1}>
                                                    {/* Danh sách các câu hỏi hiện có */}
                                                    {chunk.potential_questions.map((question, qIndex) => (
                                                        <Box 
                                                            key={qIndex} 
                                                            sx={{ 
                                                                display: 'flex', 
                                                                justifyContent: 'space-between', 
                                                                alignItems: 'center', 
                                                                p: 0.5, 
                                                                border: '1px solid #ccc', 
                                                                borderRadius: '8px' 
                                                            }}
                                                        >
                                                            <Typography variant="body2" sx={{ 
                                                                flexGrow: 1, 
                                                                wordBreak: 'break-word', 
                                                                mr: 1 
                                                            }}>
                                                                <span style={{ fontWeight: 600, color: '#1976d2' }}>[{qIndex}]</span> {question}
                                                            </Typography>
                                                            
                                                            <IconButton
                                                                size="small"
                                                                onClick={() => handleDeleteQuestion(chunk.index, qIndex, question)}
                                                                sx={{ 
                                                                    color: 'error.main', 
                                                                    minWidth: '24px', 
                                                                    height: '24px', 
                                                                    p: 0 
                                                                }}
                                                                disabled={isActionLoading}
                                                            >
                                                                <DeleteIcon fontSize="inherit" />
                                                            </IconButton>
                                                        </Box>
                                                    ))}
                                                    
                                                    {/* Form thêm câu hỏi mới */}
                                                    <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                                                        <TextField
                                                            fullWidth
                                                            variant="outlined"
                                                            size="small"
                                                            placeholder="Nhập câu hỏi mới..."
                                                            value={newQuestionInput[chunk.index] || ''}
                                                            onChange={(e) => handleNewQuestionChange(chunk.index, e.target.value)}
                                                            onKeyDown={(e) => e.key === 'Enter' && handleAddQuestion(chunk.index)}
                                                            disabled={isActionLoading}
                                                        />
                                                        <Button
                                                            variant="contained"
                                                            onClick={() => handleAddQuestion(chunk.index)}
                                                            startIcon={<AddIcon />}
                                                            size="small"
                                                            disabled={isActionLoading || !newQuestionInput[chunk.index]?.trim()}
                                                        >
                                                            Thêm
                                                        </Button>
                                                    </Stack>
                                                </Stack>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                    {chunksList.length === 0 && !isLoading && (
                                        <TableRow>
                                            <TableCell colSpan={3} align="center" sx={{ color: 'text.secondary', py: 4 }}>
                                                Tài liệu này chưa có chunks nào.
                                            </TableCell>
                                        </TableRow>
                                    )}
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
                            rowsPerPageOptions={[5, 10, 20, 50]}
                            labelRowsPerPage="Chunks mỗi trang:"
                            labelDisplayedRows={({ from, to, count }) =>
                                `${from}-${to} trên ${count} Chunks`
                            }
                        />
                    </>
                )}
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} variant="contained" color="secondary">
                    Đóng
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default DocumentChunksModal;