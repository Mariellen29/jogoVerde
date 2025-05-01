from green_game import *


class GreenGameApp:

    def __init__(self, root):
        self.root = root
        self.root.title("GreenGame Pro")
        self.root.geometry("900x600")
        self.label_pontos = ttk.Label()
        self.canvas = tk.Canvas()
        self.scrollable_frame = ttk.Frame()
        self.frame_usuarios = ttk.Frame()

        style = ttk.Style()
        style.theme_use('clam')

        # Frames principais
        frame_esquerda = ttk.Frame(root)
        frame_esquerda.pack(side="left", fill="y", expand=True, padx=10, pady=10)

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

        btn_export_csv = ttk.Button(
            frame_export,
            text="Exportar para CSV",
            command=exportar_csv)
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
            "Usou transporte público (+20 pts)": ("Uso de transporte público", 20),
            "Economizou 100L de água (+15 pts)": ("Economia de água", 15),
            "Plantou uma árvore (+50 pts)": ("Plantio de árvore", 50),
            "Usou energia solar (+40 pts)": ("Uso de energia solar", 40)
        }

        acao, pontos = mapa_acoes[acao_selecionada]

        registrar_acao(usuario_id, acao, pontos)
        messagebox.showinfo("Sucesso", f"Ação registrada: +{pontos} pontos para {usuario_selecionado}!")
        self.atualizar_interface()


# --- INICIALIZAÇÃO ---
if __name__ == "__main__":
    criar_tabelas()
    root = tk.Tk()
    app = GreenGameApp(root)
    root.mainloop()






