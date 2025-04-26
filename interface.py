import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from tkinter.ttk import Button
from green_game import *
import csv
from atualizacao import *

class GreenGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GreenGame Pro")
        self.root.geometry("900x600")

        style = ttk.Style()
        style.theme_use('clam')

        # Frames principais
        frame_esquerda = ttk.Frame(root)
        frame_esquerda.pack(side="left", fill="y", padx=10, pady=10)

        frame_direita = ttk.Frame(root)
        frame_direita.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # --- Frame Esquerda (Controles) ---
        # Cadastro de Usuário
        frame_cadastro = ttk.LabelFrame(frame_esquerda, text="Cadastrar Usuário", padding=10)
        frame_cadastro.pack(fill="x", pady=5)

        self.entry_nome = ttk.Entry(frame_cadastro)
        self.entry_nome.pack(fill="x", pady=5)

        btn_cadastrar = ttk.Button(
            frame_cadastro,
            text="Cadastrar",
            command=self.cadastrar_usuario)
        btn_cadastrar.pack(fill="x")

        # Edição de Usuário
        frame_edicao = ttk.LabelFrame(frame_esquerda, text="Editar Usuário", padding=10)
        frame_edicao.pack(fill="x", pady=5)

        self.combo_usuarios_edicao = ttk.Combobox(frame_edicao, state="readonly")
        self.combo_usuarios_edicao.pack(fill="x", pady=5)

        self.entry_novo_nome = ttk.Entry(frame_edicao)
        self.entry_novo_nome.pack(fill="x", pady=5)

        btn_editar = ttk.Button(
            frame_edicao,
            text="Editar Nome",
            command=self.editar_usuario)
        btn_editar.pack(side="left", fill="x", expand=True, padx=2)

        btn_remover = ttk.Button(
            frame_edicao,
            text="Remover",
            command=self.remover_usuario)
        btn_remover.pack(side="right", fill="x", expand=True, padx=2)

        # Registro de Ações
        frame_acoes = ttk.LabelFrame(frame_esquerda, text="Registrar Ação", padding=10)
        frame_acoes.pack(fill="x", pady=5)

        self.combo_usuarios_acao = ttk.Combobox(frame_acoes, state="readonly")
        self.combo_usuarios_acao.pack(fill="x", pady=5)

        self.combo_tipo_acao = ttk.Combobox(
            frame_acoes,
            values=[
                "Reciclou 1kg de plástico (+30 pts)",
                "Reciclou 1 kg de Latinha (+50 pts)",
                "Descartou elêtronicos corretamente (+50 pts)",
                "Descartou remédio vencido na farmácia (+30pts)",
                "Descartou embalagens e bulas na Farmacia (+30pts)",
                "Andou de bicicleta (+40 pts)",
                "Usou transporte público (+20 pts)",
                "Economizou 100L de água (+15 pts)",
                "Plantou uma árvore (+50 pts)",
                "Usou energia solar (+40 pts)"
            ],
            state="readonly")
        self.combo_tipo_acao.pack(fill="x", pady=5)

        btn_registrar_acao = ttk.Button(
            frame_acoes,
            text="Registrar Ação",
            command=self.registrar_acao)
        btn_registrar_acao.pack(fill="x")

        # Exportação de Dados
        frame_export = ttk.LabelFrame(frame_esquerda, text="Exportar Dados", padding=10)
        frame_export.pack(fill="x", pady=5)

        btn_export_csv: Button = ttk.Button(
            frame_export,
            text="Exportar para CSV",
            command=self.exportar_csv)
        btn_export_csv.pack(fill="x", pady=5)

        # --- Frame Direita (Visualização) ---
        self.notebook = ttk.Notebook(frame_direita)
        self.notebook.pack(fill="both", expand=True)

        # Aba: Usuários
        self.frame_usuarios = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_usuarios, text="Usuários")

        self.tree_usuarios = ttk.Treeview(
            self.frame_usuarios,
            columns=("id", "nome", "pontos", "cadastro"),
            show="headings")

        self.tree_usuarios.heading("id", text="ID")
        self.tree_usuarios.heading("nome", text="Nome")
        self.tree_usuarios.heading("pontos", text="Pontos")
        self.tree_usuarios.heading("cadastro", text="Data Cadastro")

        self.tree_usuarios.column("id", width=50)
        self.tree_usuarios.column("nome", width=150)
        self.tree_usuarios.column("pontos", width=80)
        self.tree_usuarios.column("cadastro", width=120)

        self.scroll_usuarios = ttk.Scrollbar(
            self.frame_usuarios,
            orient="vertical",
            command=self.tree_usuarios.yview)

        self.tree_usuarios.configure(yscrollcommand=self.scroll_usuarios.set)
        self.tree_usuarios.pack(side="left", fill="both", expand=True)
        self.scroll_usuarios.pack(side="right", fill="y")

        # Aba: Histórico
        self.frame_historico = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_historico, text="Histórico Completo")

        self.tree_historico = ttk.Treeview(
            self.frame_historico,
            columns=("data", "usuario", "acao", "pontos"),
            show="headings")

        self.tree_historico.heading("data", text="Data")
        self.tree_historico.heading("usuario", text="Usuário")
        self.tree_historico.heading("acao", text="Ação")
        self.tree_historico.heading("pontos", text="Pontos")

        self.tree_historico.column("data", width=120)
        self.tree_historico.column("usuario", width=100)
        self.tree_historico.column("acao", width=200)
        self.tree_historico.column("pontos", width=80)

        self.scroll_historico = ttk.Scrollbar(
            self.frame_historico,
            orient="vertical",
            command=self.tree_historico.yview)

        self.tree_historico.configure(yscrollcommand=self.scroll_historico.set)
        self.tree_historico.pack(side="left", fill="both", expand=True)
        self.scroll_historico.pack(side="right", fill="y")

        self.atualizar_interface()

    # --- MÉTODOS DA INTERFACE ---
    def atualizar_interface(self):
        self.atualizar_lista_usuarios()
        self.atualizar_historico()

    def atualizar_lista_usuarios(self):
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, pontos, data_cadastro FROM usuarios ORDER BY pontos DESC')
        usuarios = cursor.fetchall()
        conn.close()

        for usuario in usuarios:
            self.tree_usuarios.insert("", "end", values=usuario)

        lista_combobox = [f"{u[1]} (ID: {u[0]})" for u in usuarios]
        self.combo_usuarios_edicao["values"] = lista_combobox
        self.combo_usuarios_acao["values"] = lista_combobox

        if lista_combobox:
            self.combo_usuarios_edicao.current(0)
            self.combo_usuarios_acao.current(0)

    def atualizar_historico(self, usuario_id=None):
        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)

        historico = get_historico_acoes(usuario_id)

        for acao in historico:
            self.tree_historico.insert("", "end", values=acao)

    def cadastrar_usuario(self):
        nome = self.entry_nome.get()
        try:
            cadastrar_usuario(nome)
            messagebox.showinfo("Sucesso", f"Usuário '{nome}' cadastrado!")
            self.entry_nome.delete(0, "end")
            self.atualizar_interface()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def editar_usuario(self):
        selecao = self.combo_usuarios_edicao.get()
        novo_nome = self.entry_novo_nome.get()

        if not selecao or not novo_nome:
            messagebox.showerror("Erro", "Selecione um usuário e digite um novo nome!")
            return

        usuario_id = int(selecao.split("ID: ")[1].rstrip(")"))

        try:
            editar_usuario(usuario_id, novo_nome)
            messagebox.showinfo("Sucesso", "Nome atualizado!")
            self.entry_novo_nome.delete(0, "end")
            self.atualizar_interface()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def remover_usuario(self):
        selecao = self.combo_usuarios_edicao.get()
        if not selecao:
            messagebox.showerror("Erro", "Selecione um usuário!")
            return

        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja remover este usuário e todas suas ações?"):
            return

        usuario_id = int(selecao.split("ID: ")[1].rstrip(")"))
        remover_usuario(usuario_id)
        messagebox.showinfo("Sucesso", "Usuário removido!")
        self.atualizar_interface()

    def registrar_acao(self):
        usuario_selecionado = self.combo_usuarios_acao.get()
        acao_selecionada = self.combo_tipo_acao.get()

        if not usuario_selecionado or not acao_selecionada:
            messagebox.showerror("Erro", "Selecione um usuário e uma ação!")
            return

        usuario_id = int(usuario_selecionado.split("ID: ")[1].rstrip(")"))

        mapa_acoes = {
            "Reciclou 1kg de plástico (+30 pts)": ("Reciclagem de plástico", 30),
            "Reciclou 1kg de Latinha (+40 pts)": ("Reciclagem de Latinha", 40),
            "Descartou elêtronicos corretamente (+50 pts)": ("descarte de eletronicos", 50),
            "Descartou remédio vencido na farmácia (+30pts)": ("Descarte de Remédios vencido", 30),
            "Descartou embalagens e bulas na Farmacia (+30pts)": ("Descarte de embalagens e bulas na Farmacia", 30),
            "Andou de bicicleta (+40 pts)": ("Uso de bicicleta", 40),
            "Usou transporte público (+20 pts)": ("Uso de transporte público", 20),
            "Economizou 100L de água (+15 pts)": ("Economia de água", 15),
            "Plantou uma árvore (+50 pts)": ("Plantio de árvore", 50),
            "Usou energia solar (+40 pts)": ("Uso de energia solar", 40)
        }

        acao, pontos = mapa_acoes[acao_selecionada]

        registrar_acao(usuario_id, acao, pontos)
        messagebox.showinfo("Sucesso", f"Ação registrada: +{pontos} pontos para {usuario_selecionado}!")
        self.atualizar_interface()

    @staticmethod
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


