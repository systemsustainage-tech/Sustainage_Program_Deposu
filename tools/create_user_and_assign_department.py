#!/usr/bin/env python3
import logging
import uuid

from yonetim.kullanici_yonetimi.models.user_manager import UserManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main() -> None:
    um = UserManager()
    suffix = uuid.uuid4().hex[:6]
    username = f"dept_test_{suffix}"
    email = f"{username}@example.com"

    user_data = {
        'username': username,
        'email': email,
        'password': 'Dept123!test',
        'first_name': 'Departman',
        'last_name': 'Test',
        'phone': '5550001111',
        'department': 'Çevre',
        'position': 'Uzman',
        'is_active': True,
        'is_verified': True,
        'default_role': 'user'
    }
    user_id = um.create_user(user_data, created_by=None)
    logging.info('Created user id:', user_id)

    if user_id and user_id > 0:
        u = um.get_user_by_id(user_id)
        logging.info('User record:', {k: u.get(k) for k in ['id','username','department','roles']})
    else:
        logging.error('User creation failed')

if __name__ == '__main__':
    main()
