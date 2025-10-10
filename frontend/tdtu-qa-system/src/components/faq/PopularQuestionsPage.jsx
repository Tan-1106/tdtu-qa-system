import React from 'react';
import { Container, Typography, Accordion, AccordionSummary, AccordionDetails, Paper, Box } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';

// --- Dữ liệu mẫu ---
const mockFaqs = [
  {
    id: 1,
    question: 'Làm thế nào để xin bảng điểm?',
    answer: 'Để xin bảng điểm, sinh viên cần đăng nhập vào Cổng thông tin sinh viên, chọn mục "Dịch vụ một cửa" và làm theo hướng dẫn. Lệ phí là 10,000 VNĐ/bản.',
  },
  {
    id: 2,
    question: 'Học phí một tín chỉ là bao nhiêu?',
    answer: 'Học phí cho mỗi tín chỉ thay đổi tùy theo ngành và chương trình đào tạo. Bạn vui lòng tham khảo biểu học phí được công bố trên website của Phòng Tài chính.',
  },
  {
    id: 3,
    question: 'Thủ tục đăng ký học phần lại như thế nào?',
    answer: 'Việc đăng ký học phần lại được thực hiện trong đợt đăng ký học phần chung của mỗi học kỳ. Các môn học nợ sẽ được ưu tiên hiển thị để sinh viên lựa chọn.',
  },
];

const PopularQuestionsPage = () => {
  return (
    <Container maxWidth="md">
      <Paper
        elevation={6}
        sx={{
          p: { xs: 2, md: 4 },
          mt: 5,
          borderRadius: 5,
          boxShadow: '0 8px 32px 0 rgba(25,118,210,0.10)'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <HelpOutlineIcon color="primary" sx={{ fontSize: 38, mr: 1 }} />
          <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main', letterSpacing: 1 }}>
            Các câu hỏi thường gặp
          </Typography>
        </Box>
        <div>
          {mockFaqs.map(faq => (
            <Accordion
              key={faq.id}
              sx={{
                mt: 2,
                borderRadius: 3,
                boxShadow: '0 2px 8px 0 rgba(25,118,210,0.04)',
                '&:before': { display: 'none' },
                '&:hover': {
                  background: 'linear-gradient(90deg, #e3f2fd 60%, #f7fafd 100%)',
                  boxShadow: '0 4px 16px 0 rgba(25,118,210,0.10)'
                }
              }}
              disableGutters
            >
              <AccordionSummary
                expandIcon={<ExpandMoreIcon sx={{ color: 'primary.main' }} />}
                aria-controls={`panel${faq.id}-content`}
                id={`panel${faq.id}-header`}
                sx={{
                  borderRadius: 3,
                  minHeight: 56,
                  '& .MuiAccordionSummary-content': { alignItems: 'center', my: 1 }
                }}
              >
                <Typography fontWeight="bold" sx={{ fontSize: '1.1rem' }}>
                  {faq.question}
                </Typography>
              </AccordionSummary>
              <AccordionDetails sx={{ bgcolor: '#f7fafd', borderRadius: 2 }}>
                <Typography sx={{ color: 'text.secondary' }}>{faq.answer}</Typography>
              </AccordionDetails>
            </Accordion>
          ))}
        </div>
      </Paper>
    </Container>
  );
};

export default PopularQuestionsPage;