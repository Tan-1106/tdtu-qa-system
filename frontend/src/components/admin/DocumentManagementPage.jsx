import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
    Box, Button, Typography, Table, TableBody, TableCell, TableContainer,
    TableHead, TableRow, Paper, IconButton, Chip, TablePagination, 
    CircularProgress, Alert, TextField, FormControl, InputLabel, 
    Select, MenuItem, Grid, Stack 
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import SearchIcon from '@mui/icons-material/Search'; 
import VisibilityIcon from '@mui/icons-material/Visibility';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance'; 
import SchoolIcon from '@mui/icons-material/School'; 
import ArticleIcon from '@mui/icons-material/Article'; 

import DocumentFormModal from './DocumentFormModal'; 
import ViewDocumentModal from './ViewDocumentModal'; 

import { 
    getGeneralDocuments, getFacultyDocuments, deleteDocument, 
    getFaculties, getAllDepartments, getDocTypes, getDocumentFileBlob
} from '../../api/documentApi'; 
import useUserAuth from '../../hooks/useUserAuth';


const docTypeColor = {
    'Quy chế': 'primary',
    'Quy định': 'secondary',
    'Hướng dẫn': 'info',
    'Văn bản khác': 'default', 
    'Bộ tiêu chí': 'warning', 
    'Thông báo': 'success',
};

const getDocTypeColor = (docType) => {
    return docTypeColor[docType] || 'default'; 
};

const extractError = (error, defaultMessage = 'Lỗi không xác định.') => {
    return error.response?.data?.details || error.message || defaultMessage;
};

