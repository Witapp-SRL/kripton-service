import React, { useState, useEffect } from 'react';
import axiosClient from '../api/axiosClient';
import KpiCard from '../components/KpiCard';
import { Grid, Typography, CircularProgress, Alert, Paper } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid'; // Per le tabelle

const DashboardPage = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await axiosClient.get('/dashboard/stats/');
        setStats(response.data);
      } catch (err) {
        setError('Impossibile caricare le statistiche.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!stats) return null;

  // Colonne per la tabella "Recent Exports"
  const exportColumns = [
    { field: 'pda_id', headerName: 'PDA ID', width: 150 },
    { field: 'status', headerName: 'Stato', width: 100 },
    { field: 'insert_time', headerName: 'Data', width: 200, 
      valueFormatter: (params) => new Date(params.value).toLocaleString() 
    },
    { field: 'channel_id', headerName: 'Canale', width: 130 },
  ];

  // Colonne per "Top Batch Errors"
  const batchErrorColumns = [
    { field: 'batch', headerName: 'Nome Batch', width: 200 },
    { field: 'count', headerName: 'N. Errori', width: 100 },
  ];

  // Trasforma i dati per la tabella
  const batchErrorRows = stats.top_batch_errors.map((item, index) => ({
    id: index,
    batch: item[0], // nome
    count: item[1], // conteggio
  }));

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Dashboard</Typography>
      
      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item>
          <KpiCard 
            title="Gateway Attivi" 
            value={`${stats.kpi.active_gateways} / ${stats.kpi.total_gateways}`} 
          />
        </Grid>
        <Grid item>
          <KpiCard 
            title="Errori (24h)" 
            value={stats.kpi.errors_last_24h}
            isError={stats.kpi.errors_last_24h > 0}
          />
        </Grid>
        <Grid item>
          <KpiCard 
            title="Canali da Aggiornare" 
            value={stats.kpi.channels_to_update}
            isError={stats.kpi.channels_to_update > 0}
          />
        </Grid>
        <Grid item>
          <KpiCard 
            title="Errori da Importare" 
            value={stats.kpi.import_errors_count}
            isError={stats.kpi.import_errors_count > 0}
          />
        </Grid>
      </Grid>

      {/* Tabelle */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Typography variant="h6">Top Errori Batch (24h)</Typography>
          <Paper style={{ height: 300, width: '100%' }}>
            <DataGrid
              rows={batchErrorRows}
              columns={batchErrorColumns}
              pageSize={5}
              rowsPerPageOptions={[5]}
            />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="h6">Esportazioni Recenti</Typography>
          <Paper style={{ height: 300, width: '100%' }}>
            <DataGrid
              rows={stats.recent_exports}
              columns={exportColumns}
              getRowId={(row) => row.pk} // Usa 'pk' come ID
              pageSize={5}
              rowsPerPageOptions={[5]}
            />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;
