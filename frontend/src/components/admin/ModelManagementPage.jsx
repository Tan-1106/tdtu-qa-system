import React, { useState, useEffect } from 'react';
import {
  Box, Button, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, IconButton, Chip, TablePagination, CircularProgress, Alert,
  // 💡 Thêm components cho Filter
  TextField, FormControl, InputLabel, Select, MenuItem, Grid, Stack
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';
import StopCircleOutlinedIcon from '@mui/icons-material/StopCircleOutlined';
import SearchIcon from '@mui/icons-material/Search';
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
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);


  const fetchKeys = async (currentPage, limit, keyword, provider, isUsing) => {
    setIsLoading(true);
    setError(null);
    setSuccessMsg(null);
    
    const params = {
        page: currentPage + 1,
        limit: limit,
        name: keyword || undefined,
        description: keyword || undefined, 
        provider: provider || undefined,
        is_using: isUsing === 'true' ? true : undefined
    };
    
    Object.keys(params).forEach(key => params[key] === undefined && delete params[key]);
    
    try {
      const data = await getApiKeysList(params); 
      
      setApiKeys(data.api_keys.map(key => ({
          ...key,
          id: key._id, 
      })));
      setTotalKeys(data.total);
    } catch (err) {
      console.error("Error fetching keys:", err);
      setError(err.message || 'Không thể tải danh sách API Keys.');
    } finally {
      setIsLoading(false);
    }
  };

  const loadKeysWithFilters = (resetPage = true) => {
      const targetPage = resetPage ? 0 : page;
      
      fetchKeys(
          targetPage, 
          rowsPerPage, 
          searchKeyword, 
          filterProvider, 
          filterUsage
      );
      
      if (resetPage && page !== 0) {
          setPage(0);
      }
  };

  const handleSearchClick = () => {
      loadKeysWithFilters(true); 
  };

  useEffect(() => {
    loadKeysWithFilters(true); 
  }, [rowsPerPage]); 

  useEffect(() => {
    loadKeysWithFilters(true); 
  }, [filterProvider, filterUsage]);
  
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0); 
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
    try {
        await toggleApiKeyUsage(keyId);
        setSuccessMsg(currentStatus ? 'Đã tắt sử dụng API Key.' : 'Đã kích hoạt API Key thành công.');
        loadKeysWithFilters(false); 
    } catch (err) {
        setError(err.message || "Thao tác Bật/Tắt thất bại.");
    }
  };

  const handleDeleteKey = async (keyId, keyName) => {
    if (!window.confirm(`Bạn có chắc chắn muốn xóa API Key: ${keyName} không?`)) {
        return;
    }
    setError(null);
    setSuccessMsg(null);
    try {
        await deleteApiKey(keyId);
        setSuccessMsg(`API Key "${keyName}" đã được xóa thành công.`);
        loadKeysWithFilters(true); 
    } catch (err) {
        setError(err.message || "Thao tác Xóa thất bại.");
    }
  };
    
  if (isLoading) {
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
            background: 'linear-gradient(90deg, #2e7d32 60%, #66bb6a 100%)', // Màu xanh lá cây cho Add
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

      {/* --- PHẦN BỘ LỌC --- */}
      <Paper elevation={1} sx={{ p: 2, mb: 3, borderRadius: 3, borderLeft: '5px solid #1976d2' }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 700, color: 'primary.main', mb: -2 }}>Tìm kiếm & Lọc</Typography>
          <Grid container spacing={2} alignItems="flex-end"> 
              
              {/* 1. Tìm kiếm theo Tên/Mô tả + Nút */}
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
              
              {/* 2. Lọc theo Nhà cung cấp */}
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
                          <MenuItem value="">
                              <em>Tất cả</em>
                          </MenuItem>
                          {PROVIDER_OPTIONS.map((provider) => (
                              <MenuItem key={provider} value={provider}>{provider}</MenuItem>
                          ))}
                      </Select>
                  </FormControl>
              </Grid>
              
              {/* 3. Lọc theo Trạng thái sử dụng */}
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
                          <MenuItem value="">
                              <em>Tất cả</em>
                          </MenuItem>
                          {USAGE_STATUS_OPTIONS.map((status) => (
                              <MenuItem key={status.value} value={status.value}>{status.label}</MenuItem>
                          ))}
                      </Select>
                  </FormControl>
              </Grid>
          </Grid>
      </Paper>
      {/* --- KẾT THÚC PHẦN BỘ LỌC --- */}


      <APIKeyFormModal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveKey}
        editingKey={editingKey}
      />

      <TableContainer 
        component={Paper} 
        sx={{ borderRadius: 4, boxShadow: '0 4px 16px 0 rgba(0,0,0,0.06)' }}
      >
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><b>Tên Khóa / Mô tả</b></TableCell>
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
                    {/* 1. Nút Kích hoạt / Hủy kích hoạt */}
                    <IconButton 
                        onClick={() => handleToggleUsage(key.id, key.is_using)} 
                        sx={{ color: key.is_using ? 'error.main' : 'success.main' }} 
                        title={key.is_using ? 'Tắt sử dụng Key' : 'Kích hoạt Key'}
                        disabled={!key.using_model} 
                    >
                        {key.is_using ? <StopCircleOutlinedIcon /> : <PlayCircleOutlineIcon />}
                    </IconButton>
                  
                    {/* 2. Nút Chỉnh sửa Model/Info */}
                  <IconButton onClick={() => handleEditKey(key)} sx={{ color: 'primary.main' }} title="Chỉnh sửa Model/Thông tin">
                    <EditIcon />
                  </IconButton>
                  
                    {/* 3. Nút Xóa */}
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
            {apiKeys.length === 0 && !isLoading && (
              <TableRow>
                <TableCell colSpan={5} align="center" sx={{ color: 'text.secondary', py: 4 }}>
                  Không có API Key nào được thiết lập.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      {/* Pagination */}
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