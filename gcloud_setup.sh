#!/bin/bash

# Colores para output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Configurando entorno de Google Cloud para QA Bot...${NC}"

# Verificar si se pasó el ID del proyecto como argumento
if [ -z "$1" ]; then
    echo "Error: Debes proporcionar el ID de tu proyecto."
    echo "Uso: ./gcloud_setup.sh [PROJECT_ID]"
    exit 1
fi

PROJECT_ID=$1

echo -e "${GREEN}1. Iniciando sesión en Google Cloud...${NC}"
gcloud auth login

echo -e "${GREEN}2. Configurando el proyecto: $PROJECT_ID...${NC}"
gcloud config set project $PROJECT_ID

echo -e "${GREEN}3. Habilitando APIs necesarias (Cloud Build y Cloud Run)...${NC}"
gcloud services enable cloudbuild.googleapis.com run.googleapis.com

echo -e "${GREEN}4. Configurando autenticación de Docker...${NC}"
gcloud auth configure-docker

echo -e "${GREEN}¡Configuración completada! Ahora puedes proceder con el despliegue.${NC}"
