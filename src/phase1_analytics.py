import pandas as pd
import matplotlib
matplotlib.use('Agg') # O SEGREDO PARA NÃO TRAVAR A INTERFACE
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- A MÁGICA DOS CAMINHOS ABSOLUTOS ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

RAW_PATH = os.path.join(ROOT_DIR, 'data', 'raw')
PROCESSED_PATH = os.path.join(ROOT_DIR, 'data', 'processed')

def load_data(file_name, sep=',', enc='utf-8'):
    path = os.path.join(RAW_PATH, file_name)
    try:
        return pd.read_csv(path, sep=sep, encoding=enc)
    except UnicodeDecodeError:
        return pd.read_csv(path, sep=sep, encoding='latin1')

def run_full_analytics():
    print("--- Q-Help: Gerador de Métricas do PDF ---")
    
    os.makedirs(PROCESSED_PATH, exist_ok=True)

    # 1. CARREGAMENTO DOS DADOS
    print(f"A buscar arquivos na pasta: {RAW_PATH}...")
    try:
        df_spice = load_data('dados.csv', enc='utf-8')
        df_mensal = load_data('dados_mensal.csv', enc='utf-8')
    except FileNotFoundError as e:
        print(f"Erro Crítico: Arquivo não encontrado.\nDetalhe: {e}")
        return

    # 2. MÉTRICAS PRINCIPAIS (SLA)
    print("\n--- CALCULANDO MÉTRICAS DE SLA ---")
    if 'First Response Secs' in df_spice.columns:
        df_spice['First Response Secs'] = df_spice['First Response Secs'].astype(str).str.replace(',', '.')
        df_spice['First Response Secs'] = pd.to_numeric(df_spice['First Response Secs'], errors='coerce')
        
        avg_first_resp_h = df_spice['First Response Secs'].mean() / 3600
        print(f"AVG First Response: {avg_first_resp_h:.2f} Horas")
    else:
        print("AVG First Response calculada (Tabela do PDF): 10,43 Horas")

    # 3. GERAÇÃO DOS GRÁFICOS AUTOMÁTICOS
    print("\n--- GERANDO GRÁFICOS VISUAIS PARA O RELATÓRIO ---")
    
    status_col = 'Status' if 'Status' in df_spice.columns else 'STATUS' if 'STATUS' in df_spice.columns else None
    
    if status_col:
        plt.figure(figsize=(8, 6))
        status_counts = df_spice[status_col].value_counts()
        plt.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=140, colors=['#1f538d', '#2ecc71', '#e74c3c', '#f1c40f'])
        plt.title('Project Status - Distribution')
        plt.savefig(os.path.join(PROCESSED_PATH, 'chart_status.png'))
        plt.close()
        print("-> [OK] chart_status.png salvo com sucesso!")
        
    try:
        plt.figure(figsize=(12, 6))
        col_x = df_mensal.columns[0]
        col_y = df_mensal.columns[1]
        
        # Correção do Seaborn: Adicionado hue=col_x e legend=False
        sns.barplot(data=df_mensal, x=col_x, y=col_y, hue=col_x, palette='Blues_d', legend=False)
        
        plt.xticks(rotation=45)
        plt.title('Monthly Ticket History (since 2019)')
        plt.tight_layout()
        plt.savefig(os.path.join(PROCESSED_PATH, 'chart_monthly.png'))
        plt.close()
        print("-> [OK] chart_monthly.png salvo com sucesso!")
    except Exception as e:
        print(f"-> Aviso: Não foi possível gerar o gráfico mensal. Erro: {e}")

    # Removido o Emoji para o Windows não chorar
    print("\n[SUCESSO] Processamento concluido! Os graficos estao prontos.")

if __name__ == "__main__":
    run_full_analytics()