# 001_initial_core.py
# Temel tabloların oluşturulması (init_database.py'den taşındı)

def up(conn):
    cursor = conn.cursor()
    
    # --- Stratejik Yönetim ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            vision TEXT,
            mission TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS smart_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy_id INTEGER,
            goal TEXT NOT NULL,
            specific TEXT,
            measurable TEXT,
            achievable TEXT,
            relevant TEXT,
            time_bound TEXT,
            target_date DATE,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (strategy_id) REFERENCES strategies(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            risk_name TEXT NOT NULL,
            category TEXT,
            likelihood INTEGER,
            impact INTEGER,
            score INTEGER,
            mitigation TEXT,
            owner TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_name TEXT NOT NULL,
            category TEXT,
            score INTEGER,
            action_plan TEXT,
            owner TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ceo_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            message_type TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stakeholders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            contact TEXT,
            engagement_level TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- Kullanıcı Yönetimi ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            email TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_token TEXT,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT UNIQUE NOT NULL,
            permissions TEXT
        )
    """)
    
    # --- Companies (main.py'de referans verilen) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            industry TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
