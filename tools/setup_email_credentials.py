import logging
import os
import json
import argparse
from cryptography.fernet import Fernet

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--email', default=os.getenv('SMTP_SENDER_EMAIL') or os.getenv('SENDER_EMAIL') or 'admin@digage.tr')
    p.add_argument('--password', default=os.getenv('SMTP_PASSWORD') or os.getenv('SENDER_PASSWORD') or '')
    p.add_argument('--out', default=os.path.join(os.getcwd(), 'config', 'email_credentials.json'))
    args = p.parse_args()

    if not args.password:
        logging.error('[HATA] Parola girilmedi. --password veya SMTP_PASSWORD kullanin')
        return 1

    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(args.password.encode('utf-8')).decode('utf-8')

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as fp:
        json.dump({
            'sender_email': args.email,
            'password_enc': token,
        }, fp, ensure_ascii=False, indent=2)

    logging.info('[OK] email_credentials.json yazildi:', args.out)
    logging.info('SENDER_PASSWORD_KEY=', key.decode('utf-8'))
    logging.info('SENDER_EMAIL=', args.email)
    logging.info('Bilgi: Ortamda SENDER_PASSWORD degiskeni gerekmiyor; sifre enc dosyadan cozulur')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

