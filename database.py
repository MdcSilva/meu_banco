"""Conexão e esquema do banco de dados da aplicação."""

import os
from pathlib import Path
import sqlite3

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def _get_streamlit_secret(name: str) -> str | None:
    try:
        import streamlit as st
        return st.secrets.get(name)
    except Exception:
        return None


DATABASE_URL = os.getenv("DATABASE_URL") or _get_streamlit_secret("DATABASE_URL")


class PostgresCursor:
    """Converte os parâmetros '?' usados pelo SQLite para o psycopg."""

    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, params=None):
        return self._cursor.execute(query.replace("?", "%s"), params)

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class PostgresConnection:
    def __init__(self, connection):
        self._connection = connection

    def cursor(self):
        return PostgresCursor(self._connection.cursor())

    def commit(self):
        self._connection.commit()


def _connect():
    if DATABASE_URL:
        import psycopg
        return PostgresConnection(psycopg.connect(DATABASE_URL))

    DATA_DIR.mkdir(exist_ok=True)
    connection = sqlite3.connect(DATA_DIR / "financas.db", check_same_thread=False)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


conn = _connect()


def _create_schema():
    cursor = conn.cursor()
    if DATABASE_URL:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lancamentos (
                id BIGSERIAL PRIMARY KEY,
                data DATE NOT NULL,
                tipo TEXT NOT NULL CHECK (tipo IN ('Entrada', 'Saída')),
                categoria TEXT NOT NULL,
                forma TEXT NOT NULL,
                descricao TEXT,
                valor NUMERIC(12, 2) NOT NULL CHECK (valor >= 0)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parcelas (
                id BIGSERIAL PRIMARY KEY,
                vencimento DATE NOT NULL,
                valor NUMERIC(12, 2) NOT NULL CHECK (valor >= 0),
                status TEXT NOT NULL DEFAULT 'ABERTO' CHECK (status IN ('ABERTO', 'PAGO')),
                descricao TEXT NOT NULL,
                pago_em DATE
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lancamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                tipo TEXT NOT NULL CHECK (tipo IN ('Entrada', 'Saída')),
                categoria TEXT NOT NULL,
                forma TEXT NOT NULL,
                descricao TEXT,
                valor REAL NOT NULL CHECK (valor >= 0)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parcelas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vencimento TEXT NOT NULL,
                valor REAL NOT NULL CHECK (valor >= 0),
                status TEXT NOT NULL DEFAULT 'ABERTO' CHECK (status IN ('ABERTO', 'PAGO')),
                descricao TEXT NOT NULL,
                pago_em TEXT
            )
        """)
    conn.commit()


def carregar_tabela(nome: str) -> pd.DataFrame:
    if nome not in {"lancamentos", "parcelas"}:
        raise ValueError("Tabela não permitida")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {nome}")
    colunas = [descricao[0] for descricao in cursor.description]
    return pd.DataFrame(cursor.fetchall(), columns=colunas)


_create_schema()