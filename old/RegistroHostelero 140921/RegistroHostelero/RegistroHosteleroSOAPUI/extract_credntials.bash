#!/usr/bin/env bash
#cd RegistroHostelero\ 140921/RegistroHostelero/RegistroHosteleroSOAPUI/
openssl pkcs12 -in A19PREEMPRESA.pfx -nocerts -out drlive.key
openssl pkcs12 -in A19PREEMPRESA.pfx -clcerts -nokeys -out drlive.crt
openssl rsa -in drlive.key -out drlive-decrypted.key
openssl rsa -in drlive-decrypted.key -outform PEM -out drlive-decrypted-no-pp.pem

openssl rsa -in drlive.crt -out drlive-decrypted.crt