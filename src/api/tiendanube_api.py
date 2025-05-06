#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para interactuar con la API de Tienda Nube.
Provee funcionalidades para la obtención y actualización de productos.
"""

import time
import json
import logging
import requests
from typing import Dict, List, Optional, Any, Union

logger = logging.getLogger(__name__)

class TiendaNubeAPI:
    """Cliente para la API de Tienda Nube"""
    
    def __init__(self, config_path: str = 'config/credentials.json'):
        """
        Inicializa el cliente de la API de Tienda Nube.
        
        Args:
            config_path: Ruta al archivo de configuración con credenciales
        """
        self.api_key = None
        self.user_id = None
        self.base_url = None
        self.headers = None
        self.rate_limit = 0.5  # Tiempo entre peticiones (segundos)
        
        # Cargar configuración
        self._load_config(config_path)
        
        # Configurar API
        self._setup_api()
    
    def _load_config(self, config_path: str) -> None:
        """
        Carga la configuración desde el archivo de credenciales.
        
        Args:
            config_path: Ruta al archivo de configuración
        
        Raises:
            FileNotFoundError: Si no encuentra el archivo de configuración
            KeyError: Si falta alguna credencial necesaria
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Extraer credenciales de Tienda Nube
            tn_config = config.get('tiendanube', {})
            self.api_key = tn_config.get('api_key')
            self.user_id = tn_config.get('user_id')
            
            # Verificar que todas las credenciales necesarias estén presentes
            if not all([self.api_key, self.user_id]):
                missing = []
                if not self.api_key:
                    missing.append('api_key')
                if not self.user_id:
                    missing.append('user_id')
                
                raise KeyError(f"Faltan credenciales de Tienda Nube: {', '.join(missing)}")
            
            # Configuración adicional si existe
            if 'settings' in config and 'tn_api_rate_limit' in config['settings']:
                self.rate_limit = config['settings']['tn_api_rate_limit']
            
            logger.info("Configuración de Tienda Nube cargada correctamente")
        
        except FileNotFoundError:
            logger.error(f"No se encontró el archivo de configuración: {config_path}")
            raise
        except json.JSONDecodeError:
            logger.error(f"El archivo de configuración no es un JSON válido: {config_path}")
            raise
        except KeyError as e:
            logger.error(f"Error en la configuración: {e}")
            raise
    
    def _setup_api(self) -> None:
        """Configura la URL base y los encabezados para las peticiones a la API"""
        self.base_url = f"https://api.tiendanube.com/v1/{self.user_id}"
        self.headers = {
            "Authentication": f"bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ML-TN-Sync/1.0"
        }
    
    def get_products(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los productos de Tienda Nube.
        
        Returns:
            Lista de productos con sus detalles
        """
        url = f"{self.base_url}/products"
        
        try:
            all_products = []
            page = 1
            per_page = 50
            
            logger.info("Obteniendo productos de Tienda Nube...")
            
            while True:
                # Esperar para no exceder el límite de la API
                time.sleep(self.rate_limit)
                
                logger.debug(f"Obteniendo página {page} de productos...")
                
                response = requests.get(
                    url, 
                    headers=self.headers, 
                    params={"page": page, "per_page": per_page}
                )
                response.raise_for_status()
                products = response.json()
                
                if not products:
                    break
                    
                all_products.extend(products)
                page += 1
            
            logger.info(f"Se encontraron {len(all_products)} productos en Tienda Nube")
            return all_products
        
        except Exception as e:
            logger.error(f"Error al obtener productos de Tienda Nube: {e}")
            return []
    
    def update_product_price(self, product_id: Union[str, int], price: float, 
                            dry_run: bool = False) -> bool:
        """
        Actualiza el precio de un producto en Tienda Nube.
        
        Args:
            product_id: ID del producto en Tienda Nube
            price: Nuevo precio del producto
            dry_run: Si es True, simula la actualización sin realizarla
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        url = f"{self.base_url}/products/{product_id}"
        payload = {
            "price": price
        }
        
        try:
            if dry_run:
                logger.info(f"[SIMULACIÓN] Actualizando precio del producto {product_id} a {price}")
                return True
            
            # Esperar para no exceder el límite de la API
            time.sleep(self.rate_limit)
            
            response = requests.put(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            logger.info(f"Precio actualizado para el producto {product_id} a {price}")
            return True
        
        except Exception as e:
            logger.error(f"Error al actualizar precio del producto {product_id}: {e}")
            return False
    
    def get_product_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """
        Busca un producto por SKU en Tienda Nube.
        
        Args:
            sku: SKU del producto a buscar
            
        Returns:
            Diccionario con los detalles del producto o None si no se encuentra
        """
        # Primero obtenemos todos los productos
        products = self.get_products()
        
        for product in products:
            # Verificar SKU en el producto principal
            if product.get("sku") == sku:
                return product
            
            # Verificar SKU en las variantes
            for variant in product.get("variants", []):
                if variant.get("sku") == sku:
                    return product
        
        logger.debug(f"No se encontró producto con SKU: {sku}")
        return None