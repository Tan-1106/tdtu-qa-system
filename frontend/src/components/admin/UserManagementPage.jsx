import React, { useState, useEffect } from 'react';
import {
  Box, Button, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, IconButton, Chip, TablePagination, CircularProgress, Alert
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import BlockIcon from '@mui/icons-material/Block'; 
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'; 
import { getUsersList, banUser, unbanUser, getStudentsList, banStudent, unbanStudent} from '../../api/adminApi'; // 💡 Import API
import UserFormModal from './UserFormModal';    
import useUserAuth from '../../hooks/useUserAuth';

const roleColor = {
  'Admin': 'error',
  'Faculty Manager': 'warning',
  'Student': 'success',
};

const UserManagementPage = () => {
    const { user: currentUser } = useUserAuth(); 
    const isFacultyManager = currentUser?.role === 'Faculty Manager';
    const isAdmin = currentUser?.role === 'Admin';
    
  const [users, setUsers] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  
  const [page, setPage] = useState(0); 
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalUsers, setTotalUsers] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchUsers = async (currentPage, limit) => {
    setIsLoading(true);
    setError(null);
    try {
        let data;
        
        if (isAdmin) {
            data = await getUsersList(currentPage + 1, limit); 
        } else if (isFacultyManager) {
            console.log(`[FM Load] Đang tải người dùng cho Khoa: ${currentUser.department}`); 
            
            data = await getStudentsList(currentPage + 1, limit);
        } else {
            throw new Error("Tài khoản không có quyền truy cập trang này.");
        }
        
        if (!data || !data.users) {
            setUsers([]);
            setTotalUsers(0);
            return;
        }

        setUsers(data.users.map(u => ({
          ...u,
          id: u._id, 
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

      let defaultError = isFacultyManager 
          ? 'Không thể tải danh sách người dùng trong khoa.'
          : 'Không thể tải danh sách người dùng. Kiểm tra quyền Admin.';

      let finalError = defaultError;

      if (err.response && err.response.data && err.response.data.message) {
          finalError = err.response.data.message;
      } else if (err.message && err.message !== "Tài khoản không có quyền truy cập trang này.") {
          finalError = err.message;
      } else if (err.message === "Tài khoản không có quyền truy cập trang này.") {
          finalError = err.message;
      }
      
      setError(finalError);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
        if (currentUser) { 
            fetchUsers(page, rowsPerPage);
        }
    }, [page, rowsPerPage, currentUser]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0); 
  };


  const handleEdit = (user) => {
        if (isFacultyManager) {
            setError('Faculty Manager không có quyền chỉnh sửa phân quyền.');
            return;
        }
        setEditingUser(user);
        setIsModalOpen(true);
    };

  const handleToggleBan = async (user) => {
        try {

            const apiCall = user.banned ? (isAdmin ? unbanUser : unbanStudent) : (isAdmin ? banUser : banStudent);

            await apiCall(user.id);
            
            fetchUsers(page, rowsPerPage); 
        } catch (error) {
            console.error("Error toggling ban status:", error);
            setError(error.message || "Thao tác Chặn/Bỏ chặn thất bại.");
        }
    };

  const handleSave = (userData) => {
    console.log("Saving user data via modal, initiating fetch...");
    setIsModalOpen(false);
    fetchUsers(page, rowsPerPage);
  };
    
  if (isLoading || !currentUser) {
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
          <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main' }}>
            Quản lý người dùng
          </Typography>
        </Box>

        {isAdmin && (
            <UserFormModal
              open={isModalOpen}
              onClose={() => setIsModalOpen(false)}
              onSave={handleSave}
              user={editingUser}
            />
        )}

      <TableContainer 
        component={Paper} 
        sx={{ borderRadius: 4, boxShadow: '0 4px 16px 0 rgba(25,118,210,0.06)' }}
      >
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><b>MSSV</b></TableCell>
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
                  
                  {isAdmin && (
                            <IconButton onClick={() => handleEdit(user)} sx={{ color: 'primary.main' }} title="Phân quyền & Chi tiết">
                              <EditIcon />
                          </IconButton>
                        )}
                    
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