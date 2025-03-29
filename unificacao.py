import pandas as pd
import os
import sys

# Caminhos dos arquivos CSV
arquivos_csv = [
    r'C:\Users\argus\workspace\ProjetoSRAG\INFLUD21-01-05-2023.csv',
    r'C:\Users\argus\workspace\ProjetoSRAG\INFLUD22-03-04-2023.csv',
    r'C:\Users\argus\workspace\ProjetoSRAG\INFLUD23-24-03-2025.csv',
    r'C:\Users\argus\workspace\ProjetoSRAG\INFLUD24-24-03-2025.csv'
]

# Função melhorada para carregar arquivos CSV com tratamento robusto de erros
def carregar_csv_robusto(arquivo, tentativas=4):
    """
    Carrega um arquivo CSV tentando diferentes configurações caso ocorra erro.
    """
    if not os.path.exists(arquivo):
        print(f"ERRO: Arquivo não encontrado: {arquivo}")
        return None
    
    print(f"Tentando carregar o arquivo: {arquivo}")
    
    # Lista de configurações a tentar, em ordem de preferência
    configs = [
        # Tentativa 1: Configuração padrão - usando ; como separador (padrão brasileiro)
        {'encoding': 'latin1', 'sep': ';', 'low_memory': False},
        # Tentativa 2: Usando , como separador (padrão internacional)
        {'encoding': 'latin1', 'sep': ',', 'low_memory': False},
        # Tentativa 3: Tentando UTF-8 com ; 
        {'encoding': 'utf-8', 'sep': ';', 'low_memory': False},
        # Tentativa 4: Auto-detecção usando engine python
        {'encoding': 'latin1', 'sep': None, 'engine': 'python', 'low_memory': False}
    ]
    
    # Limitar às primeiras 'tentativas' configurações
    configs = configs[:tentativas]
    
    # Tentar cada configuração
    for i, config in enumerate(configs, 1):
        try:
            print(f"  Tentativa {i}: {config}")
            df = pd.read_csv(arquivo, **config)
            print(f"  ✓ Sucesso! Registros: {len(df)}, Colunas: {len(df.columns)}")
            return df
        except Exception as e:
            print(f"  ✗ Falha: {str(e)[:150]}...")  # Limitar tamanho da mensagem de erro
    
    # Se chegou aqui, nenhuma configuração funcionou
    print(f"ERRO: Não foi possível carregar o arquivo {arquivo} após {tentativas} tentativas.")
    
    # Tentar ver o conteúdo do arquivo para diagnóstico
    try:
        with open(arquivo, 'r', encoding='latin1') as f:
            primeiras_linhas = [next(f) for _ in range(5)]
        print("Primeiras 5 linhas do arquivo para diagnóstico:")
        for i, linha in enumerate(primeiras_linhas):
            print(f"  Linha {i+1}: {linha[:100].strip()}...")
    except Exception as e:
        print(f"Não foi possível ler o conteúdo do arquivo para diagnóstico: {e}")
    
    return None

# Lista para armazenar os DataFrames carregados
dataframes = []

# Carregar cada arquivo CSV e armazenar na lista
for arquivo in arquivos_csv:
    df = carregar_csv_robusto(arquivo)
    if df is not None:
        print(f"✓ Arquivo carregado com sucesso: {arquivo}")
        # Informações básicas sobre o DataFrame
        print(f"  - Dimensões: {df.shape[0]} linhas × {df.shape[1]} colunas")
        # Mostrar alguns nomes de colunas como validação
        print(f"  - Amostra de colunas: {', '.join(list(df.columns)[:5])}...")
        dataframes.append(df)
    else:
        print(f"⚠ Não foi possível carregar o arquivo: {arquivo}")

# Verificar se algum DataFrame foi carregado
if len(dataframes) == 0:
    print("ERRO: Nenhum arquivo válido foi carregado. Verifique os caminhos e formatos.")
    sys.exit(1)
else:
    print(f"\nUnificando {len(dataframes)} arquivos...")
    
    try:
        # Verificar colunas de cada dataframe para identificar possíveis diferenças
        for i, df in enumerate(dataframes):
            print(f"DataFrame {i+1}: {len(df.columns)} colunas")
        
        # Verificar colunas comuns (útil para diagnóstico)
        if len(dataframes) > 1:
            colunas_comuns = set(dataframes[0].columns)
            for df in dataframes[1:]:
                colunas_comuns = colunas_comuns.intersection(set(df.columns))
            print(f"Total de colunas comuns a todos os arquivos: {len(colunas_comuns)}")
        
        # Concatenar todos os DataFrames em um único DataFrame
        df_unificado = pd.concat(dataframes, ignore_index=True)
        print(f"Arquivos unificados com sucesso! Total de registros: {len(df_unificado)}")

        # Salvar o DataFrame unificado em um novo arquivo CSV
        caminho_saida = r'C:\Users\argus\workspace\ProjetoSRAG\SRAG_Unificado.csv'
        df_unificado.to_csv(caminho_saida, index=False, encoding='utf-8-sig', sep=';')
        print(f"Arquivo unificado salvo em: {caminho_saida}")
    except Exception as e:
        print(f"ERRO durante a unificação: {e}")
        sys.exit(1)
