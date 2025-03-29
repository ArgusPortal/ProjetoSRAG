#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processamento completo dos dados SRAG Hospitalizado conforme o dicionário de dados (19/09/2022).

Este script integra:
  - Carregamento dos dados (suporta DBF, CSV e Excel)
  - Limpeza e padronização dos dados
  - Mapeamento de campos categóricos (criação de colunas _desc) conforme o dicionário
  - Conversão de campos de data e criação de campos calculados derivados
  - Exportação dos dados tratados para arquivo CSV
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Função para carregar os dados (DBF, CSV ou Excel)
def carregar_dados(caminho_arquivo, encoding='latin1', sep=';', chunksize=None):
    if caminho_arquivo.lower().endswith('.dbf'):
        try:
            from dbfread import DBF
            tabela = DBF(caminho_arquivo, encoding=encoding)
            df = pd.DataFrame(iter(tabela))
        except ImportError:
            print("Instale a biblioteca dbfread: pip install dbfread")
            return None
    elif caminho_arquivo.lower().endswith(('.csv', '.csv.gz', '.csv.zip', '.csv.bz2')):
        # Otimizações avançadas para CSV
        print(f"Iniciando carregamento do arquivo CSV: {caminho_arquivo}")
        compression = 'infer'  # Detecta automaticamente se o arquivo está comprimido
        
        # Configurações padrão para CSV
        csv_opts = {
            'filepath_or_buffer': caminho_arquivo,
            'encoding': encoding,
            'sep': sep,
            'low_memory': False,
            'compression': compression,
            'on_bad_lines': 'warn'  # Não interrompe o processamento por linhas problemáticas
        }
        
        try:
            # Para arquivos grandes, usar leitura em chunks e/ou pyarrow
            if chunksize:
                print(f"Carregando arquivo CSV em partes de {chunksize} linhas...")
                csv_opts['chunksize'] = chunksize
                return pd.read_csv(**csv_opts)
            else:
                # Verificar se pyarrow está disponível para melhor desempenho
                try:
                    import pyarrow
                    csv_opts['dtype_backend'] = 'pyarrow'
                    print("Usando pyarrow para otimização de memória e desempenho")
                except ImportError:
                    print("PyArrow não disponível. Para melhor desempenho, instale: pip install pyarrow")
                
                df = pd.read_csv(**csv_opts)
                print(f"Arquivo CSV carregado com {len(df)} linhas e {len(df.columns)} colunas")
        except Exception as e:
            print(f"Erro ao carregar CSV com configuração padrão: {e}")
            print("Tentando configurações alternativas...")
            
            # Tentativa 1: Mudar encoding para UTF-8
            try:
                csv_opts['encoding'] = 'utf-8'
                df = pd.read_csv(**csv_opts)
                print("Sucesso usando encoding UTF-8")
            except Exception:
                # Tentativa 2: Testar com vírgula como separador
                try:
                    csv_opts['encoding'] = encoding  # Voltar ao encoding original
                    csv_opts['sep'] = ','
                    df = pd.read_csv(**csv_opts)
                    print("Sucesso usando vírgula como separador")
                except Exception:
                    # Tentativa 3: Usar configurações mais permissivas
                    try:
                        csv_opts['sep'] = None  # Auto-detecção de separador
                        csv_opts['engine'] = 'python'  # Engine mais flexível
                        csv_opts['on_bad_lines'] = 'skip'  # Pular linhas problemáticas
                        df = pd.read_csv(**csv_opts)
                        print("Sucesso usando configurações flexíveis e auto-detecção")
                    except Exception as final_e:
                        print(f"Todas as tentativas falharam. Erro final: {final_e}")
                        return None
    elif caminho_arquivo.lower().endswith(('.xlsx','.xls')):
        df = pd.read_excel(caminho_arquivo)
    else:
        print("Formato não suportado. Utilize DBF, CSV ou Excel.")
        return None

    print(f"Dados carregados com sucesso! Total de registros: {len(df)}")
    return df

# Função para limpar os dados (remoção de duplicatas e padronização de textos)
def limpar_dados(df):
    df_limpo = df.drop_duplicates()
    print(f"Duplicatas removidas: {len(df) - len(df_limpo)}")
    # Converter todas as colunas de texto para maiúsculas e sem espaços
    for col in df_limpo.select_dtypes(include=['object']).columns:
        try:
            df_limpo[col] = df_limpo[col].astype(str).str.strip().str.upper()
        except Exception as e:
            print(f"Erro ao tratar coluna {col}: {e}")
    return df_limpo

