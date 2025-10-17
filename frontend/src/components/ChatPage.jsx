import React, { useState, useRef, useEffect } from 'react';
import { Box, TextField, Button, CircularProgress, Typography, Paper, IconButton, Avatar, Stack } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ThumbUpOutlinedIcon from '@mui/icons-material/ThumbUpOutlined';
import ThumbDownOutlinedIcon from '@mui/icons-material/ThumbDownOutlined';
import SchoolIcon from '@mui/icons-material/School';

const ChatPage = () => {
  const [messages, setMessages] = useState([
    { id: 1, text: 'Chào bạn, tôi là trợ lý ảo của TDTU. Tôi có thể giúp gì cho bạn?', sender: 'bot' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSend = async () => {
    if (input.trim() === '') return;
    const userMessage = { id: Date.now(), text: input, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    setTimeout(() => {
      const botResponse = {
        id: Date.now() + 1,
        text: `Đây là câu trả lời cho câu hỏi "${input}". Thông tin được trích xuất từ nguồn A và nguồn B.`,
        sender: 'bot',
        source: 'Quy định học vụ năm 2025, trang 5.'
      };
      setMessages(prev => [...prev, botResponse]);
      setIsLoading(false);
    }, 2000);
  };

  const handleFeedback = (messageId, feedbackType) => {
    console.log(`Feedback cho tin nhắn ${messageId}: ${feedbackType}`);
  };

  return (
    <Paper elevation={6} sx={{
      height: { xs: '90vh', md: 'calc(100vh - 180px)' },
      maxWidth: '900px',
      margin: { xs: 1, md: '32px auto' },
      display: 'flex',
      flexDirection: 'column',
      borderRadius: 6,
      overflow: 'hidden',
      boxShadow: '0 8px 32px 0 rgba(25,118,210,0.10)'
    }}>
      {/* Header */}
      <Box sx={{
        p: 2.5,
        bgcolor: 'linear-gradient(90deg, #1976d2 60%, #42a5f5 100%)',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        gap: 1.5,
        boxShadow: '0 2px 8px 0 rgba(25,118,210,0.10)'
      }}>
        <Avatar sx={{ bgcolor: 'white', color: 'primary.main', width: 44, height: 44 }}>
          <SchoolIcon fontSize="medium" />
        </Avatar>
        <Typography variant="h5" sx={{ fontWeight: 700, letterSpacing: 1 }}>
          Trợ lý ảo TDTU
        </Typography>
      </Box>

      {/* Messages */}
      <Box sx={{
        flexGrow: 1,
        overflowY: 'auto',
        p: { xs: 1.5, md: 3 },
        bgcolor: 'background.default'
      }}>
        {messages.map((msg) => (
          <Stack
            key={msg.id}
            direction="row"
            spacing={2}
            sx={{
              mb: 2,
              justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              alignItems: 'flex-end'
            }}
          >
            {msg.sender === 'bot' && (
              <Avatar sx={{ bgcolor: 'primary.main', width: 38, height: 38 }}>
                <SchoolIcon fontSize="small" />
              </Avatar>
            )}
            <Paper
              elevation={msg.sender === 'user' ? 3 : 1}
              sx={{
                p: 2,
                borderRadius: msg.sender === 'user'
                  ? '22px 22px 8px 22px'
                  : '22px 22px 22px 8px',
                maxWidth: { xs: '80%', md: '65%' },
                bgcolor: msg.sender === 'user'
                  ? 'primary.main'
                  : 'background.paper',
                color: msg.sender === 'user'
                  ? 'white'
                  : 'text.primary',
                boxShadow: msg.sender === 'user'
                  ? '0 4px 16px 0 rgba(25,118,210,0.10)'
                  : undefined,
                position: 'relative'
              }}
            >
              <Typography variant="body1" sx={{ wordBreak: 'break-word' }}>{msg.text}</Typography>
              {msg.sender === 'bot' && msg.source && (
                <Typography variant="caption" sx={{ mt: 1, display: 'block', color: 'text.secondary' }}>
                  Nguồn: {msg.source}
                </Typography>
              )}
              {msg.sender === 'bot' && msg.id > 1 && (
                <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                  <IconButton size="small" onClick={() => handleFeedback(msg.id, 'like')}>
                    <ThumbUpOutlinedIcon fontSize="inherit" />
                  </IconButton>
                  <IconButton size="small" onClick={() => handleFeedback(msg.id, 'dislike')}>
                    <ThumbDownOutlinedIcon fontSize="inherit" />
                  </IconButton>
                </Box>
              )}
            </Paper>
            {msg.sender === 'user' && (
              <Avatar sx={{ bgcolor: 'secondary.main', width: 38, height: 38, fontWeight: 700 }}>
                Bạn
              </Avatar>
            )}
          </Stack>
        ))}
        {isLoading && <CircularProgress sx={{ display: 'block', mx: 'auto', my: 2 }} />}
        <div ref={scrollRef} />
      </Box>

      {/* Input */}
      <Box sx={{
        p: { xs: 1.5, md: 2 },
        display: 'flex',
        borderTop: '1px solid #e3e3e3',
        bgcolor: 'background.paper'
      }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Nhập câu hỏi của bạn..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !isLoading && handleSend()}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: '30px',
              bgcolor: '#f7fafd'
            }
          }}
          disabled={isLoading}
        />
        <Button
          variant="contained"
          onClick={handleSend}
          sx={{
            ml: 2,
            borderRadius: '50%',
            minWidth: '56px',
            height: '56px',
            boxShadow: '0 2px 8px 0 rgba(25,118,210,0.10)'
          }}
          disabled={isLoading || input.trim() === ''}
        >
          <SendIcon />
        </Button>
      </Box>
    </Paper>
  );
};

export default ChatPage;