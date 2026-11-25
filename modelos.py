"""Clases del dominio para clientes, servicios y reservas."""

from abc import ABC, abstractmethod
import re

from excepciones import (
    ClienteInvalidoError,
    ServicioInvalidoError,
    ParametroCalculoError,
    ReservaError,
    ServicioNoDisponibleError,
)
from registro import log


class EntidadBase(ABC):
    """Entidad abstracta con identificador y descripción."""

    def __init__(self, identificador):
        if not identificador:
            raise ValueError("El identificador es obligatorio.")
        self.identificador = identificador

    @abstractmethod
    def describir(self):
        """Devuelve una descripción de la entidad."""


class Cliente(EntidadBase):
    """Cliente con atributos encapsulados y validación."""

    def __init__(self, identificador, nombre, documento, correo, telefono):
        super().__init__(identificador)
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ClienteInvalidoError("El nombre del cliente es obligatorio.")
        self.__nombre = valor.strip()

    @property
    def documento(self):
        return self.__documento

    @documento.setter
    def documento(self, valor):
        if not str(valor).isdigit():
            raise ClienteInvalidoError("El documento debe contener solo números.")
        self.__documento = str(valor)

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        if not isinstance(valor, str) or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valor):
            raise ClienteInvalidoError("El correo electrónico no es válido.")
        self.__correo = valor

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        if not str(valor).isdigit() or len(str(valor)) < 7:
            raise ClienteInvalidoError("El teléfono debe tener al menos 7 dígitos.")
        self.__telefono = str(valor)

    def describir(self):
        return f"Cliente {self.nombre} (documento {self.documento})"


class Servicio(EntidadBase, ABC):
    """Servicio abstracto con tarifa y cálculo de costo."""

    def __init__(self, identificador, nombre, tarifa_hora):
        super().__init__(identificador)
        if not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:
            raise ServicioInvalidoError("La tarifa debe ser un número positivo.")
        self.nombre = nombre
        self.tarifa_hora = float(tarifa_hora)

    def calcular_costo(self, horas, impuesto=0.19, descuento=0.0):
        """Calcula el costo; los parámetros opcionales permiten distintas variantes."""
        if not isinstance(horas, (int, float)) or horas <= 0:
            raise ParametroCalculoError("La duración debe ser positiva.")
        if not isinstance(impuesto, (int, float)) or not 0 <= impuesto <= 1:
            raise ParametroCalculoError("El impuesto debe estar entre 0 y 1.")
        if not isinstance(descuento, (int, float)) or not 0 <= descuento <= 1:
            raise ParametroCalculoError("El descuento debe estar entre 0 y 1.")
        subtotal = self.tarifa_hora * horas
        return round(subtotal * (1 + impuesto) * (1 - descuento), 2)

    @abstractmethod
    def disponible(self):
        """Indica si el servicio tiene recursos disponibles."""

    @abstractmethod
    def reservar_recursos(self):
        """Marca o descuenta los recursos reservados."""


class ReservaSala(Servicio):
    def __init__(self, identificador, nombre, tarifa_hora, capacidad, ocupada=False):
        super().__init__(identificador, nombre, tarifa_hora)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ServicioInvalidoError("La capacidad de la sala debe ser positiva.")
        self.capacidad = capacidad
        self.ocupada = ocupada

    def disponible(self):
        return not self.ocupada

    def reservar_recursos(self):
        if not self.disponible():
            raise ServicioNoDisponibleError("La sala ya está ocupada.")
        self.ocupada = True

    def describir(self):
        return f"Sala {self.nombre}, capacidad {self.capacidad}"


class AlquilerEquipo(Servicio):
    def __init__(self, identificador, nombre, tarifa_hora, unidades, deposito=0):
        super().__init__(identificador, nombre, tarifa_hora)
        if not isinstance(unidades, int) or unidades < 0:
            raise ServicioInvalidoError("Las unidades no pueden ser negativas.")
        if deposito < 0:
            raise ServicioInvalidoError("El depósito no puede ser negativo.")
        self.unidades = unidades
        self.deposito = deposito

    def disponible(self):
        return self.unidades > 0

    def reservar_recursos(self):
        if not self.disponible():
            raise ServicioNoDisponibleError("No hay equipos disponibles.")
        self.unidades -= 1

    def describir(self):
        return f"Alquiler de {self.nombre}; unidades disponibles: {self.unidades}"


class AsesoriaEspecializada(Servicio):
    NIVELES = {"junior", "senior", "experto"}

    def __init__(self, identificador, nombre, tarifa_hora, nivel):
        if nivel not in self.NIVELES:
            raise ServicioInvalidoError("El nivel debe ser junior, senior o experto.")
        multiplicadores = {"junior": 1.0, "senior": 1.5, "experto": 2.0}
        super().__init__(identificador, nombre, tarifa_hora * multiplicadores[nivel])
        self.nivel = nivel

    def disponible(self):
        return True

    def reservar_recursos(self):
        return None

    def describir(self):
        return f"Asesoría {self.nombre}, nivel {self.nivel}"


class Reserva(EntidadBase):
    """Reserva que integra un cliente, un servicio, duración y estado."""

    def __init__(self, identificador, cliente, servicio, duracion):
        super().__init__(identificador)
        if not isinstance(cliente, Cliente):
            raise ReservaError("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaError("La reserva requiere un servicio válido.")
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "PENDIENTE"

    def confirmar(self, **opciones):
        try:
            if not isinstance(self.duracion, (int, float)) or not 1 <= self.duracion <= 24:
                raise ReservaError("La duración debe estar entre 1 y 24 horas.")
            if not self.servicio.disponible():
                raise ServicioNoDisponibleError("El servicio no está disponible.")
            costo = self.servicio.calcular_costo(self.duracion, **opciones)
        except ServicioNoDisponibleError:
            self.estado = "FALLIDA"
            log.exception("Servicio no disponible para la reserva %s", self.identificador)
            raise
        except ParametroCalculoError as error:
            self.estado = "FALLIDA"
            log.exception("Parámetros de cálculo inválidos en reserva %s", self.identificador)
            raise ReservaError("Los parámetros del costo no son válidos.") from error
        except TypeError as error:
            self.estado = "FALLIDA"
            log.exception("Opciones de costo desconocidas en reserva %s", self.identificador)
            raise ReservaError("Opciones de costo no reconocidas.") from error
        except ReservaError:
            self.estado = "FALLIDA"
            log.exception("No fue posible confirmar la reserva %s", self.identificador)
            raise
        else:
            self.servicio.reservar_recursos()
            self.estado = "CONFIRMADA"
            log.info("Reserva %s confirmada. Costo: %s", self.identificador, costo)
            return costo
        finally:
            log.info("Intento de confirmación finalizado para reserva %s", self.identificador)

    def cancelar(self):
        if self.estado != "CONFIRMADA":
            raise ReservaError("Solo se pueden cancelar reservas confirmadas.")
        self.estado = "CANCELADA"
        log.info("Reserva %s cancelada", self.identificador)

    def describir(self):
        return f"Reserva {self.identificador}: {self.estado}"
