from abc import ABC, abstractmethod  
from datetime import datetime 
import logging  



logger = logging.getLogger("SoftwareFJLogger")  
logger.setLevel(logging.INFO)  

if not logger.handlers:  
    file_handler = logging.FileHandler("software_fj.log", mode="a", encoding="utf-8")  
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s") 
    file_handler.setFormatter(formatter)  
    logger.addHandler(file_handler)  


class SoftwareFJError(Exception):  
    """Excepción base para errores del sistema Software FJ."""  


class DatoInvalidoError(SoftwareFJError):  
    """Se lanza cuando un dato o parámetro no es válido."""  


class ServicioNoDisponibleError(SoftwareFJError):  
    """Se lanza cuando un servicio no está disponible para operar."""  


class OperacionReservaError(SoftwareFJError): 
    """Se lanza cuando falla una operación asociada a una reserva."""  


class CalculoCostoError(SoftwareFJError):  
    """Se lanza cuando ocurre un error en el cálculo de costos."""  



class EntidadSistema(ABC): 
    """Clase abstracta que representa entidades generales dentro del sistema."""  

    def __init__(self, id_entidad: str):  
        if not isinstance(id_entidad, str) or not id_entidad.strip():  
            raise DatoInvalidoError("El identificador de la entidad debe ser un texto no vacío.")  
        self._id_entidad = id_entidad.strip()  

    @property
    def id_entidad(self) -> str: 
        return self._id_entidad  

    @abstractmethod
    def resumen(self) -> str:  
        """Devuelve un resumen legible de la entidad."""  



class Cliente(EntidadSistema):  
    """Representa un cliente con datos encapsulados y validaciones estrictas."""  

    def __init__(self, id_cliente: str, nombre: str, correo: str, activo: bool = True):  
        super().__init__(id_cliente)  
        self.nombre = nombre 
        self.correo = correo  
        self._activo = bool(activo)  

    @property
    def nombre(self) -> str:  
        return self._nombre  

    @nombre.setter
    def nombre(self, valor: str): 
        if not isinstance(valor, str) or len(valor.strip()) < 2: 
            raise DatoInvalidoError("El nombre del cliente debe tener al menos 2 caracteres.") 
        self._nombre = valor.strip()  

    @property
    def correo(self) -> str:  
        return self._correo  

    @correo.setter
    def correo(self, valor: str):  
        if not isinstance(valor, str) or "@" not in valor or "." not in valor.split("@")[-1]:  
            raise DatoInvalidoError(f"Correo electrónico inválido: '{valor}'.")  
        self._correo = valor.strip().lower() 

    @property
    def activo(self) -> bool:  
        return self._activo 

    def desactivar(self):  
        self._activo = False  

    def resumen(self) -> str:  
        estado = "Activo" if self._activo else "Inactivo"  
        return f"Cliente[{self.id_entidad}] {self._nombre} ({self._correo}) - {estado}"  



class Servicio(EntidadSistema, ABC):  
    """Clase abstracta base para los distintos servicios de Software FJ."""  

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, disponible: bool = True):  
        super().__init__(id_servicio) 
        if not isinstance(nombre, str) or not nombre.strip():  
            raise DatoInvalidoError("El nombre del servicio es obligatorio.")  
        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:  
            raise DatoInvalidoError("La tarifa base debe ser un número mayor que cero.")  
        self._nombre = nombre.strip()  
        self._tarifa_base = float(tarifa_base)  
        self._disponible = bool(disponible) 

    @property
    def nombre(self) -> str:  
        return self._nombre  

    @property
    def tarifa_base(self) -> float: 
        return self._tarifa_base  

    @property
    def disponible(self) -> bool: 
        return self._disponible  

    @disponible.setter
    def disponible(self, valor: bool):  
        if not isinstance(valor, bool):  
            raise DatoInvalidoError("La disponibilidad debe ser un valor booleano (True/False).")  
        self._disponible = valor  

    @abstractmethod
    def validar_parametros(self, duracion: int, **kwargs): 
        """Valida duración y parámetros específicos de cada tipo de servicio."""  

    @abstractmethod
    def describir(self) -> str: 
        """Devuelve la descripción detallada del servicio.""" 

    @abstractmethod
    def calcular_costo(  
        self,
        duracion: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        **kwargs,
    ) -> float:
        """Calcula el costo aplicando validaciones, descuentos opcionales e impuestos opcionales."""  

    def _aplicar_ajustes_financieros(self, subtotal: float, descuento_pct: float, impuesto_pct: float) -> float:  
        try:  
            if subtotal < 0:  
                raise CalculoCostoError("El subtotal no puede ser negativo.")  
            if not (0 <= descuento_pct < 100):  
                raise DatoInvalidoError("El porcentaje de descuento debe estar entre 0 y 99.99.")  
            if impuesto_pct < 0:  
                raise DatoInvalidoError("El porcentaje de impuesto no puede ser negativo.")  

            con_descuento = subtotal * (1 - descuento_pct / 100.0)  
            total = con_descuento * (1 + impuesto_pct / 100.0)  
            return round(total, 2) 
        except (TypeError, ZeroDivisionError, ValueError) as exc:  
            raise CalculoCostoError("Error interno al calcular el costo final del servicio.") from exc  

    def resumen(self) -> str: 
        estado = "Disponible" if self._disponible else "No disponible"  
        return f"Servicio[{self.id_entidad}] {self._nombre} (${self._tarifa_base:.2f}) - {estado}"  


