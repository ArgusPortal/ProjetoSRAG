# ProjetoSRAG - Processamento de Dados de SRAG Hospitalizados

Este projeto oferece ferramentas para processamento, limpeza e análise de dados de Síndrome Respiratória Aguda Grave (SRAG) do sistema SIVEP-Gripe do Ministério da Saúde do Brasil.

## Sobre o Projeto

O ProjetoSRAG surgiu da necessidade de unificar, padronizar e enriquecer os dados de vigilância epidemiológica de SRAG (Síndrome Respiratória Aguda Grave) provenientes do SIVEP-Gripe. O objetivo principal é transformar dados brutos com códigos numéricos em informações significativas, seguindo rigorosamente o dicionário de dados oficial.

### Principais Funcionalidades

- **Unificação de Bases**: Combina dados de múltiplos anos (2021-2024) em um único arquivo
- **Limpeza e Padronização**: Remove duplicatas, valores inválidos e padroniza formatos
- **Interpretação Semântica**: Converte códigos numéricos em descrições textuais conforme o dicionário oficial
- **Cálculos Derivados**: Gera campos úteis como idade em anos, tempo de internação e tempo em UTI
- **Tratamento Robusto**: Lida com diferentes formatos de arquivo e codificações com múltiplas estratégias de contingência

## Arquivos do Projeto

### Scripts Principais

1. **unificacao.py**
   - Unifica múltiplos arquivos CSV de diferentes anos em uma única base
   - Implementa estratégias robustas para lidar com diferentes formatos e codificações
   - Realiza validações básicas nos dados durante a unificação

2. **processar_srag.py**
   - Processamento completo dos dados SRAG conforme o dicionário SIVEP-Gripe
   - Realiza mapeamento de códigos para descrições em todos os campos categóricos
   - Converte datas e calcula campos derivados importantes
   - Remove colunas vazias e padroniza formatos

3. **teste.ipynb**
   - Notebook Jupyter para exploração e análise dos dados processados
   - Demonstra como carregar, visualizar e analisar os dados após o processamento

### Arquivos de Referência

- **DICIONARIO.txt**
  - Documento oficial do Ministério da Saúde com a descrição detalhada de todos os campos
  - Utilizado como referência para o mapeamento de códigos para descrições

## Fluxo de Trabalho

O projeto foi desenvolvido para seguir um fluxo de trabalho em etapas:

1. **Unificação das Bases**
   - Execute `unificacao.py` para combinar múltiplos arquivos de dados
   - Cria o arquivo `SRAG_Unificado.csv` contendo todos os registros

2. **Processamento e Enriquecimento**
   - Execute `processar_srag.py` para processar e enriquecer os dados
   - Transforma códigos em descrições conforme o dicionário
   - Cria o arquivo `dados_srag_tratados.csv` com os dados processados

3. **Análise e Visualização**
   - Utilize o notebook `teste.ipynb` para explorar os dados processados
   - Realiza análises estatísticas e prepara visualizações

## Detalhes Técnicos

### Requisitos do Sistema

- Python 3.8+
- Pandas
- NumPy
- Jupyter (para o notebook)
- PyArrow (opcional, mas recomendado para melhor desempenho)

### Otimizações Implementadas

- **Tratamento de Codificações**: Múltiplas estratégias para lidar com diferentes encodings (Latin1, UTF-8)
- **Tratamento de Separadores**: Suporte para diferentes separadores CSV (ponto e vírgula, vírgula)
- **Otimização de Memória**: Implementação que evita fragmentação do DataFrame para grandes volumes de dados
- **Diagnóstico de Erros**: Feedback detalhado quando ocorrem problemas de carregamento
- **Remoção Inteligente de Colunas**: Eliminação de colunas totalmente vazias para economizar memória

### Mapeamento de Categorias

Um dos aspectos mais importantes deste projeto é o mapeamento preciso dos códigos numéricos para suas descrições textuais, seguindo rigorosamente o dicionário oficial. Por exemplo:

- Códigos de sexo (1, 2, 9) → "Masculino", "Feminino", "Ignorado"
- Códigos de evolução (1, 2, 3, 9) → "Cura", "Óbito", "Óbito por outras causas", "Ignorado"
- Códigos de classificação final (1-5) → Descrições específicas do tipo de SRAG

## Como Usar

### Unificação de Bases

```bash
python unificacao.py
```

### Processamento dos Dados

```bash
python processar_srag.py
```

Opções disponíveis:
- `--arquivo` ou `-a`: Caminho para o arquivo a ser processado
- `--saida` ou `-s`: Caminho para o arquivo de saída

Exemplo com opções:
```bash
python processar_srag.py --arquivo dados/meu_arquivo.csv --saida resultados/dados_processados.csv
```

### Análise no Jupyter Notebook

Abra o notebook `teste.ipynb` em um ambiente Jupyter e execute as células para explorar os dados.

## Melhores Práticas e Dicas

- **Arquivos Grandes**: Para arquivos muito grandes, considere aumentar a memória disponível para o Python
- **Performance**: A instalação do PyArrow melhora significativamente o desempenho ao trabalhar com arquivos CSV grandes
- **Modificações**: Ao adicionar novos campos, consulte o dicionário SIVEP-Gripe para garantir a correta interpretação

## Resultados e Benefícios

- **Dados Interpretáveis**: Transformação de códigos numéricos em informações de fácil compreensão
- **Consolidação Temporal**: Unificação de dados de múltiplos anos em uma base coerente
- **Enriquecimento**: Campos calculados que facilitam análises epidemiológicas
- **Padronização**: Formato consistente que facilita integrações com outras ferramentas

## Limitações Conhecidas

- O processamento de arquivos muito grandes pode requerer otimizações adicionais de memória
- Alguns campos específicos podem não ter mapeamentos completos se não estiverem no dicionário oficial

## Contribuições e Desenvolvimento Futuro

Ideias para aprimoramento:
- Implementação de ferramentas de visualização integradas
- Módulos de análise estatística avançada
- Integração com sistemas de BI e dashboards

## Agradecimentos

Este projeto utiliza dados públicos do SIVEP-Gripe (Sistema de Informação de Vigilância Epidemiológica da Gripe) do Ministério da Saúde do Brasil.

---

Projeto desenvolvido para fins de análise e pesquisa epidemiológica.
