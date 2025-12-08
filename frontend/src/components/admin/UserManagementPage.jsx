import React, { useState, useEffect } from 'react';
import {
  Box, Button, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, IconButton, Chip, TablePagination, CircularProgress, Alert,
  TextField, FormControl, InputLabel, Select, MenuItem, Grid, Stack 
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import BlockIcon from '@mui/icons-material/Block'; 
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'; 
import SearchIcon from '@mui/icons-material/Search'; 
import SupervisorAccountIcon from '@mui/icons-material/SupervisorAccount';
import { 
    getUsersList, banUser, unbanUser, 
    getRoles, getFaculties 
} from '../../api/adminApi'; 
import UserFormModal from './UserFormModal';    
import useUserAuth from '../../hooks/useUserAuth';

const roleColor = {
  'Admin': 'error',
  'Teacher': 'warning',
  'Student': 'success',
};

const statusOptions = [
    { value: 'active', label: 'Hoạt động' },
    { value: 'banned', label: 'Bị Chặn' }
];

const UserManagementPage = () => {
    const { user: currentUser } = useUserAuth(); 
    const isOnlyManager = currentUser?.is_faculty_manager === true && currentUser?.role !== 'Admin';
    const isAdmin = currentUser?.role === 'Admin';
    
  const [users, setUsers] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  
  const [searchKeyword, setSearchKeyword] = useState(''); 
  const [filterRole, setFilterRole] = useState('');
  const [filterFaculty, setFilterFaculty] = useState('');
  const [filterStatus, setFilterStatus] = useState(''); 

  const [availableRoles, setAvailableRoles] = useState([]);
  const [availableFaculties, setAvailableFaculties] = useState([]);
  
  const [page, setPage] = useState(0); 
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalUsers, setTotalUsers] = useState(0);
  
  const [isInitialLoading, setIsInitialLoading] = useState(true); 
  const [isRefetching, setIsRefetching] = useState(false); 
  const [error, setError] = useState(null);
  
  const fetchFilterOptions = async () => {
      try {
          if (isAdmin) {
              const roles = await getRoles();
              if (!roles.includes('Faculty Manager')) {
                  const updatedRoles = [...roles, 'Faculty Manager'];
                  setAvailableRoles(updatedRoles);
              } else {
                  setAvailableRoles(roles);
              }
              const faculties = await getFaculties();
              setAvailableFaculties(faculties);
          }
      } catch (err) {
           console.error("Error fetching filter options:", err);
      }
  };

  const fetchUsers = async (currentPage, limit, role, faculty, banned, keyword, isInitialLoad) => {
    if (isInitialLoad) {
        setIsInitialLoading(true);
    } else {
        setIsRefetching(true);
    }
    setError(null);

    let roleFilter = undefined;
    let isFacultyManagerFilter = undefined;

    if (isAdmin && role) {
        if (role === 'Faculty Manager') {
            isFacultyManagerFilter = true;
            roleFilter = ['Teacher', 'Student']; 
        } else {
            roleFilter = role;
        }
    }
    
    const params = {
        page: currentPage + 1,
        limit: limit,
        keyword: keyword || undefined, 
        role: roleFilter,
        is_faculty_manager: isFacultyManagerFilter,
        faculty: isAdmin ? faculty : undefined, 
        banned: banned === 'banned' ? true : banned === 'active' ? false : undefined,
    };
    
    try {
        const data = await getUsersList(params); 
        
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
      let finalError = (err.response?.data?.details || err.message) || 'Lỗi không xác định.';
      setError(finalError);
    } finally {
      if (isInitialLoad) {
          setIsInitialLoading(false);
      } else {
          setIsRefetching(false);
      }
    }
  };

  const loadUsersWithFilters = (resetPage = true, isInitialLoad = false) => {
      const targetPage = resetPage ? 0 : page;
      const currentRole = isAdmin ? filterRole : undefined;
      const currentFaculty = isAdmin ? filterFaculty : undefined;
      
      fetchUsers(
          targetPage, 
          rowsPerPage, 
          currentRole, 
          currentFaculty, 
          filterStatus, 
          searchKeyword,
          isInitialLoad
      );
      
      if (resetPage && page !== 0) {
          setPage(0);
      }
  };

  const handleSearchClick = () => {
      loadUsersWithFilters(true); 
  };

  useEffect(() => {
      if (currentUser) {
          fetchFilterOptions();
          loadUsersWithFilters(true, true); 
      }
  }, [currentUser]);


  useEffect(() => {
      if (!currentUser) return; 
      
      if (!isInitialLoading) {
           loadUsersWithFilters(true); 
      }
      
  }, [filterRole, filterFaculty, filterStatus, rowsPerPage]);


  const handleChangePage = (event, newPage) => {
    setPage(newPage);
    loadUsersWithFilters(false);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0); 
    loadUsersWithFilters(true); 
  };

  const handleEdit = (user) => {
        if (isOnlyManager) {
            setError('Faculty Manager không có quyền chỉnh sửa phân quyền.');
            return;
        }
        setEditingUser(user);
        setIsModalOpen(true);
    };

  const handleToggleBan = async (user) => {
        if (!isAdmin) { 
                setError('Bạn không có quyền Chặn/Bỏ chặn người dùng.');
                return;
            }
        try {
            const apiCall = user.banned ? unbanUser : banUser;
            
            await apiCall(user.id);
            
            loadUsersWithFilters(false); 
        } catch (error) {
            console.error("Error toggling ban status:", error);
            setError(error.message || "Thao tác Chặn/Bỏ chặn thất bại.");
        }
    };

  const handleSave = (userData) => {
    console.log("Saving user data via modal, initiating fetch...");
    setIsModalOpen(false);
    loadUsersWithFilters(false); 
  };
    
  // CHỈ HIỂN THỊ LOADING TOÀN TRANG CHO LẦN TẢI ĐẦU TIÊN
  if (isInitialLoading || !currentUser) { 
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
        
        <Paper elevation={1} sx={{ p: 2, mb: 3, borderRadius: 3, borderLeft: '5px solid #1976d2' }}>
            {isAdmin && (
                <Typography variant="subtitle1" sx={{ mb: -2, fontWeight: 700, color: 'primary.main' }}>Tìm kiếm & Lọc</Typography>
            )}
            {isOnlyManager && (
                <Typography variant="subtitle1" sx={{ mb: 0, fontWeight: 700, color: 'primary.main' }}>Tìm kiếm & Lọc</Typography>
            )}
            <Grid container spacing={2} alignItems="flex-end">
                
                <Grid item xs={12} sm={6} md={3.5}>
                    <Stack direction="row" spacing={1} alignItems="flex-end">
                         <TextField
                            fullWidth
                            label="Tên hoặc MSSV"
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
                
                {isAdmin && (
                    <Grid item xs={12} sm={6} md={2.5}> 
                        <Typography variant="caption" display="block" sx={{ color: 'text.secondary', mb: 0.5 }}>
                            Vai trò
                        </Typography>
                        <FormControl fullWidth size="small" variant="outlined">
                            <Select
                                value={filterRole}
                                displayEmpty
                                onChange={(e) => setFilterRole(e.target.value)} 
                                renderValue={(selected) => (selected ? selected : <em>Tất cả</em>)} 
                            >
                                <MenuItem value="">
                                    <em>Tất cả</em>
                                </MenuItem>
                                {availableRoles.map((role) => (
                                    <MenuItem key={role} value={role}>{role}</MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Grid>
                )}
                
                {isAdmin && (
                    <Grid item xs={12} sm={6} md={3}>
                        <Typography variant="caption" display="block" sx={{ color: 'text.secondary', mb: 0.5 }}>
                            Khoa
                        </Typography>
                        <FormControl fullWidth size="small" variant="outlined">
                            <Select
                                value={filterFaculty}
                                displayEmpty
                                onChange={(e) => setFilterFaculty(e.target.value)}
                                renderValue={(selected) => (selected ? selected : <em>Tất cả</em>)} 
                            >
                                <MenuItem value="">
                                    <em>Tất cả</em>
                                </MenuItem>
                                {availableFaculties.map((faculty) => (
                                    <MenuItem key={faculty} value={faculty}>{faculty}</MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Grid>
                )}
                
                {isAdmin && (
                    <Grid item xs={12} sm={6} md={2.5}> 
                    <Typography variant="caption" display="block" sx={{ color: 'text.secondary', mb: 0.5 }}>
                        Trạng thái
                    </Typography>
                    <FormControl fullWidth size="small" variant="outlined">
                        <Select
                            value={filterStatus}
                            displayEmpty
                            onChange={(e) => setFilterStatus(e.target.value)}
                            renderValue={(selected) => (selected ? statusOptions.find(s => s.value === selected)?.label : <em>Tất cả</em>)} 
                        >
                            <MenuItem value="">
                                <em>Tất cả</em>
                            </MenuItem>
                            {statusOptions.map((status) => (
                                <MenuItem key={status.value} value={status.value}>{status.label}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    </Grid>
                )}
            </Grid>
        </Paper>


        {isAdmin && (
            <UserFormModal
              open={isModalOpen}
              onClose={() => setIsModalOpen(false)}
              onSave={handleSave}
              user={editingUser}
            />
        )}

      {/* THAY ĐỔI: Thêm inline loading overlay */}
      <TableContainer 
        component={Paper} 
        sx={{ 
            borderRadius: 4, 
            boxShadow: '0 4px 16px 0 rgba(25,118,210,0.06)',
            position: 'relative', // Quan trọng cho overlay
        }}
      >
        {/* Lớp phủ loading khi đang lọc hoặc chuyển trang */}
        {isRefetching && (
            <Box 
                sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    bgcolor: 'rgba(255, 255, 255, 0.7)', // Màu trắng mờ
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
              <TableCell><b>MSSV</b></TableCell>
              <TableCell><b>Họ và Tên</b></TableCell>
              <TableCell><b>Khoa</b></TableCell>
              <TableCell><b>Vai trò</b></TableCell>
              <TableCell><b>Trạng thái</b></TableCell>
                {isAdmin && (              
                <TableCell align="right"><b>Hành động</b></TableCell>
                )}
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id} hover>
                <TableCell>{user.studentId || user.id}</TableCell>
                <TableCell>{user.fullName}</TableCell>
                <TableCell>{user.faculty || 'N/A'}</TableCell>
                <TableCell>
                    <Stack direction="row" spacing={0.5} alignItems="center">
                        <Chip
                            label={user.role || 'N/A'}
                            color={roleColor[user.role]}
                            size="small"
                            sx={{ fontWeight: 600, borderRadius: 1 }} 
                        />
                        {user.is_faculty_manager && user.role !== 'Admin' && (
                            <SupervisorAccountIcon 
                                sx={{ color: 'info.main', fontSize: 20 }} 
                                titleAccess="Quản lý Khoa" 
                            />
                        )}
                    </Stack>
                </TableCell>
                <TableCell>
                    <Chip
                        label={user.banned ? 'Bị Chặn' : 'Hoạt động'}
                        color={user.banned ? 'error' : 'success'}
                        variant={user.banned ? 'filled' : 'outlined'}
                        sx={{ fontWeight: 500, borderRadius: 2 }} 
                    />
                </TableCell>
                {isAdmin && (
                    <TableCell align="right">
                            <IconButton onClick={() => handleEdit(user)} sx={{ color: 'primary.main' }} title="Phân quyền & Chi tiết">
                              <EditIcon />
                          </IconButton>
                    <IconButton 
                        onClick={() => handleToggleBan(user)} 
                        sx={{ color: user.banned ? 'error.main' : 'success.main' }} 
                        title={user.banned ? 'Bỏ chặn' : 'Chặn người dùng'}
                    >
                        {user.banned ? <CheckCircleOutlineIcon /> : <BlockIcon />}
                    </IconButton>
                </TableCell>)}
                
              </TableRow>
            ))}
            {users.length === 0 && !isInitialLoading && ( // Dùng isInitialLoading để tránh lỗi nhấp nháy khi tải ban đầu
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
        onPageChange={handleChangePage} // Đã thêm lại
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={handleChangeRowsPerPage} // Đã thêm lại
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