// --- MAIN COMPONENT ---
const DocumentManagementPage = () => {
    const { user: currentUser } = useUserAuth(); 
    const isAdmin = currentUser?.role === 'Admin';
    const isFacultyManager = currentUser?.is_faculty_manager;
    
    // State dữ liệu và phân trang
    const [documents, setDocuments] = useState([]);
    const [totalDocuments, setTotalDocuments] = useState(0);
    const [page, setPage] = useState(0); 
    const [rowsPerPage, setRowsPerPage] = useState(10);

    // State BỘ LỌC (Chỉ dùng để RENDER UI)
    const [searchKeyword, setSearchKeyword] = useState(''); 
    const [filterDocType, setFilterDocType] = useState('');
    const [filterFaculty, setFilterFaculty] = useState('');
    
    // REF LƯU TRỮ GIÁ TRỊ LỌC HIỆN TẠI 
    const searchKeywordRef = useRef(''); 
    const filterDocTypeRef = useRef(''); 
    const filterFacultyRef = useRef(''); 
    
    // State tùy chọn filter
    const [availableFaculties, setAvailableFaculties] = useState([]);
    const [availableDepartments, setAvailableDepartments] = useState([]); 
    const [availableDocTypes, setAvailableDocTypes] = useState([]); 
    
    // State loading & error
    const [isInitialLoading, setIsInitialLoading] = useState(true); 
    const [isRefetching, setIsRefetching] = useState(false); 
    const [error, setError] = useState(null);
    const [successMsg, setSuccessMsg] = useState(null);

    // State Modal
    const [isFormModalOpen, setIsFormModalOpen] = useState(false);
    const [isViewModalOpen, setIsViewModalOpen] = useState(false);
    const [editingDocument, setEditingDocument] = useState(null);
    const [viewingDocument, setViewingDocument] = useState(null);
    const [viewDocumentUrl, setViewDocumentUrl] = useState(null);
    const [isViewLoading, setIsViewLoading] = useState(false); 


    // --- FETCH DATA LOGIC ---

    // Cập nhật Ref mỗi khi State tương ứng thay đổi
    useEffect(() => {
        searchKeywordRef.current = searchKeyword;
    }, [searchKeyword]);
    
    useEffect(() => {
        filterDocTypeRef.current = filterDocType;
    }, [filterDocType]);
    
    useEffect(() => {
        filterFacultyRef.current = filterFaculty;
    }, [filterFaculty]);

    // Cleanup Object URL khi đóng Modal
    useEffect(() => {
        if (!isViewModalOpen && viewDocumentUrl) {
            URL.revokeObjectURL(viewDocumentUrl);
            setViewDocumentUrl(null);
            setViewingDocument(null); 
        }
    }, [isViewModalOpen, viewDocumentUrl]);


    // Lấy danh sách Khoa và Phòng Ban
    const fetchFilterOptions = async () => {
        try {
            const faculties = await getFaculties();
            setAvailableFaculties(faculties);
            
            const responseDepartments = await getAllDepartments();
            if (responseDepartments && Array.isArray(responseDepartments)) {
                const sortedDepartments = responseDepartments.map(d => d.trim()).sort(); 
                const uniqueDepartments = [...new Set(sortedDepartments)];
                setAvailableDepartments(uniqueDepartments.filter(d => d));
            } else {
                setAvailableDepartments([]);
            }

            const docTypes = await getDocTypes();
            if (docTypes && Array.isArray(docTypes)) {
                const uniqueDocTypes = [...new Set(docTypes.map(t => t.trim()))];
                setAvailableDocTypes(uniqueDocTypes.filter(t => t));
            } else {
                setAvailableDocTypes([]);
            }

        } catch (err) {
            console.error("Error fetching filter options:", err);
        }
    };
    
    // Hàm gọi API chính để tải tài liệu
    const fetchDocuments = useCallback(async (currentPage, limit, docType, faculty, department, keyword, isInitialLoad) => {
        if (!currentUser) return;

        if (isInitialLoad) {
            setIsInitialLoading(true);
        } else {
            setIsRefetching(true);
        }
        setError(null);

        const params = {
            page: currentPage + 1,
            limit: limit,
            doc_type: docType || undefined,
            keyword: keyword || undefined, 
            department: department || undefined, 
        };
        
        try {
            let data;
            
            if (isAdmin) {
                if (faculty === 'GENERAL' || department) { 
                    data = await getGeneralDocuments({ ...params }); 
                } else if (faculty) { 
                     data = await getFacultyDocuments({ ...params, faculty });
                } else { 
                    data = await getGeneralDocuments({ ...params }); 
                }

            } else if (isFacultyManager) {
                data = await getFacultyDocuments({ ...params }); 
            } else {
                return; 
            }

            if (!data || !data.documents) {
                setDocuments([]);
                setTotalDocuments(0);
                return;
            }

            setDocuments(data.documents.map(d => ({
                ...d,
                id: d._id || d.id, 
            })));
            setTotalDocuments(data.total);
            setSuccessMsg(null); 
            
        } catch (err) {
            console.error("Error fetching documents:", err);
            setError(extractError(err, 'Lỗi khi tải danh sách tài liệu.'));
        } finally {
            setIsInitialLoading(false);
            setIsRefetching(false);
        }
    }, [currentUser, isAdmin, isFacultyManager]); 


    // Hàm điều phối việc tải dữ liệu với bộ lọc (Dùng Ref để lấy giá trị lọc)
    const loadDocumentsWithFilters = useCallback((resetPage = true, isInitialLoad = false, forcePageReset = false) => {
        const currentSearchKeyword = searchKeywordRef.current;
        const currentDocType = filterDocTypeRef.current;
        const currentScope = filterFacultyRef.current;
        
        const targetPage = (resetPage || forcePageReset) ? 0 : page;
        
        let currentFacultyFilter = undefined;
        let currentDepartmentFilter = undefined;
        
        if (isAdmin && currentScope && currentScope !== 'GENERAL') {
            if (availableFaculties.includes(currentScope)) {
                currentFacultyFilter = currentScope;
            } 
            else if (availableDepartments.includes(currentScope)) {
                currentDepartmentFilter = currentScope;
            }
        }
        
        fetchDocuments(
            targetPage, 
            rowsPerPage, 
            currentDocType, 
            currentFacultyFilter,      
            currentDepartmentFilter,   
            currentSearchKeyword,
            isInitialLoad
        );
        
        if (resetPage && page !== 0) {
            setPage(0);
        }
    }, [fetchDocuments, page, rowsPerPage, isAdmin, availableFaculties, availableDepartments]); 

    
    // Initial Load: Gọi fetchFilterOptions LẦN ĐẦU, sau đó gọi loadDocuments
    useEffect(() => {
        if (currentUser) {
            fetchFilterOptions().then(() => {
                loadDocumentsWithFilters(true, true, true); 
            });
        }
    }, [currentUser]); 

    
    // Handle Filter Changes: Kích hoạt tải lại khi filter DocType hoặc Faculty thay đổi
    useEffect(() => {
        if (!isInitialLoading && currentUser) {
            loadDocumentsWithFilters(true, false, true); 
        }
    }, [filterDocType, filterFaculty, rowsPerPage, currentUser]); 

    
    // Handle Pagination Changes: Chỉ thay đổi trang
    useEffect(() => {
        if (!isInitialLoading && currentUser && page !== 0) {
            loadDocumentsWithFilters(false, false, false);
        }
    }, [page]); 

    
    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0); 
    };
    
    // Handle Filter Changes: Cập nhật state UI
    const handleFilterChange = (filterSetter, value) => {
        filterSetter(value);
        setPage(0); 
    };
    
    // Handle Search Click
    const handleSearchClick = () => {
        setPage(0); 
        loadDocumentsWithFilters(true, false, true); 
    };
    
    // --- ACTIONS ---
    const handleAddDocument = () => {
        setEditingDocument(null);
        setIsFormModalOpen(true);
    };

    const handleEditDocument = (doc) => {
        if (isFacultyManager && doc.faculty !== currentUser.faculty) {
            setError('Bạn chỉ có quyền chỉnh sửa tài liệu của Khoa mình.');
            return;
        }
        setEditingDocument(doc);
        setIsFormModalOpen(true);
    };

    const handleDeleteDocument = async (doc) => {
        if (!window.confirm(`Bạn có chắc chắn muốn xóa tài liệu "${doc.file_name}" không? Thao tác này sẽ xóa vĩnh viễn cả file, chunks và embeddings.`)) {
            return;
        }
        setError(null);
        setIsRefetching(true);
        try {
            await deleteDocument(doc.id);
            setSuccessMsg(`Tài liệu "${doc.file_name}" đã được xóa thành công.`);
            loadDocumentsWithFilters(true); 
        } catch (err) {
            console.error("Error deleting document:", err);
            setError(extractError(err, 'Xóa tài liệu thất bại.'));
            setIsRefetching(false);
        }
    };
    
    const handleViewDocument = async (doc) => {
        setError(null);
        setIsViewLoading(true); 
        setViewDocumentUrl(null); 

        try {
            setViewingDocument(doc);
            setIsViewModalOpen(true); 
            
            const pdfBlob = await getDocumentFileBlob(doc.id);
            
            const url = URL.createObjectURL(pdfBlob); 
            
            setViewDocumentUrl(url); 
        } catch (err) {
            console.error("Error fetching document file:", err);
            setError("Không thể tải tệp tài liệu. Vui lòng kiểm tra quyền truy cập.");
            
            setIsViewModalOpen(false); 
        } finally {
            setIsViewLoading(false); 
        }
    };
    
    const handleSaveDocument = () => {
        setIsFormModalOpen(false);
        setSuccessMsg(editingDocument ? 'Thông tin tài liệu đã được cập nhật.' : 'Tài liệu mới đã được thêm thành công và đang được xử lý (chunking, embedding).');
        loadDocumentsWithFilters(true); 
    };

    if (isInitialLoading) { 
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
                <CircularProgress />
                <Typography sx={{ ml: 2 }}>Đang tải dữ liệu tài liệu...</Typography>
            </Box>
        );
    }
    
    const getScopeLabel = (doc) => {
        if (doc.department) return { label: doc.department, icon: <AccountBalanceIcon fontSize="small" color="primary" />, type: 'Phòng Ban' };
        if (doc.faculty) return { label: doc.faculty, icon: <SchoolIcon fontSize="small" color="secondary" />, type: 'Khoa' };
        return { label: 'Chung/N/A', icon: null, type: 'Chung' };
    };

    return (
        <Box sx={{ p: { xs: 1, md: 3 } }}>
            {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
            {successMsg && <Alert severity="success" sx={{ mb: 3 }}>{successMsg}</Alert>}
        
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main' }}>
                    Quản lý Tài liệu Hệ thống
                </Typography>
                {(isAdmin || isFacultyManager) && (
                    <Button
                        variant="contained"
                        startIcon={<AddIcon />}
                        onClick={handleAddDocument}
                        sx={{ borderRadius: 3, fontWeight: 600 }}
                    >
                        Thêm Tài liệu
                    </Button>
                )}
            </Box>
            
            {/* --- PHẦN BỘ LỌC --- */}
            <Paper elevation={1} sx={{ p: 2, mb: 3, borderRadius: 3, borderLeft: '5px solid #1976d2' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: 'primary.main', mb: -2 }}>Tìm kiếm & Lọc</Typography>
                <Grid container spacing={2} alignItems="flex-end">
                    
                    {/* 1. Tìm kiếm theo Keyword */}
                    <Grid item xs={12} sm={6} md={3.5}>
                        <Stack direction="row" spacing={1} alignItems="flex-end" sx={{ mt: 1 }}>
                            <TextField
                                fullWidth
                                label="Tên Tài liệu"
                                variant="outlined"
                                value={searchKeyword} 
                                onChange={(e) => setSearchKeyword(e.target.value)} 
                                size="small"
                                onKeyDown={(e) => e.key === 'Enter' && handleSearchClick()} 
                            />
                            <Button
                                variant="contained"
                                onClick={handleSearchClick}
                                size="small"
                                sx={{ minWidth: '40px', height: '40px', borderRadius: '8px' }}
                            >
                                <SearchIcon />
                            </Button>
                        </Stack>
                    </Grid>

                    {/* 2. Lọc theo Loại tài liệu */}
                    <Grid item xs={12} sm={6} md={3}> 
                        <Typography variant="caption" display="block" sx={{ color: 'text.secondary', mb: 0.5 }}>
                            Loại tài liệu
                        </Typography>
                        <FormControl fullWidth size="small" variant="outlined">
                            <Select
                                value={filterDocType}
                                displayEmpty
                                onChange={(e) => handleFilterChange(setFilterDocType, e.target.value)}
                                renderValue={(selected) => (selected ? selected : <em>Tất cả</em>)} 
                            >
                                <MenuItem value=""><em>Tất cả</em></MenuItem>
                                {availableDocTypes.map((type) => (
                                    <MenuItem key={type} value={type}>{type}</MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Grid>
                    
                    {/* 3. Lọc theo Khoa/Phòng Ban (Chỉ Admin) */}
                    {isAdmin && (
                        <Grid item xs={12} sm={6} md={3}>
                            <Typography variant="caption" display="block" sx={{ color: 'text.secondary', mb: 0.5 }}>
                                Khoa/Phòng Ban
                            </Typography>
                            <FormControl fullWidth size="small" variant="outlined">
                                <Select
                                    value={filterFaculty}
                                    displayEmpty
                                    onChange={(e) => handleFilterChange(setFilterFaculty, e.target.value)}
                                    renderValue={(selected) => (selected ? selected : <em>Tất cả</em>)} 
                                >
                                    <MenuItem value=""><em>Tất cả</em></MenuItem>
                                     <MenuItem value="Tài liệu chung">Tài liệu chung</MenuItem>
                                    {availableDepartments.length > 0 && <MenuItem disabled>--- Phòng Ban ---</MenuItem>}
                                    {availableDepartments.map((dept) => (
                                        <MenuItem key={dept} value={dept}>{dept}</MenuItem>
                                    ))}
                                    {availableFaculties.length > 0 && <MenuItem disabled>--- Khoa ---</MenuItem>}
                                    {availableFaculties.map((faculty) => (
                                        <MenuItem key={faculty} value={faculty}>{faculty}</MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        </Grid>
                    )}
                    
                </Grid>
            </Paper>
            
            {/* --- MODALS --- */}
            {(isAdmin || isFacultyManager) && (
                <DocumentFormModal
                    open={isFormModalOpen}
                    onClose={() => setIsFormModalOpen(false)}
                    onSave={handleSaveDocument}
                    editingDocument={editingDocument}
                    availableFaculties={availableFaculties}
                    documentTypes={availableDocTypes} 
                />
            )}
            
            <ViewDocumentModal
                open={isViewModalOpen}
                onClose={() => setIsViewModalOpen(false)}
                document={viewingDocument}
                viewDocumentUrl={viewDocumentUrl}
            />


            <TableContainer 
                component={Paper} 
                sx={{ 
                    borderRadius: 4, 
                    boxShadow: '0 4px 16px 0 rgba(25,118,210,0.06)',
                    position: 'relative', 
                }}
            >
                {isRefetching && (
                    <Box sx={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, bgcolor: 'rgba(255, 255, 255, 0.7)', zIndex: 1000, display: 'flex', justifyContent: 'center', alignItems: 'center', borderRadius: 4 }}>
                        <CircularProgress size={40} />
                    </Box>
                )}
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell><b>Tên Tài liệu</b></TableCell>
                            <TableCell><b>Phạm vi</b></TableCell>
                            <TableCell><b>Loại</b></TableCell>
                            <TableCell><b>Ngày tải lên</b></TableCell>
                            <TableCell align="right"><b>Hành động</b></TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {documents.map((doc) => {
                            const scope = getScopeLabel(doc);
                            return (
                                <TableRow key={doc.id} hover>
                                    <TableCell>
                                        <Typography fontWeight={600} noWrap sx={{ maxWidth: 300 }}>{doc.file_name}</Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            {doc.file_url ? <a href={doc.file_url} target="_blank" rel="noopener noreferrer">Xem link gốc</a> : 'N/A'}
                                        </Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Stack direction="row" spacing={0.5} alignItems="center">
                                            {scope.icon}
                                            <Chip
                                                label={scope.label}
                                                size="small"
                                                variant="outlined"
                                                sx={{ fontWeight: 500, borderRadius: 1 }} 
                                            />
                                        </Stack>
                                    </TableCell>
                                    <TableCell>
                                        <Chip
                                            label={doc.doc_type || 'N/A'}
                                            color={getDocTypeColor(doc.doc_type)} 
                                            size="small"
                                            sx={{ fontWeight: 600, borderRadius: 1 }} 
                                        />
                                    </TableCell>
                                    <TableCell>
                                        {new Date(doc.uploaded_at).toLocaleDateString('vi-VN')}
                                    </TableCell>
                                    <TableCell align="right">
                                        <IconButton onClick={() => handleViewDocument(doc)} sx={{ color: 'success.main' }} title="Xem File PDF">
                                            <VisibilityIcon />
                                        </IconButton>
                                        <IconButton onClick={() => handleEditDocument(doc)} sx={{ color: 'primary.main' }} title="Chỉnh sửa thông tin">
                                            <EditIcon />
                                        </IconButton>
                                        <IconButton 
                                            onClick={() => handleDeleteDocument(doc)} 
                                            sx={{ color: 'error.main' }} 
                                            title="Xóa Tài liệu"
                                            disabled={isFacultyManager && doc.faculty !== currentUser.faculty}
                                        >
                                            <DeleteIcon />
                                        </IconButton>
                                    </TableCell>
                                </TableRow>
                            );
                        })}
                        {documents.length === 0 && !isInitialLoading && ( 
                            <TableRow>
                                <TableCell colSpan={5} align="center" sx={{ color: 'text.secondary', py: 4 }}>
                                    Không có tài liệu nào phù hợp với điều kiện lọc.
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
            
            <TablePagination
                component="div"
                count={totalDocuments}
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
            
        </Box>
    );
};

export default DocumentManagementPage;