import React, { useState, useEffect, useRef } from 'react'; // 1. Thêm useRef
import {
  Modal, Box, Typography, TextField, Button,
  FormControl, InputLabel, Select, MenuItem, Stack, Paper, Chip
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';

const modalStyle = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 600,
  bgcolor: 'background.paper',
  borderRadius: 4,
  boxShadow: 24,
  p: 4,
};

const initialState = { name: '', type: 'Quy định' };

const DocumentFormModal = ({ open, onClose, onSave, document }) => {
  const [formData, setFormData] = useState(initialState);
  const [selectedFile, setSelectedFile] = useState(null); // 2. State để lưu file đã chọn
  const fileInputRef = useRef(null); // 3. Ref để truy cập input ẩn

  useEffect(() => {
    if (document) {
      setFormData({
        name: document.name || '',
        type: document.type || 'Quy định',
      });
      setSelectedFile(null); // Reset file khi mở lại modal
    } else {
      setFormData(initialState);
      setSelectedFile(null);
    }
  }, [document, open]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  // 4. Hàm xử lý khi người dùng chọn file
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  // 5. Hàm xử lý khi nhấn nút "Tải lên"
  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    // Gửi cả formData và selectedFile về cho component cha
    onSave({ ...formData, id: document ? document.id : undefined, file: selectedFile });
  };

  return (
    <Modal open={open} onClose={onClose}>
      <Paper sx={modalStyle}>
        <Typography variant="h5" component="h2" sx={{ mb: 3, fontWeight: 'bold' }}>
          {document ? 'Chỉnh sửa tài liệu' : 'Thêm tài liệu mới'}
        </Typography>
        <Box component="form" onSubmit={handleSubmit}>
          <TextField
            name="name"
            label="Tên tài liệu"
            value={formData.name}
            onChange={handleChange}
            fullWidth
            required
            margin="normal"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Loại tài liệu</InputLabel>
            <Select
              name="type"
              value={formData.type}
              label="Loại tài liệu"
              onChange={handleChange}
            >
              <MenuItem value="Quy định">Quy định</MenuItem>
              <MenuItem value="Thông báo">Thông báo</MenuItem>
              <MenuItem value="Hướng dẫn">Hướng dẫn</MenuItem>
            </Select>
          </FormControl>
          
          {/* ---- 6. PHẦN UPLOAD FILE MỚI ---- */}
          <Box sx={{ mt: 2, mb: 1, p: 2, border: '1px dashed grey', borderRadius: 2 }}>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>Nội dung tài liệu</Typography>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              style={{ display: 'none' }} // Ẩn input mặc định
              accept=".doc, .docx, .pdf" // Giới hạn loại file
            />
            <Button
              variant="outlined"
              onClick={handleUploadClick}
              startIcon={<UploadFileIcon />}
            >
              Chọn file (.doc, .pdf)
            </Button>
            {selectedFile && (
              <Chip label={selectedFile.name} onDelete={() => setSelectedFile(null)} sx={{ ml: 2 }}/>
            )}
          </Box>
          
          <Stack direction="row" spacing={2} sx={{ mt: 3, justifyContent: 'flex-end' }}>
            <Button onClick={onClose} color="inherit">Hủy</Button>
            <Button type="submit" variant="contained">
              {document ? 'Lưu thay đổi' : 'Tạo mới'}
            </Button>
          </Stack>
        </Box>
      </Paper>
    </Modal>
  );
};

export default DocumentFormModal;