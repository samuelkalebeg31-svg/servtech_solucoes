import sqlite3
import os

DB_FILE = "servtech.db"

def get_conn():
    """
    Abre e retorna uma conexão com o banco SQLite.
    O arquivo é criado no diretório atual, se ainda não existir.
    """
    return sqlite3.connect(DB_FILE)

def init_db():
    """
    Cria as tabelas básicas (users e orders), caso ainda não existam,
    e insere um usuário inicial para autenticação.
    """
    conn = get_conn()
    cur = conn.cursor()

    # Cadastro de usuários
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    # Cadastro de ordens de serviço
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT,
        descricao TEXT,
        preco TEXT,
        status TEXT
    )
    """)

    # Insere um usuário padrão na inicialização (admin/admin123)
    cur.execute("INSERT INTO users (username, password) VALUES ('admin','admin123')")

    conn.commit()
    conn.close()
