# Usa un'immagine Python 3.11 ufficiale
FROM python:3.11-slim

# Imposta variabili d'ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Crea la directory di lavoro
WORKDIR /app

# Installa le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice del progetto
COPY . .

# Espone la porta 8000
EXPOSE 8000

# Comando per avviare il server Gunicorn (produzione)
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]
