/tuo_progetto/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── project/
│   ├── portal_app/
│   └── manage.py
├── frontend/
│   └── Dockerfile
├── .env
├── docker-compose.yml
└── install_docker_ubuntu.sh


Salva il file.

Rendilo eseguibile: chmod +x install_docker_ubuntu.sh

Eseguilo: ./install_docker_ubuntu.sh

Esegui il logout e il login per attivare i permessi di gruppo.




# Questo crea la cartella 'frontend' con un template React
npm create vite@latest frontend -- --template react

cd frontend

# Installa le dipendenze fondamentali
npm install axios react-router-dom@6

# Installa la libreria di componenti MUI (per tabelle, card, bottoni)
npm install @mui/material @emotion/react @emotion/styled @mui/x-data-grid

# Installa la libreria per i grafici
npm install recharts

#Installazione
docker compose up --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
