import React, { useState, useEffect } from 'react';
import axiosClient from '../api/axiosClient';
import { Paper, TextField, MenuItem, Box, Typography } from '@mui/material';
import { DataGrid, GridToolbar } from '@mui/x-data-grid';

const LogsPage = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Stati per i filtri
  const [filterLevel, setFilterLevel] = useState(''); // 'ERROR', 'WARNING', ''
  const [filterSearch, setFilterSearch] = useState('');

  // Colonne per DataGrid
  const columns = [
    { field: 'id', headerName: 'ID', width: 90 },
    { field: 'datetime', headerName: 'Timestamp', width: 200, 
      valueFormatter: (params) => new Date(params.value).toLocaleString() 
    },
    { field: 'level', headerName: 'Livello', width: 100 },
    { field: 'batch_name', headerName: 'Batch', width: 150 }, // Il nostro campo virtuale
    { field: 'action', headerName: 'Azione', width: 100 },
    { field: 'description', headerName: 'Descrizione', width: 400 },
    { field: 'doc_channel', headerName: 'Canale', width: 130 },
  ];

  useEffect(() => {
    const fetchLogs = async () => {
      setLoading(true);
      try {
        // Costruisci i parametri di query
        const params = new URLSearchParams();
        if (filterLevel) params.append('level', filterLevel);
        if (filterSearch) params.append('search', filterSearch);

        const response = await axiosClient.get(`/logs/?${params.toString()}`);
        setLogs(response.data.results || []); // Gestisce la paginazione
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    // Attendi 500ms prima di lanciare la ricerca (debounce)
    const timerId = setTimeout(fetchLogs, 500);
    return () => clearTimeout(timerId);
    
  }, [filterLevel, filterSearch]); // Ricarica i dati quando i filtri cambiano

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Log Eventi</Typography>
      
      {/* Box dei Filtri */}
      <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
        <TextField
          select
          label="Livello"
          value={filterLevel}
          onChange={(e) => setFilterLevel(e.target.value)}
          sx={{ minWidth: 150 }}
        >
          <MenuItem value="">Tutti</MenuItem>
          <MenuItem value="ERROR">Error</MenuItem>
          <MenuItem value="WARNING">Warning</MenuItem>
          <MenuItem value="INFO">Info</MenuItem>
        </TextField>
        <TextField
          label="Cerca..."
          value={filterSearch}
          onChange={(e) => setFilterSearch(e.target.value)}
          sx={{ minWidth: 300 }}
        />
      </Box>
      
      {/* Tabella dei Log */}
      <Paper style={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={logs}
          columns={columns}
          loading={loading}
          pagination // Abilita paginazione (se il backend la supporta)
          // Se usi la paginazione di Django, dovrai implementare
          // la modalità "server" di DataGrid.
          components={{ Toolbar: GridToolbar }} // Aggiunge filtri, export, etc.
        />
      </Paper>
    </Box>
  );
};

export default LogsPage;
