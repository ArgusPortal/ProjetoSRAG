#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para filtrar registros problemáticos do arquivo de dados SRAG processados.

Este script:
1. Remove registros onde TEMPO_UTI > 160 dias (potenciais erros de digitação)
2. Remove registros onde EVOLUCAO está nulo (dados incompletos)
3. Salva os dados filtrados em um novo arquivo

Uso: python filtrar_dados_srag.py [--arquivo ARQUIVO] [--saida ARQUIVO_SAIDA]
"""

import pandas as pd
import os
import argparse
import numpy as np

def filtrar_dados_srag(arquivo_entrada, arquivo_saida, backup=True):
    """
    Filtra o arquivo de dados SRAG processados para remover registros problemáticos.
    
    Args:
        arquivo_entrada: Caminho para o arquivo de dados SRAG processados
        arquivo_saida: Caminho para o arquivo de saída com dados filtrados
        backup: Se True, cria uma cópia de backup do arquivo original
    
    Returns:
        bool: True se o processo foi concluído com sucesso
    """
    try:
        print(f"Carregando dados de {arquivo_entrada}...")
        # Carregar os dados
        df = pd.read_csv(arquivo_entrada, sep=';', encoding='utf-8-sig')
        
        tamanho_original = len(df)
        print(f"Total de registros carregados: {tamanho_original}")
        
        # Criar backup se solicitado
        if backup and arquivo_entrada == arquivo_saida:
            backup_path = f"{arquivo_entrada}.bak"
            print(f"Criando backup do arquivo original em {backup_path}")
            df.to_csv(backup_path, sep=';', encoding='utf-8-sig', index=False)
        
        # Filtro 1: Remover registros com TEMPO_UTI > 160
        if 'TEMPO_UTI' in df.columns:
            registros_antes = len(df)
            df = df[~(df['TEMPO_UTI'] > 160)]
            registros_removidos = registros_antes - len(df)
            print(f"Removidos {registros_removidos} registros com TEMPO_UTI > 160")
        else:
            print("AVISO: Coluna 'TEMPO_UTI' não encontrada no arquivo")
        
        # Filtro 2: Remover registros com EVOLUCAO nulo
        if 'EVOLUCAO' in df.columns:
            registros_antes = len(df)
            df = df[~df['EVOLUCAO'].isna()]
            registros_removidos = registros_antes - len(df)
            print(f"Removidos {registros_removidos} registros com EVOLUCAO nulo")
        else:
            print("AVISO: Coluna 'EVOLUCAO' não encontrada no arquivo")
        
        # Calcular total de registros removidos
        registros_filtrados = len(df)
        total_removidos = tamanho_original - registros_filtrados
        percentual_removido = (total_removidos / tamanho_original) * 100 if tamanho_original > 0 else 0
        
        print(f"\nResumo da filtragem:")
        print(f"  - Total de registros originais: {tamanho_original}")
        print(f"  - Total de registros após filtragem: {registros_filtrados}")
        print(f"  - Registros removidos: {total_removidos} ({percentual_removido:.2f}%)")
        
        # Salvar os dados filtrados
        print(f"Salvando dados filtrados em {arquivo_saida}...")
        df.to_csv(arquivo_saida, sep=';', encoding='utf-8-sig', index=False)
        
        print("Filtro concluído com sucesso!")
        return True
    except Exception as e:
        print(f"ERRO durante a filtragem: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description='Filtra registros problemáticos do arquivo de dados SRAG processados.')
    parser.add_argument('--arquivo', '-a', type=str, 
                        default=r'C:\Users\argus\workspace\ProjetoSRAG\dados_srag_tratados.csv',
                        help='Caminho para o arquivo de dados SRAG processados')
    parser.add_argument('--saida', '-s', type=str,
                        default=r'C:\Users\argus\workspace\ProjetoSRAG\dados_srag_filtrados.csv',
                        help='Caminho para o arquivo de saída com dados filtrados')
    parser.add_argument('--sobrescrever', '-o', action='store_true',
                        help='Se especificado, sobrescreve o arquivo original (cria backup automático)')
    
    args = parser.parse_args()
    
    # Verificar se o arquivo existe
    if not os.path.exists(args.arquivo):
        print(f"ERRO: O arquivo '{args.arquivo}' não foi encontrado.")
        return 1
    
    # Se sobrescrever o arquivo original
    arquivo_saida = args.arquivo if args.sobrescrever else args.saida
    
    # Chamar a função de filtragem
    sucesso = filtrar_dados_srag(args.arquivo, arquivo_saida)
    
    return 0 if sucesso else 1

if __name__ == "__main__":
    exit(main())