class ReservaSala(Servicio): 
    """Servicio especializado para reserva de salas.""" 

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, capacidad_maxima: int, disponible: bool = True):  
        super().__init__(id_servicio, nombre, tarifa_base, disponible) 
        if not isinstance(capacidad_maxima, int) or capacidad_maxima <= 0: 
            raise DatoInvalidoError("La capacidad máxima de la sala debe ser un entero mayor que cero.")  
        self.capacidad_maxima = capacidad_maxima 

    def validar_parametros(self, duracion: int, asistentes: int = 1, **kwargs): 
        if not isinstance(duracion, int) or duracion <= 0: 
            raise DatoInvalidoError("La duración de reserva de sala debe ser un entero positivo (horas).") 
        if not isinstance(asistentes, int) or asistentes <= 0: 
            raise DatoInvalidoError("El número de asistentes debe ser mayor que cero.")  
        if asistentes > self.capacidad_maxima: 
            raise DatoInvalidoError( 
                f"Los asistentes ({asistentes}) superan la capacidad de la sala ({self.capacidad_maxima})."
            )

    def describir(self) -> str:  
        return (  
            f"[Sala] {self.nombre} | Capacidad máx.: {self.capacidad_maxima} personas | "
            f"Tarifa/hora: ${self.tarifa_base:.2f}"
        )

    def calcular_costo(  
        self,
        duracion: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        asistentes: int = 1,
        recargo_por_persona_extra: float = 0.0,
        **kwargs,
    ) -> float:
        self.validar_parametros(duracion, asistentes=asistentes)  
        subtotal = self.tarifa_base * duracion  
        if asistentes > 5 and recargo_por_persona_extra > 0:  
            subtotal += (asistentes - 5) * recargo_por_persona_extra  
        return self._aplicar_ajustes_financieros(subtotal, descuento_pct, impuesto_pct)  


class AlquilerEquipo(Servicio): 
    """Servicio especializado para alquiler de equipos."""  

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, stock_unidades: int, disponible: bool = True):
        super().__init__(id_servicio, nombre, tarifa_base, disponible) 
        if not isinstance(stock_unidades, int) or stock_unidades <= 0:
            raise DatoInvalidoError("El stock inicial de equipos debe ser un entero mayor que cero.") 
        self.stock_unidades = stock_unidades 

    def validar_parametros(self, duracion: int, unidades: int = 1, **kwargs):  
        if not isinstance(duracion, int) or duracion <= 0:
            raise DatoInvalidoError("La duración del alquiler debe ser un entero positivo.")  
        if not isinstance(unidades, int) or unidades <= 0:  
            raise DatoInvalidoError("La cantidad de equipos a alquilar debe ser mayor que cero.")  
        if unidades > self.stock_unidades: 
            raise ServicioNoDisponibleError(  
                f"Stock insuficiente para '{self.nombre}': solicitados {unidades}, disponibles {self.stock_unidades}."
            )

    def describir(self) -> str:  
        return (  
            f"[Equipo] {self.nombre} | Unidades disponibles: {self.stock_unidades} | "
            f"Tarifa/unidad/período: ${self.tarifa_base:.2f}"
        )

    def calcular_costo(  
        self,
        duracion: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        unidades: int = 1,
        **kwargs,
    ) -> float:
        self.validar_parametros(duracion, unidades=unidades)  
        subtotal = self.tarifa_base * duracion * unidades  
        return self._aplicar_ajustes_financieros(subtotal, descuento_pct, impuesto_pct)  


