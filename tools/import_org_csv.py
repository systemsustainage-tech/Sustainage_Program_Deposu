#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Org CSV → SQLite Importer
- companies, users, departments, sections import eder

Kullanım örneği:
  python tools/import_org_csv.py --db data/sdg_desktop.sqlite \
    --companies data/imports/templates/org/companies.csv \
    --users data/imports/templates/org/users.csv \
    --departments data/imports/templates/org/departments.csv \
    --sections data/imports/templates/org/sections.csv
"""
import logging
import argparse
import csv
import sqlite3

#  GÜVENLİK: Argon2 kullanılıyor
from yonetim.security.core.crypto import hash_password

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def upsert_company(cur, row) -> None:
    cur.execute(
        """
        INSERT OR IGNORE INTO companies(name, sector, country)
        VALUES(?,?,?)
        """,
        (row.get('name'), row.get('sector'), row.get('country'))
    )

def upsert_user(cur, row) -> None:
    username = row['username']
    display_name = row.get('display_name')
    email = row.get('email')
    role = row.get('role') or 'user'
    is_active = int(row.get('is_active') or 1)
    pwd_plain = row.get('password_plain') or ''
    pwd_hash = hash_password(pwd_plain)  #  Argon2
    # Try update if exists
    cur.execute("SELECT id FROM users WHERE username=? OR email=?", (username, email))
    r = cur.fetchone()
    if r:
        cur.execute(
            """
            UPDATE users SET display_name=?, email=?, password_hash=?, role=?, is_active=?
            WHERE id=?
            """,
            (display_name, email, pwd_hash, role, is_active, r[0])
        )
    else:
        cur.execute(
            """
            INSERT INTO users(username, display_name, email, password_hash, role, is_active)
            VALUES(?,?,?,?,?,?)
            """,
            (username, display_name, email, pwd_hash, role, is_active)
        )

def get_company_id(cur, company_name) -> None:
    cur.execute("SELECT id FROM companies WHERE name=?", (company_name,))
    r = cur.fetchone()
    return r[0] if r else None

def get_department_id(cur, company_id, name) -> None:
    cur.execute("SELECT id FROM departments WHERE company_id=? AND name=?", (company_id, name))
    r = cur.fetchone()
    return r[0] if r else None

def upsert_department(cur, row) -> None:
    company_name = row['company_name']
    name = row['department_name']
    parent_name = row.get('parent_department_name')
    company_id = get_company_id(cur, company_name)
    if not company_id:
        # create company on the fly
        cur.execute("INSERT INTO companies(name) VALUES(?)", (company_name,))
        company_id = get_company_id(cur, company_name)
    parent_id = None
    if parent_name:
        parent_id = get_department_id(cur, company_id, parent_name)
        if not parent_id:
            cur.execute("INSERT INTO departments(company_id, name) VALUES(?,?)", (company_id, parent_name))
            parent_id = get_department_id(cur, company_id, parent_name)
    # upsert 
    dep_id = get_department_id(cur, company_id, name)
    if dep_id:
        cur.execute("UPDATE departments SET parent_department_id=? WHERE id=?", (parent_id, dep_id))
    else:
        cur.execute(
            "INSERT INTO departments(company_id, name, parent_department_id) VALUES(?,?,?)",
            (company_id, name, parent_id)
        )

def upsert_section(cur, row) -> None:
    company_name = row['company_name']
    department_name = row['department_name']
    name = row['section_name']
    company_id = get_company_id(cur, company_name)
    if not company_id:
        cur.execute("INSERT INTO companies(name) VALUES(?)", (company_name,))
        company_id = get_company_id(cur, company_name)
    dep_id = get_department_id(cur, company_id, department_name)
    if not dep_id:
        cur.execute("INSERT INTO departments(company_id, name) VALUES(?,?)", (company_id, department_name))
        dep_id = get_department_id(cur, company_id, department_name)
    cur.execute(
        """
        INSERT OR IGNORE INTO sections(company_id, department_id, name)
        VALUES(?,?,?)
        """,
        (company_id, dep_id, name)
    )

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--companies")
    ap.add_argument("--users")
    ap.add_argument("--departments")
    ap.add_argument("--sections")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()

    if args.companies:
        with open(args.companies, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                upsert_company(cur, row)
        logging.info("companies import tamamlandı:", args.companies)

    if args.users:
        with open(args.users, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                upsert_user(cur, row)
        logging.info("users import tamamlandı:", args.users)

    if args.departments:
        with open(args.departments, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                upsert_department(cur, row)
        logging.info("departments import tamamlandı:", args.departments)

    if args.sections:
        with open(args.sections, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                upsert_section(cur, row)
        logging.info("sections import tamamlandı:", args.sections)

    conn.commit()
    conn.close()
    logging.info("Org import tamamlandı")

if __name__ == "__main__":
    main()
