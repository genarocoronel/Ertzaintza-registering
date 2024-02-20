openssl rsa -modulus -noout -in drlive-decrypted.key | openssl md5
openssl rsa -check -noout -in drlive-decrypted.key
openssl rsa -modulus -noout -in drlive-decrypted.pem | openssl md5
openssl rsa -check -noout -in drlive-decrypted.pem
openssl rsa -modulus -noout -in drlive.key | openssl md5
openssl rsa -check -noout -in drlive.key

openssl x509 -modulus -noout -in drlive.crt | openssl md5
openssl x509 -modulus -noout -in cert.pem | openssl md5