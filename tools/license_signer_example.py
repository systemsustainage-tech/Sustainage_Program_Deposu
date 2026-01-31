#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Server-side License Signer Example (DO NOT bundle into application)

Generates/loads an RSA private key and signs a license payload.
Outputs JSON payload and base64 signature.
"""
from __future__ import annotations

import logging
import base64
import json
import pathlib
import time
from typing import Dict

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def generate_private_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=3072,
        backend=default_backend(),
    )


def save_private_key_pem(priv: rsa.RSAPrivateKey, path: str, password: str | None = None) -> None:
    enc_algo = serialization.BestAvailableEncryption(password.encode()) if password else serialization.NoEncryption()
    pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=enc_algo,
    )
    pathlib.Path(path).write_bytes(pem)


def save_public_key_pem(pub, path: str) -> None:
    pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    pathlib.Path(path).write_bytes(pem)


def load_private_key_pem(path: str, password: str | None = None) -> rsa.RSAPrivateKey:
    data = pathlib.Path(path).read_bytes()
    return serialization.load_pem_private_key(data, password=password.encode() if password else None, backend=default_backend())


def sign_payload(priv: rsa.RSAPrivateKey, payload: Dict) -> str:
    data = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = priv.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("ascii")


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="RSA License Signer Example")
    ap.add_argument("--out", default="license_signed.json", help="Çıktı dosyası")
    ap.add_argument("--priv", default="private_key.pem", help="Özel anahtar PEM")
    ap.add_argument("--pub", default="public_key.pem", help="Genel anahtar PEM (oluşturur)")
    ap.add_argument("--passwd", default=None, help="Özel anahtar parolası")
    ap.add_argument("--company", required=True)
    ap.add_argument("--license_id", required=True)
    ap.add_argument("--hwid_core", required=True)
    ap.add_argument("--hwid_full", required=True)
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--modules", nargs="*", default=["core"])
    args = ap.parse_args()

    priv_path = pathlib.Path(args.priv)
    if priv_path.exists():
        priv = load_private_key_pem(str(priv_path), password=args.passwd)
    else:
        priv = generate_private_key()
        save_private_key_pem(priv, str(priv_path), password=args.passwd)
        save_public_key_pem(priv.public_key(), args.pub)

    now = int(time.time())
    payload = {
        "company": args.company,
        "license_id": args.license_id,
        "hwid_core": args.hwid_core,
        "hwid_full": args.hwid_full,
        "issued_at": now,
        "expires_at": now + (args.days * 24 * 60 * 60),
        "modules": args.modules,
        "format": "rsa_v1",
    }

    sig_b64 = sign_payload(priv, payload)
    out = {"payload": payload, "signature": sig_b64}
    pathlib.Path(args.out).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    logging.info(f"Written: {args.out}\nPublic key: {args.pub}")


if __name__ == "__main__":
    main()
