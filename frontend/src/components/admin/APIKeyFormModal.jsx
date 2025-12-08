import React, { useState, useEffect } from 'react';
import { 
    Modal, Box, Typography, TextField, Button, Select, MenuItem, 
    FormControl, InputLabel, CircularProgress, Alert, Stepper, Step, StepLabel, Stack, Divider 
} from '@mui/material';
import { createApiKey, getAvailableModels, addModelToApiKey, updateApiKeyInfo } from '../../api/modelApi';

const API_PROVIDERS = ['OpenAI', 'Google'];

const style = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: { xs: '90%', sm: 500 },
    bgcolor: 'background.paper',
    boxShadow: 24,
    p: 4,
    borderRadius: 3,
};

const extractError = (error, defaultMessage) => {
    if (error.response?.data?.details) {
        return error.response.data.details;
    }
    return error.message || defaultMessage || 'Lỗi không xác định.'; 
};

const APIKeyFormModal = ({ open, onClose, onSave, editingKey = null }) => {
    const isEditMode = !!editingKey;
    const [activeStep, setActiveStep] = useState(0);

    const [name, setName] = useState(editingKey?.name || '');
    const [description, setDescription] = useState(editingKey?.description || '');
    const [apiKey, setApiKey] = useState(editingKey?.api_key || '');
    const [provider, setProvider] = useState(editingKey?.provider || '');
    
    const [availableModels, setAvailableModels] = useState([]);
    const [selectedModel, setSelectedModel] = useState(editingKey?.using_model || '');

    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [newlyCreatedKeyId, setNewlyCreatedKeyId] = useState(null);
    
    const currentKeyForFetch = newlyCreatedKeyId ? apiKey : editingKey?.api_key;
    const currentProviderForFetch = newlyCreatedKeyId ? provider : editingKey?.provider;

    const steps = ['Nhập thông tin khóa', 'Chọn Model sử dụng'];
    const displaySteps = isEditMode ? [steps[1]] : steps; 
    const activeDisplayStep = isEditMode ? 0 : activeStep;


    useEffect(() => {
        if (open) {
            if (!isEditMode) {
                setName(''); setDescription(''); setApiKey('');
                setProvider(''); setSelectedModel(''); setNewlyCreatedKeyId(null);
                setActiveStep(0);
            } else {
                setName(editingKey?.name || '');
                setDescription(editingKey?.description || '');
                setApiKey(editingKey?.api_key || '');
                setProvider(editingKey?.provider || '');
                setNewlyCreatedKeyId(editingKey?._id || null); 

                 if (editingKey?.api_key && editingKey?.provider) {
                    handleFetchModels(editingKey.api_key, editingKey.provider, true);
                 }
                 setActiveStep(1); 
            }
            setError(null);
        }
    }, [open, isEditMode, editingKey]);


    // --- HÀM LẤY MODELS ---
    const handleFetchModels = async (key, prov, isInitialLoad = false) => {
        setIsLoading(true);
        setError(null);
        try {
            const models = await getAvailableModels(key, prov);
            setAvailableModels(models);
            
            // Xử lý selected model
            if (isInitialLoad && models.includes(editingKey.using_model)) {
                 setSelectedModel(editingKey.using_model);
            } else if (models.length > 0) {
                 setSelectedModel(models[0]);
            } else {
                 setSelectedModel('');
            }
        } catch (err) {
            console.error("Error fetching models:", err);
            const backendError = extractError(err);
            setError(`Lỗi: ${backendError}. Vẫn có thể lưu Key.`);
            setAvailableModels([]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleCreateKeyAndCheckModel = async () => {
        if (!name || !provider || !apiKey) {
            setError('Vui lòng điền đủ Tên, Khóa API và Nhà cung cấp.');
            return;
        }
        
        setIsLoading(true);
        setError(null);
        
        try {
            const newKey = await createApiKey({ name, description, api_key: apiKey, provider });
            const currentKeyId = newKey._id;
            setNewlyCreatedKeyId(currentKeyId);

            await handleFetchModels(apiKey, provider);

            setActiveStep(1);

        } catch (err) {
            console.error("Key creation failed:", err);
            const backendErrorMsg = extractError(err);            
            if (backendErrorMsg.includes("API key already exists")) {
                 setError("Khóa API này đã tồn tại trong hệ thống. Vui lòng sử dụng khóa khác.");
            } else {
                 setError(backendErrorMsg || "Tạo Khóa thất bại.");
            }

        } finally {
            setIsLoading(false);
        }
    };
    
    // --- HÀM LƯU TÊN & MODEL (EDIT/ADD MODE - STEP 1) ---
    const handleSaveInfoAndModel = async () => {
        if (!selectedModel) {
            setError('Vui lòng chọn một Model để lưu.');
            return;
        }
        
        setIsLoading(true);
        setError(null);
        
        const keyId = isEditMode ? editingKey._id : newlyCreatedKeyId;

        try {
            // 1. Cập nhật tên/mô tả (Nếu là Edit Mode)
            if (isEditMode) {
                await updateApiKeyInfo(keyId, { name, description });
            }
            // 2. Lưu Model sử dụng
            await addModelToApiKey(keyId, selectedModel);
            
            onSave(); // Tải lại bảng và đóng modal

        } catch (err) {
            console.error("Error saving model:", err);
            setError(extractError(err, "Không thể lưu Model sử dụng."));
        } finally {
            setIsLoading(false);
        }
    };


    const getStepContent = (step) => {
        if (!isEditMode && step === 0) {
            return (
                <Stack spacing={2} sx={{ mt: 2 }}>
                    <TextField fullWidth label="Tên khóa (Ví dụ: Gemini Key Production)" value={name} onChange={(e) => setName(e.target.value)} disabled={isLoading}/>
                    <TextField fullWidth label="Mô tả (Tùy chọn)" value={description} onChange={(e) => setDescription(e.target.value)} disabled={isLoading}/>
                    <FormControl fullWidth disabled={isLoading}>
                        <InputLabel>Nhà cung cấp</InputLabel>
                        <Select value={provider} label="Nhà cung cấp" onChange={(e) => setProvider(e.target.value)}>
                            {API_PROVIDERS.map(p => (<MenuItem key={p} value={p}>{p}</MenuItem>))}
                        </Select>
                    </FormControl>
                    <TextField fullWidth label="Khóa API (API Key)" value={apiKey} onChange={(e) => setApiKey(e.target.value)} disabled={isLoading} type="password"/>
                </Stack>
            );
        }
        
        if (step === 1 || (isEditMode && step === 0)) { 
            return ( 
                <Stack spacing={2} sx={{ mt: 2 }}>
                    <TextField 
                        fullWidth 
                        label="Tên khóa" 
                        value={name} 
                        onChange={(e) => setName(e.target.value)} 
                        disabled={isLoading}
                    />
                    <TextField 
                        fullWidth 
                        label="Mô tả (Tùy chọn)" 
                        value={description} 
                        onChange={(e) => setDescription(e.target.value)} 
                        disabled={isLoading}
                    />
                    <Divider sx={{ my: 1 }} />
                    
                    {isLoading && availableModels.length === 0 ? <CircularProgress size={24} /> : (
                         availableModels.length > 0 ? (
                            <>
                                <Typography variant="body2" color="text.secondary">
                                    Đã tìm thấy {availableModels.length} models từ {currentProviderForFetch}.
                                </Typography>
                                <FormControl fullWidth disabled={isLoading}>
                                    <InputLabel>Chọn Model sử dụng</InputLabel>
                                    <Select value={selectedModel} label="Chọn Model sử dụng" onChange={(e) => setSelectedModel(e.target.value)}>
                                        {availableModels.map(model => (<MenuItem key={model} value={model}>{model}</MenuItem>))}
                                    </Select>
                                </FormControl>
                            </>
                        ) : (
                             !isLoading && <Alert severity="warning">Không tìm thấy Model nào hợp lệ hoặc Key API không hỗ trợ.</Alert>
                        )
                    )}
                    
                    <Divider sx={{ my: 1 }} />
                     <Typography variant="caption" sx={{ opacity: 0.7 }}>
                        Provider: {currentProviderForFetch || 'N/A'}
                    </Typography>
                </Stack>
            );
        }
        return null;
    };


    return (
        <Modal open={open} onClose={onClose}>
            <Box sx={style}>
                <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
                    {isEditMode ? "Chỉnh sửa Model & Thông tin" : "Thêm Khóa API mới"}
                </Typography>
                
                {!isEditMode && (
                    <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 3 }}>
                        {steps.map((label) => (
                            <Step key={label}>
                                <StepLabel>{label}</StepLabel>
                            </Step>
                        ))}
                    </Stepper>
                )}
                
                {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
                
                {getStepContent(activeStep)}
                
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1, mt: 4 }}>
                    <Button onClick={onClose} variant="outlined" disabled={isLoading}>Hủy</Button>
                    
                    {activeStep === 0 && !isEditMode && (
                        <Button 
                            onClick={handleCreateKeyAndCheckModel} 
                            variant="contained" 
                            disabled={isLoading || !name || !provider || !apiKey}
                        >
                            {isLoading ? <CircularProgress size={24} color="inherit" /> : 'Tạo Khóa & Kiểm tra Model'}
                        </Button>
                    )}
                    
                    {(activeStep === 1 || isEditMode) && (
                         <Button 
                            onClick={handleSaveInfoAndModel} 
                            variant="contained" 
                            disabled={isLoading || !selectedModel}
                        >
                            {isLoading ? <CircularProgress size={24} color="inherit" /> : 'Lưu thông tin và Model'}
                        </Button>
                    )}
                </Box>
            </Box>
        </Modal>
    );
};

export default APIKeyFormModal;