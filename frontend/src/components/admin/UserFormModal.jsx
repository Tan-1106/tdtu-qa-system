import React, { useState, useEffect } from 'react';
import { 
    Modal, Box, Typography, TextField, Button, Select, MenuItem, 
    FormControl, InputLabel, CircularProgress, Alert,
    Checkbox, FormControlLabel
} from '@mui/material';
import { 
    getRoles, getFaculties, assignAdminRole, 
    assignFacultyManagerPermission, revokeFacultyManagerPermission,
    assignTeacherRole, assignStudentRole 
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

const extractError = (error, defaultMessage) => {
    if (error.response?.data?.details) {
        return error.response.data.details;
    }
    return error.message || defaultMessage || 'Lỗi không xác định.'; 
};

const UserFormModal = ({ open, onClose, user, onSave }) => {
    const [availableRoles, setAvailableRoles] = useState([]);
    const [availableFaculties, setAvailableFaculties] = useState([]);
    
    const [selectedRole, setSelectedRole] = useState(user?.role || '');
    const [selectedFaculty, setSelectedFaculty] = useState(user?.faculty || '');

    const [isManager, setIsManager] = useState(user?.is_faculty_manager || false);
    
    const [isLoadingOptions, setIsLoadingOptions] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState(null);

    // 💡 Lấy danh sách Role và Faculty khi Modal mở
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
                    
                    setSelectedRole(user?.role || '');
                    setSelectedFaculty(user?.faculty || '');
                    setIsManager(user?.is_faculty_manager || false);

                } catch (err) {
                    const errorMessage = extractError(err, 'Không thể tải các tùy chọn Phân quyền/Khoa.');
                    setError(errorMessage);
                    console.error("Error fetching options:", err);
                } finally {
                    setIsLoadingOptions(false);
                }
            };
            fetchOptions();
        }
    }, [open, user]);

    const handleSave = async () => {
        if (!user || !selectedRole) return;
        
        setIsSaving(true);
        setError(null);
        try {
            const userId = user.id;
            const originalRole = user.role;
            const originalFaculty = user.faculty;
            const originalIsManager = user.is_faculty_manager;

            let roleOrFacultyChanged = selectedRole !== originalRole || 
                                       (selectedFaculty !== originalFaculty && isFacultyRequired);

            if (roleOrFacultyChanged) {
                
                if (selectedRole === 'Admin') {
                    await assignAdminRole(userId);
                } 
                else if (selectedRole === 'Teacher') {
                    if (!selectedFaculty) throw new Error("Vui lòng chọn Khoa cho Teacher.");
                    await assignTeacherRole(userId, selectedFaculty);
                } else if (selectedRole === 'Student') {
                    if (!selectedFaculty) throw new Error("Vui lòng chọn Khoa cho Sinh viên.");
                    await assignStudentRole(userId, selectedFaculty);
                }
            }

            const newIsManagerStatus = isManager;
            
            if (newIsManagerStatus !== originalIsManager && selectedRole !== 'Admin') {
                if (newIsManagerStatus) {
                    if (!selectedFaculty || selectedFaculty === 'N/A') throw new Error("Vui lòng chọn Khoa để gán quyền Manager.");
                    await assignFacultyManagerPermission(userId, selectedFaculty);
                } else {
                    await revokeFacultyManagerPermission(userId);
                }
            }

            onSave({}); 

        } catch (err) {
            console.error("Error assigning role/permission:", err);
            setError(extractError(err, "Lưu thất bại. Vui lòng thử lại."));
        } finally {
            setIsSaving(false);
        }
    };

    const isFacultyRequired = selectedRole !== 'Admin';

    const showManagerCheckbox = selectedRole !== 'Admin' && selectedRole !== '';

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
                                    if(e.target.value === 'Admin') {
                                      setSelectedFaculty('N/A');
                                      setIsManager(false);
                                    }
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
                        {/* Checkbox Manager (Chỉ hiện khi không phải Admin) */}
                        {showManagerCheckbox && (
                            <FormControlLabel
                                control={
                                    <Checkbox 
                                        checked={isManager} 
                                        onChange={(e) => setIsManager(e.target.checked)}
                                        disabled={isSaving || !selectedFaculty} 
                                    />
                                }
                                label="Quyền Quản lý Khoa"
                                sx={{ mb: 2 }}
                            />
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