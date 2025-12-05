import React, { useState, useEffect } from 'react';
import {
  Box, Button, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, IconButton, Chip, TablePagination, CircularProgress, Alert
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';
import StopCircleOutlinedIcon from '@mui/icons-material/StopCircleOutlined';
import APIKeyFormModal from './APIKeyFormModal'; 
import { getApiKeysList, toggleApiKeyUsage, deleteApiKey } from '../../api/modelApi';

// Màu cho Provider
const providerColor = {
  'OpenAI': 'primary',
  'Google': 'secondary',
};

const ModelManagementPage = () => {
  const [apiKeys, setApiKeys] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingKey, setEditingKey] = useState(null);
  
  // State phân trang và loading
  const [page, setPage] = useState(0); 
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalKeys, setTotalKeys] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);


  // 💡 HÀM TẢI DỮ LIỆU TỪ API
  const fetchKeys = async (currentPage, limit) => {
    setIsLoading(true);
    setError(null);
    setSuccessMsg(null);
    try {
      const data = await getApiKeysList(currentPage + 1, limit); // Chuyển 0-index sang 1-index cho API
      
      setApiKeys(data.api_keys.map(key => ({
          ...key,
          // Đảm bảo key có trường id
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

  useEffect(() => {
    fetchKeys(page, rowsPerPage);
  }, [page, rowsPerPage]);

  // Hành động phân trang
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0); // Reset về trang đầu tiên khi thay đổi limit
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
    fetchKeys(page, rowsPerPage); // Tải lại trang hiện tại
  };
  
  // Hành động Bật/Tắt sử dụng Key (Toggle Usage)
  const handleToggleUsage = async (keyId, currentStatus) => {
    setError(null);
    setSuccessMsg(null);
    try {
        await toggleApiKeyUsage(keyId);
        setSuccessMsg(currentStatus ? 'Đã tắt sử dụng API Key.' : 'Đã kích hoạt API Key thành công.');
        fetchKeys(page, rowsPerPage); // Tải lại dữ liệu
    } catch (err) {
        setError(err.message || "Thao tác Bật/Tắt thất bại.");
    }
  };

  // Hành động Xóa Key
  const handleDeleteKey = async (keyId, keyName) => {
    if (!window.confirm(`Bạn có chắc chắn muốn xóa API Key: ${keyName} không?`)) {
        return;
    }
    setError(null);
    setSuccessMsg(null);
    try {
        await deleteApiKey(keyId);
        setSuccessMsg(`API Key "${keyName}" đã được xóa thành công.`);
        fetchKeys(page, rowsPerPage); // Tải lại dữ liệu
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
                        disabled={!key.using_model} // Không thể kích hoạt nếu chưa chọn model
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