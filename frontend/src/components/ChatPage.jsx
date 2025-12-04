import React, { useState, useRef, useEffect, useMemo } from 'react'; 
import { Box, TextField, Button, CircularProgress, Typography, IconButton, Avatar, Stack, useTheme } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ThumbUpOutlinedIcon from '@mui/icons-material/ThumbUpOutlined';
import ThumbDownOutlinedIcon from '@mui/icons-material/ThumbDownOutlined';
import SchoolIcon from '@mui/icons-material/School';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close'; 
import useUserAuth from '../hooks/useUserAuth';
import { useOutletContext } from 'react-router-dom'; 

const initialHistory = [
  { id: 'chat-1', title: 'Hỏi về quy chế học vụ', date: '2025-10-01' },
  { id: 'chat-2', title: 'Yêu cầu phúc khảo điểm', date: '2025-10-05' },
  { id: 'chat-3', title: 'Thông tin về học bổng', date: '2025-10-10' },
];

const BOT_WELCOME_MESSAGE = { id: 1, text: 'Chào bạn, tôi là trợ lý ảo của TDTU. Tôi có thể giúp gì cho bạn?', sender: 'bot' };

const ChatPage = () => {
    const theme = useTheme();
    const { user, isLoadingUser, isAuthenticated } = useUserAuth();
    
    const context = useOutletContext();
    const { 
        isSidebarOpen = true, 
        toggleSidebar = () => {}, 
        activeChatId = 'chat-1', 
        setActiveChatId = () => {} 
    } = context || {}; 

    const [history] = useState(initialHistory);

    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isBotAnswered, setIsBotAnswered] = useState(false); 

    const scrollRef = useRef(null); 

    useEffect(() => { 
        if (activeChatId === undefined) return; 

        if (activeChatId === null) {
            setMessages([BOT_WELCOME_MESSAGE]);
            setIsBotAnswered(false); 
        } else {
            setIsLoading(true);
            const chatTitle = history.find(c => c.id === activeChatId)?.title || 'Cuộc trò chuyện mới';
            
            setTimeout(() => {
                const simulatedMessages = [
                    BOT_WELCOME_MESSAGE,
                    { id: 103, text: `Câu hỏi mẫu: ${chatTitle}`, sender: 'user' },
                    { id: 104, text: `Câu trả lời của bot cho câu hỏi: ${chatTitle}.`, sender: 'bot' }
                ];
                setMessages(simulatedMessages);
                setIsLoading(false);
                setIsBotAnswered(true); 
            }, 500);
        }
    }, [activeChatId, history]);


    useEffect(() => { 
      scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);
  
    const handleSend = async () => {
      if (input.trim() === '' || isBotAnswered) return; 
      
      const userMessage = { id: Date.now(), text: input, sender: 'user' };

      setMessages(prev => [...prev, userMessage]);
      setInput('');
      setIsLoading(true);

      setTimeout(() => {
        const botResponse = {
          id: Date.now() + 1,
          text: `Đây là câu trả lời cho câu hỏi "${userMessage.text}". Thông tin được trích xuất từ nguồn A và nguồn B.`,
          sender: 'bot',
          source: 'Quy định học vụ năm 2025, trang 5.'
        };
        setMessages(prev => [...prev, botResponse]);
        setIsLoading(false);
        setIsBotAnswered(true); 

        if (activeChatId === null) {
            const newChatId = 'chat-new-' + Date.now();
            setActiveChatId(newChatId); 
        }

      }, 1500);
    };
  
    const handleFeedback = (messageId, feedbackType) => {
        console.log(`Feedback cho tin nhắn ${messageId}: ${feedbackType}`);
    };
    
    const currentChatTitle = useMemo(() => { 
        const chat = history.find(c => c.id === activeChatId);
        if (chat) return chat.title;
        if (activeChatId === null || (activeChatId && typeof activeChatId === 'string' && activeChatId.startsWith('chat-new-'))) return 'Trò chuyện mới';
        return 'Đang tải...';
    }, [activeChatId, history]);

    if (isLoadingUser || !isAuthenticated || !user) {
        return null; 
    }
    
    const currentUser = user;
    const isInputDisabled = isLoading || isBotAnswered; 

    return (
      <Box sx={{ 
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
                  bgcolor: msg.sender === 'user' ? 'primary.light' : 'white',
                  color: msg.sender === 'user' ? 'white' : 'text.primary',
                  boxShadow: msg.sender === 'bot' ? '0 2px 4px rgba(0,0,0,0.05)' : 'none',
                  whiteSpace: 'pre-wrap'
                }}
              >
                <Typography variant="body1" sx={{ wordBreak: 'break-word' }}>{msg.text}</Typography>
                {msg.sender === 'bot' && msg.source && (
                  <Typography variant="caption" sx={{ mt: 1, display: 'block', color: 'text.secondary', opacity: 0.7 }}>
                    Nguồn: {msg.source}
                  </Typography>
                )}
                {msg.sender === 'bot' && msg.id > 1 && (
                  <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                    <IconButton size="small" onClick={() => handleFeedback(msg.id, 'like')} sx={{ color: 'text.secondary' }}>
                      <ThumbUpOutlinedIcon fontSize="inherit" />
                    </IconButton>
                    <IconButton size="small" onClick={() => handleFeedback(msg.id, 'dislike')} sx={{ color: 'text.secondary' }}>
                      <ThumbDownOutlinedIcon fontSize="inherit" />
                    </IconButton>
                  </Box>
                )}
              </Box>

              {msg.sender === 'user' && (
                <Avatar sx={{ bgcolor: 'secondary.main', width: 38, height: 38, fontWeight: 700 }}>
                  {currentUser.avatar}
                </Avatar>
              )}
            </Stack>
          ))}
          {isLoading && <CircularProgress sx={{ display: 'block', mx: 'auto', my: 2 }} />}
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
              placeholder={isInputDisabled ? "Vui lòng tạo cuộc trò chuyện mới để hỏi câu hỏi khác." : "Nhập câu hỏi của bạn..."}
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