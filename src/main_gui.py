import customtkinter as ctk
import subprocess
import os
import sys
import threading
from tkinter import messagebox, ttk
import pandas as pd

# Configuração visual profissional
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class QHelpApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Q-Help - Executive Analytics Control")
        self.width_win = 700
        self.height_win = 700 # Aumentei um pouco para caber os 3 botões
        
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

        # Botão 1: ETL
        self.btn_etl = ctk.CTkButton(self.btn_frame, text="1. HARDWARE CORRELATION", 
                                    command=lambda: self.start_thread("phase1_etl.py"),
                                    width=300, height=45, font=("Roboto", 13))
        self.btn_etl.grid(row=0, column=0, padx=10, pady=5)

        # Botão 2: Gráficos PDF
        self.btn_analytics = ctk.CTkButton(self.btn_frame, text="2. GENERATE PDF METRICS", 
                                          command=lambda: self.start_thread("phase1_analytics.py"),
                                          width=300, height=45, font=("Roboto", 13),
                                          fg_color="#1f538d", hover_color="#14375e")
        self.btn_analytics.grid(row=0, column=1, padx=10, pady=5)

        # Botão 3: NOVO - Tabela de Métricas na UI
        self.btn_view = ctk.CTkButton(self.btn_frame, text="3. VIEW USER TICKET DASHBOARD", 
                                      command=self.open_metrics_window,
                                      width=620, height=45, font=("Roboto", 13, "bold"),
                                      fg_color="#27ae60", hover_color="#1e8449")
        self.btn_view.grid(row=1, column=0, columnspan=2, pady=(10, 5))

        # --- TERMINAL VISUAL (MANTIDO INTACTO) ---
        self.console_label = ctk.CTkLabel(self, text="Live Processing Output:", font=("Roboto", 12, "bold"), text_color="#2ecc71")
        self.console_label.pack(anchor="w", padx=35, pady=(15, 0))
        
        self.textbox = ctk.CTkTextbox(self, width=630, height=280, font=("Consolas", 13), fg_color="#1e1e1e", text_color="#d4d4d4")
        self.textbox.pack(pady=5, padx=35)
        self.textbox.insert("0.0", "Aguardando execução dos módulos...\n")
        self.textbox.configure(state="disabled")

        # Barra de Status
        self.status_bar = ctk.CTkLabel(self, text="Status: Sistema Pronto", text_color="gray")
        self.status_bar.pack(side="bottom", pady=15)

    # --- NOVA FUNÇÃO: Tabela Gráfica ---
    def open_metrics_window(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        processed_path = os.path.join(os.path.dirname(current_dir), 'data', 'processed', 'qhelp_enriched_data.csv')
        
        if not os.path.exists(processed_path):
            messagebox.showwarning("Aviso de Sistema", "O ficheiro enriquecido não existe. Por favor, corra o Passo 1 primeiro!")
            return

        try:
            self.status_bar.configure(text="A carregar dashboard de utilizadores...", text_color="yellow")
            self.update()

            # Lê os dados
            df = pd.read_csv(processed_path, encoding='utf-8')
            
            # Garante os nomes corretos das colunas
            col_user = 'Created By(Email)' if 'Created By(Email)' in df.columns else df.columns[1]
            
            # Preenche quem não tem máquina com 'Desconhecida' para a tabela não quebrar
            if 'Hardware_Vinculado' in df.columns:
                df['Hardware_Vinculado'] = df['Hardware_Vinculado'].fillna('Sem Máquina Identificada')
            else:
                df['Hardware_Vinculado'] = 'N/A'
                
            # Agrupa os dados e conta os chamados
            metrics = df.groupby([col_user, 'Hardware_Vinculado']).size().reset_index(name='Total')
            metrics = metrics.sort_values(by='Total', ascending=False)

            # Cria a Janela Secundária (Pop-up)
            win = ctk.CTkToplevel(self)
            win.title("Top Requester Analytics")
            win.geometry("850x500")
            win.minsize(850, 500)
            win.grab_set() # Foca nesta janela

            titulo = ctk.CTkLabel(win, text="📊 Volume de Chamados por Utilizador", font=("Roboto", 20, "bold"))
            titulo.pack(pady=15)

            # Container para a Tabela e Scrollbar
            table_frame = ctk.CTkFrame(win)
            table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

            # Estilização da Tabela para Dark Mode
            style = ttk.Style(win)
            style.theme_use("default")
            style.configure("Treeview", 
                            background="#2b2b2b", foreground="white", 
                            rowheight=30, fieldbackground="#2b2b2b", 
                            font=("Roboto", 11))
            style.configure("Treeview.Heading", font=("Roboto", 12, "bold"), background="#1f538d", foreground="white")
            style.map('Treeview', background=[('selected', '#2ecc71')])

            # Criando a Tabela
            colunas = ('Usuario', 'Maquina', 'Total')
            tree = ttk.Treeview(table_frame, columns=colunas, show='headings')
            
            tree.heading('Usuario', text='E-mail do Solicitante')
            tree.heading('Maquina', text='Hardware Vinculado (GLPI)')
            tree.heading('Total', text='Qtd. Chamados')
            
            tree.column('Usuario', width=350)
            tree.column('Maquina', width=250)
            tree.column('Total', width=150, anchor='center')

            # Scrollbar
            scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Preenchendo a Tabela com os dados
            for index, row in metrics.iterrows():
                tree.insert('', 'end', values=(row[col_user], row['Hardware_Vinculado'], row['Total']))

            self.status_bar.configure(text="Status: Dashboard Aberto", text_color="green")

        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"Falha ao gerar tabela gráfica:\n{str(e)}")
            self.status_bar.configure(text="Status: Sistema Pronto", text_color="gray")

    # --- FUNÇÕES DE LOG E EXECUÇÃO (MANTIDAS) ---
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
                self.after(0, lambda: self.status_bar.configure(text="Status: Erro na execução", text_color="red"))
        
        except Exception as e:
            self.after(0, self.log_to_console, f"[ERRO DE SISTEMA]: {str(e)}")
        
        finally:
            self.after(0, lambda: self.btn_etl.configure(state="normal"))
            self.after(0, lambda: self.btn_analytics.configure(state="normal"))
            self.after(0, lambda: self.btn_view.configure(state="normal"))

if __name__ == "__main__":
    app = QHelpApp()
    app.mainloop()