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
        self.width_win = 750
        self.height_win = 750 
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.width_win // 2)
        y = (screen_height // 2) - (self.height_win // 2)
        
        self.geometry(f"{self.width_win}x{self.height_win}+{x}+{y}")
        self.minsize(750, 750)

        # Título
        self.label = ctk.CTkLabel(self, text="Q-Help Management Console", font=("Roboto", 24, "bold"))
        self.label.pack(pady=(20, 10))

        # Container dos Botões Principais
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        # LINHA 1
        self.btn_etl = ctk.CTkButton(self.btn_frame, text="1. HARDWARE CORRELATION", command=lambda: self.start_thread("phase1_etl.py"), width=320, height=45, font=("Roboto", 13))
        self.btn_etl.grid(row=0, column=0, padx=10, pady=5)

        self.btn_analytics = ctk.CTkButton(self.btn_frame, text="2. GENERATE PDF METRICS", command=lambda: self.start_thread("phase1_analytics.py"), width=320, height=45, font=("Roboto", 13), fg_color="#1f538d", hover_color="#14375e")
        self.btn_analytics.grid(row=0, column=1, padx=10, pady=5)

        # LINHA 2
        self.btn_view = ctk.CTkButton(self.btn_frame, text="3. VIEW USER TICKET DASHBOARD", command=self.open_metrics_window, width=320, height=45, font=("Roboto", 13, "bold"), fg_color="#27ae60", hover_color="#1e8449")
        self.btn_view.grid(row=1, column=0, padx=10, pady=5)

        # --- NOVO BOTÃO: DASHBOARD DO PDF ---
        self.btn_kpi = ctk.CTkButton(self.btn_frame, text="4. GLOBAL IT DASHBOARD (KPIs)", command=self.open_global_dashboard, width=320, height=45, font=("Roboto", 13, "bold"), fg_color="#8e44ad", hover_color="#732d91")
        self.btn_kpi.grid(row=1, column=1, padx=10, pady=5)

        # Terminal Visual
        self.console_label = ctk.CTkLabel(self, text="Live Processing Output:", font=("Roboto", 12, "bold"), text_color="#2ecc71")
        self.console_label.pack(anchor="w", padx=35, pady=(15, 0))
        
        self.textbox = ctk.CTkTextbox(self, width=680, height=280, font=("Consolas", 13), fg_color="#1e1e1e", text_color="#d4d4d4")
        self.textbox.pack(pady=5, padx=35)
        self.textbox.insert("0.0", "Aguardando execução dos módulos...\n")
        self.textbox.configure(state="disabled")

        self.status_bar = ctk.CTkLabel(self, text="Status: Sistema Pronto", text_color="gray")
        self.status_bar.pack(side="bottom", pady=15)

    # -------------------------------------------------------------------------
    # NOVA FUNÇÃO: REPRODUZINDO O PDF DE BI NA UI
    # -------------------------------------------------------------------------
    def open_global_dashboard(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        raw_path = os.path.join(os.path.dirname(current_dir), 'data', 'raw', 'dados.csv')
        
        if not os.path.exists(raw_path):
            messagebox.showwarning("Aviso", "O arquivo dados.csv não foi encontrado na pasta raw.")
            return

        try:
            self.status_bar.configure(text="A calcular KPIs Globais...", text_color="yellow")
            self.update()

            # Lê a base com as correções de caracteres que já aprendemos
            try:
                df = pd.read_csv(raw_path, sep=None, engine='python', encoding='utf-8')
            except:
                df = pd.read_csv(raw_path, sep=None, engine='python', encoding='latin1')
            
            df.columns = df.columns.str.replace(r'[\ufeff"]', '', regex=True).str.strip()

            # --- CÁLCULO DAS MÉTRICAS DO PDF ---
            col_status = 'Status' if 'Status' in df.columns else df.columns[5]
            col_analyst = 'Assigned to' if 'Assigned to' in df.columns else df.columns[9]
            
            # KPI 1 e 2: Status
            total_open = df[df[col_status].astype(str).str.lower() == 'open'].shape[0]
            total_waiting = df[df[col_status].astype(str).str.lower() == 'waiting'].shape[0]
            
            # KPI 3: AVG First Response (Convertendo segundos para horas)
            avg_fr_h = 0.0
            if 'First Response Secs' in df.columns:
                df['First Response Secs'] = df['First Response Secs'].astype(str).str.replace(',', '.')
                df['First Response Secs'] = pd.to_numeric(df['First Response Secs'], errors='coerce')
                avg_fr_h = df['First Response Secs'].mean() / 3600

            # KPI 4: Desempenho por Analista
            analyst_stats = df.groupby([col_analyst, col_status]).size().unstack(fill_value=0).reset_index()
            if 'open' not in analyst_stats.columns: analyst_stats['open'] = 0
            if 'waiting' not in analyst_stats.columns: analyst_stats['waiting'] = 0
            if 'closed' not in analyst_stats.columns: analyst_stats['closed'] = 0
            analyst_stats['Total'] = analyst_stats['open'] + analyst_stats['waiting'] + analyst_stats['closed']
            analyst_stats = analyst_stats.sort_values(by='Total', ascending=False)

            # --- CONSTRUÇÃO DA JANELA DO DASHBOARD ---
            win = ctk.CTkToplevel(self)
            win.title("Executive IT Process Dashboard")
            win.geometry("950x650")
            win.grab_set()

            ctk.CTkLabel(win, text="📈 MONITORING IT PROCESS", font=("Roboto", 24, "bold"), text_color="#3498db").pack(pady=(15, 5))

            # Container dos "Cards" de KPI (Estilo PowerBI)
            kpi_frame = ctk.CTkFrame(win, fg_color="transparent")
            kpi_frame.pack(fill="x", padx=20, pady=15)

            def create_kpi_card(parent, title, value, color):
                card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)
                card.pack(side="left", fill="both", expand=True, padx=10)
                ctk.CTkLabel(card, text=title, font=("Roboto", 14, "bold"), text_color="white").pack(pady=(15, 5))
                ctk.CTkLabel(card, text=str(value), font=("Roboto", 30, "bold"), text_color="white").pack(pady=(0, 15))

            create_kpi_card(kpi_frame, "AVG First Response", f"{avg_fr_h:.2f} H", "#c0392b") # Vermelho
            create_kpi_card(kpi_frame, "Open Tickets", str(total_open), "#e67e22")           # Laranja
            create_kpi_card(kpi_frame, "Waiting Tickets", str(total_waiting), "#f39c12")     # Amarelo

            # Tabela de Analistas
            ctk.CTkLabel(win, text="Tabela de Desempenho por Analista", font=("Roboto", 16, "bold")).pack(pady=(10, 5))
            table_frame = ctk.CTkFrame(win)
            table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

            style = ttk.Style(win)
            style.theme_use("default")
            style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=30, fieldbackground="#2b2b2b")
            style.configure("Treeview.Heading", font=("Roboto", 11, "bold"), background="#34495e", foreground="white")

            colunas = ('Analista', 'Open', 'Waiting', 'Closed', 'Total')
            tree = ttk.Treeview(table_frame, columns=colunas, show='headings')
            
            for col in colunas:
                tree.heading(col, text=col)
                tree.column(col, anchor='center', width=100)
            tree.column('Analista', width=250, anchor='w')

            scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            for _, row in analyst_stats.iterrows():
                tree.insert('', 'end', values=(row[col_analyst], row['open'], row['waiting'], row['closed'], row['Total']))

            # BOTÃO: Preparar para Sheets
            btn_sheets = ctk.CTkButton(win, text="Exportar Dados (Preparado para Google Sheets)", 
                                       command=lambda: self.export_to_sheets_format(analyst_stats),
                                       font=("Roboto", 14, "bold"), fg_color="#217346", hover_color="#185c37") # Cor do Excel/Sheets
            btn_sheets.pack(pady=15)

            self.status_bar.configure(text="Status: Global Dashboard Aberto", text_color="green")

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao processar KPIs:\n{str(e)}")
            self.status_bar.configure(text="Status: Erro no Dashboard", text_color="red")

    def export_to_sheets_format(self, dataframe):
        """Exporta os dados formatados perfeitamente para plugar no Google Sheets."""
        try:
            export_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data', 'processed')
            os.makedirs(export_dir, exist_ok=True)
            export_path = os.path.join(export_dir, 'sheets_export_analysts.csv')
            
            # Salva o CSV usando vírgula padrão internacional (melhor para o Google Sheets API ler)
            dataframe.to_csv(export_path, index=False, encoding='utf-8')
            messagebox.showinfo("Sucesso", f"Dados formatados e salvos para o Sheets em:\n{export_path}\n\nNo futuro, este botão enviará os dados direto para a nuvem!")
        except Exception as e:
            messagebox.showerror("Erro na Exportação", str(e))

    # -------------------------------------------------------------------------
    # FUNÇÕES ANTIGAS MANTIDAS (VIEW USER, LOGS, EXECUÇÃO, ETC.)
    # -------------------------------------------------------------------------
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
            metrics = df_full.groupby([col_user, 'Hardware_Vinculado']).size().reset_index(name='Total').sort_values(by='Total', ascending=False)
            win = ctk.CTkToplevel(self)
            win.title("User Analytics Dashboard")
            win.geometry("900x600")
            win.grab_set()
            ctk.CTkLabel(win, text="📊 Volume de Chamados por Utilizador", font=("Roboto", 20, "bold")).pack(pady=10)
            search_frame = ctk.CTkFrame(win, fg_color="transparent")
            search_frame.pack(fill="x", padx=20, pady=10)
            search_entry = ctk.CTkEntry(search_frame, placeholder_text="Filtrar usuário...", width=300)
            search_entry.pack(side="left", padx=10)
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
            def on_item_click(event):
                item_id = tree.selection()[0]
                user_email = tree.item(item_id)['values'][0]
                self.show_user_history(user_email, df_full, col_user)
            tree.bind("<Double-1>", on_item_click)
            search_entry.bind("<KeyRelease>", filter_table)
            filter_table()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def show_user_history(self, email, df_full, col_user):
        user_data = df_full[df_full[col_user] == email].copy()
        date_col = 'Create Date'
        user_data[date_col] = pd.to_datetime(user_data[date_col].astype(str).str.replace(' @ ', ' '), errors='coerce')
        user_data = user_data.dropna(subset=[date_col])
        user_data['Mes/Ano'] = user_data[date_col].dt.to_period('M').astype(str)
        history = user_data.groupby('Mes/Ano').size().reset_index(name='Chamados').sort_values('Mes/Ano', ascending=False)
        detail_win = ctk.CTkToplevel(self)
        detail_win.title(f"Histórico: {email}")
        detail_win.geometry("500x500")
        detail_win.grab_set()
        ctk.CTkLabel(detail_win, text=f"Histórico de {email}", font=("Roboto", 16, "bold")).pack(pady=15)
        h_frame = ctk.CTkFrame(detail_win)
        h_frame.pack(fill="both", expand=True, padx=20, pady=10)
        h_tree = ttk.Treeview(h_frame, columns=('Periodo', 'Qtd'), show='headings')
        h_tree.heading('Periodo', text='Mês / Ano')
        h_tree.heading('Qtd', text='Qtd. Chamados')
        h_tree.pack(side="left", fill="both", expand=True)
        for _, row in history.iterrows():
            h_tree.insert('', 'end', values=(row['Mes/Ano'], row['Chamados']))

    def log_to_console(self, text):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", text + "\n")
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def start_thread(self, script_name):
        self.btn_etl.configure(state="disabled")
        self.btn_analytics.configure(state="disabled")
        self.btn_view.configure(state="disabled")
        self.btn_kpi.configure(state="disabled")
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
            self.after(0, lambda: self.btn_kpi.configure(state="normal"))

if __name__ == "__main__":
    app = QHelpApp()
    app.mainloop()