# Example fix for column name mismatches
def standardize_column_names(df):
    rename_map = {
        'FAB_COV_1': 'FAB_COV1',
        'FAB_COV_2': 'FAB_COV2',
        'FAB_COVREF': 'FAB_COVRF'
    }
    # Only rename columns that exist
    cols_to_rename = {k: v for k, v in rename_map.items() if k in df.columns}
    if cols_to_rename:
        df = df.rename(columns=cols_to_rename)
        print(f"Renamed columns: {list(cols_to_rename.keys())}")
    return df

# Função para aplicar mapeamentos categóricos conforme o dicionário de dados
def aplicar_categorias_completo(df):
    # Dicionário de mapeamento – estenda conforme necessário
    categorias = {
        # Dados de Identificação e Notificação
        "NU_NOTIFIC": {},   # Número do registro (numérico/alfanumérico – não mapeamos)
        "DT_NOTIFIC": {},   # Data de notificação (já presente e será convertida)
        "SEM_NOT": {},      # Semana epidemiológica calculada (interno)
        "DT_SIN_PRI": {},
        "SEM_PRI": {},
        "SG_UF_NOT": {},

        # Dados do Paciente 
        "TEM_CPF": {'1': "Sim", '2': "Não"},
        "ESTRANG": {'1': "Sim", '2': "Não"},
        "NU_CPF": {},       # CPF – não necessita mapeamento
        "NU_CNS": {},       # CNS
        "NM_PACIENT": {},
        "CS_SEXO": {'1': "Masculino", '2': "Feminino", '9': "Ignorado"},
        "DT_NASC": {},
        "NU_IDADE_N": {},   # Idade informada (numérica)
        "TP_IDADE": {'1': "Dia", '2': "Mês", '3': "Ano"},
        "CS_GESTANT": {'1': "1º Trimestre", '2': "2º Trimestre", '3': "3º Trimestre",
                       '4': "Idade Gestacional Ignorada", '5': "Não", '6': "Não se aplica", '9': "Ignorado"},
        "CS_RACA": {'1': "Branca", '2': "Preta", '3': "Amarela", '4': "Parda", '5': "Indígena", '9': "Ignorado"},
        "CS_ETINIA": {},
        "POV_CT": {'1': "Sim", '2': "Não"},
        "TP_POV_CT": {},
        "CS_ESCOL_N": {'0': "Sem escolaridade/Analfabeto",
                       '1': "Fundamental 1º ciclo (1ª a 5ª série)",
                       '2': "Fundamental 2º ciclo (6ª a 9ª série)",
                       '3': "Médio (1º ao 3º ano)",
                       '4': "Superior",
                       '5': "Não se aplica",
                       '9': "Ignorado"},
        "PAC_COCBO": {},
        "NM_MAE_PAC": {},
        "NU_CEP": {},
        "SG_UF": {},
        "ID_MN_RESI": {},  # Município de residência
        "NM_BAIRRO": {},
        "NM_LOGRADO": {},
        "NU_NUMERO": {},
        "NM_COMPLEM": {},
        "NU_DDD_TEL": {},
        "NU_TELEFON": {},
        "CS_ZONA": {'1': "Urbana", '2': "Rural", '3': "Periurbana", '9': "Ignorado"},
        "ID_PAIS": {},

        # Dados de Notificação Adicionais e de Contato
        "NOSOCOMIAL": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "AVE_SUINO": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "OUT_ANIM": {},

        # Sinais e Sintomas
        "FEBRE": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "TOSSE": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "GARGANTA": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "DISPNEIA": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "DESC_RESP": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "SATURACAO": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "DIARREIA": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "VOMITO": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "DOR_ABD": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "FADIGA": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "PERD_OLFT": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "PERD_PALA": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "OUTRO_SIN": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "OUTRO_DES": {},

        # Fatores de Risco
        "FATOR_RISC": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "PUERPERA": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "CARDIOPATI": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "HEMATOLOGI": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "SIND_DOWN": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "HEPATICA": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "ASMA": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "DIABETES": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "NEUROLOGIC": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "PNEUMOPATI": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "IMUNODEPRE": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "RENAL": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "OBESIDADE": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "OBES_IMC": {},

        # Vacinação e tratamento (COVID-19 e gripe)
        "VACINA_COV": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "DOSE_1_COV": {},
        "DOSE_2_COV": {},
        "DOSE_REF": {},
        "FAB_COV1": {},
        "FAB_COV2": {},
        "FAB_COVRF": {},
        "FAB_COVRF2": {},
        "ANTIVIRAL": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "TP_ANTIVIR": {'1': "Oseltamivir", '2': "Zanamivir", '3': "Outro"},
        "TRAT_COV": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "TIPO_TRAT": {'1': "Nirmatrevir/ritonavir (Paxlovid)",
                      '2': "Molnupiravir (Lagevrio)",
                      '3': "Baricitinibe (Olumiant)",
                      '4': "Outro, especifique"},
        
        # Internação, UTI e exames radiológicos
        "HOSPITAL": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "DT_INTERNA": {},
        "SG_UF_INTE": {},
        "ID_RG_INTE": {},
        "ID_MN_INTE": {},
        "ID_UN_INTE": {},
        "UTI": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "DT_ENTUTI": {},
        "DT_SAIDUTI": {},
        "SUPORT_VEN": {'1': "Sim, invasivo", '2': "Sim, não invasivo", '3': "Não", '9': "Ignorado"},
        "RAIOX_RES": {'1': "Normal", '2': "Infiltrado intersticial", '3': "Consolidação",
                      '4': "Misto", '5': "Outro", '6': "Não realizado", '9': "Ignorado"},
        "RAIOX_OUT": {},
        "DT_RAIOX": {},
        "TOMO_RES": {'1': "Típico COVID-19", '2': "Indeterminado COVID-19",
                     '3': "Atípico COVID-19", '4': "Negativo para Pneumonia",
                     '5': "Outro", '6': "Não realizado", '9': "Ignorado"},
        "TOMO_OUT": {},
        "DT_TOMO": {},
        
        # Teste Diagnóstico – Amostra, Teste Antigênico, RT-PCR e Sorologia
        "AMOSTRA": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "DT_COLETA": {},
        "TP_AMOSTRA": {'1': "Secreção de Nasoorofaringe",
                       '2': "Lavado Broco-alveolar",
                       '3': "Tecido post-mortem",
                       '4': "Outra, qual?",
                       '5': "LCR",
                       '9': "Ignorado"},
        "OUT_AMOST": {},
        "REQUI_GAL": {},
        "TP_TES_AN": {'1': "Imunofluorescência (IF)", '2': "Teste rápido antigênico"},
        "DT_RES_AN": {},
        "RES_AN": {'1': "Positivo", '2': "Negativo", '3': "Inconclusivo", '4': "Não realizado", '5': "Aguardando resultado", '9': "Ignorado"},
        "LAB_AN": {},
        "CO_LAB_AN": {},
        "POS_AN_FLU": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "TP_FLU_AN": {'1': "Influenza A", '2': "Influenza B"},
        "PCR_RESUL": {'1': "Detectável", '2': "Não Detectável", '3': "Inconclusivo", '4': "Não realizado", '5': "Aguardando Resultado", '9': "Ignorado"},
        "POS_PCRFLU": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "TP_FLU_PCR": {'1': "Influenza A", '2': "Influenza B"},
        "DT_PCR": {},
        "TP_AM_SOR": {'1': "Teste rápido", '2': "Elisa", '3': "Quimiluminescência", '4': "Outro, especifique"},
        "SOR_OUT": {},
        "DT_CO_SOR": {},
        "RES_IGG": {'1': "Positivo", '2': "Negativo"},
        "RES_IGM": {'1': "Positivo", '2': "Negativo"},
        "RES_IGA": {'1': "Positivo", '2': "Negativo"},
        "DT_RES": {},
        
        # Conclusão: Classificação, Critério, Evolução, Datas e Observações
        "CLASSI_FIN": {'1': "SRAG por influenza", '2': "SRAG por outro vírus respiratório", '3': "SRAG por outro agente etiológico", '4': "SRAG não especificado", '5': "SRAG por covid-19"},
        "CLASSI_OUT": {},
        "CRITERIO": {'1': "Laboratorial", '2': "Clínico Epidemiológico", '3': "Clínico", '4': "Clínico Imagem"},
        "EVOLUCAO": {'1': "Cura", '2': "Óbito", '3': "Óbito por outras causas", '9': "Ignorado"},
        "DT_EVOLUCA": {},
        "DT_ENCERRA": {},
        "NU_DO": {},
        "OBSERVA": {},
        "NOME_PROF": {},
        "REG_PROF": {},
        "DT_DIGITA": {}
    }
    
    # Para cada campo que possui mapeamento, cria uma nova coluna com sufixo _desc
    for campo, mapa in categorias.items():
        if campo in df.columns and mapa:
            df[campo + '_desc'] = df[campo].astype(str).str.strip().map(mapa)
            print(f"Mapeamento aplicado para campo: {campo}")
    return df

