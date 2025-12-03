import React, { useState, useEffect } from 'react';
import {
  Box, Button, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, IconButton, Chip
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import UserFormModal from './UserFormModal.jsx'; // Giả định component này tồn tại

// Dữ liệu mẫu
const mockUsers = [
  { id: 1, fullName: 'Nguyễn Văn An', email: 'an.nguyen@tdtu.edu.vn', role: 'User' },
  { id: 2, fullName: 'Trần Thị Bích', email: 'bich.tran@tdtu.edu.vn', role: 'User' },
  { id: 3, fullName: 'Lê Minh Cường', email: 'cuong.le.admin@tdtu.edu.vn', role: 'Admin' },
];

// Màu cho vai trò (Admin -> error, User -> success)
const roleColor = {
  'Admin': 'error',
  'User': 'success',
};

const UserManagementPage = () => {
  const [users, setUsers] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  useEffect(() => {
    setUsers(mockUsers);
  }, []);

  const handleAdd = () => {
    setEditingUser(null);
    setIsModalOpen(true);
  };

  const handleEdit = (user) => {
    setEditingUser(user);
    setIsModalOpen(true);
  };

  const handleDelete = (userId) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa người dùng này?')) {
      setUsers(currentUsers => currentUsers.filter(u => u.id !== userId));
      console.log(`Xóa người dùng ${userId}`);
    }
  };

  const handleSave = (userData) => {
    if (userData.id) {
      setUsers(currentUsers =>
        currentUsers.map(u => (u.id === userData.id ? { ...u, ...userData } : u))
      );
    } else {
      const newUser = { ...userData, id: Date.now() };
      setUsers(currentUsers => [newUser, ...currentUsers]);
    }
    setIsModalOpen(false);
  };

  return (
    <Box sx={{ p: { xs: 1, md: 3 } }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main' }}>Quản lý người dùng</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
          // Áp dụng style từ DocumentManagementPage
          sx={{
            borderRadius: 3,
            fontWeight: 600,
            background: 'linear-gradient(90deg, #1976d2 60%, #42a5f5 100%)',
            boxShadow: '0 2px 8px 0 rgba(25,118,210,0.10)',
            '&:hover': {
              background: 'linear-gradient(90deg, #1565c0 60%, #1976d2 100%)'
            }
          }}
        >
          Thêm người dùng
        </Button>
      </Box>

      <UserFormModal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSave}
        user={editingUser}
      />

      <TableContainer 
        component={Paper} 
        // Áp dụng style từ DocumentManagementPage
        sx={{ borderRadius: 4, boxShadow: '0 4px 16px 0 rgba(25,118,210,0.06)' }}
      >
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><b>ID</b></TableCell>
              <TableCell><b>Họ và Tên</b></TableCell>
              <TableCell><b>Email</b></TableCell>
              <TableCell><b>Vai trò</b></TableCell>
              <TableCell align="right"><b>Hành động</b></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id} hover>
                <TableCell>{user.id}</TableCell>
                <TableCell>{user.fullName}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>
                  <Chip
                    label={user.role}
                    color={roleColor[user.role]}
                    // Áp dụng style từ DocumentManagementPage
                    sx={{ fontWeight: 600, borderRadius: 2 }} 
                  />
                </TableCell>
                <TableCell align="right">
                  {/* Sử dụng sx cho màu sắc IconButton */}
                  <IconButton onClick={() => handleEdit(user)} sx={{ color: 'primary.main' }}>
                    <EditIcon />
                  </IconButton>
                  <IconButton onClick={() => handleDelete(user.id)} sx={{ color: 'error.main' }}>
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
            {users.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} align="center" sx={{ color: 'text.secondary', py: 4 }}>
                  Không có người dùng nào.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default UserManagementPage;