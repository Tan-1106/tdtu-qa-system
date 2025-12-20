import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
    Box, Typography, Table, TableBody, TableCell, TableContainer,
    TableHead, TableRow, Paper, IconButton, Chip, TablePagination, 
    CircularProgress, Alert, TextField, FormControl, 
    Select, MenuItem, Grid, Stack, Button, InputLabel
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search'; 
import VisibilityIcon from '@mui/icons-material/Visibility';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance'; 
import SchoolIcon from '@mui/icons-material/School'; 
import MenuIcon from '@mui/icons-material/Menu'; 
import CloseIcon from '@mui/icons-material/Close'; 
import { useOutletContext } from 'react-router-dom'; 

import { 
    getGeneralDocuments, getDocTypes, getDocumentFileBlob, getAllDepartments, getFacultyDocuments
} from '../../api/documentApi'; 
import useUserAuth from '../../hooks/useUserAuth';
import ViewDocumentModal from '../admin/ViewDocumentModal'; 

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

const DocumentListPage = () => {
    const { user: currentUser } = useUserAuth(); 
    
    const context = useOutletContext();
    const { isSidebarOpen = true, toggleSidebar = () => {} } = context || {};
    
    const [documents, setDocuments] = useState([]);
    const [totalDocuments, setTotalDocuments] = useState(0);
    const [page, setPage] = useState(0); 
    const [rowsPerPage, setRowsPerPage] = useState(10);

    const [searchKeyword, setSearchKeyword] = useState(''); 
    const [filterDocType, setFilterDocType] = useState('');
    const [filterScope, setFilterScope] = useState('');
    const [sortOrder, setSortOrder] = useState('newest');
    
    const searchKeywordRef = useRef(''); 
    const filterDocTypeRef = useRef(''); 
    const filterScopeRef = useRef('');
    const sortOrderRef = useRef('');
    
    const [availableDocTypes, setAvailableDocTypes] = useState([]); 
    const [availableScopes, setAvailableScopes] = useState([]);
    
    const [isInitialLoading, setIsInitialLoading] = useState(true); 
    const [isRefetching, setIsRefetching] = useState(false); 
    const [error, setError] = useState(null);
    
    const [isViewModalOpen, setIsViewModalOpen] = useState(false);
    const [viewingDocument, setViewingDocument] = useState(null);
    const [viewDocumentUrl, setViewDocumentUrl] = useState(null);
    const [isViewLoading, setIsViewLoading] = useState(false); 


    // --- SETUP LOGIC ---
    useEffect(() => {
        searchKeywordRef.current = searchKeyword;
    }, [searchKeyword]);
    
    useEffect(() => {
        filterDocTypeRef.current = filterDocType;
    }, [filterDocType]);
    
    useEffect(() => {
        filterScopeRef.current = filterScope;
    }, [filterScope]);
    
    useEffect(() => {
        sortOrderRef.current = sortOrder;
    }, [sortOrder]);

    useEffect(() => {
        if (!isViewModalOpen && viewDocumentUrl) {
            URL.revokeObjectURL(viewDocumentUrl);
            setViewDocumentUrl(null);
            setViewingDocument(null); 
        }
    }, [isViewModalOpen, viewDocumentUrl]);

    
    const fetchFilterOptions = async () => {
        if (!currentUser) return;
        
        try {
            const docTypes = await getDocTypes();
            if (docTypes && Array.isArray(docTypes)) {
                setAvailableDocTypes(docTypes.filter(t => t.trim()));
            }
            
            const departments = await getAllDepartments();
            const scopeOptions = [];
            
            if (currentUser.department && currentUser.department.trim()) {
                scopeOptions.push({ 
                    label: currentUser.department, 
                    value: `FACULTY_${currentUser.department}` 
                });
            }
            
            if (departments && Array.isArray(departments)) {
                departments.filter(d => d && d.trim()).forEach(dept => {
                    scopeOptions.push({ label: dept, value: `DEPT_${dept}` });
                });
            }
            setAvailableScopes(scopeOptions);

        } catch (err) {
            console.error("Error fetching filter options:", err);
        }
    };
    
    // Hàm gọi API chính để tải tài liệu
    const fetchDocuments = useCallback(async (currentPage, limit, docType, keyword, scope, isInitialLoad) => {
        if (!currentUser) return;

        if (isInitialLoad) {
            setIsInitialLoading(true);
        } else {
            setIsRefetching(true);
        }
        setError(null);

        const baseParams = {
            page: currentPage + 1,
            limit: limit,
            doc_type: docType || undefined,
            keyword: keyword || undefined, 
        };
        try {
            let data = { documents: [], total: 0 }; 
            let currentDocuments = [];
            
            if (scope && scope.startsWith('FACULTY_')) {
                data = await getFacultyDocuments(baseParams);
            } 
            else {
                let deptParam = undefined;
                if (scope && scope.startsWith('DEPT_')) {
                    deptParam = scope.replace('DEPT_', '');
                }
                
                data = await getGeneralDocuments({ ...baseParams, department: deptParam });
                
                if (!scope) {
                    const facultyData = await getFacultyDocuments(baseParams);
                    currentDocuments = [...(data.documents || []), ...(facultyData.documents || [])];
                }
            }
            
            if (!scope) {
                currentDocuments = currentDocuments;
            } else {
                currentDocuments = data.documents || [];
            }
            
            let totalCount = currentDocuments.length;
            
            const currentSortOrder = sortOrderRef.current;
            
            if (currentSortOrder) {
                currentDocuments.sort((a, b) => {
                    const dateA = new Date(a.uploaded_at).getTime();
                    const dateB = new Date(b.uploaded_at).getTime();
                    
                    if (currentSortOrder === 'newest') {
                        return dateB - dateA;
                    } else if (currentSortOrder === 'oldest') {
                        return dateA - dateB;
                    }
                    return 0;
                });
            }
            
            const start = currentPage * rowsPerPage;
            const end = start + rowsPerPage;
            const paginatedDocuments = currentDocuments.slice(start, end);


            if (paginatedDocuments.length === 0 && !isInitialLoad) {
                setDocuments([]);
                setTotalDocuments(0);
                return;
            }

            setDocuments(paginatedDocuments.map(d => ({
                ...d,
                id: d._id || d.id, 
            })));
            setTotalDocuments(totalCount);
            
        } catch (err) {
            console.error("Error fetching documents:", err);
            setError(extractError(err, 'Lỗi khi tải danh sách tài liệu. Vui lòng thử lại sau.'));
        } finally {
            setIsInitialLoading(false);
            setIsRefetching(false);
        }
    }, [currentUser, rowsPerPage]);

    const loadDocumentsWithFilters = useCallback((resetPage = true, isInitialLoad = false, forcePageReset = false) => {
        const currentSearchKeyword = searchKeywordRef.current;
        const currentDocType = filterDocTypeRef.current;
        const currentScope = filterScopeRef.current;
        
        const targetPage = (resetPage || forcePageReset) ? 0 : page;
        
        fetchDocuments(
            targetPage, 
            rowsPerPage, 
            currentDocType, 
            currentSearchKeyword,
            currentScope,
            isInitialLoad
        );
        
        if (resetPage && page !== 0) {
            setPage(0);
        }
    }, [fetchDocuments, page, rowsPerPage]); 

    
    useEffect(() => {
        if (currentUser) {
            fetchFilterOptions().then(() => {
                loadDocumentsWithFilters(true, true, true); 
            });
        }
    }, [currentUser]); 

    
    useEffect(() => {
        if (!isInitialLoading && currentUser) {
            loadDocumentsWithFilters(true, false, true); 
        }
    }, [filterDocType, filterScope, sortOrder, rowsPerPage, currentUser]); 
    
    const handlePageChange = (event, newPage) => {
        setPage(newPage);
        fetchDocuments(newPage, rowsPerPage, filterDocTypeRef.current, searchKeywordRef.current, filterScopeRef.current, false);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0); 
    };
    
    const handleFilterChange = (filterSetter, value) => {
        filterSetter(value);
        setPage(0); 
    };
    
    const handleSearchClick = () => {
        setPage(0); 
        loadDocumentsWithFilters(true, false, true); 
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
            setError("Không thể tải tệp tài liệu. Vui lòng kiểm tra quyền truy cập hoặc thử lại.");
            
            setIsViewModalOpen(false); 
        } finally {
            setIsViewLoading(false); 
        }
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
        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
            <Box sx={{ 
                p: 2, 
                bgcolor: 'white', 
                display: { xs: 'none', md: 'flex' }, 
                alignItems: 'center', 
                gap: 1.5, 
                borderBottom: '1px solid #e3e3e3',
                position: 'sticky', 
                top: 0,
                zIndex: 10,
                flexShrink: 0 
            }}>
                <IconButton 
                    size="large" 
                    onClick={toggleSidebar} 
                    sx={{ color: 'text.primary' }}
                >
                    {isSidebarOpen ? <CloseIcon /> : <MenuIcon />}
                </IconButton>
                
                <Typography variant="h6" sx={{ fontWeight: 700, flexGrow: 1, color: 'primary.main' }}>
                    Tài liệu hệ thống
                </Typography>
            </Box>
            
            {/* Nội dung chính */}
            <Box sx={{ p: { xs: 1, md: 3 }, overflowY: 'auto', flexGrow: 1 }}>
                {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
            
                {/* --- PHẦN BỘ LỌC --- */}
                <Paper elevation={1} sx={{ p: 2, mb: 3, borderRadius: 3, borderLeft: '5px solid #1976d2' }}>
                    <Grid container spacing={2} alignItems="flex-end">
                        
                        {/* 1. Tìm kiếm theo Keyword */}
                        <Grid item xs={12} sm={6} md={4}>
                            <Stack direction="row" spacing={1} alignItems="flex-end" sx={{ mt: 1 }}>
                                <TextField
                                    fullWidth
                                    label="Tìm kiếm theo Tên Tài liệu"
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
                        
                        {/* 3. Lọc theo Phạm vi (Phòng ban/Khoa sinh viên) */}
                        <Grid item xs={12} sm={6} md={3}> 
                            <Typography variant="caption" display="block" sx={{ color: 'text.secondary', mb: 0.5 }}>
                                Phạm vi
                            </Typography>
                            <FormControl fullWidth size="small" variant="outlined">
                                <Select
                                    value={filterScope}
                                    displayEmpty
                                    onChange={(e) => handleFilterChange(setFilterScope, e.target.value)}
                                    renderValue={(selected) => {
                                        const selectedScope = availableScopes.find(s => s.value === selected);
                                        return selectedScope ? selectedScope.label : <em>Tất cả</em>;
                                    }} 
                                >
                                    <MenuItem value=""><em>Tất cả</em></MenuItem>
                                    {availableScopes.map((scope) => (
                                        <MenuItem key={scope.value} value={scope.value}>
                                            {scope.label}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        </Grid>

                        {/* 💡 4. Sắp xếp theo Ngày tải lên */}
                        <Grid item xs={12} sm={6} md={3}>
                            <Typography variant="caption" display="block" sx={{ color: 'text.secondary', mb: 0.5 }}>
                                Ngày tải
                            </Typography>
                            <FormControl fullWidth size="small" variant="outlined">
                                <Select
                                    value={sortOrder}
                                    displayEmpty
                                    onChange={(e) => handleFilterChange(setSortOrder, e.target.value)}
                                    renderValue={(selected) => (selected ? 
                                        (selected === 'newest' ? 'Mới nhất' : 'Cũ nhất') 
                                        : <em>Mới nhất</em>)}
                                >
                                    <MenuItem value="newest">Mới nhất đến cũ nhất</MenuItem>
                                    <MenuItem value="oldest">Cũ nhất đến mới nhất</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                        
                    </Grid>
                </Paper>
                
                {/* --- MODALS --- */}
                <ViewDocumentModal
                    open={isViewModalOpen}
                    onClose={() => setIsViewModalOpen(false)}
                    document={viewingDocument}
                    viewDocumentUrl={viewDocumentUrl}
                    isViewLoading={isViewLoading}
                />

                {/* --- TABLE --- */}
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
                    onPageChange={handlePageChange}
                    rowsPerPage={rowsPerPage}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                    rowsPerPageOptions={[10, 25, 50]}
                    labelRowsPerPage="Số hàng mỗi trang:"
                    labelDisplayedRows={({ from, to, count }) =>
                        `${from}-${to} trên ${count}`
                    }
                />
            
            </Box>
        </Box>
    );
};

export default DocumentListPage;