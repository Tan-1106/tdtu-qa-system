import React, { useState, useEffect } from 'react';
import {
    Box, Button, Typography, Table, TableBody, TableCell, TableContainer,
    TableHead, TableRow, Paper, IconButton, Chip, TablePagination, CircularProgress, Alert,
    TextField, FormControl, Select, MenuItem, Grid, Stack, Popover, InputAdornment, OutlinedInput, Tooltip
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';
import StopCircleOutlinedIcon from '@mui/icons-material/StopCircleOutlined';
import SearchIcon from '@mui/icons-material/Search';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import CheckIcon from '@mui/icons-material/Check'; 
import KeyIcon from '@mui/icons-material/Key';
import APIKeyFormModal from './APIKeyFormModal';
import { getApiKeysList, toggleApiKeyUsage, deleteApiKey } from '../../api/modelApi';

const providerColor = {
    'OpenAI': 'primary',
    'Google': 'secondary',
};

const PROVIDER_OPTIONS = ['OpenAI', 'Google'];
const USAGE_STATUS_OPTIONS = [
    { value: 'true', label: 'Đang dùng' },
];

const extractError = (error) => {
    if (error.response?.data?.details) {
        return error.response.data.details;
    }
    return error.message || 'Lỗi không xác định.';
};

const ApiKeyViewCell = ({ apiKey }) => {
    const [anchorEl, setAnchorEl] = useState(null);
    const [copied, setCopied] = useState(false); 

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
        setCopied(false); 
    };

    const handleCopy = () => {
        navigator.clipboard.writeText(apiKey);
        setCopied(true); 
        
        setTimeout(() => {
            setCopied(false);
        }, 2000);
    };

    const open = Boolean(anchorEl);
    const id = open ? 'api-key-popover' : undefined;

    return (
        <TableCell>
            <Stack direction="row" spacing={1} alignItems="center">
                <Typography variant="body2" sx={{ fontFamily: 'monospace', color: 'text.secondary' }}>
                    ••••••••••••
                </Typography>
                <Tooltip title="Xem API Key">
                    <IconButton size="small" onClick={handleClick} color="primary">
                        <VisibilityIcon fontSize="small" />
                    </IconButton>
                </Tooltip>
            </Stack>

            <Popover
                id={id}
                open={open}
                anchorEl={anchorEl}
                onClose={handleClose}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
                transformOrigin={{ vertical: 'top', horizontal: 'left' }}
                PaperProps={{ sx: { p: 2, width: 320, boxShadow: 4, borderRadius: 2 } }}
            >
                <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <KeyIcon fontSize="small" color="primary" /> API Key
                </Typography>
                <OutlinedInput
                    fullWidth
                    size="small"
                    value={apiKey}
                    readOnly
                    sx={{ bgcolor: '#f8f9fa', fontFamily: 'monospace', fontSize: '0.8rem' }}
                    endAdornment={
                        <InputAdornment position="end">
                            <Tooltip title={copied ? "Đã sao chép!" : "Sao chép"}>
                                <IconButton onClick={handleCopy} edge="end" size="small" color={copied ? "success" : "default"}>
                                    {copied ? <CheckIcon fontSize="inherit" /> : <ContentCopyIcon fontSize="inherit" />}
                                </IconButton>
                            </Tooltip>
                        </InputAdornment>
                    }
                />
            </Popover>
        </TableCell>
    );
};

