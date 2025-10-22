import tkinter as tk
from tkinter import ttk, messagebox
import repository
import db
import validators

# Inicializa a base de dados e garante as tabelas mínimas
db.init_db()

# ----------------------------------
# Tela de Login
# ----------------------------------
class LoginFrame(ttk.Frame):
    def __init__(self, master, on_login_ok):
        """
        Tela de login: recebe usuário e senha e chama o callback quando
        a navegação para a próxima tela deve ocorrer.
        """
        super().__init__(master, padding=12)
        self.on_login_ok = on_login_ok

        ttk.Label(self, text="ServTech - Login", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0,12))

        ttk.Label(self, text="Usuário:").grid(row=1, column=0, sticky="e")
        self.ent_user = ttk.Entry(self, width=30)
        self.ent_user.grid(row=1, column=1, sticky="we", pady=4)

        ttk.Label(self, text="Senha:").grid(row=2, column=0, sticky="e")
        self.ent_pass = ttk.Entry(self, width=30, show="*")
        self.ent_pass.grid(row=2, column=1, sticky="we", pady=4)

        # Opção de lembrar credenciais em arquivo local (protótipo)
        self.var_remember = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Lembrar login", variable=self.var_remember).grid(row=3, column=1, sticky="w", pady=(0,8))

        ttk.Button(self, text="Entrar", command=self._do_login).grid(row=4, column=0, columnspan=2, pady=6, sticky="we")

        for i in range(2):
            self.columnconfigure(i, weight=1)

    def _do_login(self):
        """
        Obtém usuário e senha informados, e decide a navegação para a
        próxima tela conforme as regras atuais do protótipo.
        """
        user = self.ent_user.get()
        pw   = self.ent_pass.get()

        # Comportamento do protótipo: segue adiante se algum campo estiver vazio
        if user.strip() == "" or pw.strip() == "":
            self.on_login_ok(user or "anon")
            return

        # Autenticação simples via repositório
        ok = repository.check_login(user, pw)
        if ok:
            if self.var_remember.get():
                repository.save_remember_me(user, pw)
            self.on_login_ok(user)
        else:
            messagebox.showerror("Login inválido", "Usuário ou senha incorretos.")

# ----------------------------------
# Tela de Ordens de Serviço
# ----------------------------------
class OrdersFrame(ttk.Frame):
    def __init__(self, master, user):
        """
        Tela principal: cadastro, remoção, busca e listagem das ordens
        de serviço. Mostra o usuário atual no cabeçalho.
        """
        super().__init__(master, padding=12)
        self.user = user

        ttk.Label(self, text=f"ServTech - Ordens de Serviço (usuário: {user})", font=("Arial", 14, "bold")).pack(anchor="w")

        # Formulário de entrada de dados
        form = ttk.Frame(self)
        form.pack(fill="x", pady=10)

        ttk.Label(form, text="Cliente:").grid(row=0, column=0, sticky="e")
        self.ent_cliente = ttk.Entry(form, width=30)
        self.ent_cliente.grid(row=0, column=1, sticky="we", padx=4, pady=2)

        ttk.Label(form, text="Descrição:").grid(row=1, column=0, sticky="e")
        self.ent_desc = ttk.Entry(form, width=50)
        self.ent_desc.grid(row=1, column=1, sticky="we", padx=4, pady=2)

        ttk.Label(form, text="Preço (R$):").grid(row=2, column=0, sticky="e")
        self.ent_preco = ttk.Entry(form, width=12)
        self.ent_preco.grid(row=2, column=1, sticky="w", padx=4, pady=2)

        ttk.Label(form, text="Status:").grid(row=3, column=0, sticky="e")
        self.cmb_status = ttk.Combobox(form, values=["Aberto","Em andamento","Concluído","Cancelado"], state="readonly")
        self.cmb_status.current(0)
        self.cmb_status.grid(row=3, column=1, sticky="w", padx=4, pady=2)

        # Ações principais
        btns = ttk.Frame(self)
        btns.pack(fill="x", pady=(6,10))
        ttk.Button(btns, text="Criar / Atualizar", command=self._save).pack(side="left")
        ttk.Button(btns, text="Remover", command=self._delete).pack(side="left", padx=6)
        ttk.Button(btns, text="Buscar", command=self._search).pack(side="left")
        ttk.Button(btns, text="Recarregar", command=self._reload).pack(side="left", padx=6)

        # Tabela para exibir registros
        self.tree = ttk.Treeview(self, columns=("id","cliente","desc","preco","status"), show="headings", height=10)
        for col, title, w in [("id","ID",60), ("cliente","Cliente",160), ("desc","Descrição",220), ("preco","Preço",90), ("status","Status",120)]:
            self.tree.heading(col, text=title)
            self.tree.column(col, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Carrega os dados ao iniciar
        self._reload()

    def _on_select(self, _evt):
        """Copia os dados da linha selecionada para o formulário."""
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        values = item["values"]
        self.ent_cliente.delete(0, tk.END); self.ent_cliente.insert(0, values[1])
        self.ent_desc.delete(0, tk.END); self.ent_desc.insert(0, values[2])
        self.ent_preco.delete(0, tk.END); self.ent_preco.insert(0, values[3])
        self.cmb_status.set(values[4])

    def _save(self):
        """Lê campos do formulário e solicita a gravação ao repositório."""
        cliente = self.ent_cliente.get()
        desc    = self.ent_desc.get()
        preco   = self.ent_preco.get()
        status  = self.cmb_status.get()

        # Exemplo de uso de validações do módulo validators
        if not validators.is_valid_cliente(cliente):
            messagebox.showwarning("Validação", "Verifique o campo Cliente.")
            return

        repository.upsert_order(cliente, desc, preco, status)
        self._reload()

    def _delete(self):
        """Remove o registro selecionado na tabela, se houver seleção."""
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        order_id = item["values"][0]
        repository.delete_order(order_id)
        self._reload()

    def _search(self):
        """Busca registros pelo conteúdo do campo 'Cliente' e exibe na tabela."""
        termo = self.ent_cliente.get()
        rows = repository.search_orders(termo)
        self._fill(rows)

    def _reload(self):
        """Recarrega todos os registros e popula a tabela."""
        rows = repository.list_orders()
        self._fill(rows)

    def _fill(self, rows):
        """Limpa a tabela e insere as linhas informadas."""
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", values=r)

# ----------------------------------
# Aplicação principal
# ----------------------------------
class App(tk.Tk):
    def __init__(self):
        """Janela raiz: controla a exibição das telas do sistema."""
        super().__init__()
        self.title("ServTech Soluções - Protótipo")
        self.geometry("800x520")

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self._show_login()

    def _show_login(self):
        """Exibe a tela de login no container principal."""
        for w in self.container.winfo_children():
            w.destroy()
        LoginFrame(self.container, on_login_ok=self._on_login_ok).pack(fill="both", expand=True)

    def _on_login_ok(self, user):
        """Exibe a tela de ordens quando o login é concluído."""
        for w in self.container.winfo_children():
            w.destroy()
        OrdersFrame(self.container, user=user).pack(fill="both", expand=True)

if __name__ == "__main__":
    App().mainloop()
