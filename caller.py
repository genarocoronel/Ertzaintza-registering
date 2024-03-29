from tipos import (Contrato, TipoPago, Direccion, Persona, TipoCabecera,
                   DatosEstablecimiento, Establecimiento, Persona, ComunicacionRH,
                   ComunicacionPV, ItemPV,  SolicitudPV, TipoCabecera, TipoPago,
                   PeticionPV, SolicitudRH, PeticionRH, ItemRH, Direccion, Persona,)
from soap_call import get_client, read_ejemplo_PV, credentials_encrypted, ertz_cert_file
import dicttoxml, io, os
from zeep_plugins import prettify_xml
from lxml import etree

contrato = Contrato(referencia="B20805578-1", fechaContrato="2022-09-29",
                    fechaEntrada="2022-09-19T01:18:33", fechaSalida="2022-09-21T19:27:14+02:00",
                    numPersonas=2, numHabitaciones=1, internet=True, pago=TipoPago(tipoPago="EFECT", fechaPago="2022-09-29"))
direccion = Direccion(direccion="Paseo de las Camelias 456", direccion2="Retorno de los Laureles",
                      localidad="Zaragoza", provincia="Zaragoza", codigoPostal="50012", pais="ES")
persona1 = Persona(rol="TI", referencia="ref1", nombre="Juan", apellido1="Perez", apellido2="Gomez",
                   tipoDocumento="DNI", numeroDocumento="12345678", soporteDocumento="DNI",
                   fechaNacimiento="1956-05-02", nacionalidad="ES", sexo="H", direccion=direccion,
                   telefono="777777777", telefono2="777777777", correo="person1@example.com")
persona2 = Persona(rol="VI", referencia="ref2", nombre="Eliseo", apellido1="Perez", apellido2="Campa",
                   tipoDocumento="DNI", numeroDocumento="12345679", soporteDocumento="DNI",
                   fechaNacimiento="1986-02-09", nacionalidad="ES", sexo="H", direccion=direccion,
                   telefono="777777777", telefono2="777777777", correo="person2@example.com",
                   parentesco=12)
direccionEstablecimiento = Direccion(direccion="NAFARROA CALLE 37 A", direccion2="BA",
                                     localidad="Zarautz", provincia="Gipuzkoa",
                                     codigoPostal="48901", pais="ESP")
establecimiento = Establecimiento(codigoEstablecimiento="C1123",
                                  datosEstablecimiento=DatosEstablecimiento(tipo="albergue",
                                                                            nombre="BLAI BLAI ATERPETXEA BSS00029",
                                                                            direccion=direccionEstablecimiento))
cabecera = {"aplicacion": "Cloudbeds integration", "codigoArrendador": "B20805578",
            "tipoComunicacion": "PV"}
cab_convertido = TipoCabecera(**cabecera)


# https://servicios.pre.ertzaintza.eus/A19/registroHostelero/EnvioFichero

def get_test_PV_item():
    compv = ComunicacionPV(contrato=contrato, establecimiento=establecimiento, persona=[persona1, persona2])
    solpv = SolicitudPV(codigoEstablecimiento="C1123", comunicacion=compv)
    petpv = PeticionPV(solicitud=solpv)
    return ItemPV(cabecera=cab_convertido, solicitud=petpv)

def get_test_RH_item():
    comrh = ComunicacionRH(contrato=contrato, establecimiento=establecimiento, persona=[persona1, persona2])
    solrh = SolicitudRH(codigoEstablecimiento="C1123", comunicacion=comrh)
    petrh = PeticionRH(solicitud=solrh)
    return ItemRH(cabecera=cab_convertido, solicitud=petrh)
def PV_call(xml_file=None):
    #cdata = read_ejemplo_PV()
    git = get_test_PV_item()
    #xmld = dicttoxml.dicttoxml(git.solicitud.dict(), xml_declaration=False, attr_type=False, root=False)
    xmldp = prettify_xml(xmld)
    cdataer = f'<![CDATA[<alt:peticion xmlns:alt="http://www.servicios.ertzaintza.eus/Ertzaintza/ALOJADOS/A19/comunicacionPV">\n{xmldp.decode()}\n</alt:peticion>]]>'
    client = get_client("inputs/WSDL_nuevo.xml", credentials_encrypted, "a19preempresa", "1", xml_file=xml_file)
    response = client.service.envioFicheroXML(cabecera=git.cabecera.dict(), solicitud=cdataer)
    #print(response.text)
    return (response.text, response.status_code, response.headers)

def RH_call(xml_file=None):
    #cdata = read_ejemplo_PV()
    git = get_test_RH_item()
    xmld = dicttoxml.dicttoxml(git.solicitud.dict(), xml_declaration=False, attr_type=False, root=False)
    xmldp = prettify_xml(xmld)
    cdataer = f'<![CDATA[<alt:peticion xmlns:alt="http://www.servicios.ertzaintza.eus/Ertzaintza/ALOJADOS/A19/comunicacionPV">\n{xmldp.decode()}\n</alt:peticion>]]>'
    client = get_client(os.path.join("inputs", "WSDL_nuevo.xml"), credentials_encrypted, "a19preempresa", "1", xml_file=xml_file)
    response = client.service.envioFicheroXML(cabecera=git.cabecera.dict(), solicitud=cdataer)
    #print(response.text)
    return (response.text, response.status_code, response.headers)

def API_call(xml_file_or_string, credentials_file, password):
    #cdata = read_ejemplo_PV()
    git = get_test_RH_item()
    xmld = dicttoxml.dicttoxml(git.solicitud.dict(), xml_declaration=False, attr_type=False, root=False)
    xmldp = prettify_xml(xmld)
    cdataer = f'<![CDATA[<alt:peticion xmlns:alt="http://www.servicios.ertzaintza.eus/Ertzaintza/ALOJADOS/A19/comunicacionPV">\n{xmldp.decode()}\n</alt:peticion>]]>'
    if credentials_file is None:
        credentials = credentials_encrypted
    else:
        credentials = dict(key_file=credentials_file, certfile=ertz_cert_file, password=password)
    client = get_client(os.path.join("inputs", "WSDL_nuevo.xml"), credentials, "a19preempresa", "1", xml_file=xml_file_or_string)
    #as the xml_file argument was provided to the get_client function, the cabecera and solicitud arguments will be ignoered
    response = client.service.envioFicheroXML(cabecera=git.cabecera.dict(), solicitud=cdataer)
    #print(response.text)
    return (response.text, response.status_code, response.headers)

if __name__ == "__main__":
    #test_RH()
    with open(os.path.join("inputs", "perfecto2_seeu.xml"), "r") as f:
        ta = API_call(f, None,  None)
        print("Response: ", ta[1], ta[0])