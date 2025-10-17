import React, { useState, useEffect } from 'react';
import {
  Box, Button, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';

// 1. Import component Modal
import DocumentFormModal from './DocumentFormModal.jsx';

const typeColor = {
  'Quy định': 'primary',
  'Thông báo': 'success',
  'Hướng dẫn': 'info'
};

const DocumentManagementPage = () => {
  const [documents, setDocuments] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingDocument, setEditingDocument] = useState(null);

  useEffect(() => {
    const fetchedDocs = [
      { id: 1, name: 'Quy định học vụ 2025', type: 'Quy định', uploadDate: '2025-09-15' },
      { id: 2, name: 'Thông báo nghỉ lễ 30/4', type: 'Thông báo', uploadDate: '2025-09-20' },
      { id: 3, name: 'Hướng dẫn đăng ký học phần', type: 'Hướng dẫn', uploadDate: '2025-09-22' },
    ];
    setDocuments(fetchedDocs);
  }, []);

  const handleAdd = () => {
    setEditingDocument(null); // Đảm bảo không có document nào đang được edit
    setIsModalOpen(true);
  };

  const handleEdit = (doc) => {
    setEditingDocument(doc); // Set document đang được edit
    setIsModalOpen(true);
  };

  const handleDelete = (docId) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa tài liệu này?')) {
      setDocuments(docs => docs.filter(d => d.id !== docId));
      console.log(`Xóa tài liệu ${docId}`);
    }
  };
  
  // 2. Thêm hàm xử lý lưu
  const handleSave = (docData) => {
    // Nếu docData có id, tức là đang sửa
    if (docData.id) {
      setDocuments(docs => 
        docs.map(doc => (doc.id === docData.id ? { ...doc, ...docData } : doc))
      );
    } 
    // Nếu không có id, tức là đang thêm mới
    else {
      const newDoc = {
        ...docData,
        id: Date.now(), // Tạo id tạm thời
        uploadDate: new Date().toISOString().split('T')[0], // Lấy ngày hiện tại
      };
      setDocuments(docs => [newDoc, ...docs]);
    }
    setIsModalOpen(false); // Đóng modal sau khi lưu
  };

  return (
    <Box sx={{ p: { xs: 1, md: 3 } }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main' }}>Quản lý tài liệu</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
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
          Thêm tài liệu
        </Button>
      </Box>

      {/* 3. Render Modal và truyền các props cần thiết */}
      <DocumentFormModal 
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSave}
        document={editingDocument}
      />

      <TableContainer component={Paper} sx={{ borderRadius: 4, boxShadow: '0 4px 16px 0 rgba(25,118,210,0.06)' }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><b>ID</b></TableCell>
              <TableCell><b>Tên tài liệu</b></TableCell>
              <TableCell><b>Loại</b></TableCell>
              <TableCell><b>Ngày tải lên</b></TableCell>
              <TableCell align="right"><b>Hành động</b></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {documents.map((doc) => (
              <TableRow key={doc.id} hover>
                <TableCell>{doc.id}</TableCell>
                <TableCell>{doc.name}</TableCell>
                <TableCell>
                  <Chip
                    label={doc.type}
                    color={typeColor[doc.type]}
                    sx={{ fontWeight: 600, borderRadius: 2 }}
                  />
                </TableCell>
                <TableCell>{doc.uploadDate}</TableCell>
                <TableCell align="right">
                  <IconButton onClick={() => handleEdit(doc)} sx={{ color: 'primary.main' }}>
                    <EditIcon />
                  </IconButton>
                  <IconButton onClick={() => handleDelete(doc.id)} sx={{ color: 'error.main' }}>
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
            {documents.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} align="center" sx={{ color: 'text.secondary', py: 4 }}>
                  Không có tài liệu nào.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default DocumentManagementPage;