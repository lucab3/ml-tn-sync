#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para el cálculo de precios sin comisión.
"""

import logging
from typing import Union, Optional

logger = logging.getLogger(__name__)

def calculate_price_without_commission(ml_price: Union[float, str], 
                                      commission_rate: Union[float, int] = 13,
                                      round_to: Optional[int] = 2) -> float:
    """
    Calcula el precio sin la comisión de Mercado Libre.
    
    Args:
        ml_price: Precio en Mercado Libre (con comisión)
        commission_rate: Porcentaje de comisión (por defecto 13%)
        round_to: Número de decimales para redondear (None para no redondear)
        
    Returns:
        Precio sin comisión
    
    Examples:
        >>> calculate_price_without_commission(113)
        100.0
        >>> calculate_price_without_commission(113, 15)
        98.26
    """
    try:
        # Convertir a float si es string
        if isinstance(ml_price, str):
            ml_price = float(ml_price.replace(',', '.'))
        else:
            ml_price = float(ml_price)
        
        if ml_price <= 0:
            logger.warning(f"Precio inválido: {ml_price}")
            return 0.0
            
        # Convertir porcentaje a factor
        commission_factor = float(commission_rate) / 100
        
        # Calcular precio sin comisión
        # Fórmula: precio_sin_comision = precio_con_comision / (1 + comisión)
        price_without_commission = ml_price / (1 + commission_factor)
        
        # Redondear si se especifica
        if round_to is not None:
            price_without_commission = round(price_without_commission, round_to)
            
        return price_without_commission
        
    except (ValueError, TypeError) as e:
        logger.error(f"Error al calcular precio sin comisión: {e}")
        return 0.0
