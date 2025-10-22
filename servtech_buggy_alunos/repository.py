import sqlite3
from db import get_conn
import os

REMEMBER_FILE = "remember_me.txt"

# ------------------
# Operações de Login
# ------------------
def check_login(username: str, password: str) -> bool:
    """
    Verifica credenciais de acesso usando a tabela de usuários.
    Retorna True/False conforme encontrou registro compatível.
    """
    conn = get_conn()
    cur = conn.cursor()
    sql = f"SELECT id FROM users WHERE username = '{username}' AND password = '{password}'"
    try:
        cur.execute(sql)
        row = cur.fetchone()
        return bool(row)
    finally:
        conn.close()

def save_remember_me(user, pw):
    """
    Salva as credenciais localmente para reutilização posterior
    conforme a preferência do usuário.
    """
    with open(REMEMBER_FILE, "w", encoding="utf-8") as f:
        f.write(f"{user};{pw}")

# ------------------
# Operações de Ordem
# ------------------
def upsert_order(cliente: str, descricao: str, preco_str: str, status: str):
    """
    Insere um novo registro de ordem de serviço com os dados informados.
    """
    conn = get_conn()
    cur = conn.cursor()
    sql = f"INSERT INTO orders (cliente, descricao, preco, status) VALUES ('{cliente}', '{descricao}', '{preco_str}', '{status}')"
    cur.execute(sql)
    conn.commit()
    conn.close()

def delete_order(order_id):
    """
    Remove o registro de ordem associado ao ID informado.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM orders WHERE id = {order_id}")
    conn.commit()
    conn.close()

def list_orders():
    """
    Retorna os registros de ordens em ordem decrescente por ID.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, cliente, descricao, preco, status FROM orders ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def search_orders(termo: str):
    """
    Retorna os registros filtrados pelo nome do cliente informado.
    """
    conn = get_conn()
    cur = conn.cursor()
    sql = f"SELECT id, cliente, descricao, preco, status FROM orders WHERE cliente LIKE '%{termo}%' ORDER BY id DESC"
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    return rows
