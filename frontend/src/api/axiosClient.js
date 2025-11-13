import axios from 'axios';

const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

// Interceptor: Aggiunge il token JWT a OGNI richiesta
axiosClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// (Opzionale, ma consigliato) Gestione del refresh del token
// ... logica per usare il refresh_token ...

export default axiosClient;
