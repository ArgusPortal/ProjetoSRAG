#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script avançado para formatar o arquivo DICIONARIO.txt, corrigindo quebras de linha indevidas
e estruturando o conteúdo em um formato bem organizado e legível.

Este script:
1. Lê o arquivo DICIONARIO.txt original
2. Identifica e preserva seções, cabeçalhos e estruturas de tabelas
3. Reúne definições de campos que foram divididas por quebras de linha indevidas
4. Aplica formatação estruturada para melhorar a legibilidade
5. Oferece diferentes opções de formatação de saída
6. Salva o resultado em um novo arquivo formatado
"""

import os
import re
import argparse
from enum import Enum

class FormatoSaida(Enum):
    TEXTO = "texto"
    MARKDOWN = "markdown"
    ESTRUTURADO = "estruturado"

def formatar_dicionario(arquivo_entrada, arquivo_saida, formato=FormatoSaida.ESTRUTURADO):
    """
    Formata o arquivo de dicionário para corrigir quebras de linha indevidas.
    
    Args:
        arquivo_entrada: Caminho para o arquivo DICIONARIO.txt original
        arquivo_saida: Caminho para o arquivo formatado de saída
        formato: Tipo de formatação a ser aplicada na saída
    """
    print(f"Iniciando formatação do arquivo: {arquivo_entrada}")
    print(f"Formato de saída: {formato.value}")
    
    # Verificar se o arquivo existe
    if not os.path.exists(arquivo_entrada):
        print(f"ERRO: Arquivo não encontrado: {arquivo_entrada}")
        return False
    
    try:
        # Ler o conteúdo completo do arquivo
        with open(arquivo_entrada, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        print(f"Arquivo lido com sucesso. Tamanho: {len(conteudo)} bytes.")
        
        # Dividir o conteúdo em linhas para processamento
        linhas = conteudo.split('\n')
        
        # 1. Pré-processamento: Identificar cabeçalhos, seções e padrões importantes
        # Possíveis cabeçalhos de seção (letras maiúsculas, possivelmente com traços e números)
        padrao_secao = re.compile(r'^[A-ZÇÀÁÂÃÉÊÍÓÔÕÚÜ\s\-0-9]+$')
        
        # Padrão MELHORADO para identificar o início de uma definição de campo
        # Cobre mais variações de tipos e formatos
        padrao_campo = re.compile(r'^([0-9]+[\-\.].*?)\s+(Varchar2?\(\d+\)|Date|Number\(\d+\)|Número|Varchar2?|Tabela)')
        
        # Padrão adicional para campos numéricos específicos
        padrao_campo_numerico = re.compile(r'^([0-9]+[\-\.].*?)\s+(Número)')
        
        # Padrão adicional para tabelas de referência 
        padrao_campo_tabela = re.compile(r'^([0-9]+[\-\.].*?)\s+(Tabela)')
        
        # Padrão para colunas de tabelas
        padrao_tabela = re.compile(r'^[A-Z][a-zçàáâãéêíóôõúü]+\s*\(.*?\)$')
        
        # Contadores para diagnóstico
        campos_formatados = 0
        secoes_formatadas = 0
        linhas_nao_processadas = 0
        
        # 2. Processamento principal: Juntar linhas que pertencem ao mesmo campo
        linhas_processadas = []
        i = 0
        
        while i < len(linhas):
            linha_atual = linhas[i].rstrip()
            linha_processada = False
            
            # Caso 1: Linha vazia - preservar como separador
            if not linha_atual.strip():
                linhas_processadas.append('')
                i += 1
                continue
            
            # Caso 2: Linha é um cabeçalho de seção
            if padrao_secao.match(linha_atual.strip()):
                # Adicionar uma linha em branco antes do cabeçalho se não for a primeira linha
                if linhas_processadas and linhas_processadas[-1] != '':
                    linhas_processadas.append('')
                    
                linhas_processadas.append(linha_atual)
                secoes_formatadas += 1
                
                # Adicionar uma linha em branco após o cabeçalho
                linhas_processadas.append('')
                i += 1
                linha_processada = True
                continue
            
            # Caso 3: Início de definição de campo (usando padrão mais abrangente)
            match = padrao_campo.match(linha_atual)
            if not match:
                match = padrao_campo_numerico.match(linha_atual)
            if not match:
                match = padrao_campo_tabela.match(linha_atual)
                
            if match:
                nome_campo = match.group(1).strip()
                tipo_campo = match.group(2).strip()
                resto_linha = linha_atual[match.end():].strip()
                
                # Iniciar o campo formatado
                if formato == FormatoSaida.ESTRUTURADO:
                    campo_formatado = f"{nome_campo}\n    Tipo: {tipo_campo}"
                    
                    # Continuar lendo as próximas linhas até encontrar outro campo ou seção
                    descricao_campo = resto_linha
                    j = i + 1
                    
                    # Modificação: verificamos linhas até encontrar próximo campo, seção, ou linha vazia seguida de algo que parece um campo
                    while j < len(linhas):
                        linha_j = linhas[j].strip()
                        
                        # Se encontrarmos padrão de início de campo, paramos
                        if padrao_campo.match(linha_j) or padrao_campo_numerico.match(linha_j) or padrao_campo_tabela.match(linha_j):
                            break
                            
                        # Se encontrarmos padrão de seção, paramos
                        if padrao_secao.match(linha_j):
                            break
                            
                        # Se for linha vazia seguida de algo que parece um campo, paramos
                        if not linha_j and j+1 < len(linhas):
                            prox_linha = linhas[j+1].strip()
                            # Verificar se a próxima linha não-vazia parece o início de um campo
                            if re.match(r'^[0-9]+[\-\.]', prox_linha):
                                break
                        
                        # Se chegou aqui, a linha atual é parte da descrição do campo
                        if linha_j:  # Se não for linha vazia
                            descricao_campo += " " + linha_j
                        
                        j += 1
                    
                    # Adicionar a descrição formatada
                    if descricao_campo:
                        # MELHORIA: Identificar partes da descrição com mais precisão
                        # Incluir mais padrões de metadados
                        partes = re.split(r'(Descrição:|Características DBF:|Campo Obrigatório|Campo Essencial|Campo Interno|Campo Opcional)', 
                                         descricao_campo)
                        
                        # Formatar cada parte adequadamente
                        for k in range(0, len(partes), 2):
                            prefixo = partes[k-1] if k > 0 else ""
                            texto = partes[k].strip() if k < len(partes) else ""
                            
                            if prefixo:
                                campo_formatado += f"\n    {prefixo} {texto}"
                            elif texto:
                                campo_formatado += f"\n    {texto}"
                    
                    linhas_processadas.append(campo_formatado)
                    campos_formatados += 1
                    
                elif formato == FormatoSaida.MARKDOWN:
                    # Formato Markdown com cabeçalho H3 para o nome do campo
                    campo_formatado = f"### {nome_campo}\n\n**Tipo:** {tipo_campo}"
                    
                    # Processar descrição da mesma forma que acima
                    descricao_campo = resto_linha
                    j = i + 1
                    
                    while (j < len(linhas) and 
                           not padrao_campo.match(linhas[j].strip()) and 
                           not padrao_secao.match(linhas[j].strip())):
                        
                        if linhas[j].strip():
                            descricao_campo += " " + linhas[j].strip()
                        j += 1
                    
                    if descricao_campo:
                        # Formato mais simples para Markdown
                        partes = re.split(r'(Descrição:|Características DBF:|Campo Obrigatório|Campo Essencial|Campo Interno|Campo Opcional)', 
                                         descricao_campo)
                        
                        for k in range(0, len(partes), 2):
                            prefixo = partes[k-1] if k > 0 else ""
                            texto = partes[k].strip() if k < len(partes) else ""
                            
                            if prefixo:
                                campo_formatado += f"\n\n**{prefixo.strip()}** {texto}"
                            elif texto:
                                campo_formatado += f"\n\n{texto}"
                    
                    linhas_processadas.append(campo_formatado)
                    campos_formatados += 1
                    
                else:  # Formato TEXTO (simples)
                    # Juntar todas as linhas relacionadas ao campo
                    texto_completo = linha_atual
                    j = i + 1
                    
                    while (j < len(linhas) and 
                           not padrao_campo.match(linhas[j].strip()) and 
                           not padrao_campo_numerico.match(linhas[j].strip()) and
                           not padrao_campo_tabela.match(linhas[j].strip()) and
                           not padrao_secao.match(linhas[j].strip())):
                        
                        if linhas[j].strip():
                            texto_completo += " " + linhas[j].strip()
                        j += 1
                    
                    linhas_processadas.append(texto_completo)
                    campos_formatados += 1
                
                # Avançar para a próxima definição
                i = j if j > i + 1 else i + 1
                linha_processada = True
                continue
            
            # Caso 4: Outras linhas - preservar como estão
            if not linha_processada:
                linhas_processadas.append(linha_atual)
                linhas_nao_processadas += 1
                i += 1
        
        print(f"\nEstatísticas de formatação:")
        print(f"  - Campos formatados: {campos_formatados}")
        print(f"  - Seções formatadas: {secoes_formatadas}")
        print(f"  - Linhas não processadas: {linhas_nao_processadas}")
        
        # 3. Salvar o resultado formatado
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write('\n'.join(linhas_processadas))
            
        print(f"Formatação concluída. Arquivo salvo em: {arquivo_saida}")
        print(f"Linhas no arquivo original: {len(linhas)}, Linhas após formatação: {len(linhas_processadas)}")
        return True
        
    except Exception as e:
        print(f"ERRO durante a formatação: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def analisar_estrutura_dicionario(arquivo):
    """
    Analisa a estrutura do arquivo para identificar padrões comuns e estatísticas.
    
    Args:
        arquivo: Caminho para o arquivo DICIONARIO.txt
    """
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        linhas = conteudo.split('\n')
        total_linhas = len(linhas)
        
        # Estatísticas básicas
        linhas_vazias = sum(1 for linha in linhas if not linha.strip())
        
        # MELHORIA: Padrões mais abrangentes para identificar campos
        padrao_campo_principal = re.compile(r'^([0-9]+[\-\.].+?)\s+(Varchar2?\(\d+\)|Date|Number\(\d+\))')
        padrao_campo_numerico = re.compile(r'^([0-9]+[\-\.].+?)\s+(Número)')
        padrao_campo_tabela = re.compile(r'^([0-9]+[\-\.].+?)\s+(Tabela)')
        
        # Encontrar campos usando todos os padrões
        campos_tipo1 = [linha for linha in linhas if padrao_campo_principal.match(linha.strip())]
        campos_tipo2 = [linha for linha in linhas if padrao_campo_numerico.match(linha.strip())]
        campos_tipo3 = [linha for linha in linhas if padrao_campo_tabela.match(linha.strip())]
        
        total_campos = len(campos_tipo1) + len(campos_tipo2) + len(campos_tipo3)
        
        # Identificar possíveis cabeçalhos
        padrao_secao = re.compile(r'^[A-ZÇÀÁÂÃÉÊÍÓÔÕÚÜ\s\-0-9]+$')
        secoes = [linha for linha in linhas if padrao_secao.match(linha.strip()) and linha.strip()]
        
        print(f"\nAnálise da estrutura do arquivo {arquivo}:")
        print(f"Total de linhas: {total_linhas}")
        print(f"Linhas vazias: {linhas_vazias}")
        print(f"Campos identificados: {total_campos}")
        print(f"  - Com tipos padrão (Varchar, Date, Number): {len(campos_tipo1)}")
        print(f"  - Com tipo 'Número': {len(campos_tipo2)}")
        print(f"  - Com tipo 'Tabela': {len(campos_tipo3)}")
        print(f"Seções/cabeçalhos: {len(secoes)}")
        
        # NOVO: Identificar possíveis campos que não foram reconhecidos
        possivel_campo_nao_reconhecido = re.compile(r'^([0-9]+[\-\.].+)')
        todos_campos_conhecidos = set()
        for campo in campos_tipo1 + campos_tipo2 + campos_tipo3:
            match = possivel_campo_nao_reconhecido.match(campo.strip())
            if match:
                todos_campos_conhecidos.add(match.group(1).strip())
        
        campos_potenciais = []
        for i, linha in enumerate(linhas):
            match = possivel_campo_nao_reconhecido.match(linha.strip())
            if match and match.group(1).strip() not in todos_campos_conhecidos:
                # Verificar se não é um cabeçalho
                if not padrao_secao.match(linha.strip()):
                    campos_potenciais.append((i+1, linha.strip()))
        
        # Mostrar exemplos de campos
        print("\nExemplos de campos identificados:")
        for tipo, nome in [("Padrão", campos_tipo1), ("Número", campos_tipo2), ("Tabela", campos_tipo3)]:
            if nome:
                print(f"  Tipo {tipo}:")
                for i, campo in enumerate(nome[:3]):
                    print(f"    {i+1}. {campo[:100]}{'...' if len(campo) > 100 else ''}")
        
        # Mostrar exemplos de seções
        if secoes:
            print("\nExemplos de seções/cabeçalhos:")
            for i, secao in enumerate(secoes[:5]):
                print(f"  {i+1}. {secao}")
        
        # NOVO: Mostrar campos potenciais não reconhecidos
        if campos_potenciais:
            print("\nPossíveis campos não reconhecidos pelo formatador:")
            for i, (num_linha, texto) in enumerate(campos_potenciais[:10]):
                print(f"  {i+1}. Linha {num_linha}: {texto[:100]}{'...' if len(texto) > 100 else ''}")
            if len(campos_potenciais) > 10:
                print(f"  ... e mais {len(campos_potenciais) - 10} campos")
        
        # Identificar possíveis problemas
        print("\nPossíveis problemas identificados:")
        
        # Verificar linhas que parecem ser continuações de campos
        continuacoes = 0
        for i in range(1, len(linhas)):
            if (linhas[i].strip() and 
                not padrao_campo_principal.match(linhas[i].strip()) and
                not padrao_campo_numerico.match(linhas[i].strip()) and
                not padrao_campo_tabela.match(linhas[i].strip()) and
                not padrao_secao.match(linhas[i].strip()) and 
                not linhas[i-1].strip()):
                continuacoes += 1
        
        if continuacoes > 0:
            print(f"  - Aproximadamente {continuacoes} linhas parecem ser continuações de campos")
            
        # NOVO: Verificar a variação nos tipos de campos
        if linhas:
            tipos_encontrados = set()
            for linha in linhas:
                # Extrair a parte que parece ser um tipo de campo
                match = re.search(r'\s+(Varchar2?\(\d+\)|Date|Number\(\d+\)|Número|Varchar2?|Tabela|[A-Z][a-z]+)\s+', linha)
                if match:
                    tipos_encontrados.add(match.group(1))
            
            print(f"  - {len(tipos_encontrados)} tipos diferentes de campos encontrados:")
            for tipo in sorted(tipos_encontrados):
                print(f"    * {tipo}")
        
        return True
                
    except Exception as e:
        print(f"ERRO durante a análise: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Formatar arquivo DICIONARIO.txt para melhorar a legibilidade.'
    )
    parser.add_argument('--entrada', '-e', type=str, 
                        default=r'C:\Users\argus\workspace\ProjetoSRAG\DICIONARIO.txt',
                        help='Caminho para o arquivo de dicionário a ser formatado')
    parser.add_argument('--saida', '-s', type=str,
                        default=r'C:\Users\argus\workspace\ProjetoSRAG\DICIONARIO_formatado.txt',
                        help='Caminho para o arquivo de saída formatado')
    parser.add_argument('--formato', '-f', type=str, choices=['texto', 'markdown', 'estruturado'],
                        default='estruturado',
                        help='Formato de saída desejado (texto, markdown, estruturado)')
    parser.add_argument('--analisar', '-a', action='store_true',
                        help='Apenas analisar a estrutura sem formatar')
    
    args = parser.parse_args()
    
    # Verificar se o arquivo existe
    if not os.path.exists(args.entrada):
        print(f"ERRO: O arquivo '{args.entrada}' não foi encontrado.")
        exit(1)
    
    if args.analisar:
        # Modo de análise - apenas entender a estrutura
        analisar_estrutura_dicionario(args.entrada)
    else:
        # Modo de formatação - processar e salvar
        formato = FormatoSaida(args.formato)
        print(f"Processando arquivo: {args.entrada}")
        print(f"Arquivo de saída será: {args.saida}")
        formatar_dicionario(args.entrada, args.saida, formato)
