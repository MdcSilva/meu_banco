import sqlite3

conn = sqlite3.connect("banco.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS lancamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT,
        tipo TEXT,
        categoria TEXT,
        forma TEXT,
        descricao TEXT,
        valor REAL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS parcelas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT,
        valor REAL,
        vencimento TEXT,
        status TEXT DEFAULT 'ABERTO',
        pago_em TEXT
    )
""")

conn.commit()