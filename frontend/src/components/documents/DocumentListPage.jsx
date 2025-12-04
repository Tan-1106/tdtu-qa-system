import React, { useState, useMemo } from 'react';
import { Box, Typography, TextField, FormControl, InputLabel, Select, MenuItem, List, ListItem, ListItemText, ListItemIcon, Paper, Divider, Chip, IconButton } from '@mui/material';
import ArticleIcon from '@mui/icons-material/Article';
import { useOutletContext } from 'react-router-dom';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';

const mockDocuments = [
  { id: 1, name: 'Quy định học vụ năm học 2025-2026', doc_type: 'Quy định' },
  { id: 2, name: 'Thông báo về việc nghỉ lễ Quốc Khánh 2/9', doc_type: 'Thông báo' },
  { id: 3, name: 'Hướng dẫn chi tiết đăng ký học phần', doc_type: 'Hướng dẫn' },
  { id: 4, name: 'Quy chế công tác sinh viên', doc_type: 'Quy định' },
  { id: 5, name: 'Thông báo lịch thi cuối kỳ', doc_type: 'Thông báo' },
  { id: 6, name: 'Sổ tay sinh viên TDTU', doc_type: 'Hướng dẫn' },
];

const typeColor = {
  'Quy định': 'primary',
  'Thông báo': 'success',
  'Hướng dẫn': 'info'
};

const DocumentListPage = () => {
    // Lấy Context để toggle Sidebar
    const context = useOutletContext();
    const { isSidebarOpen = true, toggleSidebar = () => {} } = context || {};

    const [searchTerm, setSearchTerm] = useState('');
    const [filterType, setFilterType] = useState('all');

    const filteredDocuments = useMemo(() => {
      return mockDocuments
        .filter(doc => {
          if (filterType === 'all') return true;
          return doc.doc_type === filterType;
        })
        .filter(doc => {
          return doc.name.toLowerCase().includes(searchTerm.toLowerCase());
        });
    }, [searchTerm, filterType]);

    return (
        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* 💡 HEADER DESKTOP CHO TRANG TÀI LIỆU */}
            <Box sx={{ 
                p: 2, 
                bgcolor: 'white', 
                display: { xs: 'none', md: 'flex' }, // Chỉ hiện trên Desktop
                alignItems: 'center', 
                gap: 1.5, 
                borderBottom: '1px solid #e3e3e3',
                position: 'sticky', 
                top: 0,
                zIndex: 10,
                flexShrink: 0 
            }}>
                {/* Nút Đóng/Mở Sidebar */}
                <IconButton 
                    size="large" 
                    onClick={toggleSidebar} 
                    // Luôn hiện nút khi Sidebar đóng (Menu Icon)
                    sx={{ color: 'text.primary' }}
                >
                    {isSidebarOpen ? <CloseIcon /> : <MenuIcon />}
                </IconButton>
                
                <Typography variant="h6" sx={{ fontWeight: 600, flexGrow: 1, color: 'primary.main' }}>
                    Kho tài liệu sinh viên
                </Typography>
            </Box>
            
            {/* Nội dung chính của trang (đã sửa để cuộn nếu cần) */}
            <Box sx={{ p: { xs: 2, md: 4 }, overflowY: 'auto', flexGrow: 1 }}>
                <Paper
                    elevation={6}
                    sx={{
                        p: { xs: 2, md: 4 },
                        borderRadius: 5,
                        maxWidth: 900, 
                        mx: 'auto', 
                        boxShadow: '0 8px 32px 0 rgba(25,118,210,0.10)'
                    }}
                >
                    <Typography
                        variant="h4"
                        gutterBottom
                        sx={{
                          fontWeight: 700,
                          color: 'primary.main',
                          letterSpacing: 1,
                          mb: 2,
                          textAlign: 'center'
                        }}
                    >
                        Kho tài liệu sinh viên
                    </Typography>
                    <Box
                        sx={{
                          display: 'flex',
                          flexDirection: { xs: 'column', sm: 'row' },
                          gap: 2,
                          mb: 3
                        }}
                    >
                        <TextField
                          label="Tìm kiếm tài liệu..."
                          variant="outlined"
                          fullWidth
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          sx={{
                            '& .MuiOutlinedInput-root': { borderRadius: 3, bgcolor: '#f7fafd' }
                          }}
                        />
                        <FormControl sx={{ minWidth: 150 }}>
                          <InputLabel>Loại tài liệu</InputLabel>
                          <Select
                            value={filterType}
                            label="Loại tài liệu"
                            onChange={(e) => setFilterType(e.target.value)}
                            sx={{ borderRadius: 3, bgcolor: '#f7fafd' }}
                          >
                            <MenuItem value="all">Tất cả</MenuItem>
                            <MenuItem value="Quy định">Quy định</MenuItem>
                            <MenuItem value="Thông báo">Thông báo</MenuItem>
                            <MenuItem value="Hướng dẫn">Hướng dẫn</MenuItem>
                          </Select>
                        </FormControl>
                    </Box>
                    <Divider sx={{ mb: 2 }} />
                    <List>
                        {filteredDocuments.length > 0 ? (
                          filteredDocuments.map(doc => (
                            <ListItem
                            key={doc.id}
                            sx={{
                              borderRadius: 3,
                              mb: 1.5,
                              transition: 'background 0.18s, box-shadow 0.18s',
                              boxShadow: '0 2px 8px 0 rgba(25,118,210,0.04)',
                              '&:hover': {
                                background: 'linear-gradient(90deg, #e3f2fd 60%, #f7fafd 100%)',
                                boxShadow: '0 4px 16px 0 rgba(25,118,210,0.10)'
                              }
                            }}
                            secondaryAction={
                              <Chip
                                label={doc.doc_type}
                                color={typeColor[doc.doc_type]}
                                size="small"
                                sx={{ fontWeight: 600, fontSize: 13, px: 1.5 }}
                              />
                            }
                            >
                            <ListItemIcon>
                              <ArticleIcon color="primary" />
                            </ListItemIcon>
                            <ListItemText
                              primary={
                                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                                {doc.name}
                                </Typography>
                              }
                            />
                            </ListItem>
                          ))
                        ) : (
                          <Typography sx={{ p: 2, textAlign: 'center', color: 'text.secondary' }}>
                            Không tìm thấy tài liệu phù hợp.
                          </Typography>
                        )}
                    </List>
                </Paper>
            </Box>
        </Box>
    );
};

export default DocumentListPage;