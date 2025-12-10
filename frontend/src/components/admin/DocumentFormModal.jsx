// src/pages/Admin/DocumentFormModal.jsx
import React, { useState, useEffect } from 'react';
import { 
    Modal, Box, Typography, TextField, Button, Select, MenuItem, 
    FormControl, InputLabel, CircularProgress, Alert, Stack, Grid, 
    FormControlLabel, Checkbox
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import { uploadDocument, updateDocument } from '../../api/documentApi'; 

const style = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: { xs: '90%', sm: 600 },
    bgcolor: 'background.paper',
    boxShadow: 24,
    p: 4,
    borderRadius: 2,
};

const extractError = (error, defaultMessage = 'Lưu thất bại.') => {
    return error.response?.data?.details || error.message || defaultMessage;
};

const DocumentFormModal = ({ open, onClose, onSave, editingDocument, availableFaculties, documentTypes }) => {
    const isEditMode = !!editingDocument;
    
    // State Form
    const [fileName, setFileName] = useState('');
    const [docType, setDocType] = useState('');
    const [fileUrl, setFileUrl] = useState('');
    const [department, setDepartment] = useState(''); // Chỉ dùng Admin
    const [faculty, setFaculty] = useState(''); // Chỉ dùng Admin
    const [file, setFile] = useState(null); // Chỉ dùng cho Upload
    const [isAppendix, setIsAppendix] = useState(false); // Chỉ dùng cho Upload
    
    // State Loading/Error
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (open) {
            setError(null);
            if (isEditMode) {
                setFileName(editingDocument.file_name || '');
                setDocType(editingDocument.doc_type || '');
                setFileUrl(editingDocument.file_url || '');
                setDepartment(editingDocument.department || '');
                setFaculty(editingDocument.faculty || '');
                setFile(null); // Không thể sửa file trong Edit Mode
                setIsAppendix(false); // Không áp dụng cho Edit
            } else {
                setFileName(''); setDocType(''); setFileUrl('');
                setDepartment(''); setFaculty(''); setFile(null);
                setIsAppendix(false);
            }
        }
    }, [open, isEditMode, editingDocument]);
    
    const isFacultyDocument = faculty && faculty !== '';
    const isGeneralDocument = department && department !== '';
    
    const handleSave = async () => {
        setError(null);
        setIsLoading(true);

        try {
            if (isEditMode) {
                // --- CHỈNH SỬA THÔNG TIN ---
                const updateData = {
                    file_name: fileName,
                    doc_type: docType,
                    file_url: fileUrl,
                    department: isFacultyDocument ? null : department,
                    faculty: isGeneralDocument ? null : faculty,
                };
                
                // Loại bỏ các giá trị rỗng/null để tránh ghi đè không cần thiết (trừ department/faculty)
                Object.keys(updateData).forEach(key => (updateData[key] === '' || updateData[key] === null) && delete updateData[key]);
                
                await updateDocument(editingDocument.id, updateData);
                
            } else {
                // --- THÊM MỚI (UPLOAD) ---
                if (!file || !docType || !fileUrl) {
                    throw new Error("Vui lòng cung cấp File, Loại tài liệu và URL gốc.");
                }
                
                if (department && faculty) {
                    throw new Error("Chỉ chọn một trong hai: Khoa hoặc Phòng Ban.");
                }
                
                const formData = new FormData();
                formData.append('file', file);
                formData.append('doc_type', docType);
                formData.append('file_url', fileUrl);
                
                if (department) {
                    formData.append('department', department);
                }
                if (faculty) {
                    formData.append('faculty', faculty);
                }

                await uploadDocument(formData, isAppendix);
            }

            onSave(); 
        } catch (err) {
            console.error(err);
            setError(extractError(err));
        } finally {
            setIsLoading(false);
        }
    };
    
    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            if (selectedFile.type !== 'application/pdf') {
                setError('Chỉ chấp nhận file PDF.');
                setFile(null);
                return;
            }
            if (!isEditMode) setFileName(selectedFile.name.replace(/\.pdf$/i, ''));
            setFile(selectedFile);
            setError(null);
        }
    };
    
    // Admin có thể chọn Phạm vi, Faculty Manager không được.
    const isScopeSelectDisabled = !editingDocument && !availableFaculties.length;
    
    return (
        <Modal open={open} onClose={onClose}>
            <Box sx={style}>
                <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
                    {isEditMode ? "Chỉnh sửa Tài liệu" : "Tải lên Tài liệu mới"}
                </Typography>
                
                {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
                
                <Stack spacing={2}>
                    {/* Tên tài liệu */}
                    <TextField fullWidth label="Tên tài liệu (File Name)" value={fileName} onChange={(e) => setFileName(e.target.value)} disabled={isLoading || (!isEditMode && !file)} helperText={isEditMode ? "Tên file sẽ được cập nhật" : "Tên file sẽ được lấy từ file PDF"}/>
                    
                    {/* Link URL Gốc */}
                    <TextField fullWidth label="URL Gốc (Link xem tài liệu)" value={fileUrl} onChange={(e) => setFileUrl(e.target.value)} disabled={isLoading} required type="url" placeholder="https://tdtu.edu.vn/..."/>
                    
                    <Grid container spacing={2}>
                        {/* Loại tài liệu */}
                        <Grid item xs={12} sm={isEditMode || !availableFaculties.length ? 12 : 6}>
                            <FormControl fullWidth disabled={isLoading} required>
                                <InputLabel>Loại tài liệu</InputLabel>
                                <Select value={docType} label="Loại tài liệu" onChange={(e) => setDocType(e.target.value)}>
                                    {documentTypes.map(type => (<MenuItem key={type} value={type}>{type}</MenuItem>))}
                                </Select>
                            </FormControl>
                        </Grid>
                        
                        {/* Chỉ hiện cho Admin khi không phải Edit Mode */}
                        {!isEditMode && availableFaculties.length > 0 && (
                            <Grid item xs={12} sm={6}>
                                <FormControl fullWidth disabled={isLoading || isScopeSelectDisabled}>
                                    <InputLabel>Phạm vi (Khoa/Phòng Ban)</InputLabel>
                                    <Select 
                                        value={isFacultyDocument ? faculty : isGeneralDocument ? department : ''} 
                                        label="Phạm vi" 
                                        onChange={(e) => {
                                            const val = e.target.value;
                                            if (val === 'GENERAL') {
                                                setDepartment('Chung'); setFaculty('');
                                            } else if (availableFaculties.includes(val)) {
                                                setFaculty(val); setDepartment('');
                                            } else {
                                                setDepartment(''); setFaculty('');
                                            }
                                        }}
                                        renderValue={(selected) => {
                                            if (selected === 'Chung') return 'Tài liệu Chung';
                                            if (selected) return selected;
                                            return <em>Tất cả</em>;
                                        }}
                                    >
                                        <MenuItem value=""><em>Không chọn (Mặc định: Khoa người tải)</em></MenuItem>
                                        <MenuItem value="GENERAL">Tài liệu Chung (Phòng Ban)</MenuItem>
                                        {availableFaculties.map(f => (<MenuItem key={f} value={f}>{f} (Khoa)</MenuItem>))}
                                    </Select>
                                </FormControl>
                            </Grid>
                        )}
                    </Grid>

                    {/* File Upload (Chỉ hiện khi Thêm mới) */}
                    {!isEditMode && (
                        <>
                            <Button 
                                variant="outlined"
                                component="label"
                                startIcon={<UploadFileIcon />}
                                disabled={isLoading}
                                sx={{ justifyContent: 'flex-start', borderStyle: file ? 'dashed' : 'solid' }}
                            >
                                {file ? `Đã chọn: ${file.name}` : "Chọn File PDF"}
                                <input type="file" hidden accept=".pdf" onChange={handleFileChange} />
                            </Button>
                            <FormControlLabel
                                control={<Checkbox checked={isAppendix} onChange={(e) => setIsAppendix(e.target.checked)} disabled={isLoading} />}
                                label="Đây là tài liệu dạng Phụ lục (có nhiều bảng biểu)"
                            />
                            {isAppendix && (
                                <Alert severity="info" sx={{ mt: 1 }}>
                                    Tài liệu Phụ lục phải là **PDF dạng Text** (không phải ảnh scan) để trích xuất bảng biểu.
                                </Alert>
                            )}
                        </>
                    )}
                </Stack>
                
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1, mt: 4 }}>
                    <Button onClick={onClose} variant="outlined" disabled={isLoading}>Hủy</Button>
                    <Button 
                        onClick={handleSave} 
                        variant="contained" 
                        disabled={isLoading || !docType || !fileUrl || (!isEditMode && !file)}
                    >
                        {isLoading ? <CircularProgress size={24} color="inherit" /> : (isEditMode ? 'Lưu Thông tin' : 'Tải lên & Xử lý')}
                    </Button>
                </Box>
            </Box>
        </Modal>
    );
};

export default DocumentFormModal;