import React, { useState, useEffect } from 'react';
import {
  Box, Button, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, IconButton, Chip
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import UserFormModal from './UserFormModal.jsx'; // Sẽ tạo ở bước 2

// Dữ liệu mẫu
const mockUsers = [
  { id: 1, fullName: 'Nguyễn Văn An', email: 'an.nguyen@tdtu.edu.vn', role: 'User' },
  { id: 2, fullName: 'Trần Thị Bích', email: 'bich.tran@tdtu.edu.vn', role: 'User' },
  { id: 3, fullName: 'Lê Minh Cường', email: 'cuong.le.admin@tdtu.edu.vn', role: 'Admin' },
];

// Màu cho vai trò
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
    <Paper elevation={3} sx={{ p: 3, borderRadius: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>Quản lý người dùng</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleAdd}>
          Thêm người dùng
        </Button>
      </Box>

      <UserFormModal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSave}
        user={editingUser}
      />

      <TableContainer>
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
                    size="small"
                    sx={{ fontWeight: 600 }}
                  />
                </TableCell>
                <TableCell align="right">
                  <IconButton onClick={() => handleEdit(user)}><EditIcon color="primary" /></IconButton>
                  <IconButton onClick={() => handleDelete(user.id)}><DeleteIcon color="error" /></IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

export default UserManagementPage;