#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo principal para la sincronización de precios entre Mercado Libre y Tienda Nube.
"""

import json
import logging
from typing import Dict, Any, List, Tuple, Optional

from src.api.mercadolibre import MercadoLibreAPI
from src.api.tiendanube import TiendaNubeAPI
from src.core.price_calculator import calculate_price_without_commission

logger = logging.getLogger(__name__)

class PriceSynchronizer:
    """Clase para sincronizar precios entre Mercado Libre y Tienda Nube"""
    
    def __init__(self, ml_api: MercadoLibreAPI, tn_api: TiendaNubeAPI, 
                config_path: str = 'config/credentials.json', dry_run: bool = False):
        """
        Inicializa el sincronizador de precios.
        
        Args:
            ml_api: Instancia de la API de Mercado Libre
            tn_api: Instancia de la API de Tienda Nube
            config_path: Ruta al archivo de configuración
            dry_run: Si es True, simula la sincronización sin realizar cambios
        """
        self.ml_api = ml_api
        self.tn_api = tn_api
        self.dry_run = dry_run
        self.commission_rate = 13  # Valor por defecto
        self.match_by_sku = True   # Por defecto empareja por SKU
        
        # Cargar configuración adicional
        self._load_config(config_path)
        
        logger.info(f"Sincronizador inicializado con comisión de {self.commission_rate}% " + 
                   f"y emparejamiento {'por SKU' if self.match_by_sku else 'por nombre'}")
        
        if self.dry_run:
            logger.info("MODO SIMULACIÓN ACTIVADO: No se realizarán cambios reales")
    
    def _load_config(self, config_path: str) -> None:
        """
        Carga la configuración desde el archivo de credenciales.
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Cargar configuración de sincronización si existe
            if 'settings' in config:
                settings = config['settings']
                if 'ml_commission' in settings:
                    self.commission_rate = settings['ml_commission']
                
                if 'match_by_sku' in settings:
                    self.match_by_sku = settings['match_by_sku']
        
        except Exception as e:
            logger.warning(f"No se pudo cargar la configuración avanzada: {e}")
            logger.warning("Se usarán los valores por defecto")
    
    def find_matching_product(self, ml_product: Dict[str, Any], 
                             tn_products: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Encuentra el producto correspondiente en Tienda Nube.
        
        Args:
            ml_product: Producto de Mercado Libre
            tn_products: Lista de productos de Tienda Nube
            
        Returns:
            Producto de Tienda Nube que coincide o None si no hay coincidencia
        """
        if self.match_by_sku and ml_product.get("sku"):
            # Buscar por SKU
            sku = ml_product["sku"]
            for tn_product in tn_products:
                # Verificar SKU en el producto principal
                if tn_product.get("sku") == sku:
                    logger.debug(f"Coincidencia por SKU: {sku}")
                    return tn_product
                
                # Verificar SKU en las variantes
                for variant in tn_product.get("variants", []):
                    if variant.get("sku") == sku:
                        logger.debug(f"Coincidencia por SKU en variante: {sku}")
                        return tn_product
        else:
            # Buscar por nombre (más propenso a errores)
            ml_title = ml_product["title"].lower()
            for tn_product in tn_products:
                # Obtener nombre en español o el primer idioma disponible
                tn_name = tn_product.get("name", {}).get("es", "")
                if not tn_name and tn_product.get("name"):
                    # Tomar el primer idioma disponible
                    for lang, name in tn_product["name"].items():
                        tn_name = name
                        break
                
                tn_name = tn_name.lower()
                
                # Comparar nombres (buscamos coincidencia parcial en cualquier dirección)
                if ml_title in tn_name or tn_name in ml_title:
                    logger.debug(f"Coincidencia por nombre: ML '{ml_title}' - TN '{tn_name}'")
                    return tn_product
        
        logger.debug(f"No se encontró coincidencia para: {ml_product.get('title')} (SKU: {ml_product.get('sku')})")
        return None
    
    def sync_prices(self) -> Tuple[int, int, int]:
        """
        Sincroniza los precios entre Mercado Libre y Tienda Nube.
        
        Returns:
            Tupla con (productos_actualizados, productos_sin_cambio, productos_sin_coincidencia)
        """
        # Estadísticas para reportar
        updated_count = 0
        unchanged_count = 0
        unmatched_count = 0
        
        # Obtener productos de ambas plataformas
        logger.info("Obteniendo productos de Mercado Libre...")
        ml_products = self.ml_api.get_products()
        
        if not ml_products:
            logger.warning("No se encontraron productos en Mercado Libre")
            return 0, 0, 0
        
        logger.info("Obteniendo productos de Tienda Nube...")
        tn_products = self.tn_api.get_products()
        
        if not tn_products:
            logger.warning("No se encontraron productos en Tienda Nube")
            return 0, 0, 0
        
        logger.info(f"Sincronizando {len(ml_products)} productos de Mercado Libre con {len(tn_products)} productos de Tienda Nube")
        
        # Para cada producto de Mercado Libre, buscar su correspondiente en Tienda Nube
        for ml_product in ml_products:
            # Verificar si el producto está activo
            if ml_product.get("status") != "active":
                logger.debug(f"Ignorando producto no activo: {ml_product.get('title')}")
                continue
            
            # Buscar producto correspondiente en Tienda Nube
            tn_product = self.find_matching_product(ml_product, tn_products)
            
            if not tn_product:
                logger.warning(f"No se encontró coincidencia para: {ml_product.get('title')} (SKU: {ml_product.get('sku')})")
                unmatched_count += 1
                continue
            
            # Calcular precio sin comisión
            ml_price = ml_product.get("price", 0)
            new_price = calculate_price_without_commission(ml_price, self.commission_rate)
            
            # Verificar si hay variantes o es un producto simple
            if tn_product.get("variants") and len(tn_product["variants"]) > 0:
                # Producto con variantes
                updated = self._update_variant_prices(tn_product, new_price)
                if updated:
                    updated_count += 1
                else:
                    unchanged_count += 1
            else:
                # Producto simple
                current_price = float(tn_product.get("price", 0))
                
                # Comparar precios con una tolerancia de 0.01 para evitar cambios innecesarios
                if abs(current_price - new_price) > 0.01:
                    logger.info(f"Actualizando precio de '{tn_product.get('name', {}).get('es', 'Producto')}' " +
                              f"de {current_price} a {new_price}")
                    
                    success = self.tn_api.update_product_price(tn_product["id"], new_price, self.dry_run)
                    
                    if success:
                        updated_count += 1
                    else:
                        logger.error(f"Error al actualizar precio del producto {tn_product['id']}")
                else:
                    logger.debug(f"Precio sin cambios para '{tn_product.get('name', {}).get('es', 'Producto')}': {current_price}")
                    unchanged_count += 1
        
        # Mostrar resumen
        logger.info("=" * 50)
        logger.info("Resumen de sincronización:")
        logger.info(f"- Productos actualizados: {updated_count}")
        logger.info(f"- Productos sin cambios: {unchanged_count}")
        logger.info(f"- Productos sin coincidencia: {unmatched_count}")
        logger.info("=" * 50)
        
        return updated_count, unchanged_count, unmatched_count
    
    def _update_variant_prices(self, tn_product: Dict[str, Any], base_price: float) -> bool:
        """
        Actualiza los precios de las variantes de un producto en Tienda Nube.
        
        Args:
            tn_product: Producto de Tienda Nube con variantes
            base_price: Precio base calculado sin comisión
            
        Returns:
            True si al menos una variante fue actualizada, False en caso contrario
        """
        product_id = tn_product["id"]
        product_name = tn_product.get("name", {}).get("es", "Producto con variantes")
        variants = tn_product.get("variants", [])
        
        if not variants:
            logger.warning(f"El producto {product_id} está marcado con variantes pero no tiene ninguna")
            return False
        
        # Si hay solo una variante, actualizamos con el precio base
        if len(variants) == 1:
            variant = variants[0]
            current_price = float(variant.get("price", 0))
            
            if abs(current_price - base_price) > 0.01:
                logger.info(f"Actualizando precio de variante única de '{product_name}' " +
                          f"de {current_price} a {base_price}")
                
                # Preparar payload para actualizar la variante
                url = f"{self.tn_api.base_url}/products/{product_id}/variants/{variant['id']}"
                payload = {
                    "price": base_price
                }
                
                if self.dry_run:
                    logger.info(f"[SIMULACIÓN] Actualizando precio de variante {variant['id']} a {base_price}")
                    return True
                
                try:
                    # Esperar para no exceder el límite de la API
                    import time
                    time.sleep(self.tn_api.rate_limit)
                    
                    response = requests.put(url, headers=self.tn_api.headers, json=payload)
                    response.raise_for_status()
                    
                    logger.info(f"Precio actualizado para la variante {variant['id']} a {base_price}")
                    return True
                except Exception as e:
                    logger.error(f"Error al actualizar precio de la variante {variant['id']}: {e}")
                    return False
            else:
                logger.debug(f"Precio sin cambios para variante única de '{product_name}': {current_price}")
                return False
        
        # Si hay múltiples variantes, necesitamos calcular los precios relativos
        # Para simplificar, mantenemos la misma proporción entre variantes
        
        # Calcular precio promedio actual de las variantes
        current_prices = [float(v.get("price", 0)) for v in variants]
        avg_price = sum(current_prices) / len(current_prices)
        
        if avg_price == 0:
            logger.warning(f"El producto {product_id} tiene variantes con precio promedio 0")
            return False
        
        # Calcular factor de ajuste
        adjustment_factor = base_price / avg_price
        
        # Actualizar cada variante
        any_updated = False
        
        for variant in variants:
            variant_id = variant["id"]
            current_price = float(variant.get("price", 0))
            new_price = round(current_price * adjustment_factor, 2)
            
            if abs(current_price - new_price) > 0.01:
                logger.info(f"Actualizando precio de variante {variant_id} de '{product_name}' " +
                          f"de {current_price} a {new_price}")
                
                # Preparar payload para actualizar la variante
                url = f"{self.tn_api.base_url}/products/{product_id}/variants/{variant_id}"
                payload = {
                    "price": new_price
                }
                
                if self.dry_run:
                    logger.info(f"[SIMULACIÓN] Actualizando precio de variante {variant_id} a {new_price}")
                    any_updated = True
                    continue
                
                try:
                    # Esperar para no exceder el límite de la API
                    import time
                    time.sleep(self.tn_api.rate_limit)
                    
                    response = requests.put(url, headers=self.tn_api.headers, json=payload)
                    response.raise_for_status()
                    
                    logger.info(f"Precio actualizado para la variante {variant_id} a {new_price}")
                    any_updated = True
                except Exception as e:
                    logger.error(f"Error al actualizar precio de la variante {variant_id}: {e}")
        
        return any_updated
