from soap_call import client
import dicttoxml
from zeep_plugins import prettify_xml
from fastapi import FastAPI
from tipos import (Contrato, TipoPago, Direccion, Persona, TipoCabecera,
                   DatosEstablecimiento, Establecimiento, Persona, ComunicacionRH,
                   ComunicacionPV, ItemPV, ItemRH)

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/post")
async def read_root():
    return {"Hello": "World"}

@app.post("/PV")
def send_pv(item:ItemPV):
    xmld = dicttoxml.dicttoxml(item.solicitud.dict(), xml_declaration=False, attr_type=False, root=False)
    xmldp = prettify_xml(xmld)
    cdataer = f'<![CDATA[\n<alt:peticion xmlns:alt="http://servicios.pre.ertzaintza.eus/Ertzaintza/ALOJADOS/A19/comunicacionPV">\n{xmldp.decode()}\n</alt:peticion>]]>'
    response = client.service.envioFicheroXML(cabecera=item.cabecera.dict(), solicitud=cdataer)
    return {"response": response.text, "response_status_code": response.status_code, "response_headers": response.headers}


@app.post("/RH")
def send_rh(item:ItemRH):
    xmld = dicttoxml.dicttoxml(item.solicitud.dict(), xml_declaration=False, attr_type=False, root=False)
    xmldp = prettify_xml(xmld)
    cdataer = f'<![CDATA[\n<alt:peticion xmlns:alt="http://servicios.pre.ertzaintza.eus/Ertzaintza/ALOJADOS/A19/comunicacionPV">\n{xmldp.decode()}\n</alt:peticion>]]>'
    response = client.service.envioFicheroXML(cabecera=item.cabecera.dict(), solicitud=cdataer)
    return {"response": response.text, "response_status_code": response.status_code, "response_headers": response.headers}

@app.post("/PVe")
async def read_pve(item:ItemPV):
    #assert 0, item
    return {"Hello": "World"}