#!/bin/bash
echo "--- Installazione di Docker e Docker Compose Plugin ---"

# Aggiorna i pacchetti
sudo apt-get update

# Installa i pacchetti necessari per Docker
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Aggiungi la GPG key ufficiale di Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Imposta il repository di Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installa Docker Engine, CLI, containerd e Docker Compose
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Aggiungi il tuo utente al gruppo 'docker' per evitare di usare 'sudo'
sudo usermod -aG docker $USER

echo "--------------------------------------------------------"
echo "Installazione completata."
echo "IMPORTANTE: Esegui il logout e il login per applicare"
echo "le modifiche al gruppo 'docker' o esegui: newgrp docker"
echo "--------------------------------------------------------"
