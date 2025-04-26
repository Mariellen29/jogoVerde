from green_game import *
from interface import *

# --- ATUALIZAÇÃO O BANCO DE DADOS ---
def criar_tabelas():
    conn = conectar_db()
    cursor = conn.cursor()

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

    # Popule algumas recompensas iniciais
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


