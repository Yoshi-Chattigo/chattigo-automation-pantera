# Framework de Automatización con Playwright y Python

Este proyecto es un framework de pruebas automatizadas robusto y escalable utilizando Playwright y Python, siguiendo el patrón de diseño Page Object Model (POM).

## Estructura del Proyecto

```
automation-framework-qa/
├── config/             # Configuraciones globales
├── pages/              # Page Objects (POM)
├── tests/              # Tests y fixtures
├── utils/              # Utilidades (logs, helpers)
├── screenshots/        # Capturas de pantalla de fallos
├── pytest.ini          # Configuración de Pytest
├── requirements.txt    # Dependencias
└── README.md           # Documentación
```

## Requisitos Previos

- Python 3.12+
- Node.js (para los navegadores de Playwright)

## Instalación

1.  Clonar el repositorio (o descargar los archivos).
2.  Crear un entorno virtual (opcional pero recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```
3.  Instalar las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Instalar los navegadores de Playwright:
    ```bash
    playwright install
    ```

## Ejecución de Pruebas

Ejecutar todos los tests:
```bash
pytest
```

Ejecutar tests con interfaz gráfica (headed):
```bash
pytest --headed
```

Ejecutar tests en paralelo:
```bash
pytest -n 2  # Requiere pytest-xdist
```

Generar reporte HTML:
```bash
pytest --html=report.html
```

## Reportes Avanzados (Allure)

Este framework utiliza Allure para generar reportes detallados.

1.  Ejecutar los tests (los resultados se guardan en `allure-results`):
    ```bash
    pytest
    ```
2.  Visualizar el reporte (requiere tener Allure instalado en el sistema):
    ```bash
    allure serve allure-results
    ```

## Despliegue en Google Cloud Run

### Prerrequisitos de Google Cloud

Antes de desplegar, asegúrate de configurar tu entorno:

1.  **Instalar gcloud CLI:** [Guía de instalación](https://cloud.google.com/sdk/docs/install)
2.  **Ejecutar script de configuración:**
    ```bash
    ./gcloud_setup.sh [TU_PROJECT_ID]
    ```
    *Este script iniciará sesión, configurará el proyecto y habilitará las APIs necesarias.*

### Despliegue

Para ejecutar el bot 24/7 en la nube:

1.  **Construir la imagen:**
    ```bash
    gcloud builds submit --tag gcr.io/[TU_PROYECTO]/qa-bot
    ```

2.  **Desplegar:**
    ```bash
    gcloud run deploy qa-bot \
      --image gcr.io/[TU_PROYECTO]/qa-bot \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --min-instances 1 \
      --set-env-vars DISCORD_TOKEN="TU_TOKEN_AQUI"
    ```
    *Nota: `--min-instances 1` asegura que el bot no se "duerma" y siempre responda.*

## Calidad de Código

Para verificar el estilo y formato del código:

```bash
# Verificar estilo (PEP 8)
flake8 .

# Formatear código automáticamente
black .
```

## Ejecución en Paralelo

Para ejecutar los tests en paralelo y reducir el tiempo de ejecución:

```bash
pytest -n auto
```

## Configuración

Las variables de entorno y configuraciones globales se manejan en `config/config.py` y pueden ser sobreescritas mediante un archivo `.env` (no incluido en el repo por seguridad).

## Logs y Reportes

- Los logs se muestran en consola durante la ejecución.
- Si un test falla, se toma automáticamente una captura de pantalla en la carpeta `screenshots/`.
