import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react'; 
import { Box, TextField, Button, CircularProgress, Typography, IconButton, Avatar, Stack, useTheme, Alert } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ThumbUpOutlinedIcon from '@mui/icons-material/ThumbUpOutlined';
import ThumbDownOutlinedIcon from '@mui/icons-material/ThumbDownOutlined';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import ThumbDownIcon from '@mui/icons-material/ThumbDown';
import SchoolIcon from '@mui/icons-material/School';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close'; 
import { useOutletContext } from 'react-router-dom'; 

import useUserAuth from '../hooks/useUserAuth';
import { sendQuery, sendFeedback } from '../api/chatApi'; 
import axiosInstance from '../axiosInstance';


const BOT_WELCOME_MESSAGE = { id: 1, text: 'Chào bạn, tôi là trợ lý ảo của TDTU. Tôi có thể giúp gì cho bạn?', sender: 'bot' };

const ChatPage = () => {
    const theme = useTheme();
    const { user, isLoadingUser, isAuthenticated } = useUserAuth();
    
    // Lấy context từ UserLayout
    const context = useOutletContext();
    const { 
        isSidebarOpen = true, 
        toggleSidebar = () => {}, 
        activeChatId = null, 
        setActiveChatId = () => {},
        setReloadHistoryKey = () => {}
    } = context || {}; 

    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showLoadingIndicator, setShowLoadingIndicator] = useState(false);
    const [fetchError, setFetchError] = useState(null);

    const scrollRef = useRef(null); 
    const chatContentRef = useRef(null);

    const loadChatSession = useCallback(async (sessionId) => {
        if (!sessionId) {
            setMessages([BOT_WELCOME_MESSAGE]); 
            setFetchError(null);
            return;
        }
        
        setIsLoading(true);
        setFetchError(null);

        try {
            const record = await axiosInstance.get(`/qa/${sessionId}`); 
            const qaRecord = record.data.details;
            
            const botAnswer = qaRecord.answer || qaRecord.manager_answer;
            const botSource = qaRecord.source || 'N/A'; 
            
            const sessionMessages = [
                BOT_WELCOME_MESSAGE,
                { 
                    id: `${sessionId}-q`, 
                    text: qaRecord.question, 
                    sender: 'user' 
                },
                { 
                    id: sessionId,
                    qa_record_id: sessionId,
                    text: botAnswer, 
                    sender: 'bot',
                    feedback: qaRecord.feedback, 
                    source: botSource 
                }
            ];
            setMessages(sessionMessages);

        } catch (error) {
            setMessages([BOT_WELCOME_MESSAGE]);
            console.error("Failed to load chat session:", error);
            setFetchError("Không thể tải lịch sử trò chuyện này.");
        } finally {
            setIsLoading(false);
        }
    }, []);


    useEffect(() => { 
        if (activeChatId !== undefined) {
            setInput('');
            loadChatSession(activeChatId);
        }
    }, [activeChatId, loadChatSession]);


    useEffect(() => { 
      scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isLoading]);
    
    // Gửi tin nhắn mới (Tích hợp RAG API)
    const handleSend = async () => {
        if (input.trim() === '' || isLoading) return; 

        const question = input.trim();
        const userMessage = { id: Date.now(), text: question, sender: 'user' };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        const timer = setTimeout(() => {
            setShowLoadingIndicator(true);
        }, 300);

        try {
            const result = await sendQuery(question); 

            let botAnswerText;
            let newQaRecordId = null;
            if (result && result.answer && result.question_id) {
                botAnswerText = result.answer;
                newQaRecordId = result.question_id; 
            } else {
                throw new Error("Invalid response format from bot (missing question_id or answer).");
            }
            
            // Format câu trả lời
            const botResponse = {
                id: newQaRecordId, 
                text: botAnswerText, 
                sender: 'bot',
                source: 'N/A', 
                qa_record_id: newQaRecordId, 
                feedback: null
            };
            
            setMessages(prev => [...prev, botResponse]);
            
            if (activeChatId === null && newQaRecordId !== null) {
                setActiveChatId(newQaRecordId); 
                setReloadHistoryKey(Date.now());
            }

        } catch (error) {
            console.error("Error sending query:", error);
            
            let errorMessage = error.message;
            if (error.response && error.response.data && error.response.data.message) {
                 errorMessage = error.response.data.message;
            }

            setMessages(prev => [...prev, { 
                id: Date.now() + 1, 
                text: `Lỗi: Không thể kết nối hoặc xử lý câu hỏi. (${errorMessage || 'Lỗi không xác định'})`, 
                sender: 'bot' 
            }]);
        } finally {
            clearTimeout(timer);
            setShowLoadingIndicator(false);
            setIsLoading(false);
        }
    };
    
    // Gửi Feedback
    const handleFeedback = async (qa_record_id, feedbackType) => {
        if (isLoading) return;
        try {
            await sendFeedback(qa_record_id, feedbackType);
            
            setMessages(prevMessages => 
                prevMessages.map(msg => 
                    msg.id === qa_record_id ? { ...msg, feedback: feedbackType } : msg
                )
            );

        } catch (error) {
            setFetchError("Không thể gửi phản hồi. Vui lòng kiểm tra kết nối.");
        }
    };
    
    const currentChatTitle = useMemo(() => { 
        if (activeChatId === null) return 'Trò chuyện mới';
        if (isLoading) return '...';
        const initialUserMsg = messages.find(msg => msg.id === `${activeChatId}-q`);
        return initialUserMsg ? initialUserMsg.text : ' ';
    }, [activeChatId, messages, isLoading]);


    if (isLoadingUser || !isAuthenticated || !user) {
        return null; 
    }
    
    const currentUser = user;
    const isViewingHistory = activeChatId !== null; 
    const isInputDisabled = isLoading || isViewingHistory; 
    const userAvatarLetter = currentUser.name ? currentUser.name[0] : '?';

    return (
      <Box 
        ref={chatContentRef}
        sx={{ 
            flexGrow: 1, 
            display: 'flex', 
            flexDirection: 'column', 
            height: '100%' 
        }}> 
        
        <Box sx={{ 
          p: 2, 
          bgcolor: 'white', 
          display: { xs: 'none', md: 'flex' },
          alignItems: 'center', 
          gap: 1.5, 
          borderBottom: '1px solid #e3e3e3',
          position: 'sticky', 
          top: 0,
          zIndex: 10,
          flexShrink: 0 
        }}>
          <IconButton 
              size="large" 
              onClick={toggleSidebar} 
              sx={{ color: 'text.primary' }}
          >
            {isSidebarOpen ? <CloseIcon /> : <MenuIcon />}
          </IconButton>
          
          <Typography variant="h6" sx={{ fontWeight: 600, flexGrow: 1, color: 'primary.main' }}>
            {currentChatTitle} 
          </Typography>
        </Box>

        <Box sx={{
          flexGrow: 1, 
          overflowY: 'auto', 
          p: { xs: 1.5, md: 4 },
          maxWidth: '850px', 
          width: '100%',
          mx: 'auto', 
          pt: { xs: 1.5, md: 8 },
          pb: 4 
        }}>
            {fetchError && <Alert severity="error" sx={{ mb: 2 }}>{fetchError}</Alert>}
          {messages.map((msg) => (
            <Stack
              key={msg.id}
              direction="row"
              spacing={2}
              sx={{
                mb: 3, 
                justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                alignItems: 'flex-start',
                mx: 'auto' 
              }}
            >
              {msg.sender === 'bot' && (
                <Avatar sx={{ bgcolor: 'primary.main', width: 38, height: 38 }}>
                  <SchoolIcon fontSize="small" />
                </Avatar>
              )}

              <Box
                sx={{
                  p: 2,
                  borderRadius: 2,
                  maxWidth: { xs: '90%', md: '75%' },
                  bgcolor: msg.sender === 'user' ? 'primary.main' : 'white', 
                  color: msg.sender === 'user' ? 'white' : 'text.primary',
                  boxShadow: msg.sender === 'bot' ? '0 2px 4px rgba(0,0,0,0.05)' : 'none',
                  whiteSpace: 'pre-wrap'
                }}
              >
                <Typography variant="body1">{msg.text}</Typography>

                                
                {msg.sender === 'bot' && msg.qa_record_id && (
                  <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                    <IconButton 
                        size="small" 
                        onClick={() => handleFeedback(msg.qa_record_id, 'Like')} 
                        sx={{ color: msg.feedback === 'Like' ? 'success.main' : 'text.secondary' }}
                    >
                        {msg.feedback === 'Like' 
                            ? <ThumbUpIcon fontSize="inherit" /> 
                            : <ThumbUpOutlinedIcon fontSize="inherit" />}
                    </IconButton>
                    <IconButton 
                        size="small" 
                        onClick={() => handleFeedback(msg.qa_record_id, 'Dislike')} 
                        sx={{ color: msg.feedback === 'Dislike' ? 'error.main' : 'text.secondary' }}
                    >
                        {msg.feedback === 'Dislike' 
                            ? <ThumbDownIcon fontSize="inherit" /> 
                            : <ThumbDownOutlinedIcon fontSize="inherit" />}
                    </IconButton>
                  </Box>
                )}
              </Box>

              {msg.sender === 'user' && (
                <Avatar sx={{ bgcolor: 'secondary.main', width: 38, height: 38, fontWeight: 700 }}>
                  {userAvatarLetter}
                </Avatar>
              )}
            </Stack>
          ))}
            {showLoadingIndicator && (
            <Stack 
                direction="row" 
                spacing={2} 
                alignItems="flex-start" 
                sx={{ 
                mb: 3, 
                mr: 'auto',
                maxWidth: '75%',
                px: 1
                }}
            >
                <Avatar sx={{ bgcolor: 'primary.main', width: 38, height: 38 }}>
                    <SchoolIcon fontSize="small" />
                </Avatar>

                <Box
                sx={{
                    p: 2,
                    pl: 2.5,
                    pr: 2.5,
                    borderRadius: 3,
                    bgcolor: '#ffffff',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                    display: 'inline-flex',
                    alignItems: 'center',
                    border: '1px solid #e9e9e9',
                }}
                >
                <Box className="typing-dots-container">
                    <span className="typing-dot"></span>
                    <span className="typing-dot"></span>
                    <span className="typing-dot"></span>
                </Box>
                </Box>
            </Stack>
            )}

          <div ref={scrollRef} />
        </Box>

        <Box sx={{ 
            position: 'sticky',
            bottom: 0,
            flexShrink: 0,
            
            px: { xs: 1.5, md: 2 },
            py: { xs: 1.5, md: 2 },
            width: '100%',
            display: 'flex',
            justifyContent: 'center',
            borderTop: '1px solid #e3e3e3',
            bgcolor: 'white',
            zIndex: 9 
        }}>
          <Box sx={{ width: '100%', maxWidth: '850px', display: 'flex', alignItems: 'center' }}>
            <TextField
              fullWidth
                placeholder={isViewingHistory ? "Bạn đang xem lịch sử trò chuyện" : "Nhập câu hỏi của bạn..."} // Cập nhật placeholder              
                value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !isInputDisabled && handleSend()}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: '15px', 
                  bgcolor: '#f1f1f1'
                }
              }}
              disabled={isInputDisabled}
            />
            <Button
              variant="contained"
              onClick={handleSend}
              sx={{
                ml: 1,
                borderRadius: '15px',
                minWidth: '56px',
                height: '56px',
                  background: 'linear-gradient(135deg, #1976d2 30%, #42a5f5 90%)',
                  boxShadow: '0 2px 6px rgba(25, 118, 210, 0.4)',
              }}
              disabled={isInputDisabled || input.trim() === ''}
            >
              <SendIcon />
            </Button>
          </Box>
        </Box>
      </Box>
    );
};

export default ChatPage;    