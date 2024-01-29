## easyrsa
- Download and initialize easyrsa3.
- Generate a new Certificate Authority (CA).
- Generate the server certificate and key.


## openssl
- Generate a `ca.key` with 2048 bits.
- Create a `ca.crt` based on ca.key.
- Generate a `server.key` with 2048 bits.
- Create a config file for generating a Certificate Signing Request (CSR).
- Generate the certificate signing request based on the config file.
- Generate the server certificate using `ca.key`, `ca.crt`, and `server.csr`.


## cfssl
- Download and prepare the command-line tools.
- Create a directory to hold the artifacts and initialize cfssl.
- Generate CA key (`ca-key.pem`) and certificate (`ca.pem`).
- Generate the key and certificate for the API server.