# --- INICIALIZAÇÃO ---
if __name__ == "__main__":
    criar_tabelas()
    root = tk.Tk()
    app = GreenGameApp(root)
    root.mainloop()

    from atualizacao import *


    class GreenGameApp:
        def __init__(self, root):

            # nova aba para loja
            self.root = root
            self.frame_loja = ttk.Frame(self.notebook)
            self.notebook.add(self.frame_loja, text="Loja de Recompensas")

            self.criar_aba_loja()

        def criar_aba_loja(self):
            # Frame superior (pontos do usuário)
            frame_pontos = ttk.Frame(self.frame_loja)
            frame_pontos.pack(fill="x", pady=5)

            self.label_pontos = ttk.Label(frame_pontos, text="Seus pontos: 0", font=('Arial', 12, 'bold'))
            self.label_pontos.pack(side="left")

            # Frame das recompensas
            frame_recompensas = ttk.Frame(self.frame_loja)
            frame_recompensas.pack(fill="both", expand=True)

            self.canvas = tk.Canvas(frame_recompensas)
            scrollbar = ttk.Scrollbar(frame_recompensas, orient="vertical", command=self.canvas.yview)
            self.scrollable_frame = ttk.Frame(self.canvas)

            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(
                    scrollregion=self.canvas.bbox("all")
                )
            )

            self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            self.canvas.configure(yscrollcommand=scrollbar.set)

            self.canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            self.carregar_recompensas()

        def carregar_recompensas(self):
            # Limpa recompensas anteriores
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

            # Busca recompensas do banco
            recompensas = get_recompensas_disponiveis()

            for rec in recompensas:
                id_rec, nome, descricao, custo, estoque = rec

                frame = ttk.Frame(self.scrollable_frame, padding=10, relief="groove", borderwidth=1)
                frame.pack(fill="x", pady=5, padx=5)

                ttk.Label(frame, text=nome, font=('Arial', 12, 'bold')).pack(anchor="w")
                ttk.Label(frame, text=descricao).pack(anchor="w")

                info = ttk.Frame(frame)
                info.pack(fill="x")

                ttk.Label(info, text=f"🪙 {custo} pontos", foreground="green").pack(side="left")
                ttk.Label(info, text=f"📦 Estoque: {estoque}", foreground="blue").pack(side="right")

                btn_resgatar = ttk.Button(
                    frame,
                    text="Resgatar",
                    command=lambda id=id_rec: self.resgatar_recompensa(id)
                )
                btn_resgatar.pack(anchor="e")

        def atualizar_pontos_loja(self):
            usuario_selecionado = self.combo_usuarios_acao.get()
            if usuario_selecionado:
                usuario_id = int(usuario_selecionado.split("ID: ")[1].rstrip(")"))
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute('SELECT pontos FROM usuarios WHERE id = ?', (usuario_id,))
                pontos = cursor.fetchone()[0]
                self.label_pontos.config(text=f"Seus pontos: {pontos} 🪙")
                conn.close()

        def resgatar_recompensa(self, recompensa_id):
            usuario_selecionado = self.combo_usuarios_acao.get()
            if not usuario_selecionado:
                messagebox.showerror("Erro", "Selecione um usuário primeiro!")
                return

            usuario_id = int(usuario_selecionado.split("ID: ")[1].rstrip(")"))

            try:
                if resgatar_recompensa(usuario_id, recompensa_id):
                    messagebox.showinfo("Sucesso", "Recompensa resgatada com sucesso!")
                    self.atualizar_interface()
                    self.carregar_recompensas()
                    self.atualizar_pontos_loja()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        # Atualize o método atualizar_interface
        def atualizar_interface(self):
            self.atualizar_lista_usuarios()
            self.atualizar_historico()
            self.atualizar_pontos_loja()  # Nova linha adicionada