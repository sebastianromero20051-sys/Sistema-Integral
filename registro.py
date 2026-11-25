"""Configuración del registro de eventos y errores."""

import logging
from pathlib import Path

RUTA_LOGS = Path(__file__).resolve().parent / "logs"
RUTA_LOGS.mkdir(parents=True, exist_ok=True)
RUTA_ARCHIVO_LOG = RUTA_LOGS / "eventos.log"

def configurar_logger():
    """Configura un logger que escribe eventos en logs/eventos.log."""
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)

    # Evita agregar manejadores duplicados si se llama más de una vez.
    if not logger.handlers:
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )
        archivo = logging.FileHandler(RUTA_ARCHIVO_LOG, encoding="utf-8")
        archivo.setFormatter(formato)
        consola = logging.StreamHandler()
        consola.setFormatter(formato)
        logger.addHandler(archivo)
        logger.addHandler(consola)

    return logger

log = configurar_logger()