const ModelManagementPage = () => {
    const [apiKeys, setApiKeys] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingKey, setEditingKey] = useState(null);

    const [searchKeyword, setSearchKeyword] = useState('');
    const [filterProvider, setFilterProvider] = useState('');
    const [filterUsage, setFilterUsage] = useState('');

    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [totalKeys, setTotalKeys] = useState(0);

    const [isInitialLoading, setIsInitialLoading] = useState(true);
    const [isRefetching, setIsRefetching] = useState(false);

    const [error, setError] = useState(null);
    const [successMsg, setSuccessMsg] = useState(null);

    const fetchKeys = async (currentPage, limit, keyword, provider, isInitialLoad) => {
        if (isInitialLoad) setIsInitialLoading(true);
        else setIsRefetching(true);

        setError(null);
        setSuccessMsg(null);

        const params = {
            page: currentPage + 1,
            limit: limit,
            keyword: keyword || undefined,
            provider: provider || undefined,
        };

        Object.keys(params).forEach(key => params[key] === undefined && delete params[key]);

        try {
            const data = await getApiKeysList(params);
            const mappedKeys = data.api_keys.map(key => ({ ...key, id: key._id }));
            
            let filteredKeys = mappedKeys;
            if (filterUsage === 'true') {
                filteredKeys = mappedKeys.filter(key => key.is_using === true);
            }

            setApiKeys(filteredKeys);
            setTotalKeys(data.total);
        } catch (err) {
            console.error("Error fetching keys:", err);
            setError(extractError(err));
        } finally {
            setIsInitialLoading(false);
            setIsRefetching(false);
        }
    };

    const loadKeysWithFilters = (resetPage = true, isInitialLoad = false) => {
        const targetPage = resetPage ? 0 : page;
        fetchKeys(targetPage, rowsPerPage, searchKeyword, filterProvider, isInitialLoad);
        if (resetPage && page !== 0) setPage(0);
    };

    const handleSearchClick = () => {
        loadKeysWithFilters(true);
    };

    useEffect(() => {
        loadKeysWithFilters(true, true);
    }, []);

    useEffect(() => {
        if (!isInitialLoading) {
            loadKeysWithFilters(true);
        }
    }, [filterProvider, filterUsage, rowsPerPage]);

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
        fetchKeys(newPage, rowsPerPage, searchKeyword, filterProvider, false);
    };

    const handleChangeRowsPerPage = (event) => {
        const newRows = parseInt(event.target.value, 10);
        setRowsPerPage(newRows);
        setPage(0);
        fetchKeys(0, newRows, searchKeyword, filterProvider, false);
    };

    const handleAddKey = () => {
        setEditingKey(null);
        setIsModalOpen(true);
    };

    const handleEditKey = (key) => {
        setEditingKey(key);
        setIsModalOpen(true);
    };

    const handleSaveKey = () => {
        setIsModalOpen(false);
        setSuccessMsg('Thao tác thành công! Danh sách đang được cập nhật.');
        loadKeysWithFilters(true);
    };

    const handleToggleUsage = async (keyId, currentStatus) => {
        setError(null);
        setSuccessMsg(null);
        setIsRefetching(true);
        try {
            await toggleApiKeyUsage(keyId);
            setSuccessMsg(currentStatus ? 'Đã tắt sử dụng API Key.' : 'Đã kích hoạt API Key thành công.');
            loadKeysWithFilters(false);
        } catch (err) {
            console.error("Error toggling usage:", err);
            setError(extractError(err));
        } finally {
            setIsRefetching(false);
        }
    };

    const handleDeleteKey = async (keyId, keyName) => {
        if (!window.confirm(`Bạn có chắc chắn muốn xóa API Key: ${keyName} không?`)) {
            return;
        }
        setError(null);
        setSuccessMsg(null);
        setIsRefetching(true);
        try {
            await deleteApiKey(keyId);
            setSuccessMsg(`API Key "${keyName}" đã được xóa thành công.`);
            loadKeysWithFilters(true);
        } catch (err) {
            console.error("Error deleting key:", err);
            setError(extractError(err));
        } finally {
            setIsRefetching(false);
        }
    };

    if (isInitialLoading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
                <CircularProgress />
                <Typography sx={{ ml: 2 }}>Đang tải danh sách Model Keys...</Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ p: { xs: 1, md: 3 } }}>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main' }}>Quản lý Model và API Keys</Typography>
                <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={handleAddKey}
                    sx={{
                        borderRadius: 3,
                        fontWeight: 600,
                        background: 'linear-gradient(90deg, #2e7d32 60%, #66bb6a 100%)',
                        '&:hover': {
                            background: 'linear-gradient(90deg, #1b5e20 60%, #2e7d32 100%)'
                        }
                    }}
                >
                    Thêm API Key
                </Button>
            </Box>

            {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
            {successMsg && <Alert severity="success" sx={{ mb: 3 }}>{successMsg}</Alert>}

            <Paper elevation={1} sx={{ p: 2, mb: 3, borderRadius: 3, borderLeft: '5px solid #1976d2' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: 'primary.main', mb: -2 }}>Tìm kiếm & Lọc</Typography>
                <Grid container spacing={2} alignItems="flex-end">
                    <Grid item xs={12} sm={6} md={4}>
                        <Stack direction="row" spacing={1} alignItems="flex-end" sx={{ mt: 1 }}>
                            <TextField
                                fullWidth
                                label="Tên Key hoặc Mô tả"
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

                    <Grid item xs={12} sm={6} md={3}>
                        <Typography variant="caption" display="block" sx={{ color: 'text.secondary', mb: 0.5 }}>
                            Nhà cung cấp
                        </Typography>
                        <FormControl fullWidth size="small" variant="outlined">
                            <Select
                                value={filterProvider}
                                displayEmpty
                                onChange={(e) => setFilterProvider(e.target.value)}
                                renderValue={(selected) => (selected ? selected : <em>Tất cả</em>)}
                            >
                                <MenuItem value=""><em>Tất cả</em></MenuItem>
                                {PROVIDER_OPTIONS.map((provider) => (
                                    <MenuItem key={provider} value={provider}>{provider}</MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Grid>

                    <Grid item xs={12} sm={6} md={3}>
                        <Typography variant="caption" display="block" sx={{ color: 'text.secondary', mb: 0.5 }}>
                            Trạng thái sử dụng
                        </Typography>
                        <FormControl fullWidth size="small" variant="outlined">
                            <Select
                                value={filterUsage}
                                displayEmpty
                                onChange={(e) => setFilterUsage(e.target.value)}
                                renderValue={(selected) => (selected ? USAGE_STATUS_OPTIONS.find(s => s.value === selected)?.label : <em>Tất cả</em>)}
                            >
                                <MenuItem value=""><em>Tất cả</em></MenuItem>
                                {USAGE_STATUS_OPTIONS.map((status) => (
                                    <MenuItem key={status.value} value={status.value}>{status.label}</MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Grid>
                </Grid>
            </Paper>

            <APIKeyFormModal
                open={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSave={handleSaveKey}
                editingKey={editingKey}
            />

            <TableContainer
                component={Paper}
                sx={{
                    borderRadius: 4,
                    boxShadow: '0 4px 16px 0 rgba(0,0,0,0.06)',
                    position: 'relative',
                }}
            >
                {isRefetching && (
                    <Box
                        sx={{
                            position: 'absolute',
                            top: 0, left: 0, right: 0, bottom: 0,
                            bgcolor: 'rgba(255, 255, 255, 0.7)',
                            zIndex: 1000,
                            display: 'flex',
                            justifyContent: 'center',
                            alignItems: 'center',
                            borderRadius: 4,
                        }}
                    >
                        <CircularProgress size={40} />
                    </Box>
                )}
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell><b>Tên Khóa / Mô tả</b></TableCell>
                            <TableCell><b>API Key</b></TableCell>
                            <TableCell><b>Nhà cung cấp</b></TableCell>
                            <TableCell><b>Model</b></TableCell>
                            <TableCell><b>Trạng thái</b></TableCell>
                            <TableCell align="right"><b>Hành động</b></TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {apiKeys.map((key) => (
                            <TableRow key={key.id} hover>
                                <TableCell>
                                    <Typography fontWeight={600}>{key.name}</Typography>
                                    <Typography variant="caption" color="text.secondary">{key.description || 'Không mô tả'}</Typography>
                                </TableCell>
                                
                                <ApiKeyViewCell apiKey={key.api_key} />

                                <TableCell>
                                    <Chip
                                        label={key.provider}
                                        color={providerColor[key.provider]}
                                        sx={{ fontWeight: 600, borderRadius: 1 }}
                                    />
                                </TableCell>
                                <TableCell>
                                    <Chip
                                        label={key.using_model || 'Chưa chọn'}
                                        variant="outlined"
                                        size="small"
                                        color={key.is_using ? 'success' : 'default'}
                                        sx={{ fontWeight: 500, borderRadius: 1 }}
                                    />
                                </TableCell>
                                <TableCell>
                                    <Chip
                                        label={key.is_using ? 'Đang dùng' : 'Không dùng'}
                                        color={key.is_using ? 'success' : 'default'}
                                        variant={key.is_using ? 'filled' : 'outlined'}
                                        sx={{ fontWeight: 500, borderRadius: 1 }}
                                    />
                                </TableCell>
                                <TableCell align="right">
                                    <IconButton
                                        onClick={() => handleToggleUsage(key.id, key.is_using)}
                                        sx={{ color: key.is_using ? 'error.main' : 'success.main' }}
                                        title={key.is_using ? 'Tắt sử dụng Key' : 'Kích hoạt Key'}
                                        disabled={!key.using_model}
                                    >
                                        {key.is_using ? <StopCircleOutlinedIcon /> : <PlayCircleOutlineIcon />}
                                    </IconButton>

                                    <IconButton onClick={() => handleEditKey(key)} sx={{ color: 'primary.main' }} title="Chỉnh sửa Model/Thông tin">
                                        <EditIcon />
                                    </IconButton>

                                    <IconButton
                                        onClick={() => handleDeleteKey(key.id, key.name)}
                                        sx={{ color: 'text.secondary' }}
                                        title="Xóa Key"
                                    >
                                        <DeleteIcon />
                                    </IconButton>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>

            <TablePagination
                component="div"
                count={totalKeys}
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

export default ModelManagementPage;