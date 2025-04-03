#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analisar um dicionário formatado e identificar seções que não foram
adequadamente processadas, comparando com o dicionário original.

Este script:
1. Carrega o arquivo original e o formatado
2. Compara os conteúdos para detectar seções problemáticas
3. Identifica e lista campos que podem não ter sido formatados corretamente
4. Realiza análise de cobertura para verificar se todos os campos foram processados
"""

import os
import re
import argparse
import difflib
from collections import defaultdict

def analisar_formatacao(arquivo_original, arquivo_formatado):
    """
    Analisa a qualidade da formatação comparando os arquivos original e formatado.
    
    Args:
        arquivo_original: Caminho para o arquivo DICIONARIO.txt original
        arquivo_formatado: Caminho para o arquivo formatado
    """
    # Verificar se os arquivos existem
    for arquivo in [arquivo_original, arquivo_formatado]:
        if not os.path.exists(arquivo):
            print(f"ERRO: Arquivo não encontrado: {arquivo}")
            return False
    
    try:
        # Ler os conteúdos dos arquivos
        with open(arquivo_original, 'r', encoding='utf-8') as f:
            conteudo_original = f.read()
        
        with open(arquivo_formatado, 'r', encoding='utf-8') as f:
            conteudo_formatado = f.read()
        
        # Dividir em linhas
        linhas_original = conteudo_original.split('\n')
        linhas_formatado = conteudo_formatado.split('\n')
        
        print(f"Análise de formatação:")
        print(f"  Original: {len(linhas_original)} linhas")
        print(f"  Formatado: {len(linhas_formatado)} linhas")
        
        # 1. Identificar todos os campos definidos no documento original
        padrao_campo = re.compile(r'^([0-9]+[\-\.].+?)\s+(Varchar2?\(\d+\)|Date|Number\(\d+\)|Número|Varchar2?|Tabela)')
        
        campos_original = []
        for i, linha in enumerate(linhas_original):
            match = padrao_campo.match(linha.strip())
            if match:
                nome_campo = match.group(1).strip()
                campos_original.append((i, nome_campo))
        
        print(f"\nCampos identificados no documento original: {len(campos_original)}")
        
        # 2. Identificar todos os campos no documento formatado
        campos_formatado = []
        for i, linha in enumerate(linhas_formatado):
            match = padrao_campo.match(linha.strip())
            if match:
                nome_campo = match.group(1).strip()
                campos_formatado.append((i, nome_campo))
        
        print(f"Campos identificados no documento formatado: {len(campos_formatado)}")
        
        # 3. Calcular cobertura de campos
        nomes_original = set(nome for _, nome in campos_original)
        nomes_formatado = set(nome for _, nome in campos_formatado)
        
        campos_em_ambos = nomes_original.intersection(nomes_formatado)
        campos_apenas_original = nomes_original - nomes_formatado
        campos_apenas_formatado = nomes_formatado - nomes_original
        
        print(f"\nCobertura de campos:")
        print(f"  Campos em ambos documentos: {len(campos_em_ambos)}")
        print(f"  Campos apenas no original: {len(campos_apenas_original)}")
        print(f"  Campos apenas no formatado: {len(campos_apenas_formatado)}")
        
        # 4. Listar os campos que estão apenas no original (não formatados)
        if campos_apenas_original:
            print("\nCampos que podem não ter sido formatados corretamente:")
            for i, nome in enumerate(sorted(campos_apenas_original)):
                if i < 20:  # Limitar a 20 exemplos
                    print(f"  {i+1}. {nome}")
                else:
                    print(f"  ... e mais {len(campos_apenas_original) - 20} campos")
                    break
        
        # 5. Analisar a estrutura do documento formatado
        estrutura_formatado = defaultdict(int)
        for linha in linhas_formatado:
            linha_limpa = linha.strip()
            if not linha_limpa:
                estrutura_formatado["Linha vazia"] += 1
            elif padrao_campo.match(linha_limpa):
                estrutura_formatado["Definição de campo"] += 1
            elif re.match(r'^[A-ZÇÀÁÂÃÉÊÍÓÔÕÚÜ\s\-0-9]+$', linha_limpa):
                estrutura_formatado["Cabeçalho/Seção"] += 1
            elif linha_limpa.startswith("    "):
                estrutura_formatado["Descrição formatada"] += 1
            else:
                estrutura_formatado["Outras linhas"] += 1
        
        print("\nEstrutura do documento formatado:")
        for tipo, contagem in estrutura_formatado.items():
            print(f"  {tipo}: {contagem} linhas")
        
        # 6. Identificar possíveis problemas de formatação
        problemas = []
        
        # 6.1 Campos que deveriam ter descrição indentada mas não têm
        for i, linha in enumerate(linhas_formatado):
            if padrao_campo.match(linha.strip()):
                # Se esta é uma definição de campo, a próxima linha não-vazia deveria ser indentada
                j = i + 1
                while j < len(linhas_formatado) and not linhas_formatado[j].strip():
                    j += 1
                
                if j < len(linhas_formatado) and not linhas_formatado[j].strip().startswith("    "):
                    # Próxima linha não-vazia não está indentada
                    match = padrao_campo.match(linha.strip())
                    if match:
                        problemas.append((i+1, f"Campo '{match.group(1)}' não tem descrição indentada"))
        
        # 6.2 Seções sem linha em branco antes ou depois
        for i, linha in enumerate(linhas_formatado):
            if i > 0 and i < len(linhas_formatado) - 1:
                if re.match(r'^[A-ZÇÀÁÂÃÉÊÍÓÔÕÚÜ\s\-0-9]+$', linha.strip()) and linha.strip():
                    # Esta é uma linha de seção
                    if linhas_formatado[i-1].strip() or linhas_formatado[i+1].strip():
                        problemas.append((i+1, f"Seção '{linha.strip()}' não tem linhas vazias antes/depois"))
        
        # 6.3 Texto que parece continuação de campos mas não está anexado
        for i in range(1, len(linhas_formatado)):
            if (linhas_formatado[i].strip() and 
                not padrao_campo.match(linhas_formatado[i].strip()) and
                not re.match(r'^[A-ZÇÀÁÂÃÉÊÍÓÔÕÚÜ\s\-0-9]+$', linhas_formatado[i].strip()) and
                not linhas_formatado[i].strip().startswith("    ") and
                padrao_campo.match(linhas_formatado[i-1].strip())):
                # Esta linha parece ser uma continuação não formatada
                problemas.append((i+1, f"Possível continuação não formatada: '{linhas_formatado[i][:50]}...'"))
        
        if problemas:
            print("\nPossíveis problemas de formatação encontrados:")
            for linha, descricao in problemas[:20]:
                print(f"  Linha {linha}: {descricao}")
            if len(problemas) > 20:
                print(f"  ... e mais {len(problemas) - 20} problemas")
        else:
            print("\nNenhum problema óbvio de formatação detectado.")
            
        # 7. Verificar presença de termos importantes em metadados
        termos_metadados = [
            "Campo Obrigatório", "Campo Essencial", "Campo Interno", 
            "Campo Opcional", "Descrição:", "Características DBF:"
        ]
        
        metadados_contagem = defaultdict(int)
        for termo in termos_metadados:
            # Contar em ambos os documentos
            metadados_contagem[f"Original: {termo}"] = conteudo_original.count(termo)
            metadados_contagem[f"Formatado: {termo}"] = conteudo_formatado.count(termo)
        
        print("\nPresença de termos importantes de metadados:")
        for termo, contagem in metadados_contagem.items():
            print(f"  {termo}: {contagem}")
        
        if any(metadados_contagem[f"Original: {termo}"] != metadados_contagem[f"Formatado: {termo}"] 
               for termo in termos_metadados):
            print("\n⚠️ AVISO: Discrepância na quantidade de termos de metadados entre os arquivos.")
        
        return True
    
    except Exception as e:
        print(f"ERRO durante a análise de formatação: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verificar_consistencia_mapeamento(arquivo_formatado, arquivo_codigo_python=None):
    """
    Verifica se o mapeamento no dicionário é consistente com o utilizado no código Python.
    
    Args:
        arquivo_formatado: Caminho para o dicionário formatado
        arquivo_codigo_python: Caminho para o código Python com os mapeamentos (opcional)
    """
    try:
        # Ler o dicionário formatado
        with open(arquivo_formatado, 'r', encoding='utf-8') as f:
            conteudo_dicionario = f.read()
        
        # Se arquivo de código Python foi fornecido
        if arquivo_codigo_python and os.path.exists(arquivo_codigo_python):
            with open(arquivo_codigo_python, 'r', encoding='utf-8') as f:
                codigo_python = f.read()
            
            # Extrair os mapeamentos do código Python
            mapeamentos_codigo = {}
            # Procurar por estruturas como "CAMPO": {'1': "Valor1", '2': "Valor2"}
            padrao_mapeamento = re.compile(r'"([A-Z_]+)":\s*\{([^}]+)\}')
            for match in padrao_mapeamento.finditer(codigo_python):
                campo = match.group(1)
                definicoes = match.group(2)
                
                # Extrair os pares de código-valor
                mapeamentos_codigo[campo] = {}
                padrao_pares = re.compile(r"'(\d+)':\s*\"([^\"]+)\"")
                for par_match in padrao_pares.finditer(definicoes):
                    codigo = par_match.group(1)
                    valor = par_match.group(2)
                    mapeamentos_codigo[campo][codigo] = valor
            
            print(f"\nMapeamentos encontrados no código Python: {len(mapeamentos_codigo)}")
            
            # Extrair os mapeamentos do dicionário para comparação
            # Aqui precisaríamos de uma análise mais complexa do texto formatado
            # Esta é uma versão simplificada que busca padrões de texto como "1-Valor1" no mesmo parágrafo que menciona o nome do campo
            
            # Primeiro passo: identificar os campos e suas descrições
            campos_dicionario = {}
            linhas = conteudo_dicionario.split('\n')
            campo_atual = None
            descricao_atual = []
            
            for linha in linhas:
                # Se é o início de um novo campo
                match = re.match(r'^([0-9]+[\-\.][^:]+?)(?:\s+|$)', linha.strip())
                if match:
                    # Salvar o campo anterior se existir
                    if campo_atual:
                        campos_dicionario[campo_atual] = '\n'.join(descricao_atual)
                    
                    # Iniciar novo campo
                    campo_atual = match.group(1).strip()
                    descricao_atual = [linha]
                elif campo_atual:
                    # Continuar acumulando descrição
                    descricao_atual.append(linha)
            
            # Adicionar o último campo
            if campo_atual:
                campos_dicionario[campo_atual] = '\n'.join(descricao_atual)
            
            # Segundo passo: tentar extrair mapeamentos dessas descrições
            mapeamentos_dicionario = {}
            for campo, descricao in campos_dicionario.items():
                # Tentar identificar o DBF_FIELD que corresponde ao campo do Python
                match_dbf = re.search(r'DBF:?\s*([A-Z_]+)', descricao, re.IGNORECASE)
                if match_dbf:
                    dbf_field = match_dbf.group(1)
                    
                    # Procurar por padrões de categorias no formato "1-Nome" ou "1 - Nome"
                    mapeamentos = {}
                    padrao_categoria = re.compile(r'(\d+)\s*[\-:]\s*([^\n\d]+)')
                    for cat_match in padrao_categoria.finditer(descricao):
                        codigo = cat_match.group(1)
                        valor = cat_match.group(2).strip()
                        mapeamentos[codigo] = valor
                    
                    if mapeamentos:
                        mapeamentos_dicionario[dbf_field] = mapeamentos
            
            print(f"Mapeamentos identificados no dicionário: {len(mapeamentos_dicionario)}")
            
            # Comparar os mapeamentos
            campos_comuns = set(mapeamentos_codigo.keys()) & set(mapeamentos_dicionario.keys())
            print(f"Campos com mapeamentos em ambas as fontes: {len(campos_comuns)}")
            
            if campos_comuns:
                diferenças = []
                for campo in campos_comuns:
                    codigos_dicionario = set(mapeamentos_dicionario[campo].keys())
                    codigos_codigo = set(mapeamentos_codigo[campo].keys())
                    
                    # Verificar códigos que estão em ambos mas têm valores diferentes
                    for codigo in codigos_dicionario & codigos_codigo:
                        if mapeamentos_dicionario[campo][codigo] != mapeamentos_codigo[campo][codigo]:
                            diferenças.append((campo, codigo, 
                                               mapeamentos_dicionario[campo][codigo], 
                                               mapeamentos_codigo[campo][codigo]))
                
                if diferenças:
                    print("\nDiferenças encontradas em mapeamentos comuns:")
                    for campo, codigo, valor_dic, valor_cod in diferenças[:10]:
                        print(f"  Campo {campo}, Código {codigo}:")
                        print(f"    Dicionário: '{valor_dic}'")
                        print(f"    Código Python: '{valor_cod}'")
                    if len(diferenças) > 10:
                        print(f"  ... e mais {len(diferenças) - 10} diferenças")
                else:
                    print("\nTodos os mapeamentos comuns são consistentes! 👍")
        else:
            print("\nNenhum arquivo de código Python especificado ou encontrado para análise de consistência.")
        
        return True
    
    except Exception as e:
        print(f"ERRO durante a verificação de consistência: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def comparar_textos(texto1, texto2):
    """
    Compara dois textos e retorna uma medida de similaridade
    """
    return difflib.SequenceMatcher(None, texto1, texto2).ratio()

def sugerir_correcoes(arquivo_formatado):
    """
    Analisa o arquivo formatado e sugere possíveis correções
    """
    try:
        with open(arquivo_formatado, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        sugestoes = []
        
        # Verificar linhas consecutivas que parecem ser continuação
        for i in range(1, len(linhas)):
            linha_atual = linhas[i].strip()
            linha_anterior = linhas[i-1].strip()
            
            # Se a linha atual não começa com número ou espaços, e a linha anterior
            # termina sem pontuação, pode ser uma continuação
            if (linha_atual and not linha_atual.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9', '0', ' ')) 
                and linha_anterior and linha_anterior[-1] not in '.,:;?!'):
                sugestoes.append((i+1, f"Possível continuação não formatada: '{linha_atual[:50]}...'"))
        
        if sugestoes:
            print("\nSugestões de correção:")
            for linha, sugestao in sugestoes[:15]:
                print(f"  Linha {linha}: {sugestao}")
            if len(sugestoes) > 15:
                print(f"  ... e mais {len(sugestoes) - 15} sugestões")
            
            return True
        else:
            print("\nNenhuma sugestão de correção adicional.")
            return True
    
    except Exception as e:
        print(f"ERRO ao gerar sugestões: {str(e)}")
        return False

def main():
    """Função principal do script"""
    parser = argparse.ArgumentParser(
        description='Analisa um dicionário formatado e identifica possíveis problemas ou inconsistências.'
    )
    parser.add_argument('--original', '-o', type=str, 
                        default=r'C:\Users\argus\workspace\ProjetoSRAG\DICIONARIO.txt',
                        help='Caminho para o arquivo de dicionário original')
    parser.add_argument('--formatado', '-f', type=str,
                        default=r'C:\Users\argus\workspace\ProjetoSRAG\DICIONARIO_formatado.txt',
                        help='Caminho para o arquivo de dicionário formatado')
    parser.add_argument('--codigo', '-c', type=str,
                        default=r'C:\Users\argus\workspace\ProjetoSRAG\processar_srag.py',
                        help='Caminho para o código Python com os mapeamentos')
    parser.add_argument('--sugestoes', '-s', action='store_true',
                        help='Gerar sugestões de correção para o arquivo formatado')
    
    args = parser.parse_args()
    
    # Verificar se os arquivos existem
    if not os.path.exists(args.formatado):
        print(f"ERRO: O arquivo formatado '{args.formatado}' não foi encontrado.")
        exit(1)
    
    print("=== Análise de Dicionário Formatado ===")
    print(f"Arquivo original: {args.original}")
    print(f"Arquivo formatado: {args.formatado}")
    
    # Analisar formatação
    if os.path.exists(args.original):
        print("\n--- Análise de Formatação ---")
        analisar_formatacao(args.original, args.formatado)
    else:
        print(f"\nArquivo original não encontrado: {args.original}")
        print("Pulando análise comparativa.")
    
    # Verificar consistência com código Python
    if args.codigo and os.path.exists(args.codigo):
        print("\n--- Verificação de Consistência com Código Python ---")
        verificar_consistencia_mapeamento(args.formatado, args.codigo)
    
    # Gerar sugestões de correção
    if args.sugestoes:
        print("\n--- Sugestões de Correção ---")
        sugerir_correcoes(args.formatado)
    
    print("\n=== Análise Concluída ===")

if __name__ == "__main__":
    main()
