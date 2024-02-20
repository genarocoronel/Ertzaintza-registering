from typing import Literal, List, Optional
from pydantic import BaseModel
import datetime
class TipoPago(BaseModel):
    tipoPago: str
    fechaPago: datetime.date


class TipoCabecera(BaseModel):
    aplicacion: str
    codigoArrendador: str
    tipoComunicacion: Literal["PV", "RH"]


class Contrato(BaseModel):
    referencia: str
    fechaContrato: datetime.date
    fechaEntrada: datetime.datetime
    fechaSalida: datetime.datetime
    numPersonas: int
    numHabitaciones: int
    internet: bool
    pago: TipoPago


class Direccion(BaseModel):
    direccion: str
    direccion2: str
    localidad: str
    provincia: str
    codigoPostal: str
    pais: str


class Persona(BaseModel):
    rol: Literal["TI", "VI"]
    nombre: str
    apellido1: str
    apellido2: str
    tipoDocumento: str
    numeroDocumento: str
    soporteDocumento: str
    fechaNacimiento: datetime.date
    nacionalidad: str
    sexo: Literal["H", "M"]
    direccion: Direccion
    telefono: str
    telefono2: str
    correo: str
    parentesco: Optional[int] = None

    #Pero fechaNacimiento es un string de fecha, tipo 2022-09-29, no un string normal


class DatosEstablecimiento(BaseModel):
    tipo: str
    nombre: str
    direccion: Direccion


class Establecimiento(BaseModel):
    codigoEstablecimiento: str #CodigoEstablecimientoType?
    datosEstablecimiento: DatosEstablecimiento


class ComunicacionPV(BaseModel):
    #cabecera: TipoCabecera
    contrato: Contrato
    persona: List[Persona]


class SolicitudPV(BaseModel):
    #cabecera: TipoCabecera
    codigoEstablecimiento: str
    comunicacion: ComunicacionPV

class PeticionPV(BaseModel):
    solicitud: SolicitudPV


class ItemPV(BaseModel):
    cabecera: TipoCabecera
    solicitud: PeticionPV

class ComunicacionRH(BaseModel):
    #cabecera: TipoCabecera
    establecimiento: Establecimiento
    contrato: Contrato
    persona: List[Persona]

class SolicitudRH(BaseModel):
    #cabecera: TipoCabecera
    codigoEstablecimiento: str
    comunicacion: ComunicacionRH

class PeticionRH(BaseModel):
    solicitud: SolicitudRH


class ItemRH(BaseModel):
    cabecera: TipoCabecera
    solicitud: PeticionRH
