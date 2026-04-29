import customtkinter as ctk
import subprocess
import os
import sys
import threading
from tkinter import messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt

# Configuração visual profissional
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class QHelpApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Q-Help - Executive Analytics Control")
        self.width_win = 700
        self.height_win = 700 
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.width_win // 2)
        y = (screen_height // 2) - (self.height_win // 2)
        
        self.geometry(f"{self.width_win}x{self.height_win}+{x}+{y}")
        self.minsize(700, 700)

        # Título
        self.label = ctk.CTkLabel(self, text="Q-Help Management Console", font=("Roboto", 24, "bold"))
        self.label.pack(pady=(30, 10))

        # Container dos Botões
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        self.btn_etl = ctk.CTkButton(self.btn_frame, text="1. HARDWARE CORRELATION", 
                                    command=lambda: self.start_thread("phase1_etl.py"),
                                    width=300, height=45, font=("Roboto", 13))
        self.btn_etl.grid(row=0, column=0, padx=10, pady=5)

        self.btn_analytics = ctk.CTkButton(self.btn_frame, text="2. GENERATE PDF METRICS", 
                                          command=lambda: self.start_thread("phase1_analytics.py"),
                                          width=300, height=45, font=("Roboto", 13),
                                          fg_color="#1f538d", hover_color="#14375e")
        self.btn_analytics.grid(row=0, column=1, padx=10, pady=5)

        self.btn_view = ctk.CTkButton(self.btn_frame, text="3. VIEW USER TICKET DASHBOARD", 
                                      command=self.open_metrics_window,
                                      width=620, height=45, font=("Roboto", 13, "bold"),
                                      fg_color="#27ae60", hover_color="#1e8449")
        self.btn_view.grid(row=1, column=0, columnspan=2, pady=(10, 5))

        # Terminal Visual
        self.console_label = ctk.CTkLabel(self, text="Live Processing Output:", font=("Roboto", 12, "bold"), text_color="#2ecc71")
        self.console_label.pack(anchor="w", padx=35, pady=(15, 0))
        
        self.textbox = ctk.CTkTextbox(self, width=630, height=280, font=("Consolas", 13), fg_color="#1e1e1e", text_color="#d4d4d4")
        self.textbox.pack(pady=5, padx=35)
        self.textbox.insert("0.0", "Aguardando execução dos módulos...\n")
        self.textbox.configure(state="disabled")

        self.status_bar = ctk.CTkLabel(self, text="Status: Sistema Pronto", text_color="gray")
        self.status_bar.pack(side="bottom", pady=15)

    def open_metrics_window(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        processed_path = os.path.join(os.path.dirname(current_dir), 'data', 'processed', 'qhelp_enriched_data.csv')
        
        if not os.path.exists(processed_path):
            messagebox.showwarning("Aviso", "Corra o Passo 1 primeiro!")
            return

        try:
            df_full = pd.read_csv(processed_path, encoding='utf-8')
            col_user = 'Created By(Email)' if 'Created By(Email)' in df_full.columns else df_full.columns[1]
            df_full['Hardware_Vinculado'] = df_full.get('Hardware_Vinculado', 'N/A').fillna('Sem Máquina')
            
            metrics = df_full.groupby([col_user, 'Hardware_Vinculado']).size().reset_index(name='Total')
            metrics = metrics.sort_values(by='Total', ascending=False)

            win = ctk.CTkToplevel(self)
            win.title("User Analytics Dashboard")
            win.geometry("900x600")
            win.grab_set()

            ctk.CTkLabel(win, text="📊 Volume de Chamados por Utilizador", font=("Roboto", 20, "bold")).pack(pady=10)
            ctk.CTkLabel(win, text="(Dica: Clique duplo em um usuário para ver o histórico mensal)", font=("Roboto", 11), text_color="gray").pack()

            # Busca
            search_frame = ctk.CTkFrame(win, fg_color="transparent")
            search_frame.pack(fill="x", padx=20, pady=10)
            search_entry = ctk.CTkEntry(search_frame, placeholder_text="Filtrar usuário...", width=300)
            search_entry.pack(side="left", padx=10)

            # Tabela
            table_frame = ctk.CTkFrame(win)
            table_frame.pack(fill="both", expand=True, padx=20, pady=10)

            tree = ttk.Treeview(table_frame, columns=('Usuario', 'Maquina', 'Total'), show='headings')
            tree.heading('Usuario', text='E-mail do Solicitante')
            tree.heading('Maquina', text='Hardware (GLPI)')
            tree.heading('Total', text='Total')
            tree.column('Total', width=100, anchor='center')
            tree.pack(side="left", fill="both", expand=True)

            def filter_table(event=None):
                query = search_entry.get().lower()
                for item in tree.get_children(): tree.delete(item)
                for _, row in metrics.iterrows():
                    if query in str(row[col_user]).lower():
                        tree.insert('', 'end', values=(row[col_user], row['Hardware_Vinculado'], row['Total']))

            # --- NOVA FUNÇÃO: DETALHAMENTO AO CLICAR ---
            def on_item_click(event):
                item_id = tree.selection()[0]
                user_email = tree.item(item_id)['values'][0]
                self.show_user_history(user_email, df_full, col_user)

            tree.bind("<Double-1>", on_item_click) # Duplo clique para detalhar
            search_entry.bind("<KeyRelease>", filter_table)
            filter_table()

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def show_user_history(self, email, df_full, col_user):
        """Abre uma janela com o histórico mensal/anual do usuário selecionado."""
        user_data = df_full[df_full[col_user] == email].copy()
        
        # Tratamento de data similar ao analytics
        date_col = 'Create Date'
        user_data[date_col] = pd.to_datetime(user_data[date_col].astype(str).str.replace(' @ ', ' '), errors='coerce')
        user_data = user_data.dropna(subset=[date_col])
        user_data['Mes/Ano'] = user_data[date_col].dt.to_period('M').astype(str)
        
        history = user_data.groupby('Mes/Ano').size().reset_index(name='Chamados').sort_values('Mes/Ano', ascending=False)

        # Janela de Detalhes
        detail_win = ctk.CTkToplevel(self)
        detail_win.title(f"Histórico: {email}")
        detail_win.geometry("500x500")
        detail_win.grab_set()

        ctk.CTkLabel(detail_win, text=f"Histórico de {email}", font=("Roboto", 16, "bold")).pack(pady=15)

        # Tabela de Meses
        h_frame = ctk.CTkFrame(detail_win)
        h_frame.pack(fill="both", expand=True, padx=20, pady=10)

        h_tree = ttk.Treeview(h_frame, columns=('Periodo', 'Qtd'), show='headings')
        h_tree.heading('Periodo', text='Mês / Ano')
        h_tree.heading('Qtd', text='Qtd. Chamados')
        h_tree.pack(side="left", fill="both", expand=True)

        for _, row in history.iterrows():
            h_tree.insert('', 'end', values=(row['Mes/Ano'], row['Chamados']))

        ctk.CTkButton(detail_win, text="Fechar", command=detail_win.destroy).pack(pady=10)

    # ... (Mantenha as funções de log_to_console, start_thread e execute_script iguais ao anterior)
    def log_to_console(self, text):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", text + "\n")
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def start_thread(self, script_name):
        self.btn_etl.configure(state="disabled")
        self.btn_analytics.configure(state="disabled")
        self.btn_view.configure(state="disabled")
        self.status_bar.configure(text=f"Processando {script_name}...", text_color="yellow")
        self.log_to_console(f"\n--- [START] Executando {script_name} ---")
        thread = threading.Thread(target=self.execute_script, args=(script_name,))
        thread.start()

    def execute_script(self, script_name):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        script_path = os.path.normpath(os.path.join(current_dir, script_name))
        python_exe = sys.executable
        try:
            cmd = f'"{python_exe}" "{script_path}"'
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='latin1')
            for line in process.stdout:
                self.after(0, self.log_to_console, line.strip())
            process.wait()
            if process.returncode == 0:
                self.after(0, self.log_to_console, f"--- [OK] {script_name} finalizado ---")
                self.after(0, lambda: self.status_bar.configure(text=f"Status: {script_name} OK.", text_color="green"))
            else:
                error_output = process.stderr.read()
                self.after(0, self.log_to_console, f"\n[ERRO CRÍTICO]:\n{error_output}")
        except Exception as e:
            self.after(0, self.log_to_console, f"[ERRO]: {str(e)}")
        finally:
            self.after(0, lambda: self.btn_etl.configure(state="normal"))
            self.after(0, lambda: self.btn_analytics.configure(state="normal"))
            self.after(0, lambda: self.btn_view.configure(state="normal"))

if __name__ == "__main__":
    app = QHelpApp()
    app.mainloop()