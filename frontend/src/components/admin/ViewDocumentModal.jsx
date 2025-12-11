import React from 'react';
import { Modal, Box, Typography, IconButton, CircularProgress } from '@mui/material'; 
import CloseIcon from '@mui/icons-material/Close';

const style = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: '95%',
    height: '95%', 
    bgcolor: 'background.paper',
    boxShadow: 24,
    borderRadius: 2,
    display: 'flex',
    flexDirection: 'column',
};

const ViewDocumentModal = ({ open, onClose, document, viewDocumentUrl }) => {
    if (!document) return null;
    
    const viewUrl = viewDocumentUrl; 

    return (
        <Modal open={open} onClose={onClose}>
            <Box sx={style}>
                <Box sx={{ p: 2, borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h6" component="h2">
                        Xem Tài liệu: {document.file_name}
                    </Typography>
                    <IconButton onClick={onClose}>
                        <CloseIcon />
                    </IconButton>
                </Box>
                <Box sx={{ flexGrow: 1, position: 'relative' }}>
                    {viewUrl ? (
                        <iframe 
                            src={viewUrl}
                            title={`View ${document.file_name}`}
                            style={{ width: '100%', height: '100%', border: 'none' }}
                            allowFullScreen
                        />
                    ) : (
                        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                            <CircularProgress />
                            <Typography sx={{ ml: 2 }}>Đang tải tệp tài liệu...</Typography>
                        </Box>
                    )}
                </Box>
            </Box>
        </Modal>
    );
};

export default ViewDocumentModal;