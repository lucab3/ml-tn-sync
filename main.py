#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script principal para sincronización de precios entre Mercado Libre y Tienda Nube.
Ajusta los precios en Tienda Nube basándose en los precios de Mercado Libre,
descontando automáticamente las comisiones.

Autor: Luca Belotti
Fecha: Mayo 2025
"""

import os
import sys
import logging
import argparse
from datetime import datetime

# Asegurar que podemos importar módulos desde src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.api.mercadolibre import MercadoLibreAPI
from src.api.tiendanube import TiendaNubeAPI
from src.core.synchronizer import PriceSynchronizer
from src.utils.logger import setup_logger

def parse_arguments():
    """Analiza los argumentos de la línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Sincronizador de precios entre Mercado Libre y Tienda Nube')
    
    parser.add_argument('--debug', action='store_true',
                        help='Activa el modo de depuración (más información en los logs)')
    
    parser.add_argument('--dry-run', action='store_true',
                        help='Ejecuta en modo simulación (no realiza cambios reales)')
    
    parser.add_argument('--config', type=str, default='config/credentials.json',
                        help='Ruta al archivo de configuración (por defecto: config/credentials.json)')
    
    return parser.parse_args()

def main():
    """Función principal"""
    # Parsear argumentos
    args = parse_arguments()
    
    # Configurar logger
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = setup_logger(log_level)
    
    # Mostrar información de inicio
    logger.info("=" * 80)
    logger.info(f"Iniciando sincronización ML-TN: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Crear instancias de las APIs
        ml_api = MercadoLibreAPI(config_path=args.config)
        tn_api = TiendaNubeAPI(config_path=args.config)
        
        # Crear sincronizador
        synchronizer = PriceSynchronizer(ml_api, tn_api, dry_run=args.dry_run)
        
        # Ejecutar sincronización
        synchronizer.sync_prices()
        
        # Mostrar información de finalización
        logger.info("Sincronización completada correctamente")
        
    except Exception as e:
        logger.error(f"Error durante la sincronización: {e}", exc_info=args.debug)
        return 1
    
    logger.info("=" * 80)
    return 0

if __name__ == "__main__":
    sys.exit(main())
