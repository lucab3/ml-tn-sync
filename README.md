# ML-TN-Sync

ML-TN-Sync es una herramienta para sincronizar productos y precios entre plataformas de comercio electrónico MercadoLibre y TiendaNube, permitiendo mantener consistencia en su catálogo de productos a través de múltiples canales de venta.

## Características

- Sincronización bidireccional de productos entre MercadoLibre y TiendaNube
- Actualización automática de precios según reglas configurables
- Registro detallado de operaciones para seguimiento y solución de problemas
- Fácil configuración mediante archivos JSON
- Scripts de instalación para Windows y Linux/Mac

## Requisitos previos

- Python 3.7 o superior
- Cuenta de MercadoLibre con credenciales de API
- Cuenta de TiendaNube con credenciales de API
- Permisos de escritura en el directorio de instalación

## Instalación

### En Linux/Mac

```bash
# Clonar el repositorio
git clone https://github.com/lucab3/ml-tn-sync.git
cd ml-tn-sync

# Crear y activar entorno virtual
python -m venv ml_tn_sync_env
source ml_tn_sync_env/bin/activate

# Ejecutar script de instalación
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### En Windows

```cmd
# Clonar el repositorio
git clone https://github.com/lucab3/ml-tn-sync.git
cd ml-tn-sync

# Crear y activar entorno virtual
python -m venv ml_tn_sync_env
ml_tn_sync_env\Scripts\activate

# Ejecutar script de instalación
scripts\setup.bat
```

## Configuración

1. Copia el archivo `config/credentials.example.json` a `config/credentials.json`
2. Edita `config/credentials.json` para incluir tus credenciales de API:

```json
{
    "mercadolibre": {
        "client_id": "TU_CLIENT_ID_MERCADOLIBRE",
        "client_secret": "TU_CLIENT_SECRET_MERCADOLIBRE",
        "refresh_token": "TU_REFRESH_TOKEN_MERCADOLIBRE",
        "user_id": "TU_USER_ID_MERCADOLIBRE"
    },
    "tiendanube": {
        "api_key": "TU_API_KEY_TIENDANUBE",
        "user_id": "TU_USER_ID_TIENDANUBE"
    }
}
```

### Obtener credenciales de MercadoLibre

1. Crea una aplicación en [MercadoLibre Developers](https://developers.mercadolibre.com/)
2. Configura la URL de redirección a `https://localhost`
3. Obtén el Client ID y Client Secret
4. Sigue el flujo de autorización OAuth para obtener el refresh token

### Obtener credenciales de TiendaNube

1. Ve a tu Panel de Administración de TiendaNube
2. Navega a Configuración > API
3. Genera un nuevo token de acceso y copia la API Key
4. Tu User ID es el número que aparece en la URL de tu tienda

## Uso

### Ejecutar sincronización

En Linux/Mac:
```bash
source ml_tn_sync_env/bin/activate
./scripts/run.sh
```

En Windows:
```cmd
ml_tn_sync_env\Scripts\activate
scripts\run.bat
```

También puedes ejecutar el script directamente:
```
python main.py
```

### Opciones de configuración

El archivo `config/settings.py` contiene ajustes para personalizar el comportamiento:

- `SYNC_INTERVAL`: Intervalo de sincronización (en segundos)
- `PRICE_THRESHOLD`: Umbral para actualizar precios (porcentaje)
- `LOG_LEVEL`: Nivel de detalle para el registro

## Estructura del proyecto

```
ml-tn-sync/                      # Carpeta raíz del proyecto
│
├── src/                         # Código fuente
│   ├── api/                     # Módulos de conexión a APIs
│   ├── core/                    # Lógica principal
│   └── utils/                   # Utilidades
│
├── config/                      # Archivos de configuración
├── scripts/                     # Scripts de instalación y ejecución
├── logs/                        # Directorio para archivos de registro
├── tests/                       # Pruebas unitarias
│
└── main.py                      # Punto de entrada principal
```

## Resolución de problemas

Si encuentra errores durante la sincronización:

1. Revise los archivos de registro en el directorio `logs/`
2. Asegúrese de que las credenciales de API sean correctas y estén vigentes
3. Compruebe su conexión a Internet
4. Verifique el estado de las APIs de MercadoLibre y TiendaNube

## Contribuir

Las contribuciones son bienvenidas:

1. Fork el repositorio
2. Crea una nueva rama (`git checkout -b feature/nueva-caracteristica`)
3. Realiza tus cambios y escribe pruebas
4. Ejecuta las pruebas (`python -m pytest`)
5. Commit tus cambios (`git commit -am 'Agrega nueva característica'`)
6. Push a la rama (`git push origin feature/nueva-caracteristica`)
7. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulte el archivo LICENSE para más detalles.

## Contacto

Para soporte o preguntas, por favor abra un issue en el repositorio GitHub.
