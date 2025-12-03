import React, { useState, useRef, useEffect, useMemo } from 'react'; 
import { Box, TextField, Button, CircularProgress, Typography, IconButton, Avatar, Stack, useTheme } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ThumbUpOutlinedIcon from '@mui/icons-material/ThumbUpOutlined';
import ThumbDownOutlinedIcon from '@mui/icons-material/ThumbDownOutlined';
import SchoolIcon from '@mui/icons-material/School';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close'; // Đảm bảo CloseIcon đã được import
import useUserAuth from '../hooks/useUserAuth';
import { useOutletContext } from 'react-router-dom'; 

// **********************************************
// DỮ LIỆU MẪU (BỔ SUNG)
// **********************************************
const initialHistory = [
  { id: 'chat-1', title: 'Hỏi về quy chế học vụ', date: '2025-10-01' },
  { id: 'chat-2', title: 'Yêu cầu phúc khảo điểm', date: '2025-10-05' },
  { id: 'chat-3', title: 'Thông tin về học bổng', date: '2025-10-10' },
];

const BOT_WELCOME_MESSAGE = { id: 1, text: 'Chào bạn, tôi là trợ lý ảo của TDTU. Tôi có thể giúp gì cho bạn?', sender: 'bot' };

// **********************************************
// COMPONENT CHÍNH: ChatPage
// **********************************************

const ChatPage = () => {
    // ----------------------------------------------------
    // BƯỚC 1: GỌI TẤT CẢ CÁC HOOKS TRƯỚC BẤT KỲ CÂU LỆNH RETURN NÀO
    // ----------------------------------------------------
    const theme = useTheme();
    const { user, isLoadingUser, isAuthenticated } = useUserAuth();
    
    // Lấy Context an toàn và gán giá trị mặc định cho destructuring
    const context = useOutletContext();
    const { 
        isSidebarOpen = true, 
        toggleSidebar = () => {}, 
        activeChatId = 'chat-1', 
        setActiveChatId = () => {} 
    } = context || {}; 

    // State Lịch sử (Chỉ dùng để lấy tiêu đề active)
    const [history] = useState(initialHistory);

    // State Chat (Tin nhắn hiển thị)
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    // State mới: Theo dõi xem bot đã trả lời trong cuộc trò chuyện hiện tại chưa
    const [isBotAnswered, setIsBotAnswered] = useState(false); 

    const scrollRef = useRef(null); 

    // LOGIC TẢI/KHỞI TẠO TIN NHẮN MỖI KHI activeChatId THAY ĐỔI
    useEffect(() => { 
        if (activeChatId === undefined) return; 

        if (activeChatId === null) {
            // FIX: HIỂN THỊ LỜI CHÀO MỪNG KHI LÀ CHAT MỚI
            setMessages([BOT_WELCOME_MESSAGE]);
            setIsBotAnswered(false); 
        } else {
            // Tải lịch sử chat
            setIsLoading(true);
            const chatTitle = history.find(c => c.id === activeChatId)?.title || 'Cuộc trò chuyện mới';
            
            setTimeout(() => {
                // FIX: Xóa các tin nhắn mô phỏng gây lỗi
                const simulatedMessages = [
                    BOT_WELCOME_MESSAGE, // Lời chào
                    { id: 103, text: `Câu hỏi mẫu: ${chatTitle}`, sender: 'user' },
                    { id: 104, text: `Câu trả lời của bot cho câu hỏi: ${chatTitle}.`, sender: 'bot' }
                ];
                setMessages(simulatedMessages);
                setIsLoading(false);
                // Vô hiệu hóa input ngay lập tức nếu bot đã trả lời trong lịch sử
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
      
      // 🛑 FIX: XÓA LOGIC GÁN ID TẠM THỜI Ở ĐÂY. Việc gửi tin nhắn đầu tiên
      // KHÔNG CẦN kích hoạt lại useEffect, chỉ cần hiển thị tin nhắn.
      // Việc tạo ID chat (và lưu vào history) sẽ được xử lý khi Bot trả lời
      // hoặc trong logic backend thực tế.

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
        // VÔ HIỆU HÓA INPUT SAU KHI BOT TRẢ LỜI (Q&A 1 lần)
        setIsBotAnswered(true); 

        // FIX: Nếu đây là chat mới (activeChatId là null), cần gán ID mới 
        if (activeChatId === null) {
            const newChatId = 'chat-new-' + Date.now();
            setActiveChatId(newChatId); // Gán ID cho cuộc trò chuyện mới
        }

      }, 1500);
    };
  
    const handleFeedback = (messageId, feedbackType) => {
        console.log(`Feedback cho tin nhắn ${messageId}: ${feedbackType}`);
    };
    
    const currentChatTitle = useMemo(() => { 
        const chat = history.find(c => c.id === activeChatId);
        if (chat) return chat.title;
        // FIX: Chỉ hiển thị 'Trò chuyện mới' nếu là null HOẶC ID tạm thời.
        if (activeChatId === null || (activeChatId && typeof activeChatId === 'string' && activeChatId.startsWith('chat-new-'))) return 'Trò chuyện mới';
        return 'Đang tải...';
    }, [activeChatId, history]);

    // ----------------------------------------------------
    // BƯỚC 2: KIỂM TRA ĐIỀU KIỆN SAU KHI GỌI TẤT CẢ HOOKS
    // ----------------------------------------------------
    if (isLoadingUser || !isAuthenticated || !user) {
        return null; 
    }
    
    const currentUser = user;
    // Kiểm tra trạng thái input cuối cùng
    const isInputDisabled = isLoading || isBotAnswered; 

    return (
      <Box sx={{ 
            flexGrow: 1, 
            display: 'flex', 
            flexDirection: 'column', 
            height: '100%' 
        }}> 
        
        {/* Header (Chỉ hiện trên Desktop, Mobile Header đã ở UserLayout) */}
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
          {/* 💡 FIX: Nút Đóng/Mở Sidebar cho Desktop (Luôn hiện) */}
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

        {/* Messages (Đã sửa: dùng flexGrow: 1 để chiếm hết không gian còn lại và tạo scroll) */}
        <Box sx={{
          flexGrow: 1, // Chiếm hết không gian còn lại
          overflowY: 'auto', // Cho phép cuộn
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
              {/* Avatar Bot */}
              {msg.sender === 'bot' && (
                <Avatar sx={{ bgcolor: 'primary.main', width: 38, height: 38 }}>
                  <SchoolIcon fontSize="small" />
                </Avatar>
              )}

              {/* Nội dung tin nhắn */}
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
                {/* Chỉ cho phép đánh giá nếu tin nhắn là của bot VÀ bot đã trả lời VÀ chưa đánh giá (Logic đơn giản) */}
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

              {/* User Avatar */}
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

        {/* 3. Input Footer (SỬ DỤNG STICKY) */}
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
          {/* Inner Box giữ maxWidth và căn giữa nội dung */}
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
              // Vô hiệu hóa input nếu đang loading HOẶC bot đã trả lời
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