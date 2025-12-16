import React from 'react';
import { Card, CardContent, Typography, Box, Tooltip, Grid } from '@mui/material';

const DashboardMetricCard = ({ title, value, icon, color, subtitle, tooltip }) => {
    return (
        <Grid item xs={12} sm={6} md={3}>
            <Tooltip title={tooltip || ""}>
                <Card 
                    elevation={2} 
                    sx={{ 
                        borderRadius: 3, 
                        borderLeft: `5px solid ${color}`, 
                        minHeight: 120,
                        cursor: tooltip ? 'help' : 'default',
                        transition: '0.3s',
                        '&:hover': {
                            boxShadow: `0 4px 20px 0 ${color}33`,
                        }
                    }}
                >
                    <CardContent sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box>
                            <Typography color="text.secondary" gutterBottom sx={{ fontWeight: 600, fontSize: 14 }}>
                                {title}
                            </Typography>
                            <Typography variant="h5" component="div" sx={{ fontWeight: 700, color: color }}>
                                {value}
                            </Typography>
                            {subtitle && (
                                <Typography variant="caption" color="text.secondary">
                                    {subtitle}
                                </Typography>
                            )}
                        </Box>
                        <Box sx={{ color: color, fontSize: 40, opacity: 0.8 }}>
                            {icon}
                        </Box>
                    </CardContent>
                </Card>
            </Tooltip>
        </Grid>
    );
};

export default DashboardMetricCard;