# Função para converter campos de data e criar campos calculados
def criar_campos_calculados(df):
    # Lista de campos de data – acrescente ou remova conforme sua base
    campos_data = [
        'DT_NOTIFIC', 'DT_SIN_PRI', 'DT_NASC', 'DT_INTERNA', 'DT_ENTUTI',
        'DT_SAIDUTI', 'DT_EVOLUCA', 'DT_ENCERRA', 'DOSE_1_COV', 'DOSE_2_COV',
        'DOSE_REF', 'DT_RAIOX', 'DT_TOMO', 'DT_COLETA', 'DT_RES_AN',
        'DT_PCR', 'DT_CO_SOR', 'DT_RES', 'DT_DIGITA'
    ]
    for campo in campos_data:
        if campo in df.columns:
            try:
                df[campo] = pd.to_datetime(df[campo], errors='coerce', dayfirst=True)
                print(f"Campo convertido para data: {campo}")
            except Exception as e:
                print(f"Erro convertendo campo {campo}: {e}")
    
    # Exemplo: calcular idade em anos usando DT_NASC e DT_SIN_PRI
    if 'DT_NASC' in df.columns and 'DT_SIN_PRI' in df.columns:
        try:
            df['IDADE_ANOS'] = (df['DT_SIN_PRI'] - df['DT_NASC']).dt.days / 365.25
            df['IDADE_ANOS'] = df['IDADE_ANOS'].round(1)
            print("Campo calculado: IDADE_ANOS")
        except Exception as e:
            print(f"Erro ao calcular idade: {e}")
    
    # Exemplo: tempo de internação (dias) usando DT_INTERNA e DT_EVOLUCA
    if 'DT_INTERNA' in df.columns and 'DT_EVOLUCA' in df.columns:
        try:
            df['TEMPO_INTERNACAO'] = (df['DT_EVOLUCA'] - df['DT_INTERNA']).dt.days
            print("Campo calculado: TEMPO_INTERNACAO")
        except Exception as e:
            print(f"Erro ao calcular tempo de internação: {e}")
    
    # Exemplo: tempo de UTI usando DT_ENTUTI e DT_SAIDUTI
    if 'DT_ENTUTI' in df.columns and 'DT_SAIDUTI' in df.columns:
        try:
            df['TEMPO_UTI'] = (df['DT_SAIDUTI'] - df['DT_ENTUTI']).dt.days
            print("Campo calculado: TEMPO_UTI")
        except Exception as e:
            print(f"Erro ao calcular tempo de UTI: {e}")
            
    return df

