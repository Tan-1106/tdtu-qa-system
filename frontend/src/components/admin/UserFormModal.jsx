// File: src/components/admin/UserFormModal.jsx
import React, { useState, useEffect } from 'react';
import { 
    Modal, Box, Typography, TextField, Button, Select, MenuItem, 
    FormControl, InputLabel, CircularProgress, Alert 
} from '@mui/material';
import { 
    getRoles, getFaculties, assignAdminRole, 
    assignFacultyManagerRole, assignStudentRole 
} from '../../api/adminApi'; 

const style = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 400,
    bgcolor: 'background.paper',
    boxShadow: 24,
    p: 4,
    borderRadius: 2,
};

const UserFormModal = ({ open, onClose, user, onSave }) => {
    // State cho tùy chọn Role và Faculty
    const [availableRoles, setAvailableRoles] = useState([]);
    const [availableFaculties, setAvailableFaculties] = useState([]);
    
    // State cho form
    const [selectedRole, setSelectedRole] = useState(user?.role || '');
    const [selectedFaculty, setSelectedFaculty] = useState(user?.faculty || '');
    
    const [isLoadingOptions, setIsLoadingOptions] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState(null);

    // 💡 Lấy danh sách Role và Faculty khi Modal mở (2.1.2 & 2.1.3)
    useEffect(() => {
        if (open) {
            const fetchOptions = async () => {
                setIsLoadingOptions(true);
                setError(null);
                try {
                    const roles = await getRoles();
                    setAvailableRoles(roles);

                    const faculties = await getFaculties();
                    setAvailableFaculties(faculties);
                    
                    // Reset selected values nếu có user
                    setSelectedRole(user?.role || '');
                    setSelectedFaculty(user?.faculty || '');

                } catch (err) {
                    setError('Không thể tải các tùy chọn Phân quyền/Khoa.');
                    console.error("Error fetching options:", err);
                } finally {
                    setIsLoadingOptions(false);
                }
            };
            fetchOptions();
        }
    }, [open, user]);

    // Xử lý lưu (Phân quyền: 2.1.4, 2.1.5, 2.1.6)
    const handleSave = async () => {
        if (!user || !selectedRole) return;
        
        setIsSaving(true);
        setError(null);
        try {
            let result;
            
            if (selectedRole === 'Admin') {
                result = await assignAdminRole(user.id);
            } else if (selectedRole === 'Faculty Manager') {
                if (!selectedFaculty) throw new Error("Vui lòng chọn Khoa cho Faculty Manager.");
                result = await assignFacultyManagerRole(user.id, selectedFaculty);
            } else if (selectedRole === 'Student') {
                 if (!selectedFaculty) throw new Error("Vui lòng chọn Khoa cho Sinh viên.");
                result = await assignStudentRole(user.id, selectedFaculty);
            } else {
                 throw new Error("Vai trò không hợp lệ.");
            }
            
            // Gọi onSave để component cha (UserManagementPage) tải lại danh sách
            onSave(result.details); 

        } catch (err) {
            console.error("Error assigning role:", err);
            // Hiển thị thông báo lỗi cụ thể từ API (ví dụ: Khoa không hợp lệ - 400)
            setError(err.message || "Lưu thất bại. Vui lòng thử lại.");
        } finally {
            setIsSaving(false);
        }
    };

    const isFacultyRequired = selectedRole !== 'Admin';

    return (
        <Modal open={open} onClose={onClose}>
            <Box sx={style}>
                <Typography variant="h6" component="h2" sx={{ mb: 2 }}>
                    Phân quyền cho {user?.fullName || 'Người dùng mới'}
                </Typography>
                
                {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

                {user && (
                    <TextField
                        fullWidth
                        label="ID Người dùng"
                        value={user.studentId || user.id}
                        disabled
                        sx={{ mb: 2 }}
                    />
                )}
                
                {isLoadingOptions ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
                        <CircularProgress size={24} />
                    </Box>
                ) : (
                    <>
                        {/* Dropdown Phân quyền */}
                        <FormControl fullWidth sx={{ mb: 2 }} disabled={isSaving}>
                            <InputLabel id="role-select-label">Vai trò</InputLabel>
                            <Select
                                labelId="role-select-label"
                                value={selectedRole}
                                label="Vai trò"
                                onChange={(e) => {
                                    setSelectedRole(e.target.value);
                                    // Reset khoa khi đổi vai trò sang Admin
                                    if(e.target.value === 'Admin') setSelectedFaculty('N/A');
                                }}
                            >
                                {availableRoles.map((role) => (
                                    <MenuItem key={role} value={role}>{role}</MenuItem>
                                ))}
                            </Select>
                        </FormControl>

                        {/* Dropdown Khoa (Chỉ hiện khi không phải Admin) */}
                        {isFacultyRequired && (
                            <FormControl fullWidth sx={{ mb: 3 }} disabled={isSaving || selectedRole === 'Admin'}>
                                <InputLabel id="faculty-select-label">Khoa</InputLabel>
                                <Select
                                    labelId="faculty-select-label"
                                    value={selectedFaculty}
                                    label="Khoa"
                                    onChange={(e) => setSelectedFaculty(e.target.value)}
                                >
                                    {availableFaculties.map((faculty) => (
                                        <MenuItem key={faculty} value={faculty}>{faculty}</MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        )}
                    </>
                )}

                <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                    <Button onClick={onClose} variant="outlined" disabled={isSaving}>Hủy</Button>
                    <Button 
                        onClick={handleSave} 
                        variant="contained" 
                        disabled={isSaving || (isFacultyRequired && !selectedFaculty) || !selectedRole}
                    >
                        {isSaving ? <CircularProgress size={24} color="inherit" /> : 'Lưu & Phân quyền'}
                    </Button>
                </Box>
            </Box>
        </Modal>
    );
};

export default UserFormModal;