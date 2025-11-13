import React, { createContext, useState, useContext } from 'react';
import axiosClient from '../api/axiosClient';
import { jwtDecode } from 'jwt-decode'; // Installa con: npm install jwt-decode

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const token = localStorage.getItem('access_token');
    if (token) return jwtDecode(token);
    return null;
  });
  const [token, setToken] = useState(localStorage.getItem('access_token'));

  const login = async (username, password) => {
    try {
      const response = await axiosClient.post('/token/', {
        username,
        password,
      });
      
      const accessToken = response.data.access;
      const refreshToken = response.data.refresh;
      
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
      
      const userData = jwtDecode(accessToken);
      setUser(userData);
      setToken(accessToken);
      
      return true;
    } catch (error) {
      console.error('Login fallito:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook personalizzato per un facile accesso
export const useAuth = () => {
  return useContext(AuthContext);
};
