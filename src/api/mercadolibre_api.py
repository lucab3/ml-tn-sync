#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para interactuar con la API de Mercado Libre.
Provee funcionalidades para autenticación y obtención de productos.
"""

import time
import json
import logging
import requests
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class MercadoLibreAPI:
    """Cliente para la API de Mercado Libre"""
    
    def __init__(self, config_path: str = 'config/credentials.json'):
        """
        Inicializa el cliente de la API de Mercado Libre.
        
        Args:
            config_path: Ruta al archivo de configuración con credenciales
        """
        self.base_url = "https://api.mercadolibre.com"
        self.access_token = None
        self.refresh_token = None
        self.client_id = None
        self.client_secret = None
        self.user_id = None
        self.rate_limit = 0.5  # Tiempo entre peticiones (segundos)
        
        # Cargar configuración
        self._load_config(config_path)
        
        # Actualizar token
        self.refresh_access_token()
    
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
            
            # Extraer credenciales de Mercado Libre
            ml_config = config.get('mercadolibre', {})
            self.client_id = ml_config.get('client_id')
            self.client_secret = ml_config.get('client_secret')
            self.refresh_token = ml_config.get('refresh_token')
            self.user_id = ml_config.get('user_id')
            
            # Verificar que todas las credenciales necesarias estén presentes
            if not all([self.client_id, self.client_secret, self.refresh_token, self.user_id]):
                missing = []
                if not self.client_id:
                    missing.append('client_id')
                if not self.client_secret:
                    missing.append('client_secret')
                if not self.refresh_token:
                    missing.append('refresh_token')
                if not self.user_id:
                    missing.append('user_id')
                
                raise KeyError(f"Faltan credenciales de Mercado Libre: {', '.join(missing)}")
            
            # Configuración adicional si existe
            if 'settings' in config and 'ml_api_rate_limit' in config['settings']:
                self.rate_limit = config['settings']['ml_api_rate_limit']
            
            logger.info("Configuración de Mercado Libre cargada correctamente")
        
        except FileNotFoundError:
            logger.error(f"No se encontró el archivo de configuración: {config_path}")
            raise
        except json.JSONDecodeError:
            logger.error(f"El archivo de configuración no es un JSON válido: {config_path}")
            raise
        except KeyError as e:
            logger.error(f"Error en la configuración: {e}")
            raise
    
    def refresh_access_token(self) -> None:
        """
        Refresca el token de acceso de Mercado Libre.
        
        Raises:
            Exception: Si hay un error al refrescar el token
        """
        url = f"{self.base_url}/oauth/token"
        headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded"
        }
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token
        }
        
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            data = response.json()
            
            self.access_token = data["access_token"]
            # Guardar el nuevo refresh token
            self.refresh_token = data["refresh_token"]
            
            # Se podría implementar guardar el nuevo refresh token en el archivo de configuración
            
            logger.info("Token de Mercado Libre actualizado correctamente")
        except Exception as e:
            logger.error(f"Error al refrescar token de Mercado Libre: {e}")
            raise
    
    def get_products(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los productos del vendedor en Mercado Libre.
        
        Returns:
            Lista de productos con sus detalles
        """
        url = f"{self.base_url}/users/{self.user_id}/items/search"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            all_products = []
            offset = 0
            limit = 50
            
            # Primera petición para obtener el total
            response = requests.get(
                url, 
                headers=headers, 
                params={"offset": offset, "limit": limit}
            )
            response.raise_for_status()
            data = response.json()
            
            total_items = len(data["results"])
            paging_total = data.get("paging", {}).get("total", 0)
            
            logger.info(f"Se encontraron {paging_total} productos en Mercado Libre")
            
            # Añadir resultados de la primera petición
            all_products.extend(data["results"])
            
            # Obtener el resto de páginas
            while offset + limit < paging_total:
                offset += limit
                # Esperar para no exceder el límite de la API
                time.sleep(self.rate_limit)
                
                logger.debug(f"Obteniendo productos: {offset}-{offset+limit} de {paging_total}")
                
                response = requests.get(
                    url, 
                    headers=headers, 
                    params={"offset": offset, "limit": limit}
                )
                response.raise_for_status()
                data = response.json()
                all_products.extend(data["results"])
            
            # Obtener detalles de cada producto
            product_details = []
            total_products = len(all_products)
            
            logger.info(f"Obteniendo detalles de {total_products} productos...")
            
            for i, item_id in enumerate(all_products, 1):
                # Informar progreso cada 10 productos o en múltiplos del 10%
                if i % 10 == 0 or i % max(1, int(total_products * 0.1)) == 0:
                    logger.debug(f"Progreso: {i}/{total_products} productos procesados ({i/total_products*100:.1f}%)")
                
                # Esperar para no exceder el límite de la API
                time.sleep(self.rate_limit)
                product = self.get_product_details(item_id)
                if product:
                    product_details.append(product)
            
            logger.info(f"Se obtuvieron detalles de {len(product_details)} productos")
            return product_details
        
        except Exception as e:
            logger.error(f"Error al obtener productos de Mercado Libre: {e}")
            return []
    
    def get_product_details(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un producto específico.
        
        Args:
            item_id: ID del producto en Mercado Libre
            
        Returns:
            Diccionario con los detalles del producto o None si hay error
        """
        url = f"{self.base_url}/items/{item_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Extraer SKU de los atributos si existe
            sku = None
            for attr in data.get("attributes", []):
                if attr.get("id") == "SELLER_SKU":
                    sku = attr.get("value_name")
                    break
            
            # Crear objeto de producto con los datos necesarios
            product = {
                "id": data["id"],
                "title": data["title"],
                "price": data["price"],
                "currency_id": data["currency_id"],
                "sku": sku,
                "permalink": data["permalink"],
                "category_id": data.get("category_id"),
                "listing_type_id": data.get("listing_type_id"),
                "available_quantity": data.get("available_quantity", 0),
                "status": data.get("status")
            }
            
            return product
        
        except Exception as e:
            logger.error(f"Error al obtener detalles del producto {item_id}: {e}")
            return None