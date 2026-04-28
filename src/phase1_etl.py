import pandas as pd
import os

# Configuração de caminhos
RAW_DATA_PATH = 'data/raw/'
PROCESSED_DATA_PATH = 'data/processed/'

def run_phase1():
    print("--- Q-Help: Phase 1 - Data Discovery & Mapping ---")

    # 1. CARREGAMENTO DOS DADOS
    # O GLPI usa ponto e vírgula como separador
    try:
        df_glpi = pd.read_csv(os.path.join(RAW_DATA_PATH, 'glpi.csv'), sep=';', encoding='utf-8')
        df_spice = pd.read_csv(os.path.join(RAW_DATA_PATH, 'dados.csv'), encoding='utf-8')
    except FileNotFoundError as e:
        print(f"Erro: Certifica-te que os ficheiros CSV estão em {RAW_DATA_PATH}. {e}")
        return

    # 2. PADRONIZAÇÃO (SANATIZATION)
    print("A higienizar dados...")

    # Criar uma chave comum: o ID do utilizador (ex: mcaffarate)
    # No Spiceworks: extrair o que vem antes do @ no e-mail
    df_spice['user_id'] = df_spice['Created By(Email)'].str.split('@').str[0].str.lower().str.strip()

    #limpar o campo Usuário
    df_glpi['user_id'] = df_glpi['Usuário'].astype(str).str.lower().str.strip()

    # 3. TRATAMENTO DE DATAS (SPICEWORKS)
    # Formato original: 2022-07-04 @ 10:44 AM
    print("A converter formatos de data...")
    df_spice['Create Date'] = pd.to_datetime(df_spice['Create Date'].str.replace(' @ ', ' '), errors='coerce')
    df_spice['Close Date'] = pd.to_datetime(df_spice['Close Date'].str.replace(' @ ', ' '), errors='coerce')

    # 4. CORRELAÇÃO DE DADOS (THE JOIN)
    print("A realizar o cruzamento de bases (Merge)...")
    
   
    glpi_cols = ['user_id', 'Fabricante', 'Número de série', 'Tipo do item', 
                 'Informações financeiras e administrativas - Data da compra']
    
    qhelp_master = pd.merge(df_spice, df_glpi[glpi_cols], on='user_id', how='left')

    # 5. QA & MÉTRICAS INICIAIS
    total_tickets = len(df_spice)
    matched_tickets = qhelp_master['Número de série'].notna().sum()
    match_rate = (matched_tickets / total_tickets) * 100

    print("\n--- Relatório de Qualidade de Dados (QA) ---")
    print(f"Total de Tickets: {total_tickets}")
    print(f"Tickets com Hardware Identificado: {matched_tickets}")
    print(f"Taxa de Sucesso na Correlação: {match_rate:.2f}%")

    # 6. EXPORTAÇÃO
    output_file = os.path.join(PROCESSED_DATA_PATH, 'qhelp_enriched_data.csv')
    qhelp_master.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nSucesso! Ficheiro enriquecido guardado em: {output_file}")

if __name__ == "__main__":
    run_phase1()