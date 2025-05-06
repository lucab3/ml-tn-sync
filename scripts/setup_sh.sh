#!/bin/bash

# Script de instalación para ML-TN-Sync en Linux/Mac
# Autor: Luca Belotti
# Fecha: Mayo 2025

echo "==================================================="
echo "     Instalación de ML-TN-Sync (Linux/Mac)         "
echo "==================================================="

# Detectar directorio del proyecto
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR" || { echo "Error: No se pudo acceder al directorio del proyecto"; exit 1; }

echo "Directorio del proyecto: $PROJECT_DIR"
echo

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado"
    echo "Por favor, instala Python 3.8 o superior desde https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Usando Python $PYTHON_VERSION"

# Crear entorno virtual
echo "Creando entorno virtual..."
python3 -m venv ml_tn_sync_env

# Activar entorno virtual
echo "Activando entorno virtual..."
source ml_tn_sync_env/bin/activate

# Verificar activación
if [ $? -ne 0 ]; then
    echo "Error: No se pudo activar el entorno virtual"
    exit 1
fi

# Actualizar pip
echo "Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: No se pudieron instalar las dependencias"
    exit 1
fi

# Verificar estructura de carpetas
echo "Verificando estructura de carpetas..."
mkdir -p logs

# Crear archivo de configuración si no existe
if [ ! -f "config/credentials.json" ]; then
    echo "Creando archivo de configuración..."
    cp config/credentials.example.json config/credentials.json
    
    echo
    echo "⚠️  IMPORTANTE: Edita el archivo config/credentials.json"
    echo "   y agrega tus credenciales de Mercado Libre y Tienda Nube."
fi

echo
echo "✅ Instalación completada correctamente"
echo
echo "Para activar el entorno virtual, ejecuta:"
echo "  source ml_tn_sync_env/bin/activate"
echo
echo "Para ejecutar el sincronizador:"
echo "  python main.py"
echo "  o"
echo "  ./scripts/run.sh"
echo