# Função para exportar os dados tratados para CSV (separador ; e codificação UTF-8-SIG)
def exportar_dados(df, nome_arquivo="dados_srag_tratados.csv"):
    try:
        df.to_csv(nome_arquivo, index=False, encoding='utf-8-sig', sep=';')
        print(f"Dados exportados com sucesso para {nome_arquivo}")
        return True
    except Exception as e:
        print("Erro ao exportar dados:", e)
        return False

# Função principal que orquestra o processamento completo
def processar_dados_srag(caminho_arquivo, arquivo_saida="dados_srag_tratados.csv"):
    print("Iniciando o processamento dos dados SRAG Hospitalizado...")
    df = carregar_dados(caminho_arquivo)
    if df is None:
        print("Erro ao carregar os dados.")
        return None

    df = limpar_dados(df)
    df = standardize_column_names(df)
    df = aplicar_categorias_completo(df)
    df = criar_campos_calculados(df)
    
    sucesso = exportar_dados(df, arquivo_saida)
    if sucesso:
        print("Processamento concluído com sucesso!")
        return df
    else:
        print("Falha na exportação dos dados.")
        return None

# Bloco principal de execução
if __name__ == "__main__":
    # Substitua pelo caminho real do seu arquivo (pode ser DBF, CSV ou Excel)
    caminho_arquivo = "caminho/para/seu/arquivo/srag.dbf"  # Exemplo: "dados/SRAG.dbf"
    df_processado = processar_dados_srag(caminho_arquivo)
    
    if df_processado is not None:
        print("\nVisualizando as primeiras linhas dos dados processados:")
        print(df_processado.head())
