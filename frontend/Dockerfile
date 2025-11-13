# --- FASE 1: Build ---
# Usiamo Node.js 20 per costruire l'app React
FROM node:20-alpine AS build
WORKDIR /app

# Copia package.json e installa le dipendenze
COPY package.json package-lock.json ./
RUN npm install

# Copia il resto del codice sorgente e costruisce l'app
COPY . .
RUN npm run build

# --- FASE 2: Serve ---
# Usiamo Nginx per servire i file statici
FROM nginx:1.25-alpine
WORKDIR /usr/share/nginx/html

# Rimuove il contenuto di default
RUN rm -rf ./*

# Copia i file buildati dalla fase precedente
COPY --from=build /app/build .

# (Opzionale, ma consigliato) Copia una configurazione Nginx
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Espone la porta 80
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
