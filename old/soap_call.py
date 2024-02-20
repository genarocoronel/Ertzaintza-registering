from zeep.transports import Transport
from requests import Session
from zeep import Client
import zeep_plugins, tokens
from zeep.wsse import BinarySignature
from zeep.wsse.signature import Signature
from xmlsec import constants

session = Session()


ertz_key_file_encrypted = 'old/RegistroHostelero 140921/RegistroHostelero/RegistroHosteleroSOAPUI/drlive.key'
ertz_cert_chain_file = 'old/RegistroHostelero 140921/RegistroHostelero/RegistroHosteleroSOAPUI/cert.pem'  #that is a chain certificate
ertz_cert_file = 'old/RegistroHostelero 140921/RegistroHostelero/RegistroHosteleroSOAPUI/drlive.crt'
#ertz_cert_file = ertz_cert_chain_file
#ertz_key_file = 'RegistroHostelero 140921/RegistroHostelero/RegistroHosteleroSOAPUI/drlive-decrypted.pem'
pkcs12_der_key = 'old/RegistroHostelero 140921/RegistroHostelero/RegistroHosteleroSOAPUI/A19PREEMPRESA.pfx'
#ertz_key_file = 'RegistroHostelero 140921/RegistroHostelero/RegistroHosteleroSOAPUI/drlive.key'
ertz_key_file = 'old/RegistroHostelero 140921/RegistroHostelero/RegistroHosteleroSOAPUI/drlive-decrypted.key'
#session.cert = (ertz_cert_file, ertz_key_file)
session.cert = ertz_cert_file
session.verify = ertz_cert_chain_file
#session.verify = False
credentials = dict(certfile=ertz_cert_file, key_file=ertz_key_file)
#credentials_encrypted = dict(certfile=ertz_cert_file, key_file=ertz_key_file_encrypted, pwd=b'pempa')
credentials_encrypted = dict(certfile=ertz_cert_file, key_file=pkcs12_der_key, pwd=b'1')
mycredentials = dict(certfile='mycert/fullchain.pem', key_file='mycert/privkey.pem')
bsignature = BinarySignature(key_file=ertz_key_file, certfile=ertz_cert_file, signature_method=constants.TransformRsaSha1)
signature = Signature(**credentials, signature_method=constants.TransformRsaSha1)
mysignature = Signature(**mycredentials, signature_method=constants.TransformRsaSha1)



timestamp_token = tokens.get_username_token()

session.cert = (ertz_cert_file, ertz_key_file)
#session.auth = HTTPBasicAuth('202004', 'lkdKJ93s')
transport = Transport(session=session)
#wsses = [ bsignature]
#wsses = [signature, bsignature]

wsses = []
logging_plugin_instance = zeep_plugins.MyLoggingPlugin([timestamp_token, bsignature], xmlsec_sign=False,
                                                       body_id="idBody",
                                                       signature_template="signature_template_BST_trimmed.xml",
                                                       **credentials_encrypted)

plugins = []
#plugins.append(WsAddressingPlugin())
plugins.append(logging_plugin_instance)
#client = Client('https://servicios.pre.ertzaintza.eus/A19/registroHostelero/EnvioFicheroXML?wsdl', transport=transport)
#with open("A19/RegistroHostelero/Manuales_Usuario/EnvioFicheroXML.wsdl", "rb") as f:
with open("WSDL_nuevo.xml", "rb") as f:
    client = Client(f, transport=transport, wsse=wsses, plugins=plugins)

with open("ejemplo.xml", "r") as f:
    data = f.read()
client.settings.raw_response = True
client.settings.strict = False
# https://servicios.pre.ertzaintza.eus/A19/registroHostelero/EnvioFichero
response_local = client.service.envioFicheroXML(cabecera={"aplicacion": "Cloudbeds integration", "codigoArrendador": "B20805578", "tipoComunicacion": "PV"}, solicitud=data)
print(response_local)