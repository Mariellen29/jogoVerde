from atualizacao import *

class GreenGameApp:
    def __init__(self, root):

        #nova aba para loja
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