class AsesoriaEspecializada(Servicio):  
    """Servicio especializado para asesorías técnicas o estratégicas."""  

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, especialidad: str, disponible: bool = True):  
        super().__init__(id_servicio, nombre, tarifa_base, disponible)  
        if not isinstance(especialidad, str) or not especialidad.strip():  
            raise DatoInvalidoError("La especialidad de la asesoría es obligatoria.") 
        self.especialidad = especialidad.strip()  

    def validar_parametros(self, duracion: int, modalidad: str = "remota", **kwargs):  
        if not isinstance(duracion, int) or duracion <= 0: 
            raise DatoInvalidoError("La duración de la asesoría debe ser un entero positivo.") 
        if modalidad not in ("remota", "presencial"): 
            raise DatoInvalidoError("La modalidad de asesoría debe ser 'remota' o 'presencial'.") 

    def describir(self) -> str:  
        return (  
            f"[Asesoría] {self.nombre} | Especialidad: {self.especialidad} | "
            f"Tarifa base: ${self.tarifa_base:.2f}"
        )

    def calcular_costo(  
        self,
        duracion: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        modalidad: str = "remota",
        recargo_presencial: float = 20.0,
        **kwargs,
    ) -> float:
        self.validar_parametros(duracion, modalidad=modalidad)  
        subtotal = self.tarifa_base * duracion  
        if modalidad == "presencial":  
            subtotal += recargo_presencial 
        return self._aplicar_ajustes_financieros(subtotal, descuento_pct, impuesto_pct)  



class Reserva(EntidadSistema):  
    """Gestiona una reserva con confirmación, cancelación y manejo de excepciones."""  

    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA")  

    def __init__(  
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        **detalle_servicio,
    ):
        super().__init__(id_reserva)  
        if not isinstance(cliente, Cliente):  
            raise DatoInvalidoError("Se requiere una instancia válida de Cliente.") 
        if not isinstance(servicio, Servicio): 
            raise DatoInvalidoError("Se requiere una instancia válida de Servicio.")  
        if not cliente.activo: 
            raise OperacionReservaError(f"El cliente '{cliente.nombre}' no está activo para realizar reservas.")  
        if not servicio.disponible:  
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible actualmente.")  

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion 
        self.detalle_servicio = detalle_servicio 
        self.estado = "PENDIENTE"
        self.creada_en = datetime.now().isoformat(timespec="seconds")
        self.costo_total = self.servicio.calcular_costo(  
            duracion=self.duracion,
            descuento_pct=descuento_pct,
            impuesto_pct=impuesto_pct,
            **self.detalle_servicio,
        )

    def confirmar(self):  
        if self.estado == "CANCELADA":  
            raise OperacionReservaError(f"No se puede confirmar la reserva {self.id_entidad}: está CANCELADA.")  
        if self.estado == "CONFIRMADA":  
            raise OperacionReservaError(f"La reserva {self.id_entidad} ya se encuentra CONFIRMADA.")  
        if not self.servicio.disponible: 
            raise ServicioNoDisponibleError(f"No se puede confirmar: el servicio '{self.servicio.nombre}' no está disponible.")  

        self.servicio.validar_parametros(self.duracion, **self.detalle_servicio) 
        if isinstance(self.servicio, AlquilerEquipo):  
            unidades = self.detalle_servicio.get("unidades", 1) 
            self.servicio.stock_unidades -= unidades 
            if self.servicio.stock_unidades == 0: 
                self.servicio.disponible = False  

        self.estado = "CONFIRMADA"  

    def cancelar(self, motivo: str = "Sin motivo especificado"):  
        if self.estado == "CANCELADA":  
            raise OperacionReservaError(f"La reserva {self.id_entidad} ya está CANCELADA.")  

        if self.estado == "CONFIRMADA" and isinstance(self.servicio, AlquilerEquipo):  
            unidades = self.detalle_servicio.get("unidades", 1)  
            self.servicio.stock_unidades += unidades  
            self.servicio.disponible = True 

        self.estado = "CANCELADA"  
        logger.info(f"Reserva {self.id_entidad} cancelada. Motivo: {motivo}")  

    def resumen(self) -> str:  
        return (  
            f"Reserva[{self.id_entidad}] | Estado: {self.estado} | Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | Duración: {self.duracion} | Total: ${self.costo_total:.2f}"
        )


