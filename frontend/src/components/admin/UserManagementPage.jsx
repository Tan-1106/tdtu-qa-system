import React, { useState, useEffect } from 'react';
import {
  Box, Button, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, IconButton, Chip, TablePagination, CircularProgress, Alert
} from '@mui/material';
// import AddIcon from '@mui/icons-material/Add'; // Không cần thiết
import EditIcon from '@mui/icons-material/Edit';
import BlockIcon from '@mui/icons-material/Block'; // Icon chặn
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'; // Icon bỏ chặn
import { getUsersList, banUser, unbanUser } from '../../api/adminApi'; // 💡 Import API
import UserFormModal from './UserFormModal';

// Màu cho vai trò
const roleColor = {
  'Admin': 'error',
  'Faculty Manager': 'warning',
  'Student': 'success',
};

const UserManagementPage = () => {
  const [users, setUsers] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  
  // State phân trang và loading
  const [page, setPage] = useState(0); // Mui TablePagination dùng 0-index
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalUsers, setTotalUsers] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // 💡 HÀM TẢI DỮ LIỆU TỪ API
  const fetchUsers = async (currentPage, limit) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getUsersList(currentPage + 1, limit); // Chuyển 0-index sang 1-index cho API
      setUsers(data.users.map(u => ({
          ...u,
          // FIX: Đảm bảo trường ID là _id để thao tác API
          id: u._id, 
          // Cần dùng sub để hiển thị MSSV/ID cho sinh viên
          studentId: u.sub, 
          fullName: u.name,
          email: u.email,
          role: u.role,
          banned: u.banned,
          faculty: u.faculty,
      })));
      setTotalUsers(data.total);
    } catch (err) {
      console.error("Error fetching users:", err);
      // Giữ nguyên thông báo lỗi chung
      setError('Không thể tải danh sách người dùng. Kiểm tra quyền Admin.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers(page, rowsPerPage);
  }, [page, rowsPerPage]);

  // Hành động phân trang
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0); // Reset về trang đầu tiên khi thay đổi limit
  };


  const handleEdit = (user) => {
    setEditingUser(user);
    setIsModalOpen(true);
  };

  // Hành động Chặn/Bỏ chặn
  const handleToggleBan = async (user) => {
    try {
      if (user.banned) {
          console.log(`Bỏ chặn người dùng ${user.id}`);
          await unbanUser(user.id);
      } else {
          console.log(`Chặn người dùng ${user.id}`);
          await banUser(user.id);
      }
      // Sau khi thao tác, tải lại trang hiện tại
      fetchUsers(page, rowsPerPage); 
    } catch (error) {
      // Xử lý lỗi cụ thể cho Chặn/Bỏ chặn nếu cần (ví dụ: không thể tự chặn chính mình)
      console.error("Error toggling ban status:", error);
      setError(error.message || "Thao tác Chặn/Bỏ chặn thất bại.");
    }
  };

  const handleSave = (userData) => {
    // Sau khi modal UserFormModal gọi API Phân quyền (assign-*), ta gọi fetchUsers
    console.log("Saving user data via modal, initiating fetch...");
    setIsModalOpen(false);
    fetchUsers(page, rowsPerPage);
  };
    
  if (isLoading) {
      return (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
              <CircularProgress />
              <Typography sx={{ ml: 2 }}>Đang tải dữ liệu người dùng...</Typography>
          </Box>
      );
  }

  return (
    <Box sx={{ p: { xs: 1, md: 3 } }}>
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main' }}>Quản lý người dùng</Typography>
        {/* 🛑 Đã loại bỏ nút "Chỉnh sửa phân quyền" ở đây */}
      </Box>

      <UserFormModal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSave}
        user={editingUser}
      />

      <TableContainer 
        component={Paper} 
        sx={{ borderRadius: 4, boxShadow: '0 4px 16px 0 rgba(25,118,210,0.06)' }}
      >
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><b>MSSV/ID</b></TableCell>
              <TableCell><b>Họ và Tên</b></TableCell>
              <TableCell><b>Khoa</b></TableCell>
              <TableCell><b>Vai trò</b></TableCell>
              <TableCell><b>Trạng thái</b></TableCell>
              <TableCell align="right"><b>Hành động</b></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id} hover>
                <TableCell>{user.studentId || user.id}</TableCell>
                <TableCell>{user.fullName}</TableCell>
                <TableCell>{user.faculty || 'N/A'}</TableCell>
                <TableCell>
                  <Chip
                    label={user.role}
                    color={roleColor[user.role]}
                    sx={{ fontWeight: 600, borderRadius: 2 }} 
                  />
                </TableCell>
                <TableCell>
                    <Chip
                        label={user.banned ? 'Bị Chặn' : 'Hoạt động'}
                        color={user.banned ? 'error' : 'success'}
                        variant={user.banned ? 'filled' : 'outlined'}
                        sx={{ fontWeight: 500, borderRadius: 2 }} 
                    />
                </TableCell>
                <TableCell align="right">
                  
                    {/* 1. Nút Phân quyền (Edit) */}
                  <IconButton onClick={() => handleEdit(user)} sx={{ color: 'primary.main' }} title="Phân quyền & Chi tiết">
                    <EditIcon />
                  </IconButton>
                    
                    {/* 2. Nút Chặn/Bỏ chặn */}
                    <IconButton 
                        onClick={() => handleToggleBan(user)} 
                        sx={{ color: user.banned ? 'success.main' : 'error.main' }} 
                        title={user.banned ? 'Bỏ chặn' : 'Chặn người dùng'}
                    >
                        {user.banned ? <CheckCircleOutlineIcon /> : <BlockIcon />}
                    </IconButton>
                </TableCell>
              </TableRow>
            ))}
            {users.length === 0 && !isLoading && (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ color: 'text.secondary', py: 4 }}>
                  Không có người dùng nào.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      {/* Pagination */}
      <TablePagination
        component="div"
        count={totalUsers}
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

export default UserManagementPage;