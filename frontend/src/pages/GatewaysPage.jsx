import React, { useState, useEffect } from 'react';
import axiosClient from '../api/axiosClient';
import { Paper, Box, Typography, CircularProgress, Alert } from '@mui/material';
import { DataGrid, GridToolbar } from '@mui/x-data-grid';

// Funzione helper per formattare lo stato
const getStatusChip = (lastCall) => {
  if (!lastCall) {
    return { label: 'Mai', color: 'grey.500' };
  }
  
  const lastCallDate = new Date(lastCall);
  const now = new Date();
  const diffMinutes = (now - lastCallDate) / (1000 * 60);

  if (diffMinutes <= 15) {
    return { label: 'Online', color: 'success.main' };
  } else if (diffMinutes <= 60) {
    return { label: 'Inattivo', color: 'warning.main' };
  } else {
    return { label: 'Offline', color: 'error.main' };
  }
};

const GatewaysPage = () => {
  const [gateways, setGateways] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Colonne per DataGrid
  const columns = [
    { field: 'pk', headerName: 'ID', width: 70 },
    { field: 'gtw_name', headerName: 'Nome', width: 150 },
    { field: 'gtw_uid', headerName: 'Gateway UID', width: 250 },
    { 
      field: 'last_date_call', 
      headerName: 'Ultimo Contatto', 
      width: 200,
      valueFormatter: (params) => {
        return params.value ? new Date(params.value).toLocaleString() : 'N/A';
      }
    },
    { 
      field: 'status', 
      headerName: 'Stato', 
      width: 120,
      renderCell: (params) => {
        // Usiamo 'last_date_call' per determinare lo stato
        const status = getStatusChip(params.row.last_date_call);
        return (
          <Box 
            sx={{ 
              color: status.color, 
              border: `1px solid ${status.color}`, 
              borderRadius: '16px', 
              padding: '4px 8px',
              backgroundColor: `${status.color.split('.')[0]}.lighter`, // Funziona se usi un tema MUI completo
            }}
          >
            {status.label}
          </Box>
        );
      }
    },
    { field: 'sw_version', headerName: 'Ver. SW', width: 100 },
    { field: 'current_version', headerName: 'Ver. Attuale', width: 100 },
    { field: 'gateway_description', headerName: 'Descrizione', width: 250 },
  ];

  useEffect(() => {
    const fetchGateways = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await axiosClient.get('/gateways/');
        setGateways(response.data.results || []); // Gestisce la paginazione
      } catch (err) {
        setError('Impossibile caricare i gateway.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchGateways();
  }, []); // Esegui solo al caricamento

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Gestione Gateway</Typography>
      
      {/* Tabella dei Gateway */}
      <Paper style={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={gateways}
          columns={columns}
          getRowId={(row) => row.pk} // Specifica 'pk' come ID univoco
          loading={loading}
          components={{ Toolbar: GridToolbar }} // Aggiunge filtri, export, etc.
        />
      </Paper>
    </Box>
  );
};

export default GatewaysPage;
