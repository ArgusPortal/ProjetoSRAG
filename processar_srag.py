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

# Função para remover colunas com valores nulos
def remover_colunas_nulas(df, threshold=1.0):
    """
    Remove colunas que possuem percentual de valores nulos acima do threshold.
    
    Parâmetros:
        df (pandas.DataFrame): DataFrame a ser processado
        threshold (float): Valor entre 0 e 1 que define o percentual mínimo de valores nulos
                          para remover a coluna. Default 1.0 (100% nulos)
    
    Retorna:
        pandas.DataFrame: DataFrame sem as colunas removidas
    """
    # Calcular percentual de valores nulos em cada coluna
    percentual_nulos = df.isnull().mean()
    
    # Identificar colunas a serem removidas (acima do threshold)
    colunas_remover = percentual_nulos[percentual_nulos >= threshold].index.tolist()
    
    if colunas_remover:
        print(f"Removendo {len(colunas_remover)} colunas com {threshold*100}% ou mais de valores nulos:")
        print(f"  {', '.join(colunas_remover[:10])}" + ("..." if len(colunas_remover) > 10 else ""))
        return df.drop(columns=colunas_remover)
    else:
        print(f"Nenhuma coluna com {threshold*100}% ou mais de valores nulos encontrada.")
        return df

# Função para limpar os dados (remoção de duplicatas e padronização de textos)
def limpar_dados(df):
    df_limpo = df.drop_duplicates()
    print(f"Duplicatas removidas: {len(df) - len(df_limpo)}")
    
    # Remover colunas completamente nulas
    colunas_antes = len(df_limpo.columns)
    df_limpo = remover_colunas_nulas(df_limpo)
    print(f"Colunas removidas por conterem apenas valores nulos: {colunas_antes - len(df_limpo.columns)}")
    
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
    # Dicionário de mapeamento completo com base no dicionário SIVEP-Gripe (19/09/2022)
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
        "TP_POV_CT": {},  # Tabela de povos e comunidades tradicionais - será mapeado separadamente se disponível
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
        "OUT_MORBI": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # Outros fatores de risco
        "MORB_DESC": {},  # Descrição de outros fatores de risco

        # Vacinação contra COVID-19
        "VACINA_COV": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "DOSE_1_COV": {},  # Data da 1ª dose (será convertida)
        "DOSE_2_COV": {},  # Data da 2ª dose (será convertida)
        "DOSE_REF": {},    # Data da dose de reforço (será convertida)
        "DOSE_2REF": {},   # Data da 2ª dose de reforço
        "FAB_COV1": {},    # Fabricante da 1ª dose
        "FAB_COV2": {},    # Fabricante da 2ª dose
        "FAB_COVRF": {},   # Fabricante da dose de reforço
        "FAB_COVRF2": {},  # Fabricante da 2ª dose de reforço
        "LOTE_1_COV": {},  # Lote da 1ª dose
        "LOTE_2_COV": {},  # Lote da 2ª dose
        "LOTE_REF": {},    # Lote da dose de reforço
        "LOTE_REF2": {},   # Lote da 2ª dose de reforço
        "FNT_IN_COV": {'1': "Manual", '2': "Integração"},  # Fonte dos dados de vacinação

        # Vacinação contra Gripe
        "VACINA": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # Recebeu vacina contra gripe
        "DT_UT_DOSE": {},  # Data da última dose
        "MAE_VAC": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # Mãe vacinada (para < 6 meses)
        "DT_VAC_MAE": {},  # Data da vacinação da mãe
        "M_AMAMENTA": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # Mãe amamenta (para < 6 meses)
        "DT_DOSEUNI": {},  # Data dose única (6m-8a)
        "DT_1_DOSE": {},   # Data 1ª dose (6m-8a)
        "DT_2_DOSE": {},   # Data 2ª dose (6m-8a)

        # Tratamento - Antiviral e outros
        "ANTIVIRAL": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "TP_ANTIVIR": {'1': "Oseltamivir", '2': "Zanamivir", '3': "Outro"},
        "OUT_ANTIV": {},   # Outro antiviral (descrição)
        "DT_ANTIVIR": {},  # Data início do tratamento com antiviral
        
        # Tratamento COVID-19
        "TRAT_COV": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # Recebeu tratamento para COVID-19
        "TIPO_TRAT": {'1': "Nirmatrevir/ritonavir (Paxlovid)",
                      '2': "Molnupiravir (Lagevrio)",
                      '3': "Baricitinibe (Olumiant)",
                      '4': "Outro, especifique"},
        "OUT_TRAT": {},    # Outro tratamento COVID-19 (descrição)
        "DT_TRT_COV": {},  # Data início do tratamento COVID-19
        
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
        
        # Teste Diagnóstico – Amostras e Coleta
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
        
        # Teste Antigênico
        "TP_TES_AN": {'1': "Imunofluorescência (IF)", '2': "Teste rápido antigênico"},
        "DT_RES_AN": {},
        "RES_AN": {'1': "Positivo", '2': "Negativo", '3': "Inconclusivo", 
                  '4': "Não realizado", '5': "Aguardando resultado", '9': "Ignorado"},
        "LAB_AN": {},
        "CO_LAB_AN": {},
        
        # Resultados de Testes Antigênicos (Influenza e outros vírus)
        "POS_AN_FLU": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # Positivo para Influenza
        "TP_FLU_AN": {'1': "Influenza A", '2': "Influenza B"},
        "POS_AN_OUT": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # Positivo para outros vírus
        "AN_SARS2": {'1': "Sim"},  # SARS-CoV-2
        "AN_VSR": {'1': "Sim"},    # VSR
        "AN_PARA1": {'1': "Sim"},  # Parainfluenza 1
        "AN_PARA2": {'1': "Sim"},  # Parainfluenza 2
        "AN_PARA3": {'1': "Sim"},  # Parainfluenza 3
        "AN_ADENO": {'1': "Sim"},  # Adenovírus
        "AN_OUTRO": {'1': "Sim"},  # Outro vírus
        "DS_AN_OUT": {},           # Outro vírus (descrição)
        
        # RT-PCR / Biologia Molecular
        "PCR_RESUL": {'1': "Detectável", '2': "Não Detectável", '3': "Inconclusivo", 
                     '4': "Não realizado", '5': "Aguardando Resultado", '9': "Ignorado"},
        "DT_PCR": {},
        
        # Resultados de RT-PCR (Influenza e subtipos)
        "POS_PCRFLU": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # PCR positivo para Influenza
        "TP_FLU_PCR": {'1': "Influenza A", '2': "Influenza B"},    # Tipo de Influenza por PCR
        
        # Subtipo de Influenza A por PCR
        "PCR_FLUASU": {'1': "Influenza A(H1N1)pdm09", 
                      '2': "Influenza A (H3N2)", 
                      '3': "Influenza A não subtipado",
                      '4': "Influenza A não subtipável",
                      '5': "Inconclusivo",
                      '6': "Outro, especifique"},
        "FLUASU_OUT": {},  # Outro subtipo Influenza A (descrição)
        
        # Linhagem de Influenza B por PCR
        "PCR_FLUBLI": {'1': "Victoria", 
                      '2': "Yamagatha", 
                      '3': "Não realizado",
                      '4': "Inconclusivo",
                      '5': "Outro, especifique"},
        "FLUBLI_OUT": {},  # Outra linhagem Influenza B (descrição)
        
        # Outros vírus por PCR
        "POS_PCROUT": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # PCR positivo para outros vírus
        "PCR_SARS2": {'1': "Sim"},  # SARS-CoV-2
        "PCR_VSR": {'1': "Sim"},    # VSR
        "PCR_PARA1": {'1': "Sim"},  # Parainfluenza 1
        "PCR_PARA2": {'1': "Sim"},  # Parainfluenza 2
        "PCR_PARA3": {'1': "Sim"},  # Parainfluenza 3
        "PCR_PARA4": {'1': "Sim"},  # Parainfluenza 4
        "PCR_ADENO": {'1': "Sim"},  # Adenovírus
        "PCR_METAP": {'1': "Sim"},  # Metapneumovírus
        "PCR_BOCA": {'1': "Sim"},   # Bocavírus
        "PCR_RINO": {'1': "Sim"},   # Rinovírus
        "PCR_OUTRO": {'1': "Sim"},  # Outro vírus
        "DS_PCR_OUT": {},           # Outro vírus (descrição)
        
        # Laboratório PCR
        "LAB_PCR": {},              # Laboratório que realizou o PCR
        "CO_LAB_PCR": {},           # Código do laboratório
        
        # Sorologia para SARS-CoV-2
        "TP_AM_SOR": {'1': "Sangue/plasma/soro", '2': "Outra, qual?", '9': "Ignorado"},
        "SOR_OUT": {},              # Outra amostra sorológica (descrição)
        "DT_CO_SOR": {},            # Data da coleta sorológica
        "TP_SOR": {'1': "Teste rápido", '2': "Elisa", '3': "Quimiluminescência", '4': "Outro, qual"},
        "OUT_SOR": {},              # Outro tipo de sorologia (descrição)
        "RES_IGG": {'1': "Positivo", '2': "Negativo"},  # Resultado IgG
        "RES_IGM": {'1': "Positivo", '2': "Negativo"},  # Resultado IgM
        "RES_IGA": {'1': "Positivo", '2': "Negativo"},  # Resultado IgA
        "DT_RES": {},               # Data do resultado
        
        # Conclusão: Classificação, Critério, Evolução, Datas e Observações
        "CLASSI_FIN": {'1': "SRAG por influenza", 
                      '2': "SRAG por outro vírus respiratório", 
                      '3': "SRAG por outro agente etiológico", 
                      '4': "SRAG não especificado", 
                      '5': "SRAG por covid-19"},
        "CLASSI_OUT": {},           # Outro agente etiológico (descrição)
        "CRITERIO": {'1': "Laboratorial", 
                    '2': "Clínico Epidemiológico", 
                    '3': "Clínico", 
                    '4': "Clínico Imagem"},
        "EVOLUCAO": {'1': "Cura", '2': "Óbito", '3': "Óbito por outras causas", '9': "Ignorado"},
        "DT_EVOLUCA": {},           # Data da evolução (alta ou óbito)
        "DT_ENCERRA": {},           # Data do encerramento
        "NU_DO": {},                # Número da declaração de óbito
        "OBSERVA": {},              # Observações
        "NOME_PROF": {},            # Nome do profissional responsável
        "REG_PROF": {},             # Registro profissional
        "DT_DIGITA": {}             # Data da digitação
    }
    
    # Para cada campo que possui mapeamento, cria uma nova coluna com sufixo _desc
    for campo, mapa in categorias.items():
        if campo in df.columns and mapa:
            try:
                df[campo + '_desc'] = df[campo].astype(str).str.strip().map(mapa)
                print(f"Mapeamento aplicado para campo: {campo}")
            except Exception as e:
                print(f"ERRO ao mapear campo {campo}: {e}")
    
    # Tratamento especial para campos com '1' significando 'Sim' (marcação de checkbox)
    campos_checkbox = ['AN_SARS2', 'AN_VSR', 'AN_PARA1', 'AN_PARA2', 'AN_PARA3', 'AN_ADENO', 'AN_OUTRO', 
                     'PCR_SARS2', 'PCR_VSR', 'PCR_PARA1', 'PCR_PARA2', 'PCR_PARA3', 'PCR_PARA4', 
                     'PCR_ADENO', 'PCR_METAP', 'PCR_BOCA', 'PCR_RINO', 'PCR_OUTRO']
    
    for campo in campos_checkbox:
        if campo in df.columns:
            try:
                # Converter para string e limpar
                valores = df[campo].astype(str).str.strip()
                # Criar coluna descritiva - onde '1' ou '1.0' significa 'Sim', qualquer outro valor é 'Não'
                df[campo + '_desc'] = np.where(valores.isin(['1', '1.0']), 'Sim', 'Não')
                print(f"Mapeamento checkbox aplicado para campo: {campo}")
            except Exception as e:
                print(f"ERRO ao mapear campo checkbox {campo}: {e}")
    
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
    
    # Primeiro, converter todos os campos de data
    for campo in campos_data:
        if campo in df.columns:
            try:
                df[campo] = pd.to_datetime(df[campo], errors='coerce', dayfirst=True)
                print(f"Campo convertido para data: {campo}")
            except Exception as e:
                print(f"Erro convertendo campo {campo}: {e}")
    
    # Dicionário para armazenar temporariamente os novos campos calculados
    novos_campos = {}
    
    # Calcular idade em anos usando DT_NASC e DT_SIN_PRI
    if 'DT_NASC' in df.columns and 'DT_SIN_PRI' in df.columns:
        try:
            novos_campos['IDADE_ANOS'] = (df['DT_SIN_PRI'] - df['DT_NASC']).dt.days / 365.25
            novos_campos['IDADE_ANOS'] = novos_campos['IDADE_ANOS'].round(1)
            print("Campo calculado: IDADE_ANOS")
        except Exception as e:
            print(f"Erro ao calcular idade: {e}")
    
    # Calcular tempo de internação (dias) usando DT_INTERNA e DT_EVOLUCA
    if 'DT_INTERNA' in df.columns and 'DT_EVOLUCA' in df.columns:
        try:
            novos_campos['TEMPO_INTERNACAO'] = (df['DT_EVOLUCA'] - df['DT_INTERNA']).dt.days
            print("Campo calculado: TEMPO_INTERNACAO")
        except Exception as e:
            print(f"Erro ao calcular tempo de internação: {e}")
    
    # Calcular tempo de UTI usando DT_ENTUTI e DT_SAIDUTI
    if 'DT_ENTUTI' in df.columns and 'DT_SAIDUTI' in df.columns:
        try:
            novos_campos['TEMPO_UTI'] = (df['DT_SAIDUTI'] - df['DT_ENTUTI']).dt.days
            print("Campo calculado: TEMPO_UTI")
        except Exception as e:
            print(f"Erro ao calcular tempo de UTI: {e}")
    
    # Adicionar todos os novos campos calculados ao DataFrame de uma só vez
    if novos_campos:
        # Criar um DataFrame temporário com os novos campos
        df_novos_campos = pd.DataFrame(novos_campos, index=df.index)
        
        # Concatenar o DataFrame original com o DataFrame dos novos campos
        df = pd.concat([df, df_novos_campos], axis=1)
        print(f"Adicionados {len(novos_campos)} campos calculados de uma só vez para evitar fragmentação")
    
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
    import argparse
    import os.path
    
    # Configurar parser de argumentos para aceitar o caminho do arquivo como entrada
    parser = argparse.ArgumentParser(description='Processamento de dados SRAG.')
    parser.add_argument('--arquivo', '-a', type=str, 
                        default=r'C:\Users\argus\workspace\ProjetoSRAG\SRAG_Unificado.csv',
                        help='Caminho para o arquivo a ser processado (DBF, CSV ou Excel)')
    parser.add_argument('--saida', '-s', type=str,
                        default=r'C:\Users\argus\workspace\ProjetoSRAG\dados_srag_tratados.csv',
                        help='Caminho para o arquivo de saída (CSV)')
    
    args = parser.parse_args()
    
    # Verificar se o arquivo existe
    if not os.path.exists(args.arquivo):
        print(f"ERRO: O arquivo '{args.arquivo}' não foi encontrado.")
        print("Possíveis soluções:")
        print("1. Execute o script de unificação primeiro para criar o arquivo SRAG_Unificado.csv")
        print("2. Especifique o caminho correto usando o argumento --arquivo")
        print("   Exemplo: python processar_srag.py --arquivo caminho/para/seu/arquivo.csv")
        exit(1)
    
    print(f"Usando arquivo de entrada: {args.arquivo}")
    print(f"Arquivo de saída será: {args.saida}")
    
    # Processamento do arquivo
    df_processado = processar_dados_srag(args.arquivo, args.saida)
    
    if df_processado is not None:
        print("\nVisualizando as primeiras linhas dos dados processados:")
        print(df_processado.head())
        
        # Resumo dos dados processados
        print("\nResumo do processamento:")
        print(f"Total de registros processados: {len(df_processado)}")
        print(f"Total de colunas após processamento: {len(df_processado.columns)}")
        
        # Contar valores únicos em algumas colunas categóricas importantes com descrição
        colunas_desc = [col for col in df_processado.columns if col.endswith('_desc') and not df_processado[col].isna().all()]
        if colunas_desc:
            print("\nDistribuição de algumas categorias importantes:")
            for col in colunas_desc[:5]:  # Limitar a 5 colunas para não sobrecarregar a saída
                print(f"\n{col}:")
                contagem = df_processado[col].value_counts(dropna=False).head(10)
                for valor, qtd in contagem.items():
                    print(f"  {valor}: {qtd}")
