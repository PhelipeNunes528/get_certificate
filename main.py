import ssl
import socket
import hashlib
import sys
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timezone

def get_certificate_der(host: str, port: int = 443) -> bytes:
    ctx = ssl.create_default_context()

    with socket.create_connection((host, port), timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as tls_sock:
            der_cert = tls_sock.getpeercert(binary_form=True)

    return der_cert

def extract_public_key_der(der_cert: bytes) -> bytes:

    cert = x509.load_der_x509_certificate(der_cert)
    pub_key = cert.public_key()
    pub_key_der = pub_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return cert, pub_key_der

def sha256_b64(data: bytes) -> str:
    import base64
    digest = hashlib.sha256(data).digest()
    return base64.b64encode(digest).decode("ascii")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main():
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 443

    print(f"\033[92mConectando em {host}:{port} ...\n\033[0m")

    try:
        der_cert = get_certificate_der(host, port)
    except Exception as e:
        print("\033[91m[ERRO] Falha ao conectar/handshake\033[0m")
        sys.exit(1)

    cert, pub_key_der = extract_public_key_der(der_cert)

    print("=" * 70)
    print("CERTIFICADO DO SERVIDOR")
    print("=" * 70)
    print(f"Subject              : {cert.subject.rfc4514_string()}")
    print(f"Issuer (quem assinou): {cert.issuer.rfc4514_string()}")
    print(f"Número de série      : {cert.serial_number}")
    print(f"Válido a partir de   : {cert.not_valid_before_utc}")
    print(f"Válido até           : {cert.not_valid_after_utc}")

    now = datetime.now(timezone.utc)
    dias_restantes = (cert.not_valid_after_utc - now).days
    print(f"Dias até expirar     : {dias_restantes}")

    try:
        san_ext = cert.extensions.get_extension_for_class(
            __import__("cryptography.x509", fromlist=["SubjectAlternativeName"]).SubjectAlternativeName
        )
        sans = san_ext.value.get_values_for_type(
            __import__("cryptography.x509", fromlist=["DNSName"]).DNSName
        )
        print(f"SANs (outros domínios): {', '.join(sans[:10])}{' ...' if len(sans) > 10 else ''}")
    except Exception:
        print("SANs                 : não encontrado")

    print()
    print("=" * 70)
    print("CHAVE PÚBLICA")
    print("=" * 70)
    print(f"Algoritmo            : {cert.public_key().__class__.__name__}")

    print()
    print("--- HASH DO CERTIFICADO INTEIRO ---")
    print(f"SHA-256 (hex)        : {sha256_hex(der_cert)}")
    print(f"SHA-256 (base64)     : {sha256_b64(der_cert)}")

    print()
    print("--- HASH DA CHAVE PÚBLICA ---")
    print(f"SHA-256 (hex)        : {sha256_hex(pub_key_der)}")
    print(f"SHA-256 (base64)     : {sha256_b64(pub_key_der)}")

if __name__ == "__main__":
    main()