class SistemaGestionSoftwareFJ: 
    """Sistema en memoria para gestionar clientes, servicios y reservas de Software FJ."""  

    def __init__(self): 
        self.clientes: list[Cliente] = []  
        self.servicios: list[Servicio] = []  
        self.reservas: list[Reserva] = []  

    def _buscar_cliente(self, id_cliente: str) -> Cliente: 
        for cliente in self.clientes:  
            if cliente.id_entidad == id_cliente:  
                return cliente 
        raise DatoInvalidoError(f"No existe ningún cliente con ID '{id_cliente}'.")  

    def _buscar_servicio(self, id_servicio: str) -> Servicio: 
        for servicio in self.servicios:  
            if servicio.id_entidad == id_servicio:  
                return servicio  
        raise DatoInvalidoError(f"No existe ningún servicio con ID '{id_servicio}'.")  

    def _buscar_reserva(self, id_reserva: str) -> Reserva:  
        for reserva in self.reservas:  
            if reserva.id_entidad == id_reserva:  
                return reserva  
        raise DatoInvalidoError(f"No existe ninguna reserva con ID '{id_reserva}'.")  

    def registrar_cliente(self, id_cliente: str, nombre: str, correo: str, activo: bool = True) -> bool:  
        try:  
            if any(c.id_entidad == id_cliente for c in self.clientes):  
                raise DatoInvalidoError(f"Ya existe un cliente registrado con el ID '{id_cliente}'.")  
            nuevo_cliente = Cliente(id_cliente, nombre, correo, activo)  
        except SoftwareFJError as exc:  
            logger.error(f"Error al registrar cliente '{id_cliente}': {exc}")  
            print(f"[ERROR CLIENTE] {exc}")  
            return False  
        except Exception as exc:  
            raise OperacionReservaError("Fallo inesperado al registrar cliente.") from exc  
            
        else: 
            self.clientes.append(nuevo_cliente)  
            logger.info(f"Cliente registrado exitosamente: {nuevo_cliente.resumen()}") 
            print(f"[OK] {nuevo_cliente.resumen()}")  
            return True  
        finally:  
            logger.info(f"Fin de intento de registro de cliente (ID: {id_cliente}).")  

    def registrar_servicio(self, servicio: Servicio) -> bool:  
        try:  
            if not isinstance(servicio, Servicio):  
                raise DatoInvalidoError("El objeto proporcionado no es un Servicio válido.") 
            if any(s.id_entidad == servicio.id_entidad for s in self.servicios):  
                raise DatoInvalidoError(f"Ya existe un servicio con ID '{servicio.id_entidad}'.")  
        except SoftwareFJError as exc:  
            logger.error(f"Error al registrar servicio: {exc}") 
            print(f"[ERROR SERVICIO] {exc}")  
            return False  
        else:  
            self.servicios.append(servicio)  
            logger.info(f"Servicio registrado: {servicio.describir()}")  
            print(f"[OK] {servicio.describir()}") 
            return True  
        finally:  
            logger.info("Fin de intento de registro de servicio.")  

    def crear_reserva(  
        self,
        id_reserva: str,
        id_cliente: str,
        id_servicio: str,
        duracion: int,
        confirmar_inmediatamente: bool = True,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        **detalle_servicio,
    ) -> bool:
        try:  
            cliente = self._buscar_cliente(id_cliente)  
            servicio = self._buscar_servicio(id_servicio)  
            if any(r.id_entidad == id_reserva for r in self.reservas):  
                raise OperacionReservaError(f"Ya existe una reserva con el ID '{id_reserva}'.")  

            nueva_reserva = Reserva(  
                id_reserva=id_reserva,
                cliente=cliente,
                servicio=servicio,
                duracion=duracion,
                descuento_pct=descuento_pct,
                impuesto_pct=impuesto_pct,
                **detalle_servicio,
            )
            if confirmar_inmediatamente:  
                nueva_reserva.confirmar()  
        except SoftwareFJError as exc:  
            logger.error(f"Error en reserva '{id_reserva}': {exc}")  
            print(f"[ERROR RESERVA] {exc}")  
            return False  
        except Exception as exc:  
            raise OperacionReservaError(f"Error no previsto al procesar reserva '{id_reserva}'.") from exc
            
        else:  
            self.reservas.append(nueva_reserva)  
            logger.info(f"Reserva procesada: {nueva_reserva.resumen()}")  
            print(f"[OK] {nueva_reserva.resumen()}")  
            return True  
        finally:  
            logger.info(f"Fin de procesamiento de reserva (ID: {id_reserva}).")  

    def cancelar_reserva(self, id_reserva: str, motivo: str = "Cancelada por el usuario") -> bool:  
        try:  
            reserva = self._buscar_reserva(id_reserva) 
            reserva.cancelar(motivo=motivo)  
        except SoftwareFJError as exc:  
            logger.warning(f"No se pudo cancelar la reserva '{id_reserva}': {exc}")  
            print(f"[ERROR CANCELACIÓN] {exc}")  
            return False  
        else:  
            print(f"[OK] {reserva.resumen()}")  
            return True  
        finally:  
            logger.info(f"Fin de intento de cancelación de reserva (ID: {id_reserva}).")  



