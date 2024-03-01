from zeep.transports import Transport
from requests import Session
from zeep import Client
import zeep_plugins, tokens
from zeep.wsse import Signature
import os, certifi, pathlib
cawhere = pathlib.Path(certifi.where())
print("cwhr", cawhere)
session = Session()

ertz_key_file_encrypted = 'A19/RegistroHostelero/RegistroHosteleroSOAPUI/drlive.key'
ertz_cert_chain_file = 'A19/RegistroHostelero/RegistroHosteleroSOAPUI/cert.pem'  #that is a chain certificate
ertz_cert_file = 'A19/RegistroHostelero/RegistroHosteleroSOAPUI/drlive.crt'
pkcs12_der_key = 'A19/RegistroHostelero/RegistroHosteleroSOAPUI/A19PREEMPRESA.pfx'
ertz_key_file_decrypted = 'A19/RegistroHostelero/RegistroHosteleroSOAPUI/drlive-decrypted.key'

#session.cert = (ertz_cert_file, ertz_key_file_decrypted)
#session.verify = ertz_cert_chain_file
session.cafile = cawhere
session.capath = cawhere.parent
session.verify = False
session.auth = ('a19preempresa', '1')
transport = Transport(session=session)


#credentials = dict(key_file=ertz_key_file_decrypted, certfile=ertz_cert_file)
credentials_encrypted = dict(certfile=ertz_cert_file, key_file=pkcs12_der_key, password='1')

def apply_logging_plugin_instance(wsdl_file, credentials, wsses, xmlsec_sign, xmlsec_verify,
                                  signature_template, xml_file):
    logging_plugin_instance = zeep_plugins.MyLoggingPlugin(wsses,
                                                           xmlsec_sign=xmlsec_sign,
                                                           xmlsec_verify=xmlsec_verify,
                                                           body_id="idBody",
                                                           signature_template=signature_template,
                                                           xml_file=xml_file,
                                                           **credentials)
    plugins = [logging_plugin_instance]
    with open(wsdl_file, "rb") as f:
        client = Client(f, transport=transport, wsse=[], plugins=plugins)
    client.settings.raw_response = True
    client.settings.strict = False
    return client


def get_client(wsdl_file, credentials_encrypted, username, password, xml_file=None):
    timestamp_token = tokens.get_username_token(username, password, use_digest=True)
    #timestamp_token = tokens.get_original_utt(username, password)
    digest_method = None
    signature_method = None # instead of constants.TransformRsaSha1
    signature = Signature(**credentials_encrypted, signature_method=signature_method, digest_method=digest_method)#or signature constants.TransformSha1
    #bsignature = tokens.BinarySignature(**credentials_encrypted, signature_method=signature_method, digest_method=digest_method)
    pbsignature = tokens.PersonalizedBinarySignature(**credentials_encrypted,
                                                    signature_method=signature_method,
                                                     digest_method=digest_method,key_format=6) # 6 is the format for PCKS12 PEM
    return apply_logging_plugin_instance(wsdl_file, credentials_encrypted, [timestamp_token, pbsignature],
                                         False, True, os.path.join("inputs", "signature_template_BST_2_other_algorithm.xml"),
                                         xml_file=xml_file)


def read_ejemplo_PV():
    with open(os.path.join("inputs", "ejemploPV.xml"), "r") as f:
        cdata = f.read()
    return cdata

if __name__ == "__main__":
    cdata = read_ejemplo_PV()
    credentials = dict(key_file="old/mycert/privkey.pem", certfile="old/mycert/fullchain.pem")
    #client = get_client("WSDL_nuevo.xml", credentials_encrypted, "202004", "lkdKJ93s")
    client = get_client("inputs/WSDL_nuevo.xml", credentials_encrypted, "a19preempresa",
                        "1", xml_file=None)
    #response = client.service.envioFicheroXML(cabecera={"aplicacion": "A19", "codigoArrendador": "B20805578", "tipoComunicacion": "PV"}, solicitud=cdata)
    #response = client.service.envioFicheroXML(cabecera={"aplicacion": "A19", "codigoArrendador": "codBueno", "tipoComunicacion": "PV"}, solicitud=cdata)
    response = client.service.envioFicheroXML(cabecera={"aplicacion": "Sistema de comunicaciones para alojamientos", "codigoArrendador": "B76345879", "tipoComunicacion": "PV"}, solicitud=cdata)
    print(response.text)