#!/bin/bash

# Script de ejecución para ML-TN-Sync en Linux/Mac
# Autor: Luca Belotti
# Fecha: Mayo 2025

# Detectar directorio del proyecto
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR" || { echo "Error: No se pudo acceder al directorio del proyecto"; exit 1; }

# Verificar si el entorno virtual existe
if [ ! -d "ml_tn_sync_env" ]; then
    echo "Error: Entorno virtual no encontrado"
    echo "Ejecuta primero el script de instalación: ./scripts/setup.sh"
    exit 1
fi

# Activar entorno virtual
source ml_tn_sync_env/bin/activate

# Procesar argumentos
DRY_RUN=""
DEBUG=""

for arg in "$@"
do
    case $arg in
        --dry-run)
        DRY_RUN="--dry-run"
        shift
        ;;
        --debug)
        DEBUG="--debug"
        shift
        ;;
        *)
        # Argumento desconocido
        ;;
    esac
done

# Ejecutar el sincronizador
echo "Ejecutando ML-TN-Sync..."
python main.py $DRY_RUN $DEBUG

# Guardar código de salida
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Sincronización completada correctamente"
else
    echo "❌ La sincronización falló con código de error: $EXIT_CODE"
    echo "Revisa los logs para más detalles"
fi

# Desactivar entorno virtual
deactivate

exit $EXIT_CODE
