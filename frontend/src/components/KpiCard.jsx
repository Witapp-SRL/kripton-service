import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';

const KpiCard = ({ title, value, isError = false }) => {
  return (
    <Card sx={{ minWidth: 200, textAlign: 'center' }}>
      <CardContent>
        <Typography sx={{ fontSize: 14 }} color="text.secondary" gutterBottom>
          {title}
        </Typography>
        <Typography 
          variant="h4" 
          component="div" 
          color={isError ? 'error.main' : 'text.primary'}
        >
          {value}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default KpiCard;
