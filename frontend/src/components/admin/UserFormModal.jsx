import React, { useState, useEffect } from 'react';
import {
  Modal, Box, Typography, TextField, Button,
  FormControl, InputLabel, Select, MenuItem, Stack, Paper
} from '@mui/material';

const modalStyle = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 500,
  bgcolor: 'background.paper',
  borderRadius: 4,
  boxShadow: 24,
  p: 4,
};

const initialState = { fullName: '', email: '', role: 'User' };

const UserFormModal = ({ open, onClose, onSave, user }) => {
  const [formData, setFormData] = useState(initialState);

  useEffect(() => {
    if (user) {
      setFormData({
        fullName: user.fullName || '',
        email: user.email || '',
        role: user.role || 'User',
      });
    } else {
      setFormData(initialState);
    }
  }, [user, open]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSave({ ...formData, id: user ? user.id : undefined });
  };

  return (
    <Modal open={open} onClose={onClose}>
      <Paper sx={modalStyle}>
        <Typography variant="h5" component="h2" sx={{ mb: 3 }}>
          {user ? 'Chỉnh sửa người dùng' : 'Thêm người dùng mới'}
        </Typography>
        <Box component="form" onSubmit={handleSubmit}>
          <TextField
            name="fullName"
            label="Họ và Tên"
            value={formData.fullName}
            onChange={handleChange}
            fullWidth required margin="normal"
          />
          <TextField
            name="email"
            label="Email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            fullWidth required margin="normal"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Vai trò</InputLabel>
            <Select
              name="role"
              value={formData.role}
              label="Vai trò"
              onChange={handleChange}
            >
              <MenuItem value="User">User</MenuItem>
              <MenuItem value="Admin">Admin</MenuItem>
            </Select>
          </FormControl>
          <Stack direction="row" spacing={2} sx={{ mt: 3, justifyContent: 'flex-end' }}>
            <Button onClick={onClose} color="inherit">Hủy</Button>
            <Button type="submit" variant="contained">
              {user ? 'Lưu thay đổi' : 'Tạo mới'}
            </Button>
          </Stack>
        </Box>
      </Paper>
    </Modal>
  );
};

export default UserFormModal;