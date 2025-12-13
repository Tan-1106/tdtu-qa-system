export const extractError = (error, defaultMessage = 'Lỗi không xác định.') => {
    return error.response?.data?.details || error.message || defaultMessage;
};