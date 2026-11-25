"""Excepciones personalizadas del Sistema Integral de Software FJ."""

class ErrorSoftwareFJ(Exception):
    """Excepción base para los errores propios del sistema."""


class ClienteInvalidoError(ErrorSoftwareFJ):
    """Se produce cuando los datos de un cliente no son válidos."""


class ServicioInvalidoError(ErrorSoftwareFJ):
    """Se produce cuando un servicio tiene datos o configuración inválidos."""


class ParametroCalculoError(ErrorSoftwareFJ):
    """Se produce cuando los parámetros de cálculo no son válidos."""


class ReservaError(ErrorSoftwareFJ):
    """Se produce cuando una reserva no puede procesarse."""


class ServicioNoDisponibleError(ReservaError):
    """Se produce cuando no hay recursos disponibles para reservar."""
