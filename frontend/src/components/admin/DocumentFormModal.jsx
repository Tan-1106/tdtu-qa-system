import React, { useState, useEffect, useMemo } from 'react';
import { 
    Modal, Box, Typography, Button, IconButton, TextField, 
    FormControl, InputLabel, Select, MenuItem, Grid, Alert, 
    CircularProgress, FormHelperText, ToggleButtonGroup, ToggleButton, Stack 
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import SaveIcon from '@mui/icons-material/Save';

import { uploadDocument, updateDocument } from '../../api/documentApi'; 
import useUserAuth from '../../hooks/useUserAuth';

// --- STYLING ---
const style = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: { xs: '95%', sm: '85%', md: '850px' }, 
    bgcolor: 'background.paper',
    boxShadow: 24,
    borderRadius: 3, 
    p: { xs: 2, md: 4 },
    maxHeight: '95vh',
    overflowY: 'auto',
};

// --- UTILS ---
const extractError = (error, defaultMessage = 'Lỗi không xác định.') => {
    return error.response?.data?.details || error.message || defaultMessage;
};

const docUploadType = {
    NORMAL: 'NORMAL',
    APPENDIX: 'APPENDIX'
};


// --- MAIN COMPONENT ---
const DocumentFormModal = ({ open, onClose, onSave, editingDocument, availableFaculties, documentTypes, availableDepartments }) => {
    const { user: currentUser } = useUserAuth(); 
    const isAdmin = currentUser?.role === 'Admin';
    const isFacultyManager = currentUser?.is_faculty_manager;

    // State form
    const [formData, setFormData] = useState({
        file: null,
        file_name: '',
        doc_type: '',
        file_url: '',
        department: '',
        faculty: '',
        is_appendix: docUploadType.NORMAL,
    });
    
    const [fileDisplayName, setFileDisplayName] = useState('');
    const [scopeSelection, setScopeSelection] = useState(editingDocument?.department ? 'department' : (editingDocument?.faculty ? 'faculty' : '')); 

    // State quản lý thao tác
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const isEditMode = useMemo(() => !!editingDocument, [editingDocument]);

    // Lấy danh sách Khoa và Phòng ban đã lọc
    const departmentOptions = useMemo(() => {
        return availableDepartments?.filter(d => d) || [];
    }, [availableDepartments]);

    const facultyOptions = useMemo(() => {
        return availableFaculties?.filter(f => f) || [];
    }, [availableFaculties]);


    // --- EFFECT: Khởi tạo/Reset Form ---
    useEffect(() => {
        if (open) {
            setError(null);
            
            if (editingDocument) {
                setFormData({
                    file: null, 
                    file_name: editingDocument.file_name || '',
                    doc_type: editingDocument.doc_type || '',
                    file_url: editingDocument.file_url || '',
                    department: editingDocument.department || '',
                    faculty: editingDocument.faculty || '',
                    is_appendix: docUploadType.NORMAL, 
                });
                setFileDisplayName(editingDocument.file_name + '.pdf');
                
                if (isAdmin) {
                    if (editingDocument.department) {
                        setScopeSelection('department');
                    } else if (editingDocument.faculty) {
                        setScopeSelection('faculty');
                    } else {
                        setScopeSelection('');
                    }
                }
            } else {
                setFormData({
                    file: null,
                    file_name: '',
                    doc_type: '',
                    file_url: '',
                    department: '',
                    faculty: isFacultyManager ? currentUser.faculty : '', 
                    is_appendix: docUploadType.NORMAL,
                });
                setFileDisplayName('');
                setScopeSelection('');
            }
        }
    }, [open, editingDocument, isAdmin, isFacultyManager, currentUser]);

    // --- HANDLERS ---

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile && selectedFile.type === 'application/pdf') {
            setFormData(prev => ({ ...prev, file: selectedFile, file_name: selectedFile.name.replace(/\.pdf$/i, '') }));
            setFileDisplayName(selectedFile.name);
        } else {
            setError('Chỉ cho phép tải lên tệp PDF.');
            setFormData(prev => ({ ...prev, file: null, file_name: '' }));
            setFileDisplayName('');
        }
    };
    
    const handleScopeChange = (e, newScope) => {
        if (newScope !== null) {
            setScopeSelection(newScope);
            setFormData(prev => ({ 
                ...prev, 
                department: newScope === 'department' ? prev.department : '',
                faculty: newScope === 'faculty' ? prev.faculty : '',
            }));
        }
    };

    const handleScopeValueChange = (e) => {
        const value = e.target.value;
        if (scopeSelection === 'department') {
            setFormData(prev => ({ ...prev, department: value, faculty: '' }));
        } else if (scopeSelection === 'faculty') {
            setFormData(prev => ({ ...prev, faculty: value, department: '' }));
        }
    };


    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        if (!isEditMode && !formData.file) {
            setError('Vui lòng chọn tệp PDF để tải lên.');
            return;
        }
        if (!formData.doc_type || !formData.file_url) {
            setError('Vui lòng điền đầy đủ Loại tài liệu và URL gốc.');
            return;
        }
        if (isAdmin) {
            if (!scopeSelection || (scopeSelection === 'department' && !formData.department) || (scopeSelection === 'faculty' && !formData.faculty)) {
                setError('Vui lòng chọn phạm vi (Khoa hoặc Phòng Ban) cụ thể.');
                return;
            }
        }
        
        setIsLoading(true);

        try {
            if (isEditMode) {
                const updatePayload = {
                    file_name: formData.file_name,
                    doc_type: formData.doc_type,
                    file_url: formData.file_url,
                };
                if (isAdmin) {
                    updatePayload.department = formData.department || null;
                    updatePayload.faculty = formData.faculty || null;
                }

                await updateDocument(editingDocument.id, updatePayload);
            } else {
                const payload = new FormData();
                payload.append('file', formData.file);
                payload.append('doc_type', formData.doc_type);
                payload.append('file_url', formData.file_url);

                if (isAdmin && formData.department) {
                    payload.append('department', formData.department);
                }
                if (isAdmin && formData.faculty) {
                    payload.append('faculty', formData.faculty);
                }
                if (isFacultyManager && !isAdmin) {
                    payload.append('faculty', currentUser.faculty);
                }
                
                await uploadDocument(payload, formData.is_appendix === docUploadType.APPENDIX);
            }

            onSave(); 
            onClose();

        } catch (err) {
            console.error("Submission Error:", err);
            setError(extractError(err, isEditMode ? 'Cập nhật tài liệu thất bại.' : 'Tải lên tài liệu thất bại.'));
        } finally {
            setIsLoading(false);
        }
    };
    
    
    // --- RENDER ---
    return (
    <Modal open={open} onClose={onClose}>
        <Box sx={style} component="form" onSubmit={handleSubmit}>

            {/* HEADER */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.main' }}>
                    {isEditMode ? 'Chỉnh sửa tài liệu' : 'Tải lên tài liệu mới'}
                </Typography>
                <IconButton onClick={onClose} disabled={isLoading}>
                    <CloseIcon />
                </IconButton>
            </Box>

            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

            <Stack spacing={4}>

                <Box sx={{ p: 3, borderRadius: 2, border: '1px solid #e0e0e0' }}>
                    <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>Thông tin tệp & Tên tài liệu</Typography>
                    
                    <Grid container spacing={3}>
                        
                        <Grid item xs={12}>
                            <Stack spacing={1}>
                                <InputLabel htmlFor="file-upload" sx={{ fontWeight: 600 }}>Tệp PDF</InputLabel>
                                <input
                                    accept="application/pdf"
                                    id="file-upload"
                                    type="file"
                                    style={{ display: 'none' }}
                                    onChange={handleFileChange}
                                    disabled={isEditMode || isLoading} 
                                />
                                <label htmlFor="file-upload">
                                    <Button
                                        variant="contained"
                                        component="span"
                                        startIcon={<UploadFileIcon />}
                                        disabled={isEditMode || isLoading}
                                        color={fileDisplayName && !isEditMode ? 'success' : 'primary'}
                                    >
                                        {isEditMode ? "Tệp đã tải lên" : (fileDisplayName ? "Đã chọn file" : "Chọn PDF")}
                                    </Button>
                                </label>

                                {fileDisplayName && !isEditMode && (
                                    <FormHelperText sx={{ color: 'text.primary', mt: 1 }}>
                                        Tên tài liệu: {fileDisplayName}
                                    </FormHelperText>
                                )}
                                {!fileDisplayName && !isEditMode && (
                                    <FormHelperText>Chỉ chấp nhận file PDF. Tên tài liệu sẽ được tự động lấy từ tên file.</FormHelperText>
                                )}
                            </Stack>
                        </Grid>
                        
                    </Grid>
                    
                    {isEditMode && ( 
                        <Box sx={{ mt: 3 }}>
                            <TextField
                                fullWidth
                                label="Tên tài liệu"
                                name="file_name"
                                value={formData.file_name} 
                                onChange={handleChange} 
                                required
                                disabled={isLoading}
                                helperText="Tên hiển thị của tài liệu."
                            />
                        </Box>
                    )}
                </Box>

                <Box sx={{ p: 3, borderRadius: 2, border: '1px solid #e0e0e0' }}>
                    <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>Chi tiết tài liệu</Typography>

                    <Stack spacing={3}> 
                        
                        <TextField
                            fullWidth
                            label="URL gốc"
                            name="file_url"
                            value={formData.file_url}
                            onChange={handleChange}
                            required
                            disabled={isLoading}
                            helperText="Link gốc của tài liệu (ví dụ: link trên Website trường)."
                        />

                        <FormControl fullWidth required disabled={isLoading}>
                            <InputLabel>Loại tài liệu</InputLabel>
                            <Select
                                name="doc_type"
                                label="Loại tài liệu"
                                value={formData.doc_type}
                                onChange={handleChange}
                            >
                                {documentTypes.map(type => (
                                    <MenuItem key={type} value={type}>{type}</MenuItem>
                                ))}
                            </Select>
                            <FormHelperText>Chọn loại tài liệu phù hợp.</FormHelperText>
                        </FormControl>
                    </Stack>
                </Box>

               {(isAdmin || isFacultyManager) && (
                        <Box sx={{ p: 3, borderRadius: 2, border: '1px solid #e0e0e0' }}>
                            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>Phạm vi áp dụng</Typography>

                            {isAdmin ? (
                                <Stack spacing={2}>
                                    <Stack direction="row" spacing={2} alignItems="flex-start">
                                        <ToggleButtonGroup
                                            value={scopeSelection}
                                            exclusive
                                            onChange={handleScopeChange}
                                            disabled={isLoading}
                                            sx={{ '& .MuiToggleButton-root': { borderRadius: 2 } }}
                                        >
                                            <ToggleButton value="department">Phòng ban</ToggleButton>
                                            <ToggleButton value="faculty">Khoa</ToggleButton>
                                        </ToggleButtonGroup>

                                        {scopeSelection && (
                                            <FormControl sx={{ flex: 1 }} required disabled={isLoading}>
                                                <InputLabel>
                                                    {scopeSelection === 'department' ? 'Chọn phòng ban' : 'Chọn khoa'}
                                                </InputLabel>
                                                <Select
                                                    value={scopeSelection === 'department' ? formData.department : formData.faculty}
                                                    label={scopeSelection === 'department' ? 'Chọn phòng ban' : 'Chọn khoa'}
                                                    onChange={handleScopeValueChange}
                                                >
                                                    <MenuItem value="">-- Chọn --</MenuItem>
                                                    {scopeSelection === 'department'
                                                        ? departmentOptions.map(d => <MenuItem key={d} value={d}>{d}</MenuItem>)
                                                        : facultyOptions.map(f => <MenuItem key={f} value={f}>{f}</MenuItem>)
                                                    }
                                                </Select>
                                            </FormControl>
                                        )}
                                    </Stack>
                                    <FormHelperText>Chọn Phòng Ban cho tài liệu chung, hoặc Khoa cho tài liệu chuyên môn.</FormHelperText>
                                </Stack>
                            ) : (
                                <Alert severity="info">
                                    Tài liệu này sẽ được gắn với Khoa {currentUser.faculty}. Bạn không có quyền thay đổi phạm vi.
                                </Alert>
                            )}
                        </Box>
                    )}

                {!isEditMode && (
                    <Box sx={{ p: 3, borderRadius: 2, border: '1px solid #e0e0e0' }}>
                        <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>Kiểu phân đoạn</Typography>
                        <Typography variant="body2" sx={{ mb: 3, color: 'text.secondary' }}>
                            Chọn cách trích xuất dữ liệu phù hợp với loại tài liệu.
                        </Typography>

                        <ToggleButtonGroup
                            exclusive
                            value={formData.is_appendix}
                            onChange={(e, v) => v && setFormData(prev => ({ ...prev, is_appendix: v }))}
                            sx={{
                                '& .MuiToggleButton-root': {
                                    borderRadius: 2,
                                    px: 3
                                }
                            }}
                        >
                            <ToggleButton value="NORMAL">Tài liệu thường</ToggleButton>
                            <ToggleButton value="APPENDIX">Phụ lục (bảng biểu)</ToggleButton>
                        </ToggleButtonGroup>
                    </Box>
                )}

                <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    startIcon={isLoading ? <CircularProgress size={20} /> : (isEditMode ? <SaveIcon /> : <AddCircleOutlineIcon />)}
                    disabled={isLoading}
                    sx={{ py: 1.5, borderRadius: 2, fontWeight: 700 }}
                >
                    {isLoading ? "Đang xử lý..." : (isEditMode ? "Lưu thay đổi" : "Tải lên tài liệu")}
                </Button>

            </Stack>
        </Box>
    </Modal>
);

};

export default DocumentFormModal;