import customtkinter as ctk
import subprocess
import os
import sys
from tkinter import messagebox

# Configuração visual profissional
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class QHelpApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Forçando o tamanho e impedindo o "nanismo" (DPI scaling do Windows)
        self.title("Q-Help - Executive Analytics Control")
        self.width_win = 600
        self.height_win = 480
        
        # Cálculo de centralização
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.width_win // 2)
        y = (screen_height // 2) - (self.height_win // 2)
        
        self.geometry(f"{self.width_win}x{self.height_win}+{x}+{y}")
        self.minsize(600, 480)

        # Título Principal
        self.label = ctk.CTkLabel(self, text="Q-Help Management Console", font=("Roboto", 24, "bold"))
        self.label.pack(pady=(40, 20))

        # Botão 1: Correlação Hardware (GLPI + Spiceworks)
        self.btn_etl = ctk.CTkButton(self, text="1. RUN HARDWARE CORRELATION (GLPI)", 
                                    command=lambda: self.execute("phase1_etl.py"),
                                    width=400, height=50, font=("Roboto", 14))
        self.btn_etl.pack(pady=15)

        # Botão 2: Analytics Completo (Métricas do PDF)
        self.btn_analytics = ctk.CTkButton(self, text="2. GENERATE PDF METRICS & ANALYTICS", 
                                          command=lambda: self.execute("phase1_analytics.py"),
                                          width=400, height=50, font=("Roboto", 14),
                                          fg_color="#1f538d", hover_color="#14375e")
        self.btn_analytics.pack(pady=15)

        # Barra de Status
        self.status_bar = ctk.CTkLabel(self, text="Status: Sistema Pronto", text_color="gray")
        self.status_bar.pack(side="bottom", pady=20)

    def execute(self, script_name):
        # 1. Localiza o diretório real onde este arquivo (main_gui.py) está
        current_dir = os.path.dirname(os.path.realpath(__file__))
        
        # 2. Constrói o caminho absoluto para o script vizinho e normaliza para o Windows
        script_path = os.path.normpath(os.path.join(current_dir, script_name))
        
        # 3. Pega o executável do Python do ambiente virtual (venv)
        python_exe = sys.executable

        self.status_bar.configure(text=f"Processando {script_name}...", text_color="yellow")
        self.update()

        try:
            # Roda o script usando aspas duplas para evitar erros com espaços no caminho
            # shell=True é necessário para o Windows interpretar corretamente o comando com aspas
            cmd = f'"{python_exe}" "{script_path}"'
            
            process = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='latin1')
            
            if process.returncode == 0:
                # Se o script deu certo, as métricas do PDF (AVG First Response, etc) aparecem aqui
                print(f"--- OUTPUT {script_name} ---\n{process.stdout}")
                messagebox.showinfo("Sucesso", f"O módulo {script_name} foi processado com sucesso!")
                self.status_bar.configure(text=f"Status: {script_name} concluído.", text_color="green")
            else:
                # Se o arquivo não existir ou o script quebrar, o erro aparece aqui
             import customtkinter as ctk
import subprocess
import os
import sys
import threading
from tkinter import messagebox

# Configuração visual profissional
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class QHelpApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Q-Help - Executive Analytics Control")
        self.width_win = 700
        self.height_win = 650 # Aumentei a janela para caber o terminal
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.width_win // 2)
        y = (screen_height // 2) - (self.height_win // 2)
        
        self.geometry(f"{self.width_win}x{self.height_win}+{x}+{y}")
        self.minsize(700, 650)

        # Título
        self.label = ctk.CTkLabel(self, text="Q-Help Management Console", font=("Roboto", 24, "bold"))
        self.label.pack(pady=(30, 10))

        # Container dos Botões
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        self.btn_etl = ctk.CTkButton(self.btn_frame, text="1. HARDWARE CORRELATION", 
                                    command=lambda: self.start_thread("phase1_etl.py"),
                                    width=300, height=45, font=("Roboto", 13))
        self.btn_etl.grid(row=0, column=0, padx=10)

        self.btn_analytics = ctk.CTkButton(self.btn_frame, text="2. GENERATE PDF METRICS", 
                                          command=lambda: self.start_thread("phase1_analytics.py"),
                                          width=300, height=45, font=("Roboto", 13),
                                          fg_color="#1f538d", hover_color="#14375e")
        self.btn_analytics.grid(row=0, column=1, padx=10)

        # --- O NOVO TERMINAL VISUAL ---
        self.console_label = ctk.CTkLabel(self, text="Live Processing Output:", font=("Roboto", 12, "bold"), text_color="#2ecc71")
        self.console_label.pack(anchor="w", padx=35, pady=(20, 0))
        
        self.textbox = ctk.CTkTextbox(self, width=630, height=250, font=("Consolas", 13), fg_color="#1e1e1e", text_color="#d4d4d4")
        self.textbox.pack(pady=5, padx=35)
        self.textbox.insert("0.0", "Aguardando execução dos módulos...\n")
        self.textbox.configure(state="disabled")

        # Barra de Status
        self.status_bar = ctk.CTkLabel(self, text="Status: Sistema Pronto", text_color="gray")
        self.status_bar.pack(side="bottom", pady=15)

    # Função para escrever no terminal da tela
    def log_to_console(self, text):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", text + "\n")
        self.textbox.see("end") # Rola para o final automaticamente
        self.textbox.configure(state="disabled")

    # Inicia o script em background (Threading) para NÃO TRAVAR a interface
    def start_thread(self, script_name):
        self.btn_etl.configure(state="disabled")
        self.btn_analytics.configure(state="disabled")
        self.status_bar.configure(text=f"Processando {script_name}...", text_color="yellow")
        
        self.log_to_console(f"\n--- [START] Executando {script_name} ---")
        
        # Cria uma thread secundária
        thread = threading.Thread(target=self.execute_script, args=(script_name,))
        thread.start()

    def execute_script(self, script_name):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        script_path = os.path.normpath(os.path.join(current_dir, script_name))
        python_exe = sys.executable

        try:
            cmd = f'"{python_exe}" "{script_path}"'
            # Popen em vez de run() permite ler as linhas enquanto o script roda
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='latin1')
            
            # Lê o que o script está printando e manda para o nosso TextBox
            for line in process.stdout:
                self.after(0, self.log_to_console, line.strip())
            
            process.wait() # Aguarda terminar
            
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
            # Libera os botões de novo
            self.after(0, lambda: self.btn_etl.configure(state="normal"))
            self.after(0, lambda: self.btn_analytics.configure(state="normal"))

if __name__ == "__main__":
    app = QHelpApp()
    app.mainloop()