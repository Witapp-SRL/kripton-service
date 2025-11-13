import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

// Importa le Pagine
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import GatewaysPage from './pages/GatewaysPage';
import LogsPage from './pages/LogsPage';
import MetricDetailPage from './pages/MetricDetailPage'; // Per i grafici

// Importa i Componenti
import Layout from './components/Layout'; // Il nostro layout con la sidebar
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  const { user } = useAuth();

  return (
    <Routes>
      {/* Rotta di Login (pubblica) */}
      <Route path="/login" element={<LoginPage />} />

      {/* Rotte Protette (con Layout) */}
      <Route 
        path="/" 
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        {/* La rotta di default è la Dashboard */}
        <Route index element={<Navigate to="/dashboard" replace />} />
        
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="gateways" element={<GatewaysPage />} />
        <Route path="logs" element={<LogsPage />} />
        
        {/* Esempio di rotta per il dettaglio di una metrica */}
        <Route path="metrics/mirth/:gatewayUid/:channelName" element={<MetricDetailPage />} />
        
        {/* Altre rotte... */}
      </Route>

      {/* Fallback per rotte non trovate */}
      <Route path="*" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
    </Routes>
  );
}

export default App;