def ejecutar_simulacion():  
    sistema = SistemaGestionSoftwareFJ()  
    logger.info("=== INICIO DE SIMULACIÓN SOFTWARE FJ ===")  
    print("\n--- INICIANDO SIMULACIÓN DE OPERACIONES (SOFTWARE FJ) ---\n")  

    
    sistema.registrar_cliente("CLI-01", "Laura Gómez", "laura.gomez@correo.com", activo=True)

    
    sistema.registrar_cliente("CLI-02", "Carlos Ruiz", "correo_sin_arroba", activo=True)

    
    sistema.registrar_cliente("CLI-03", "Andrés Pérez", "andres.perez@empresa.co", activo=True)

    
    sala_reuniones = ReservaSala("SRV-SALA-1", "Sala Ejecutiva Norte", tarifa_base=50.0, capacidad_maxima=10)
    sistema.registrar_servicio(sala_reuniones)

    
    alquiler_laptops = AlquilerEquipo("SRV-EQ-1", "Laptops Desarrollador", tarifa_base=30.0, stock_unidades=4)
    sistema.registrar_servicio(alquiler_laptops)

    
    asesoria_arq = AsesoriaEspecializada("SRV-ASE-1", "Arquitectura Cloud", tarifa_base=120.0, especialidad="Cloud")
    sistema.registrar_servicio(asesoria_arq)

    
    try:  
        servicio_invalido = ReservaSala("SRV-ERR", "Sala Rota", tarifa_base=-15.0, capacidad_maxima=5)
        sistema.registrar_servicio(servicio_invalido)
    except SoftwareFJError as exc:  
        logger.error(f"Error al instanciar servicio inválido: {exc}")
        print(f"[ERROR SERVICIO] {exc}")

    #
    sistema.crear_reserva(
        id_reserva="RES-01",
        id_cliente="CLI-01",
        id_servicio="SRV-SALA-1",
        duracion=3,
        confirmar_inmediatamente=True,
        descuento_pct=10.0,
        impuesto_pct=19.0,
        asistentes=6,
    )

    
    sistema.crear_reserva(
        id_reserva="RES-02",
        id_cliente="CLI-03",
        id_servicio="SRV-EQ-1",
        duracion=2,
        confirmar_inmediatamente=True,
        unidades=2,
    )

    
    sistema.crear_reserva(
        id_reserva="RES-03",
        id_cliente="CLI-01",
        id_servicio="SRV-EQ-1",
        duracion=2,
        confirmar_inmediatamente=True,
        unidades=5,
    )

    
    sistema.crear_reserva(
        id_reserva="RES-04",
        id_cliente="CLI-99",
        id_servicio="SRV-ASE-1",
        duracion=2,
        confirmar_inmediatamente=True,
        modalidad="remota",
    )

    
    sistema.crear_reserva(
        id_reserva="RES-05",
        id_cliente="CLI-01",
        id_servicio="SRV-ASE-1",
        duracion=2,
        confirmar_inmediatamente=True,
        impuesto_pct=19.0,
        modalidad="presencial",
    )

    
    sistema.cancelar_reserva("RES-02", motivo="Cambio de cronograma del cliente")

    
    sistema.cancelar_reserva("RES-02", motivo="Intento duplicado de cancelación")

    
    print("\n--- ESTADO FINAL EN MEMORIA ---")
    for r in sistema.reservas: 
        print(r.resumen()) 

    logger.info("=== FIN DE SIMULACIÓN SOFTWARE FJ ===")  
    print("\nSimulación finalizada. Revisa el archivo 'software_fj.log' para ver el historial de eventos y errores.")


if __name__ == "__main__":  
    ejecutar_simulacion()  