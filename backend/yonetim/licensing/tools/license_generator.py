#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUSTAINAGE Lisans Üretim Aracı (Offline)
Ed25519 asimetrik kripto kullanarak güvenli lisans anahtarları oluşturur.

Kullanım:
  python yonetim/licensing/tools/license_generator.py generate --product SUSTAINAGE --edition CORE --days 365 --hwid_core XXXX-XXXX-XXXX-XXXX [--max_users 10] [--note "Müşteri Adı"]
  python yonetim/licensing/tools/license_generator.py create_keys --output_dir ./keys
"""

import logging
import argparse
import base64
import json
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import \
        Ed25519PrivateKey
except ImportError:
    logging.info("Gerekli kütüphaneler eksik. Lütfen şu komutu çalıştırın:")
    logging.info("pip install cryptography")
    exit(1)

DEFAULT_PRIVATE_KEY_PATH = "./keys/license_private_key.pem"
DEFAULT_PUBLIC_KEY_PATH = "./keys/license_public_key.pem"

def create_key_pair(output_dir: str) -> Tuple[str, str]:
    """Ed25519 anahtar çifti oluşturur ve belirtilen dizine kaydeder."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    # Özel anahtarı PEM formatında kaydet
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Genel anahtarı PEM formatında kaydet
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    private_key_path = os.path.join(output_dir, "license_private_key.pem")
    public_key_path = os.path.join(output_dir, "license_public_key.pem")
    
    with open(private_key_path, "wb") as f:
        f.write(private_pem)
    
    with open(public_key_path, "wb") as f:
        f.write(public_pem)
    
    logging.info("Anahtar çifti oluşturuldu:")
    logging.info(f"Özel anahtar: {private_key_path}")
    logging.info(f"Genel anahtar: {public_key_path}")
    logging.info("\nÖNEMLİ: Özel anahtarı güvenli bir yerde saklayın ve asla paylaşmayın!")
    logging.info("Genel anahtarı uygulamanın içine gömün.")
    
    return private_key_path, public_key_path

def load_private_key(key_path: str) -> Ed25519PrivateKey:
    """PEM formatındaki özel anahtarı yükler."""
    with open(key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )
    return private_key

def b64url_encode(data: bytes) -> str:
    """Base64URL kodlaması yapar (padding olmadan)."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def format_license_key(payload_b64: str, signature_b64: str) -> str:
    """Lisans anahtarını okunabilir formatta biçimlendirir."""
    # Payload ve imzayı birleştir
    license_raw = f"{payload_b64}.{signature_b64}"
    return license_raw

def generate_license(
    private_key_path: str,
    product: str,
    edition: str,
    hwid_core: str,
    hwid_full: Optional[str] = None,
    days: int = 365,
    max_users: Optional[int] = None,
    note: Optional[str] = None,
    exp_date: Optional[str] = None,
    customer: Optional[str] = None,
    contract_id: Optional[str] = None,
    mode: Optional[str] = None
) -> str:
    """
    Belirtilen parametrelerle lisans anahtarı oluşturur.
    """
    # Özel anahtarı yükle
    private_key = load_private_key(private_key_path)
    
    # Son geçerlilik tarihini hesapla
    if exp_date:
        exp = int(datetime.strptime(exp_date, "%Y-%m-%d").timestamp())
    else:
        exp = int((datetime.utcnow() + timedelta(days=days)).timestamp())
    
    # Lisans içeriğini oluştur
    payload: Dict[str, Any] = {
        "product": product,
        "edition": edition,
        "issued_at": int(time.time()),
        "exp": exp,
        "hwid_core": hwid_core
    }
    
    # Opsiyonel alanları ekle
    if hwid_full:
        payload["hwid_full"] = hwid_full
    
    if max_users:
        payload["max_users"] = max_users
    
    if note:
        payload["note"] = note
    if customer:
        payload["customer"] = customer
    if contract_id:
        payload["contract"] = contract_id
    if mode:
        payload["mode"] = mode
    
    # JSON'a dönüştür ve UTF-8 olarak kodla
    payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    
    # Base64URL ile kodla
    payload_b64 = b64url_encode(payload_json)
    
    # İmzala
    signature = private_key.sign(payload_json)
    signature_b64 = b64url_encode(signature)
    
    # Lisans anahtarını oluştur
    license_key = format_license_key(payload_b64, signature_b64)
    
    return license_key

def main() -> None:
    parser = argparse.ArgumentParser(description="SUSTAINAGE Lisans Üretim Aracı")
    subparsers = parser.add_subparsers(dest="command", help="Komut")
    
    # Anahtar çifti oluşturma komutu
    create_keys_parser = subparsers.add_parser("create_keys", help="Ed25519 anahtar çifti oluştur")
    create_keys_parser.add_argument("--output_dir", default="./keys", help="Anahtarların kaydedileceği dizin")
    
    # Lisans oluşturma komutu
    generate_parser = subparsers.add_parser("generate", help="Lisans anahtarı oluştur")
    generate_parser.add_argument("--private_key", default=DEFAULT_PRIVATE_KEY_PATH, help="Özel anahtar dosya yolu")
    generate_parser.add_argument("--product", default="SUSTAINAGE", help="Ürün adı")
    generate_parser.add_argument("--edition", default="CORE", choices=["CORE", "SDG", "ENTERPRISE"], help="Ürün sürümü")
    generate_parser.add_argument("--hwid_core", required=True, help="Cihaz donanım kimliği (temel)")
    generate_parser.add_argument("--hwid_full", help="Tam donanım kimliği (opsiyonel)")
    generate_parser.add_argument("--days", type=int, default=365, help="Geçerlilik süresi (gün)")
    generate_parser.add_argument("--exp_date", help="Son geçerlilik tarihi (YYYY-MM-DD formatında)")
    generate_parser.add_argument("--max_users", type=int, help="Maksimum kullanıcı sayısı")
    generate_parser.add_argument("--note", help="Not (müşteri adı, sözleşme no vb.)")
    generate_parser.add_argument("--customer", help="Müşteri adı")
    generate_parser.add_argument("--contract_id", help="Sözleşme numarası")
    generate_parser.add_argument("--mode", choices=["test","prod"], help="Lisans modu")
    
    args = parser.parse_args()
    
    if args.command == "create_keys":
        create_key_pair(args.output_dir)
    
    elif args.command == "generate":
        license_key = generate_license(
            private_key_path=args.private_key,
            product=args.product,
            edition=args.edition,
            hwid_core=args.hwid_core,
            hwid_full=args.hwid_full,
            days=args.days,
            max_users=args.max_users,
            note=args.note,
            exp_date=args.exp_date,
            customer=args.customer,
            contract_id=args.contract_id,
            mode=args.mode
        )
        
        logging.info("\nOluşturulan Lisans Anahtarı:")
        logging.info(license_key)
        logging.info("\nBu anahtarı uygulamanın 'Lisans Anahtarı' alanına yapıştırın ve 'Kaydet' düğmesine basın.")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
