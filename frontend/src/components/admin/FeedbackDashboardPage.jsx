import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Paper, Select, MenuItem, FormControl, InputLabel, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow
} from '@mui/material';
import ThumbUpAltIcon from '@mui/icons-material/ThumbUpAlt';
import ThumbDownAltIcon from '@mui/icons-material/ThumbDownAlt';

const allFeedbacks = [
  { id: 1, question: 'Học phí một tín chỉ là bao nhiêu?', answer: '...', feedback: 'like', date: '2025-10-01', status: 'new' },
  { id: 2, question: 'Lịch nghỉ Tết khi nào có?', answer: '...', feedback: 'dislike', date: '2025-10-02', status: 'new' },
  { id: 3, question: 'Thủ tục xin bảng điểm?', answer: '...', feedback: 'like', date: '2025-10-02', status: 'reviewed' },
];

const FeedbackDashboardPage = () => {
  const [stats, setStats] = useState({ totalQuestions: 1250, positiveFeedback: 850, negativeFeedback: 150 });
  const [feedbacks, setFeedbacks] = useState(allFeedbacks);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    if (filter === 'all') {
      setFeedbacks(allFeedbacks);
    } else {
      setFeedbacks(allFeedbacks.filter(fb => fb.feedback === filter));
    }
  }, [filter]);

  return (
    <Box sx={{ p: { xs: 1, md: 3 } }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, color: 'primary.main', mb: 3 }}>
        Thống kê và Phản hồi
      </Typography>

      {/* Phần thống kê */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={4}>
          <Paper sx={{
            p: 2, textAlign: 'center', borderRadius: 4, boxShadow: '0 4px 16px 0 rgba(25,118,210,0.08)'
          }}>
            <Typography variant="h6" sx={{ color: 'text.secondary' }}>Tổng số câu hỏi</Typography>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'primary.main' }}>{stats.totalQuestions}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Paper sx={{
            p: 2, textAlign: 'center', borderRadius: 4, boxShadow: '0 4px 16px 0 rgba(76,175,80,0.08)'
          }}>
            <Typography variant="h6" sx={{ color: 'success.main' }}>Phản hồi tích cực</Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
              <ThumbUpAltIcon color="success" />
              <Typography variant="h3" sx={{ fontWeight: 700, color: 'success.main' }}>{stats.positiveFeedback}</Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Paper sx={{
            p: 2, textAlign: 'center', borderRadius: 4, boxShadow: '0 4px 16px 0 rgba(244,67,54,0.08)'
          }}>
            <Typography variant="h6" sx={{ color: 'error.main' }}>Phản hồi cần cải thiện</Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
              <ThumbDownAltIcon color="error" />
              <Typography variant="h3" sx={{ fontWeight: 700, color: 'error.main' }}>{stats.negativeFeedback}</Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>Lọc phản hồi</Typography>

      {/* Phần bộ lọc */}
      <Box sx={{ mb: 3 }}>
        <FormControl sx={{ minWidth: 140, mr: 2 }}>
          <InputLabel>Loại</InputLabel>
          <Select value={filter} label="Loại" onChange={(e) => setFilter(e.target.value)} sx={{ borderRadius: 3 }}>
            <MenuItem value={'all'}>Tất cả</MenuItem>
            <MenuItem value={'like'}>Tích cực</MenuItem>
            <MenuItem value={'dislike'}>Cần cải thiện</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Bảng hiển thị feedback */}
      <TableContainer component={Paper} sx={{ borderRadius: 4, boxShadow: '0 4px 16px 0 rgba(25,118,210,0.06)' }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><b>ID</b></TableCell>
              <TableCell><b>Câu hỏi</b></TableCell>
              <TableCell><b>Loại phản hồi</b></TableCell>
              <TableCell><b>Ngày</b></TableCell>
              <TableCell><b>Trạng thái</b></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {feedbacks.map((fb) => (
              <TableRow key={fb.id} hover>
                <TableCell>{fb.id}</TableCell>
                <TableCell>{fb.question}</TableCell>
                <TableCell>
                  <Chip
                    label={fb.feedback === 'like' ? 'Tích cực' : 'Cần cải thiện'}
                    color={fb.feedback === 'like' ? 'success' : 'error'}
                    icon={fb.feedback === 'like' ? <ThumbUpAltIcon /> : <ThumbDownAltIcon />}
                    sx={{ fontWeight: 600, borderRadius: 2 }}
                  />
                </TableCell>
                <TableCell>{fb.date}</TableCell>
                <TableCell>
                  <Chip
                    label={fb.status === 'new' ? 'Mới' : 'Đã xem'}
                    color={fb.status === 'new' ? 'info' : 'default'}
                    size="small"
                    sx={{ fontWeight: 500, borderRadius: 2 }}
                  />
                </TableCell>
              </TableRow>
            ))}
            {feedbacks.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} align="center" sx={{ color: 'text.secondary', py: 4 }}>
                  Không có phản hồi nào phù hợp.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default FeedbackDashboardPage;