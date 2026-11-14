import os
import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager

from validators import validar_pessoa


# Configuração local (usada quando DATABASE_URL não está definida)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "app_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD","")
}


@contextmanager
def get_connection():
    """
    Gerencia conexão e fecha automaticamente.
    Prioriza DATABASE_URL (Render) e cai para DB_CONFIG (local).
    """
    db_url = os.getenv("DATABASE_URL")

    if db_url:
        # Render fornece formato postgres://; psycopg3 prefere postgresql://
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        conn = psycopg.connect(db_url)
    else:
        conn = psycopg.connect(**DB_CONFIG)

    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Cria a tabela se não existir. Seguro para rodar múltiplas vezes."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pessoas (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(150) NOT NULL,
                    cidade VARCHAR(100) NOT NULL,
                    estado CHAR(2) NOT NULL
                        CHECK (estado IN (
                            'AC','AL','AP','AM','BA','CE','DF','ES','GO',
                            'MA','MT','MS','MG','PA','PB','PR','PE','PI',
                            'RJ','RN','RS','RO','RR','SC','SP','SE','TO'
                        )),
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()


def listar_pessoas():
    """Retorna todas as pessoas ordenadas por nome."""
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT id, nome, cidade, estado, criado_em
                FROM pessoas
                ORDER BY nome ASC;
            """)
            return cur.fetchall()


def buscar_pessoa(pessoa_id):
    """Retorna uma pessoa pelo ID (ou None)."""
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT id, nome, cidade, estado, criado_em
                FROM pessoas
                WHERE id = %s;
            """, (pessoa_id,))
            return cur.fetchone()


def criar_pessoa(nome, cidade, estado):
    """Insere uma nova pessoa. Retorna o ID gerado."""
    dados = validar_pessoa(nome, cidade, estado)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO pessoas (nome, cidade, estado)
                VALUES (%s, %s, %s)
                RETURNING id;
            """, (dados["nome"], dados["cidade"], dados["estado"]))
            novo_id = cur.fetchone()[0]
            conn.commit()
            return novo_id


def atualizar_pessoa(pessoa_id, nome, cidade, estado):
    """Atualiza uma pessoa existente."""
    dados = validar_pessoa(nome, cidade, estado)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE pessoas
                SET nome = %s, cidade = %s, estado = %s
                WHERE id = %s;
            """, (dados["nome"], dados["cidade"], dados["estado"], pessoa_id))
            conn.commit()
            return cur.rowcount > 0


def deletar_pessoa(pessoa_id):
    """Remove uma pessoa."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pessoas WHERE id = %s;", (pessoa_id,))
            conn.commit()
            return cur.rowcount > 0