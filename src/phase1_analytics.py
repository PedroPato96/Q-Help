import pandas as pd
import matplotlib
matplotlib.use('Agg') # Mantém a interface sem travar
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- CAMINHOS ---
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

    print(f"A ler a base de dados...")
    try:
        df_spice = load_data('dados.csv', enc='utf-8')
        df_mensal = load_data('dados_mensal.csv', enc='utf-8')
    except FileNotFoundError as e:
        print(f"Erro Crítico: {e}")
        return

    # --- MÉTRICAS DE SLA ---
    print("\n--- CALCULANDO MÉTRICAS DE SLA ---")
    if 'First Response Secs' in df_spice.columns:
        df_spice['First Response Secs'] = df_spice['First Response Secs'].astype(str).str.replace(',', '.')
        df_spice['First Response Secs'] = pd.to_numeric(df_spice['First Response Secs'], errors='coerce')
        avg_first_resp_h = df_spice['First Response Secs'].mean() / 3600
        print(f"AVG First Response: {avg_first_resp_h:.2f} Horas")

    print("\n--- GERANDO GRÁFICOS VISUAIS PARA O RELATÓRIO ---")
    
    # 1. GRÁFICO DE STATUS (DONUT CHART)
    status_col = 'Status' if 'Status' in df_spice.columns else 'STATUS' if 'STATUS' in df_spice.columns else None
    if status_col:
        plt.figure(figsize=(8, 6))
        status_counts = df_spice[status_col].value_counts()
        
        # Paleta de cores moderna
        colors = ['#1f538d', '#e74c3c', '#f1c40f', '#2ecc71']
        
        plt.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=140, colors=colors, pctdistance=0.85)
        
        # Desenhando o círculo branco no meio para virar Rosca (Donut)
        centre_circle = plt.Circle((0,0), 0.65, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        
        plt.title('Ticket Status - Histórico Global')
        plt.savefig(os.path.join(PROCESSED_PATH, 'chart_status.png'))
        plt.close()
        print("-> [OK] chart_status.png (Donut) gerado com sucesso!")

    # 2. GRÁFICO MENSAL (CORRIGIDO: AGRUPADO POR MÊS E ANO)
    try:
        print("-> A agrupar dados temporais...")
        
        # Pega a coluna de data e garante que o Python entenda que é uma data
        date_col = 'Create Date' if 'Create Date' in df_mensal.columns else df_mensal.columns[1]
        df_mensal[date_col] = pd.to_datetime(df_mensal[date_col].astype(str).str.replace(' @ ', ' '), errors='coerce')
        
        # Tira as linhas vazias e extrai apenas o Ano e Mês (Ex: 2023-01)
        df_valid = df_mensal.dropna(subset=[date_col]).copy()
        df_valid['Ano-Mes'] = df_valid[date_col].dt.to_period('M').astype(str)
        
        # Conta quantos tickets rolaram em cada mês
        monthly_counts = df_valid.groupby('Ano-Mes').size().reset_index(name='Total Tickets')
        monthly_counts = monthly_counts.sort_values('Ano-Mes')
        
        # Desenha um Gráfico de Linha com preenchimento (muito mais profissional para tempo)
        plt.figure(figsize=(12, 5))
        sns.lineplot(data=monthly_counts, x='Ano-Mes', y='Total Tickets', marker='o', color='#1f538d', linewidth=2)
        plt.fill_between(monthly_counts['Ano-Mes'], monthly_counts['Total Tickets'], color='#1f538d', alpha=0.3)
        
        # Mostra apenas um rótulo a cada 6 meses no eixo X para não embolar
        plt.xticks(ticks=range(0, len(monthly_counts), 6), rotation=45)
        
        plt.title('Monthly Ticket History (Aggregated)')
        plt.xlabel('Mês/Ano')
        plt.ylabel('Volume de Tickets')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        plt.savefig(os.path.join(PROCESSED_PATH, 'chart_monthly.png'))
        plt.close()
        print("-> [OK] chart_monthly.png (Linha do Tempo) salvo com sucesso!")
    except Exception as e:
        print(f"-> Aviso: Falha ao processar linha do tempo. Erro: {e}")

    print("\n[SUCESSO] Modulo finalizado. Graficos reconstruidos com sucesso!")

if __name__ == "__main__":
    run_full_analytics()