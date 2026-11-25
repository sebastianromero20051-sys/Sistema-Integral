"""Punto de entrada y simulaciones del Sistema Integral Software FJ."""

from excepciones import (
    ClienteInvalidoError,
    ServicioInvalidoError,
    ReservaError,
    ServicioNoDisponibleError,
)
from modelos import (
    Cliente, ReservaSala, AlquilerEquipo, AsesoriaEspecializada, Reserva
)
from registro import log


def ejecutar_simulaciones():
    """Ejecuta 16 escenarios de prueba, válidos e inválidos."""
    print("\\nSISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ\\n")
    resultados = []

    def registrar(numero, descripcion, operacion):
        try:
            resultado = operacion()
            mensaje = f"{numero}. {descripcion}: ÉXITO"
            resultados.append(mensaje)
            print(mensaje, resultado if resultado is not None else "")
        except Exception as error:
            mensaje = f"{numero}. {descripcion}: {type(error).__name__}"
            resultados.append(mensaje)
            print(mensaje, "-", error)
            log.exception("Simulación %s: %s", numero, descripcion)

    cliente = None

    def crear_cliente():
        nonlocal cliente
        cliente = Cliente("C1", "Ana Pérez", "12345678", "ana@correo.com", "3001234567")
        return cliente.describir()

    registrar(1, "Registro de cliente válido", crear_cliente)
    registrar(2, "Cliente con correo inválido",
              lambda: Cliente("C2", "Luis", "12345678", "correo-invalido", "3001234567"))
    registrar(3, "Cliente con documento no numérico",
              lambda: Cliente("C3", "Luis", "ABC123", "luis@correo.com", "3001234567"))

    def crear_equipo():
        equipo = AlquilerEquipo("E1", "Proyector", 25000, 1, deposito=50000)
        return equipo.describir()

    registrar(4, "Creación de equipo válido", crear_equipo)
    registrar(5, "Servicio con tarifa negativa",
              lambda: ReservaSala("S1", "Sala A", -1000, 10))
    registrar(6, "Asesoría con nivel inexistente",
              lambda: AsesoriaEspecializada("A1", "Consultoría", 180000, "principiante"))

    sala = ReservaSala("S2", "Sala principal", 80000, 20)
    asesor = AsesoriaEspecializada("A2", "Consultoría", 180000, "junior")
    equipo = AlquilerEquipo("E2", "Portátil", 30000, 1, deposito=40000)

    registrar(7, "Reserva de sala (3 h, IVA 19 %)",
              lambda: Reserva("R7", cliente, sala, 3).confirmar())
    registrar(8, "Asesoría con 10 % de descuento",
              lambda: Reserva("R8", cliente, asesor, 1).confirmar(descuento=0.10))
    registrar(9, "Reserva del único equipo disponible",
              lambda: Reserva("R9", cliente, equipo, 2).confirmar())

    equipo_agotado = AlquilerEquipo("E3", "Tableta", 20000, 0)
    registrar(10, "Reserva con equipo agotado",
              lambda: Reserva("R10", cliente, equipo_agotado, 1).confirmar())

    sala_ocupada = ReservaSala("S3", "Sala ocupada", 80000, 10, ocupada=True)
    registrar(11, "Reserva con sala ocupada",
              lambda: Reserva("R11", cliente, sala_ocupada, 1).confirmar())
    registrar(12, "Duración inválida (30 h)",
              lambda: Reserva("R12", cliente, sala, 30).confirmar())
    registrar(13, "Descuento fuera de rango",
              lambda: Reserva("R13", cliente, asesor, 1).confirmar(descuento=1.5))
    registrar(14, "Opción de costo desconocida",
              lambda: Reserva("R14", cliente, asesor, 1).confirmar(opcion_desconocida=True))

    reserva_cancelar = Reserva("R15", cliente, asesor, 1)
    def cancelar_confirmada():
        reserva_cancelar.confirmar()
        reserva_cancelar.cancelar()
        return reserva_cancelar.estado
    registrar(15, "Cancelación de reserva confirmada", cancelar_confirmada)

    reserva_repetida = Reserva("R16", cliente, asesor, 1)
    def cancelar_repetida():
        reserva_repetida.confirmar()
        reserva_repetida.cancelar()
        reserva_repetida.cancelar()
    registrar(16, "Cancelación repetida", cancelar_repetida)

    print("\\nSimulaciones ejecutadas:", len(resultados))
    print("Los eventos y errores se guardan en logs/eventos.log.")
    return resultados


if __name__ == "__main__":
    ejecutar_simulaciones()
