#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pruebas unitarias para el módulo de API de Mercado Libre.
"""

import os
import sys
import unittest
import json
from unittest import mock

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.mercadolibre import MercadoLibreAPI

class TestMercadoLibreAPI(unittest.TestCase):
    """Pruebas para la clase MercadoLibreAPI"""
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        # Crear un archivo de configuración temporal para pruebas
        self.test_config = {
            "mercadolibre": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "refresh_token": "test_refresh_token",
                "user_id": "test_user_id"
            }
        }
        
        self.config_path = "test_config.json"
        with open(self.config_path, 'w') as f:
            json.dump(self.test_config, f)
    
    def tearDown(self):
        """Limpieza después de cada prueba"""
        # Eliminar archivo de configuración temporal
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
    
    @mock.patch('requests.post')
    def test_refresh_access_token(self, mock_post):
        """Prueba la función de actualización del token de acceso"""
        # Configurar el mock para la respuesta de la API
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Crear instancia de API con el archivo de configuración temporal
        api = MercadoLibreAPI(config_path=self.config_path)
        
        # Verificar que el token se haya actualizado correctamente
        self.assertEqual(api.access_token, "new_access_token")
        self.assertEqual(api.refresh_token, "new_refresh_token")
        
        # Verificar que se haya hecho la petición con los parámetros correctos
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['data']['client_id'], "test_client_id")
        self.assertEqual(kwargs['data']['client_secret'], "test_client_secret")
        self.assertEqual(kwargs['data']['refresh_token'], "test_refresh_token")
    
    @mock.patch('requests.get')
    @mock.patch('src.api.mercadolibre.MercadoLibreAPI.refresh_access_token')
    def test_get_products(self, mock_refresh, mock_get):
        """Prueba la función de obtención de productos"""
        # Configurar mocks para las respuestas de la API
        mock_response_search = mock.Mock()
        mock_response_search.json.return_value = {
            "results": ["ML123", "ML456"],
            "paging": {"total": 2}
        }
        mock_response_search.raise_for_status.return_value = None
        
        mock_response_detail1 = mock.Mock()
        mock_response_detail1.json.return_value = {
            "id": "ML123",
            "title": "Producto 1",
            "price": 100,
            "currency_id": "ARS",
            "attributes": [{"id": "SELLER_SKU", "value_name": "SKU123"}],
            "permalink": "http://permalink1.com"
        }
        mock_response_detail1.raise_for_status.return_value = None
        
        mock_response_detail2 = mock.Mock()
        mock_response_detail2.json.return_value = {
            "id": "ML456",
            "title": "Producto 2",
            "price": 200,
            "currency_id": "ARS",
            "attributes": [{"id": "SELLER_SKU", "value_name": "SKU456"}],
            "permalink": "http://permalink2.com"
        }
        mock_response_detail2.raise_for_status.return_value = None
        
        # Configurar el comportamiento del mock para devolver diferentes respuestas
        mock_get.side_effect = [
            mock_response_search,
            mock_response_detail1,
            mock_response_detail2
        ]
        
        # Crear instancia de API con el archivo de configuración temporal
        api = MercadoLibreAPI(config_path=self.config_path)
        api.get_product_details = mock.MagicMock(side_effect=[
            {
                "id": "ML123",
                "title": "Producto 1",
                "price": 100,
                "currency_id": "ARS",
                "sku": "SKU123",
                "permalink": "http://permalink1.com"
            },
            {
                "id": "ML456",
                "title": "Producto 2",
                "price": 200,
                "currency_id": "ARS",
                "sku": "SKU456",
                "permalink": "http://permalink2.com"
            }
        ])
        
        # Ejecutar la función a probar
        products = api.get_products()
        
        # Verificar resultados
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0]["id"], "ML123")
        self.assertEqual(products[0]["title"], "Producto 1")
        self.assertEqual(products[1]["id"], "ML456")
        self.assertEqual(products[1]["title"], "Producto 2")

if __name__ == '__main__':
    unittest.main()
