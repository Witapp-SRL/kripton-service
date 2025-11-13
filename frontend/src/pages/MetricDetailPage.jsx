import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axiosClient from '../api/axiosClient';
import { Typography, CircularProgress, Alert, Paper, Box, TextField, MenuItem } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const MetricDetailPage = () => {
  const { gatewayUid, channelName } = useParams();
  const [data, setData] = useState([]);
  const [range, setRange] = useState('24h'); // '24h' o '7d'
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams({
          gateway_uid: gatewayUid,
          channel_name: channelName,
          range: range,
        });
        const response = await axiosClient.get(`/metrics/mirth/history/?${params.toString()}`);
        
        // Trasforma i dati per il grafico (parsa la data)
        const chartData = response.data.map(item => ({
          ...item,
          time: new Date(item.gateway_timestamp).toLocaleString(),
        }));
        setData(chartData);
        
      } catch (err) {
        setError('Impossibile caricare lo storico.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [gatewayUid, channelName, range]); // Ricarica se i parametri cambiano

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Storico Metriche: {channelName}
      </Typography>
      <Typography variant="h6" gutterBottom>
        Gateway: {gatewayUid}
      </Typography>

      <TextField
        select
        label="Intervallo"
        value={range}
        onChange={(e) => setRange(e.target.value)}
        sx={{ mb: 2, minWidth: 150 }}
      >
        <MenuItem value="24h">Ultime 24 ore</MenuItem>
        <MenuItem value="7d">Ultimi 7 giorni</MenuItem>
      </TextField>

      {loading && <CircularProgress />}
      {error && <Alert severity="error">{error}</Alert>}
      
      {!loading && !error && (
        <Paper style={{ height: 400, width: '100%', padding: '1rem' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="received" stroke="#8884d8" />
              <Line type="monotone" dataKey="sent" stroke="#82ca9d" />
              <Line type="monotone" dataKey="error" stroke="#e74c3c" />
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      )}
    </Box>
  );
};

export default MetricDetailPage;
