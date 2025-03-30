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

# Lista de colunas a manter - conforme especificação
colunas_para_manter = [
    'DT_NOTIFIC', 'DT_SIN_PRI', 'SG_UF_NOT', 'ID_REGIONA', 
    'ID_MUNICIP',  'ID_UNIDADE', 'CS_SEXO', 'DT_NASC', 
    'NU_IDADE_N', 'TP_IDADE', 'CS_GESTANT', 'CS_RACA', 'CS_ESCOL_N',
    'ID_PAIS', 'SG_UF', 'ID_RG_RESI', 'ID_MN_RESI', 
    'NOSOCOMIAL', 'AVE_SUINO', 'FEBRE', 'TOSSE', 'GARGANTA', 'DISPNEIA', 'DESC_RESP', 
    'SATURACAO', 'DIARREIA', 'VOMITO', 'OUTRO_SIN', 'OUTRO_DES', 'PUERPERA', 
    'FATOR_RISC', 'CARDIOPATI', 'HEMATOLOGI', 'SIND_DOWN', 'HEPATICA', 'ASMA', 
    'DIABETES', 'NEUROLOGIC', 'PNEUMOPATI', 'IMUNODEPRE', 'RENAL', 'OBESIDADE', 
    'OBES_IMC', 'OUT_MORBI', 'MORB_DESC', 'VACINA', 'DT_UT_DOSE', 'ANTIVIRAL', 
    'TP_ANTIVIR', 'DT_INTERNA', 'SG_UF_INTE', 'ID_RG_INTE', 
    'ID_MN_INTE', 'UTI', 'DT_ENTUTI', 'DT_SAIDUTI', 'SUPORT_VEN', 
    'RAIOX_RES', 'RAIOX_OUT', 'DT_RAIOX', 'AMOSTRA', 'DT_COLETA', 'TP_AMOSTRA', 
    'OUT_AMOST', 'PCR_RESUL', 'DT_PCR', 'POS_PCRFLU', 'TP_FLU_PCR', 'PCR_FLUASU', 
    'FLUASU_OUT', 'CLASSI_FIN', 'CLASSI_OUT', 'CRITERIO', 'EVOLUCAO', 'DT_EVOLUCA', 
    'DT_ENCERRA', 'DT_DIGITA', 'PAC_DSCBO', 'DOR_ABD', 'FADIGA', 'PERD_OLFT', 
    'PERD_PALA', 'TOMO_RES', 'TOMO_OUT', 'DT_TOMO', 'DS_AN_OUT', 'TP_TES_AN', 
    'DT_RES_AN', 'RES_AN', 'POS_AN_FLU', 'TP_FLU_AN', 'POS_AN_OUT', 'AN_SARS2', 
    'AN_VSR', 'ESTRANG', 'VACINA_COV', 'DOSE_1_COV', 'DOSE_2_COV', 'DOSE_REF', 
    'FAB_COV_1', 'FAB_COV_2', 'FAB_COVREF', 'LAB_PR_COV'
]

# Função para filtrar colunas que existem no DataFrame
def filtrar_colunas_existentes(df, colunas_desejadas):
    """
    Filtra o DataFrame para manter apenas as colunas desejadas que existem nele.
    """
    # Identificar quais colunas desejadas realmente existem no DataFrame
    colunas_existentes = [col for col in colunas_desejadas if col in df.columns]
    
    # Colunas desejadas que não existem no DataFrame
    colunas_ausentes = [col for col in colunas_desejadas if col not in df.columns]
    if colunas_ausentes:
        print(f"  Aviso: {len(colunas_ausentes)} colunas solicitadas não existem neste DataFrame:")
        print(f"  {', '.join(colunas_ausentes[:10])}{'...' if len(colunas_ausentes) > 10 else ''}")
    
    # Retornar DataFrame apenas com as colunas existentes
    return df[colunas_existentes]

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
            
            # Filtrar colunas antes de retornar
            print(f"  Filtrando colunas para manter apenas as solicitadas...")
            df_filtrado = filtrar_colunas_existentes(df, colunas_para_manter)
            print(f"  ✓ Dataset reduzido de {len(df.columns)} para {len(df_filtrado.columns)} colunas")
            
            return df_filtrado
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
        if len(dataframes) > 1:  # Fixed: Added missing parentheses
            colunas_comuns = set(dataframes[0].columns)
            for df in dataframes[1:]:
                colunas_comuns = colunas_comuns.intersection(set(df.columns))
            print(f"Total de colunas comuns a todos os arquivos: {len(colunas_comuns)}")
            print(f"Colunas comuns: {', '.join(sorted(list(colunas_comuns))[:10])}...")
        
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
