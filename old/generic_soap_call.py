from zeep import Client
from zeep.transports import Transport
from requests import Session
import requests, pathlib, base64
session = Session()
#session.verify = 'RegistroHostelero 140921/RegistroHostelero/RegistroHosteleroSOAPUI/cert.pem'
#session.verify = True
#session.cert = 'RegistroHostelero 140921/RegistroHostelero/RegistroHosteleroSOAPUI/cert.pem'
# C1123-148.txt
from zeep import Client
url = "http://footballpool.dataaccess.eu/data/info.wso?WSDL"
cnt = Client(url)
#print(cnt.service.Info())
print(cnt.service.StadiumNames())
client_id = '202004'
nombre_fichero = '202004.txt'
contenido_fichero = pathlib.Path(nombre_fichero).read_text()
contenido_fichero_base64 = base64.b64encode(contenido_fichero.encode('utf-8'))
ejemplo=pathlib.Path('ejemplo_noheader_template.xml').read_text()
#samplefilepath = "RegistroHostelero 140921/RegistroHostelero/RegistroHosteleroSOAPUI/Registro-Hostelero-soapui-project_v2.xml"

#with open(samplefilepath, "rb") as f:
#rg = session.get('https://servicios.pre.ertzaintza.eus/A19/registroHostelero/EnvioFichero', verify=False)
ejemplo_substituido= ejemplo.format(contenido_fichero_base64, nombre_fichero)
rp = session.post('https://servicios.pre.ertzaintza.eus/A19/registroHostelero/EnvioFichero', data=ejemplo_substituido, verify=False)
assert 0, rp
transport = Transport(session=session)
client = Client('https://servicios.pre.ertzaintza.eus/A19/registroHostelero/EnvioFichero',
                transport=transport)
assert 0, client
result = client.service.ConvertSpeed(
    100, 'kilometersPerhour', 'milesPerhour')
print(result)