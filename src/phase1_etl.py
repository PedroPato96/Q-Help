import pandas as pd
import unicodedata
import os

# --- CAMINHOS ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
RAW_PATH = os.path.join(ROOT_DIR, 'data', 'raw')
PROCESSED_PATH = os.path.join(ROOT_DIR, 'data', 'processed')

def normalizar_texto(texto):
    """Remove acentos, espaços extras e coloca em minúsculo."""
    if pd.isna(texto):
        return ""
    texto = str(texto).lower().strip()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto

def extrair_prefixo_email(email):
    """Corta o domínio. Ex: 'jdaros@panamerican.com.br' vira 'jdaros'."""
    texto_limpo = normalizar_texto(email)
    if '@' in texto_limpo:
        return texto_limpo.split('@')[0]
    return texto_limpo

def gerar_username_glpi(nome_completo):
    """Transforma 'Pedro Silveira Ricardo' em 'pricardo'."""
    nome_limpo = normalizar_texto(nome_completo)
    partes = nome_limpo.split()
    
    if len(partes) >= 2:
        primeira_letra = partes[0][0]
        ultimo_sobrenome = partes[-1]
        return f"{primeira_letra}{ultimo_sobrenome}"
    elif len(partes) == 1:
        return partes[0]
    return ""

def load_safe_csv(filename):
    """Lê o CSV independentemente se usa vírgula ou ponto-e-vírgula."""
    path = os.path.join(RAW_PATH, filename)
    try:
        return pd.read_csv(path, sep=None, engine='python', encoding='utf-8')
    except UnicodeDecodeError:
        return pd.read_csv(path, sep=None, engine='python', encoding='latin1')

def run_etl():
    print("--- Q-Help: Phase 1 - Data Discovery & Mapping ---")
    os.makedirs(PROCESSED_PATH, exist_ok=True)

    print("A carregar bases de dados (Spiceworks e GLPI)...")
    try:
        df_spice = load_safe_csv('dados.csv')
        df_glpi = load_safe_csv('glpi.csv')
    except Exception as e:
        print(f"Erro Critico ao ler arquivos: {e}")
        return

    # --- O TRUQUE DE MESTRE: LIMPANDO OS CABEÇALHOS ---
    # Remove o maldito \ufeff e aspas duplas escondidas nos nomes das colunas
    df_spice.columns = df_spice.columns.str.replace(r'[\ufeff"]', '', regex=True).str.strip()
    df_glpi.columns = df_glpi.columns.str.replace(r'[\ufeff"]', '', regex=True).str.strip()

    # Nomes EXATOS após a nossa investigação
    col_user_spice = 'Created By(Email)'
    col_user_glpi = 'Usuário'
    col_maquina_glpi = 'Nome'

    print("A higienizar dados e reconstruir usernames...")
    # 1. Spiceworks: Pega o e-mail e corta o @dominio.com
    df_spice['Chave_Merge'] = df_spice[col_user_spice].apply(extrair_prefixo_email)
    
    # 2. GLPI: Pega o Nome Completo e transforma em username (P + Ricardo)
    df_glpi['Chave_Merge'] = df_glpi[col_user_glpi].apply(gerar_username_glpi)

    print("A tratar conflitos de colunas e realizar cruzamento...")
    df_glpi_subset = df_glpi[['Chave_Merge', col_maquina_glpi]].copy()
    df_glpi_subset = df_glpi_subset.dropna(subset=['Chave_Merge'])
    df_glpi_subset = df_glpi_subset.drop_duplicates(subset=['Chave_Merge'])
    df_glpi_subset = df_glpi_subset.rename(columns={col_maquina_glpi: 'Hardware_Vinculado'})

    df_enriched = pd.merge(df_spice, df_glpi_subset, on='Chave_Merge', how='left')

    # --- QA & ESTATÍSTICAS ---
    total_tickets = len(df_enriched)
    tickets_com_hardware = df_enriched['Hardware_Vinculado'].notna().sum()
    taxa_sucesso = (tickets_com_hardware / total_tickets) * 100 if total_tickets > 0 else 0

    print("\n--- Relatorio de Qualidade de Dados (QA) ---")
    print(f"Total de Tickets Processados: {total_tickets}")
    print(f"Tickets com Hardware Identificado: {tickets_com_hardware}")
    print(f"Taxa de Sucesso na Correlacao: {taxa_sucesso:.2f}%")

    # Limpeza final e exportação
    df_enriched = df_enriched.drop(columns=['Chave_Merge'])
    output_file = os.path.join(PROCESSED_PATH, 'qhelp_enriched_data.csv')
    df_enriched.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n[SUCESSO] Ficheiro enriquecido guardado!")

if __name__ == "__main__":
    run_etl()