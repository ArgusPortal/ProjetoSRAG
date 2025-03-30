#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processamento completo dos dados SRAG Hospitalizado conforme o dicionário de dados (19/09/2022).

Este script integra:
  - Carregamento dos dados (suporta DBF, CSV e Excel)
  - Limpeza e padronização dos dados
  - Mapeamento de campos categóricos conforme o dicionário
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
    # Dicionário de mapeamento atualizado conforme DICIONARIO.txt oficial (19/09/2022)
    categorias = {
        # Dados de Identificação e Notificação
        "NU_NOTIFIC": {},   # Número do registro (numérico/alfanumérico – não mapeamos)
        "DT_NOTIFIC": {},   # Data de notificação (será convertida)
        "SEM_NOT": {},      # Semana epidemiológica calculada (interno)
        "DT_SIN_PRI": {},   # Data dos primeiros sintomas (será convertida)
        "SEM_PRI": {},      # Semana epidemiológica dos sintomas (interno)
        "SG_UF_NOT": {},    # UF de notificação (tabela IBGE)
        "ID_REGIONA": {},   # Região de saúde de notificação (tabela IBGE)
        "CO_REGIONA": {},   # Código da região de notificação (tabela IBGE)
        "ID_MUNICIP": {},   # Município de notificação (tabela IBGE)
        "CO_MUN_NOT": {},   # Código do município de notificação (tabela IBGE)
        "ID_UNIDADE": {},   # Unidade de saúde (tabela CNES)

        # Dados do Paciente 
        "TEM_CPF": {'1': "Sim", '2': "Não"},
        "ESTRANG": {'1': "Sim", '2': "Não"},
        "CS_SEXO": {'1': "Masculino", '2': "Feminino", '9': "Ignorado"},
        "DT_NASC": {},      # Data de nascimento (será convertida)
        "NU_IDADE_N": {},   # Idade informada (numérica)
        "TP_IDADE": {'1': "Dia", '2': "Mês", '3': "Ano"},
        # COD_IDADE não foi encontrado no dicionário
        "CS_GESTANT": {'1': "1º Trimestre", '2': "2º Trimestre", '3': "3º Trimestre",
                       '4': "Idade Gestacional Ignorada", '5': "Não", '6': "Não se aplica", '9': "Ignorado"},
        "CS_RACA": {'1': "Branca", '2': "Preta", '3': "Amarela", '4': "Parda", '5': "Indígena", '9': "Ignorado"},
        "CS_ESCOL_N": {'0': "Sem escolaridade/Analfabeto",
                       '1': "Fundamental 1º ciclo (1ª a 5ª série)",
                       '2': "Fundamental 2º ciclo (6ª a 9ª série)",
                       '3': "Médio (1º ao 3º ano)",
                       '4': "Superior",
                       '5': "Não se aplica",
                       '9': "Ignorado"},
        "ID_PAIS": {},      # País de residência (tabela de países)
        "SG_UF": {},        # UF de residência (tabela IBGE)
        "ID_RG_RESI": {},   # Região de saúde de residência (tabela IBGE)
        "CO_RG_RESI": {},   # Código região de residência (tabela IBGE)
        "ID_MN_RESI": {},   # Município de residência (tabela IBGE)
        # SURTO_SG não foi encontrado no dicionário

        # Dados de Notificação Adicionais e de Contato
        "NOSOCOMIAL": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # Caso nosocomial (infecção hospitalar)
        "AVE_SUINO": {'1': "Sim", '2': "Não", '9': "Ignorado"},   # Contato com aves ou suínos
        "OUT_ANIM": {},     # Descrição de outro animal (se aplicável)

        # Sinais e Sintomas (todos usam o mesmo mapeamento)
        "FEBRE": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "TOSSE": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "GARGANTA": {'1': "Sim", '2': "Não", '9': "Ignorado"},    # Dor de garganta
        "DISPNEIA": {'1': "Sim", '2': "Não", '9': "Ignorado"},    # Dificuldade para respirar
        "DESC_RESP": {'1': "Sim", '2': "Não", '9': "Ignorado"},   # Desconforto respiratório
        "SATURACAO": {'1': "Sim", '2': "Não", '9': "Ignorado"},   # Saturação O2 < 95%
        "DIARREIA": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "VOMITO": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "DOR_ABD": {'1': "Sim", '2': "Não", '9': "Ignorado"},     # Dor abdominal
        "FADIGA": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "PERD_OLFT": {'1': "Sim", '2': "Não", '9': "Ignorado"},   # Perda do olfato
        "PERD_PALA": {'1': "Sim", '2': "Não", '9': "Ignorado"},   # Perda do paladar
        "OUTRO_SIN": {'1': "Sim", '2': "Não", '9': "Ignorado"},   # Outros sintomas
        "OUTRO_DES": {},    # Descrição de outros sintomas

        # Fatores de Risco (todos usam o mesmo mapeamento)
        "FATOR_RISC": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # Tem fator de risco
        "PUERPERA": {'1': "Sim", '2': "Não", '9': "Ignorado"},    # Puérpera (até 45 dias após parto)
        "CARDIOPATI": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # Doença cardiovascular crônica
        "HEMATOLOGI": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # Doença hematológica crônica
        "SIND_DOWN": {'1': "Sim", '2': "Não", '9': "Ignorado"},   # Síndrome de Down
        "HEPATICA": {'1': "Sim", '2': "Não", '9': "Ignorado"},    # Doença hepática crônica
        "ASMA": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "DIABETES": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "NEUROLOGIC": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # Doença neurológica crônica
        "PNEUMOPATI": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # Pneumopatia crônica
        "IMUNODEPRE": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # Imunodeficiência/Imunodepressão
        "RENAL": {'1': "Sim", '2': "Não", '9': "Ignorado"},       # Doença renal crônica
        "OBESIDADE": {'1': "Sim", '2': "Não", '9': "Ignorado"},
        "OBES_IMC": {},     # Valor do IMC (numérico)
        "OUT_MORBI": {'1': "Sim", '2': "Não", '9': "Ignorado"},   # Outros fatores de risco
        "MORB_DESC": {},    # Descrição de outros fatores de risco

        # Vacinação contra Gripe e COVID-19
        "VACINA": {'1': "Sim", '2': "Não", '9': "Ignorado"},      # Recebeu vacina contra gripe
        "DT_UT_DOSE": {},   # Data da última dose de vacina (será convertida)
        "VACINA_COV": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # Recebeu vacina COVID-19
        "DOSE_1_COV": {},   # Data da 1ª dose COVID-19 (será convertida)
        "DOSE_2_COV": {},   # Data da 2ª dose COVID-19 (será convertida)
        "DOSE_REF": {},     # Data da dose reforço COVID-19 (será convertida)
        "FAB_COV_1": {},    # Fabricante da 1ª dose COVID-19
        "FAB_COV_2": {},    # Fabricante da 2ª dose COVID-19
        "FAB_COVREF": {},   # Fabricante da dose reforço COVID-19
        "LAB_PR_COV": {},   # Lab.produtor da vacina - não há mapeamento no dicionário

        # Tratamento - Antiviral
        "ANTIVIRAL": {'1': "Sim", '2': "Não", '9': "Ignorado"},   # Usou antiviral para gripe
        "TP_ANTIVIR": {'1': "Oseltamivir", '2': "Zanamivir", '3': "Outro"},

        # Internação e UTI
        "DT_INTERNA": {},   # Data da internação (será convertida)
        "SG_UF_INTE": {},   # UF de internação (tabela IBGE)
        "ID_RG_INTE": {},   # Região de saúde de internação (tabela IBGE)
        "CO_RG_INTE": {},   # Código da região de internação (tabela IBGE)
        "ID_MN_INTE": {},   # Município de internação (tabela IBGE)
        "CO_MU_INTE": {},   # Código do município de internação (tabela IBGE)
        "UTI": {'1': "Sim", '2': "Não", '9': "Ignorado"},         # Internado em UTI
        "DT_ENTUTI": {},    # Data de entrada na UTI (será convertida)
        "DT_SAIDUTI": {},   # Data de saída da UTI (será convertida)
        "SUPORT_VEN": {'1': "Sim, invasivo", '2': "Sim, não invasivo", '3': "Não", '9': "Ignorado"},

        # Exames radiológicos
        "RAIOX_RES": {'1': "Normal", '2': "Infiltrado intersticial", '3': "Consolidação",
                      '4': "Misto", '5': "Outro", '6': "Não realizado", '9': "Ignorado"},
        "RAIOX_OUT": {},    # Descrição de outro resultado de RX
        "DT_RAIOX": {},     # Data do RX (será convertida)
        "TOMO_RES": {'1': "Típico COVID-19", '2': "Indeterminado COVID-19",
                     '3': "Atípico COVID-19", '4': "Negativo para Pneumonia",
                     '5': "Outro", '6': "Não realizado", '9': "Ignorado"},
        "TOMO_OUT": {},     # Descrição de outro resultado de tomografia
        "DT_TOMO": {},      # Data da tomografia (será convertida)

        # Teste Diagnóstico - Amostra e Coleta
        "AMOSTRA": {'1': "Sim", '2': "Não", '9': "Ignorado"},     # Coletou amostra
        "DT_COLETA": {},    # Data da coleta (será convertida)
        "TP_AMOSTRA": {'1': "Secreção de Nasoorofaringe",
                       '2': "Lavado Broco-alveolar",
                       '3': "Tecido post-mortem",
                       '4': "Outra, qual?",
                       '5': "LCR",
                       '9': "Ignorado"},
        "OUT_AMOST": {},    # Descrição de outro tipo de amostra

        # Teste Antigênico
        "TP_TES_AN": {'1': "Imunofluorescência (IF)", '2': "Teste rápido antigênico"},
        "DT_RES_AN": {},    # Data do resultado do teste antigênico (será convertida)
        "RES_AN": {'1': "Positivo", '2': "Negativo", '3': "Inconclusivo", 
                   '4': "Não realizado", '5': "Aguardando resultado", '9': "Ignorado"},
        "POS_AN_FLU": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # Positivo para Influenza
        "TP_FLU_AN": {'1': "Influenza A", '2': "Influenza B"},    # Tipo de Influenza
        "POS_AN_OUT": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # Positivo para outros vírus
        "DS_AN_OUT": {},    # Descrição de outro vírus no teste antigênico

        # Teste molecular (RT-PCR)
        "PCR_RESUL": {'1': "Detectável", '2': "Não Detectável", '3': "Inconclusivo", 
                     '4': "Não realizado", '5': "Aguardando Resultado", '9': "Ignorado"},
        "DT_PCR": {},       # Data do resultado do PCR (será convertida)
        "POS_PCRFLU": {'1': "Sim", '2': "Não", '9': "Ignorado"},  # PCR positivo para Influenza
        "TP_FLU_PCR": {'1': "Influenza A", '2': "Influenza B"},   # Tipo de Influenza por PCR
        "PCR_FLUASU": {'1': "Influenza A(H1N1)pdm09", 
                      '2': "Influenza A (H3N2)", 
                      '3': "Influenza A não subtipado",
                      '4': "Influenza A não subtipável",
                      '5': "Inconclusivo",
                      '6': "Outro, especifique"},
        "FLUASU_OUT": {},   # Descrição de outro subtipo de Influenza A

        # Resultados virais - campos checkbox
        "AN_SARS2": {'1': "Sim"},  # SARS-CoV-2 por teste antigênico
        "AN_VSR": {'1': "Sim"},    # VSR por teste antigênico

        # Conclusão e evolução do caso
        "CLASSI_FIN": {'1': "SRAG por influenza", 
                      '2': "SRAG por outro vírus respiratório", 
                      '3': "SRAG por outro agente etiológico", 
                      '4': "SRAG não especificado", 
                      '5': "SRAG por covid-19"},
        "CLASSI_OUT": {},   # Descrição de outro agente etiológico
        "CRITERIO": {'1': "Laboratorial", 
                    '2': "Clínico Epidemiológico", 
                    '3': "Clínico", 
                    '4': "Clínico Imagem"},
        "EVOLUCAO": {'1': "Cura", '2': "Óbito", '3': "Óbito por outras causas", '9': "Ignorado"},
        "DT_EVOLUCA": {},   # Data da evolução (será convertida) 
        "DT_ENCERRA": {},   # Data do encerramento (será convertida)
        "DT_DIGITA": {},    # Data da digitação (será convertida)
        "PAC_DSCBO": {},    # Ocupação do paciente (CBO)
    }
    
    # Construir lista de valores textuais mapeados para todas as categorias 
    todos_valores_texto = set()
    for campo, mapa in categorias.items():
        if mapa:  # Se há um mapeamento para este campo
            todos_valores_texto.update([str(v).upper() for v in mapa.values()])
    
    # Lista para fins de diagnóstico
    campos_ja_mapeados = []
    campos_mapeados_agora = []
    campos_nao_mapeados = []
    
    # Processar cada campo categórico
    for campo, mapa in categorias.items():
        if campo in df.columns and mapa:
            try:
                # CORREÇÃO: Converter para tipo objeto primeiro para evitar problemas de tipo
                df[campo] = df[campo].astype(object)
                
                # Obter valores únicos (não nulos) como strings normalizadas
                valores_unicos = df[campo].dropna().astype(str).str.strip().str.upper().unique()
                
                # Verificar se já contém valores textuais mapeados
                valores_texto = [v for v in valores_unicos if v in todos_valores_texto]
                valores_originais = [v for v in valores_unicos if v not in todos_valores_texto]
                
                # Pular se já totalmente mapeado
                if valores_texto and not valores_originais:
                    campos_ja_mapeados.append(campo)
                    print(f"Campo {campo} já contém valores mapeados: {', '.join(valores_texto[:3])}...")
                    continue
                
                # Mapear códigos para descrições
                print(f"Mapeando campo {campo}...")
                mapeados = 0
                
                for codigo, descricao in mapa.items():
                    try:
                        # Criar máscaras para códigos exatos e decimais
                        mascara = (
                            df[campo].astype(str).str.strip() == str(codigo).strip()
                        ) | (
                            df[campo].apply(
                                lambda x: str(x).replace('.0', '') == str(codigo).strip() 
                                if pd.notnull(x) else False
                            )
                        )
                        
                        if mascara.any():
                            df.loc[mascara, campo] = descricao
                            mapeados += mascara.sum()
                            
                    except Exception as e:
                        print(f"   Erro no código {codigo} ({campo}): {str(e)}")
                
                # Registrar resultados
                if mapeados > 0:
                    campos_mapeados_agora.append(f"{campo} ({mapeados})")
                else:
                    campos_nao_mapeados.append(campo)
                    
            except Exception as e:
                print(f"ERRO processando {campo}: {str(e)}")
    
    print("\nResumo do mapeamento de categorias:")
    print(f"Campos já mapeados (pulados): {len(campos_ja_mapeados)}")
    if campos_ja_mapeados:
        print(f"  {', '.join(campos_ja_mapeados[:10])}{'...' if len(campos_ja_mapeados) > 10 else ''}")
    
    print(f"Campos mapeados neste processamento: {len(campos_mapeados_agora)}")
    if campos_mapeados_agora:
        print(f"  {', '.join(campos_mapeados_agora[:10])}{'...' if len(campos_mapeados_agora) > 10 else ''}")
    
    print(f"Campos que não precisaram mapeamento: {len(campos_nao_mapeados)}")
    
    # Tratamento especial para campos checkbox
    campos_checkbox = ['AN_SARS2', 'AN_VSR', 'AN_PARA1', 'AN_PARA2', 'AN_PARA3', 'AN_ADENO', 'AN_OUTRO', 
                       'PCR_SARS2', 'PCR_VSR', 'PCR_PARA1', 'PCR_PARA2', 'PCR_PARA3', 'PCR_PARA4', 
                       'PCR_ADENO', 'PCR_METAP', 'PCR_BOCA', 'PCR_RINO', 'PCR_OUTRO']
    
    # Processar os checkboxes
    campos_checkbox_ja_mapeados = []
    campos_checkbox_mapeados = []
    
    for campo in campos_checkbox:
        if campo in df.columns:
            try:
                # Converter para objeto primeiro
                df[campo] = df[campo].astype(object)
                
                # Verificar se já tem "SIM" ou "NÃO"
                valores = set(df[campo].dropna().astype(str).str.upper().unique())
                if "SIM" in valores or "NÃO" in valores:
                    campos_checkbox_ja_mapeados.append(campo)
                    print(f"Campo checkbox {campo} já contém valores mapeados")
                    continue
                
                # Mapear valores 1/1.0 para "Sim" e outros para "Não"
                print(f"Mapeando campo checkbox {campo}...")
                
                # Criar máscara simplificada para valores que representam "1"
                mascara_sim = df[campo].apply(
                    lambda x: str(x).strip() == '1' or str(x).strip() == '1.0' 
                    if pd.notnull(x) else False
                )
                
                # Aplicar mapeamento usando loc
                if mascara_sim.any():
                    df.loc[mascara_sim, campo] = "Sim"
                    df.loc[~mascara_sim & df[campo].notna(), campo] = "Não"
                    campos_checkbox_mapeados.append(campo)
                
            except Exception as e:
                print(f"ERRO ao processar campo checkbox {campo}: {e}")
    
    print(f"\nCampos checkbox já mapeados: {len(campos_checkbox_ja_mapeados)}")
    print(f"Campos checkbox mapeados neste processamento: {len(campos_checkbox_mapeados)}")
    if campos_checkbox_mapeados:
        print(f"  {', '.join(campos_checkbox_mapeados)}")
    
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
        
        # Contar valores únicos em algumas colunas categóricas importantes 
        colunas_categoricas = [
            'CS_SEXO', 'CS_GESTANT', 'CS_RACA', 'EVOLUCAO', 
            'CLASSI_FIN', 'CRITERIO'
        ]
        colunas_categoricas = [col for col in colunas_categoricas if col in df_processado.columns]
        
        if colunas_categoricas:
            print("\nDistribuição de algumas categorias importantes:")
            for col in colunas_categoricas:  # Remover o limite de 5 colunas
                print(f"\n{col}:")
                contagem = df_processado[col].value_counts(dropna=False).head(10)
                for valor, qtd in contagem.items():
                    print(f"  {valor}: {qtd}")

