#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuración general para el sincronizador ML-TN-Sync.
Este módulo contiene variables de configuración que no son secretas 
y no requieren estar en credentials.json.
"""

import os
import json
from pathlib import Path

# Rutas importantes
ROOT_DIR = Path(__file__).parent.parent
CONFIG_DIR = ROOT_DIR / "config"
LOG_DIR = ROOT_DIR / "logs"

# Asegurar que el directorio de logs existe
os.makedirs(LOG_DIR, exist_ok=True)

# Nombre del archivo de log actual
LOG_FILENAME = "ml_tn_sync.log"

# Configuración por defecto
DEFAULT_CONFIG = {
    "settings": {
        # Porcentaje de comisión de Mercado Libre
        "ml_commission": 13.0,
        
        # Tiempo entre peticiones a la API de Mercado Libre (en segundos)
        "ml_api_rate_limit": 0.5,
        
        # Tiempo entre peticiones a la API de Tienda Nube (en segundos)
        "tn_api_rate_limit": 0.5,
        
        # Emparejar productos por SKU (si es False, intenta emparejar por nombre)
        "match_by_sku": True,
        
        # Decimales para redondear precios
        "price_round_digits": 2,
        
        # Diferencia mínima de precio para realizar actualización (para evitar cambios innecesarios)
        "min_price_diff": 0.01
    }
}

def load_settings(config_path=None):
    """
    Carga la configuración combinando los valores por defecto con los del archivo.
    
    Args:
        config_path: Ruta al archivo de configuración (opcional)
        
    Returns:
        dict: Configuración combinada
    """
    config = DEFAULT_CONFIG.copy()
    
    if not config_path:
        config_path = os.path.join(CONFIG_DIR, "credentials.json")
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                
            # Actualizar configuración con valores del usuario
            if 'settings' in user_config:
                config['settings'].update(user_config['settings'])
    except Exception as e:
        print(f"Error al cargar configuración: {e}")
    
    return config

# Cargar configuración al importar el módulo
SETTINGS = load_settings().get('settings', {})
