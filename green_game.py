import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv


# --- BANCO DE DADOS ---
def conectar_db():
    return sqlite3.connect('green_game.db')


def criar_tabelas():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS usuarios
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       nome
                       TEXT
                       UNIQUE,
                       pontos
                       INTEGER
                       DEFAULT
                       0,
                       data_cadastro
                       TEXT
                   )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS acoes
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       usuario_id
                       INTEGER,
                       acao
                       TEXT,
                       pontos
                       INTEGER,
                       data
                       TEXT,
                       FOREIGN
                       KEY
                   (
                       usuario_id
                   ) REFERENCES usuarios
                   (
                       id
                   )
                       )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS recompensas
                   (
                       id
                           INTEGER
                           PRIMARY
                               KEY
                           AUTOINCREMENT,
                       nome
                           TEXT,
                       descricao
                           TEXT,
                       custo_pontos
                           INTEGER,
                       estoque
                           INTEGER
                           DEFAULT
                               10
                   )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS resgates
                   (
                       id
                           INTEGER
                           PRIMARY
                               KEY
                           AUTOINCREMENT,
                       usuario_id
                           INTEGER,
                       recompensa_id
                           INTEGER,
                       data
                           TEXT,
                       FOREIGN
                           KEY
                           (
                            usuario_id
                               ) REFERENCES usuarios
                           (
                            id
                               ),
                       FOREIGN KEY
                           (
                            recompensa_id
                               ) REFERENCES recompensas
                           (
                            id
                               )
                   )
                   ''')
    cursor.execute('SELECT COUNT(*) FROM recompensas')

    if cursor.fetchone()[0] == 0:
        recompensas_iniciais = [
            ("Cupom 10% EcoStore", "Desconto em loja sustentável", 100, 5),
            ("Livro Sustentabilidade", "E-book grátis", 200, 3),
            ("Caneca Ecológica", "Caneca de bambu personalizada", 300, 2),
            ("Plantio de Árvore", "Uma árvore plantada em seu nome", 500, 10)
        ]
        cursor.executemany(
            'INSERT INTO recompensas (nome, descricao, custo_pontos, estoque) VALUES (?, ?, ?, ?)',
            recompensas_iniciais
        )

    conn.commit()
    conn.close()


# --- FUNÇÕES PRINCIPAIS ---
def cadastrar_usuario(nome):
    """Cadastra novo usuário com validação"""
    if not nome or len(nome.strip()) < 3:
        raise ValueError("Nome deve ter pelo menos 3 caracteres")

    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO usuarios (nome, data_cadastro) VALUES (?, ?)',
            (nome.strip(), datetime.now().strftime("%d/%m/%Y %H:%M"))
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError("Usuário já existe!")
    finally:
        conn.close()


def editar_usuario(usuario_id, novo_nome):
    """Edita nome do usuário"""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE usuarios SET nome = ? WHERE id = ?',
            (novo_nome.strip(), usuario_id))
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Nome já está em uso!")
    finally:
        conn.close()


def remover_usuario(usuario_id):
    """Remove usuário e suas ações"""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM acoes WHERE usuario_id = ?', (usuario_id,))
    cursor.execute('DELETE FROM usuarios WHERE id = ?', (usuario_id,))
    conn.commit()
    conn.close()


def registrar_acao(usuario_id, acao, pontos):
    """Registra ação e atualiza pontos"""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO acoes (usuario_id, acao, pontos, data) VALUES (?, ?, ?, ?)',
        (usuario_id, acao, pontos, datetime.now().strftime("%d/%m/%Y %H:%M")))
    cursor.execute(
        'UPDATE usuarios SET pontos = pontos + ? WHERE id = ?',
        (pontos, usuario_id))
    conn.commit()
    conn.close()


def get_historico_acoes(usuario_id=None):
    """Retorna histórico de ações (filtrado ou geral)"""
    conn = conectar_db()
    cursor = conn.cursor()

    if usuario_id:
        cursor.execute('''
                       SELECT a.data, u.nome, a.acao, a.pontos
                       FROM acoes a
                                JOIN usuarios u ON a.usuario_id = u.id
                       WHERE a.usuario_id = ?
                       ORDER BY a.data DESC
                       ''', (usuario_id,))
    else:
        cursor.execute('''
                       SELECT a.data, u.nome, a.acao, a.pontos
                       FROM acoes a
                                JOIN usuarios u ON a.usuario_id = u.id
                       ORDER BY a.data DESC
                       ''')

    historico = cursor.fetchall()
    conn.close()
    return historico
# --- NOVAS FUNÇÕES ---
def get_recompensas_disponiveis():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT id, nome, descricao, custo_pontos, estoque
                   FROM recompensas
                   WHERE estoque > 0
                   ''')
    recompensas = cursor.fetchall()
    conn.close()
    return recompensas


def resgatar_recompensa(usuario_id, recompensa_id):
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        # Verifica pontos e estoque
        cursor.execute('SELECT pontos FROM usuarios WHERE id = ?', (usuario_id,))
        pontos_usuario = cursor.fetchone()[0]

        cursor.execute('SELECT custo_pontos, estoque FROM recompensas WHERE id = ?', (recompensa_id,))
        custo, estoque = cursor.fetchone()

        if pontos_usuario < custo:
            raise ValueError("Pontos insuficientes!")

        if estoque <= 0:
            raise ValueError("Recompensa esgotada!")

        # Atualiza estoque e pontos
        cursor.execute('UPDATE recompensas SET estoque = estoque - 1 WHERE id = ?', (recompensa_id,))
        cursor.execute('UPDATE usuarios SET pontos = pontos - ? WHERE id = ?', (custo, usuario_id))

        # Registra o resgate
        cursor.execute('''
                       INSERT INTO resgates (usuario_id, recompensa_id, data)
                       VALUES (?, ?, ?)
                       ''', (usuario_id, recompensa_id, datetime.now().strftime("%d/%m/%Y %H:%M")))

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()



# --- INTERFACE GRÁFICA ---
def exportar_csv():
    filepath = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("Arquivos CSV", "*.csv")],
        title="Salvar como")

    if not filepath:
        return

    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Data", "Usuário", "Ação", "Pontos"])

            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT a.data, u.nome, a.acao, a.pontos
                           FROM acoes a
                                    JOIN usuarios u ON a.usuario_id = u.id
                           ORDER BY a.data DESC
                           ''')

            for row in cursor.fetchall():
                writer.writerow(row)

            conn.close()

        messagebox.showinfo("Sucesso", f"Dados exportados para:\n{filepath}")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao exportar:\n{str(e)}")

