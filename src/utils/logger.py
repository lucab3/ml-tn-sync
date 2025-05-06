#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuración del sistema de logging para ML-TN-Sync.
"""

import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

# Obtener directorio de logs
ROOT_DIR = Path(__file__).parent.parent.parent
LOG_DIR = os.path.join(ROOT_DIR, "logs")

# Asegurar que el directorio de logs existe
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(level=logging.INFO, log_file=None):
    """
    Configura y devuelve un logger con formato específico.
    
    Args:
        level: Nivel de log (default: logging.INFO)
        log_file: Nombre del archivo de log (opcional)
        
    Returns:
        logging.Logger: Logger configurado
    """
    # Si no se especifica un archivo de log, usar uno con la fecha actual
    if not log_file:
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = f"ml_tn_sync_{date_str}.log"
    
    log_path = os.path.join(LOG_DIR, log_file)
    
    # Crear logger raíz
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Limpiar handlers existentes
    if logger.handlers:
        logger.handlers.clear()
    
    # Crear formato para logs
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)
    
    # Handler para archivo
    file_handler = logging.handlers.RotatingFileHandler(
        log_path, 
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)
    
    # Log inicial
    logger.info(f"Logger inicializado con nivel {logging.getLevelName(level)}")
    logger.info(f"Guardando logs en: {log_path}")
    
    return logger

def get_module_logger(name):
    """
    Obtiene un logger para un módulo específico.
    
    Args:
        name: Nombre del módulo (normalmente __name__)
        
    Returns:
        logging.Logger: Logger para el módulo
    """
    return logging.getLogger(name)
