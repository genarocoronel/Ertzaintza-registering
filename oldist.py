import soap_call, pathlib
fichero = pathlib.Path("old/202004.txt").read_text()
credentials = dict(key_file="old/mycert/privkey.pem", certfile="old/mycert/fullchain.pem")
#client_old = soap_call.get_client("old/EnvioFichero.xml", soap_call.credentials_encrypted, "a19preempresa", "1")
client_old = soap_call.get_client("old/EnvioFichero.xml", credentials, "a19preempresa", "1")
response = client_old.service.envioFichero(fichero=fichero, language="es", nombreFichero="202004.txt", cif="B20805578")
print(response.text)