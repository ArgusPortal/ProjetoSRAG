# ProjetoSRAG - Processamento de Dados de SRAG Hospitalizados

Este projeto oferece ferramentas para processamento, limpeza e análise de dados de Síndrome Respiratória Aguda Grave (SRAG) do sistema SIVEP-Gripe do Ministério da Saúde do Brasil.

## Objetivo do Projeto

Este projeto tem como objetivo analisar os dados epidemiológicos relacionados à Síndrome Respiratória Aguda Grave (SRAG) no Brasil, utilizando informações públicas provenientes das notificações realizadas por unidades de saúde. Os dados analisados abrangem características demográficas, clínicas e temporais dos pacientes, permitindo a construção de indicadores que subsidiem estratégias de vigilância e planejamento em saúde pública.

É importante destacar que a qualidade dos resultados obtidos depende diretamente da correta inserção das informações no sistema de notificação. Assim, eventuais inconsistências ou lacunas nos registros podem impactar a interpretação dos achados e a formulação de ações baseadas nos dados. Por isso, na análise de Internações e Perfil Vacinal foram excluídos casos com informações faltantes ou dados discrepantes.

## Sobre o Projeto

O ProjetoSRAG surgiu da necessidade de unificar, padronizar e enriquecer os dados de vigilância epidemiológica de SRAG (Síndrome Respiratória Aguda Grave) provenientes do SIVEP-Gripe. O objetivo principal é transformar dados brutos com códigos numéricos em informações significativas, seguindo rigorosamente o dicionário de dados oficial.

### Principais Funcionalidades

- **Unificação de Bases**: Combina dados de múltiplos anos (2021-2024) em um único arquivo
- **Limpeza e Padronização**: Remove duplicatas, valores inválidos e padroniza formatos
- **Interpretação Semântica**: Converte códigos numéricos em descrições textuais conforme o dicionário oficial
- **Cálculos Derivados**: Gera campos úteis como idade em anos, tempo de internação e tempo em UTI
- **Tratamento Robusto**: Lida com diferentes formatos de arquivo e codificações com múltiplas estratégias de contingência
- **Filtragem Avançada**: Remove registros com dados inconsistentes (como tempo de UTI irrealmente alto)

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

3. **filtrar_dados_srag.py**
   - Remove registros com TEMPO_UTI > 160 dias (possíveis erros de digitação)
   - Exclui registros onde o campo EVOLUCAO está nulo
   - Gera relatórios detalhados sobre os registros filtrados

4. **formatar_dicionario.py** e **analisar_dicionario_formatado.py**
   - Ferramentas auxiliares para trabalhar com o dicionário de dados oficial
   - Corrigem quebras de linha indevidas e melhoram a legibilidade
   - Analisam a consistência do dicionário com o código de processamento

### Arquivos de Referência

- **DICIONARIO.txt**
  - Documento oficial do Ministério da Saúde com a descrição detalhada de todos os campos
  - Utilizado como referência para o mapeamento de códigos para descrições

## Análise da Situação Epidemiológica da SRAG no Brasil

O dashboard analisado apresenta um panorama detalhado sobre os casos de Síndrome Respiratória Aguda Grave (SRAG) no Brasil, com foco em internações hospitalares, suporte clínico e adesão à vacinação contra COVID-19. A análise dos dados evidencia padrões epidemiológicos, desigualdades no acesso à saúde e oportunidades para intervenções estratégicas. A seguir, são apresentados os principais achados e suas implicações.

### Internações e Suporte Clínico

#### Internações Hospitalares
Os dados indicam que a SRAG continua a ser um problema de saúde pública significativo no Brasil. Com um total de 2.171.580 pacientes registrados, 2.138.995 (98,5%) necessitaram de internação hospitalar. Esse número reflete a gravidade da condição e a pressão exercida sobre o sistema de saúde, especialmente em períodos de maior circulação viral.

A alta taxa de internações sugere que a SRAG está frequentemente associada a complicações graves que requerem cuidados hospitalares. Isso reforça a importância de estratégias preventivas, como vacinação em massa e campanhas educativas para reduzir a exposição aos fatores de risco.

#### Uso de UTI
Entre os pacientes internados, 710.420 (32,7%) necessitaram de cuidados em Unidade de Terapia Intensiva (UTI). A maior parte dos pacientes (65,4%) não precisou de UTI, enquanto 1,9% dos registros não informaram essa variável.

A proporção significativa de internações em UTI demonstra a gravidade dos casos mais críticos e aponta para a necessidade de manter uma infraestrutura robusta de cuidados intensivos. Estratégias como o fortalecimento da rede hospitalar e o treinamento contínuo das equipes médicas são essenciais para lidar com picos epidêmicos.

#### Suporte Ventilatório
O suporte ventilatório foi amplamente utilizado entre os pacientes:

- 56,2% receberam suporte ventilatório não invasivo
- 16,8% necessitaram de ventilação invasiva
- Apenas 23,9% dos pacientes não precisaram dessa intervenção

O uso elevado de ventilação não invasiva pode indicar uma abordagem clínica voltada para evitar complicações associadas à ventilação mecânica invasiva. No entanto, a alta proporção de casos graves que demandaram ventilação invasiva reforça a importância de estratégias preventivas para reduzir o número de hospitalizações severas.

#### Tempo Médio de Internação
O tempo médio de internação geral foi consistente ao longo do ano, com uma média de 11 dias. Da mesma forma, o tempo médio na UTI também foi de aproximadamente 11 dias. Nos meses finais do ano (novembro e dezembro), observou-se uma leve redução para cerca de 10 dias.

Essa redução pode estar associada à menor gravidade dos casos mais recentes ou à adoção de protocolos clínicos mais eficazes. O monitoramento contínuo do tempo médio de internação é fundamental para avaliar a eficiência do manejo clínico e identificar oportunidades para otimização dos recursos hospitalares.

### Vacinação Contra COVID-19

#### Cobertura Vacinal
A análise da cobertura vacinal contra COVID-19 revela um padrão preocupante:

- Apenas 34% dos pacientes receberam a primeira dose
- A adesão à segunda dose foi ainda menor (28%)
- Apenas 12% completaram o esquema vacinal com a dose de reforço

Esses números indicam uma baixa adesão às doses subsequentes da vacina, o que pode estar associado à diminuição da percepção do risco ao longo do tempo ou à falta de acesso em algumas regiões. Campanhas educativas e estratégias logísticas direcionadas são necessárias para aumentar a adesão vacinal, especialmente entre os grupos mais vulneráveis.

#### Diferenças por Sexo
As mulheres apresentaram maior adesão à vacinação em todas as doses:

- Primeira dose: 36% (feminino) vs. 31% (masculino)
- Segunda dose: 30% (feminino) vs. 25% (masculino)
- Dose de reforço: 13% (feminino) vs. 10% (masculino)

Essas diferenças podem refletir maior conscientização ou acesso aos serviços de saúde entre as mulheres. Estratégias específicas devem ser implementadas para aumentar a adesão vacinal entre os homens, como campanhas direcionadas ou parcerias com ambientes predominantemente masculinos (ex.: locais de trabalho).

#### Diferenças por Raça
A análise por raça evidencia desigualdades significativas:

- Grupos Amarelo e Branco apresentaram as maiores taxas de vacinação
- Grupos Pardo e Preto tiveram menores taxas em todas as doses

Essas disparidades sugerem barreiras no acesso à vacinação entre determinados grupos raciais, possivelmente relacionadas a fatores socioeconômicos ou geográficos. Políticas públicas devem priorizar essas populações vulneráveis por meio da ampliação do acesso às vacinas em comunidades periféricas e rurais.

#### Evolução Temporal da Vacinação
A adesão vacinal atingiu seu pico em 2021:

- Primeira dose: 56%
- Segunda dose: 33%

Nos anos seguintes, houve uma queda acentuada:

- Em 2025, apenas 41% receberam a primeira dose
- Apenas 38% completaram a segunda dose
- Apenas 18% receberam o reforço

Essa queda na adesão ao longo do tempo reflete desafios na manutenção do engajamento populacional com campanhas vacinais prolongadas. Estratégias como comunicação clara sobre os benefícios das doses subsequentes e incentivos diretos podem ajudar a reverter essa tendência.

## Implicações Epidemiológicas

Os dados apresentados no dashboard têm implicações importantes para o planejamento estratégico em saúde pública:

### Fortalecimento da Vigilância Epidemiológica
- O monitoramento contínuo dos casos graves é essencial para identificar surtos precocemente
- A integração dos dados hospitalares com sistemas regionais pode melhorar a alocação eficiente dos recursos

### Foco na Prevenção
- A alta taxa de internações e uso intensivo de UTI reforçam a necessidade de estratégias preventivas robustas
- Campanhas educativas sobre higiene respiratória e vacinação devem ser ampliadas para reduzir o número de casos graves

### Redução das Desigualdades
- As disparidades observadas na vacinação por sexo e raça destacam desigualdades no acesso aos serviços de saúde
- Políticas específicas devem ser implementadas para alcançar populações vulneráveis, incluindo campanhas itinerantes em áreas remotas e periféricas

### Fortalecimento da Rede Hospitalar
- O uso elevado de suporte ventilatório e o tempo prolongado na UTI demonstram a necessidade contínua de investimentos na infraestrutura hospitalar
- Treinamento das equipes médicas deve ser priorizado para garantir um manejo eficiente durante períodos críticos

### Aumento da Adesão Vacinal
- A baixa cobertura vacinal contra COVID-19 é preocupante e exige ações imediatas
- Estratégias como parcerias comunitárias e incentivos financeiros podem aumentar as taxas de vacinação nas populações menos engajadas

## Processos de Limpeza e Transformação de Dados

### 1. Carregamento e Unificação de Dados

O processo inicia com a unificação de múltiplas bases de dados usando o script `unificacao.py`:

- **Carregamento Robusto**: Implementamos um sistema que tenta múltiplas configurações de encoding (Latin1, UTF-8) e separadores (';', ',') para garantir o carregamento bem-sucedido de arquivos de diferentes origens.

- **Detecção Automática de Formatos**: O script identifica automaticamente se arquivos estão comprimidos e seleciona a melhor estratégia de leitura.

- **Filtragem Inteligente de Colunas**: Apenas as colunas relevantes conforme o dicionário oficial são mantidas, reduzindo o tamanho do dataset.

- **Diagnóstico de Qualidade**: São gerados relatórios detalhados sobre os arquivos carregados, incluindo métricas de completude e consistência.

### 2. Limpeza e Padronização de Dados

A fase de limpeza no script `processar_srag.py` inclui:

- **Remoção de Duplicatas**: Registros duplicados são identificados e removidos.

- **Eliminação de Colunas Vazias**: Colunas com percentual de valores nulos acima de um threshold configurável são automaticamente removidas.

- **Padronização de Texto**: Todas as strings são convertidas para maiúsculas e espaços desnecessários são removidos.

- **Normalização de Nomes de Colunas**: Nomes de colunas são padronizados para corresponder exatamente ao dicionário oficial.

### 3. Mapeamento de Categorias

Este foi o desafio mais complexo do projeto, resolvido através das seguintes estratégias:

- **Conversão Segura de Tipos**: Todos os campos são convertidos para tipo `object` antes do processamento para evitar erros de tipo quando lidando com campos já mapeados.

- **Detecção de Valores Pré-mapeados**: O algoritmo verifica se uma coluna já contém valores descritivos antes de tentar mapear, evitando erros de conversão.

- **Abordagem Multi-estratégia para Códigos Numéricos**:
  - Correspondência exata de strings
  - Manipulação especial para números decimais (como 1.0 → 1)
  - Tratamento diferenciado para campos de checkbox (1 → "Sim")

- **Mapeamento Baseado em Dicionário**: Utilizamos o dicionário oficial SIVEP-Gripe (19/09/2022) para garantir que todos os códigos sejam convertidos para suas descrições corretas, como:
  - Códigos de sexo (1, 2, 9) → "Masculino", "Feminino", "Ignorado"
  - Códigos de classificação final (1-5) → Descrições específicas de SRAG
  - Códigos de evolução (1, 2, 3, 9) → "Cura", "Óbito", "Óbito por outras causas", "Ignorado"

- **Aplicação Seletiva de Mapeamentos**: Utilizamos máscaras booleanas e o método `.loc` para atualizar somente os valores específicos que precisam ser alterados.

### 4. Conversão de Datas e Cálculos Derivados

- **Normalização de Datas**: Campos de data são convertidos para objetos datetime do pandas com tratamento de erros inteligente.

- **Cálculos Derivados Importantes**:
  - **IDADE_ANOS**: Calculada precisamente a partir da data de nascimento e data dos primeiros sintomas
  - **TEMPO_INTERNACAO**: Duração da internação em dias
  - **TEMPO_UTI**: Tempo de permanência em UTI

- **Otimização de Memória**: Todos os novos campos são calculados em um DataFrame temporário e depois concatenados de uma vez para evitar fragmentação de memória.

### 5. Filtragem de Dados Problemáticos

Após o processamento inicial, aplicamos filtros para remover registros que possam comprometer a qualidade da análise:

- **Remoção de Valores Extremos**: Excluímos registros com TEMPO_UTI > 160 dias, que provavelmente representam erros de digitação
- **Eliminação de Registros Incompletos**: Removemos casos onde o campo EVOLUCAO está nulo, garantindo maior confiabilidade em análises de desfecho

## Desafios Técnicos e Soluções

### 1. Problema: Tipos Mistos de Dados
**Desafio**: Algumas colunas já continham valores textuais em vez de códigos, causando erros de conversão durante o mapeamento.

**Solução**: 
- Implementamos uma fase de detecção prévia que verifica se uma coluna já contém valores de texto mapeados
- Convertemos todos os campos para o tipo `object` antes de qualquer operação
- Criamos um conjunto de todos os valores possíveis após mapeamento para comparação rápida

```python
# Verificar se a coluna já contém valores textuais mapeados
valores_texto = [v for v in valores_unicos if v in todos_valores_texto]
valores_originais = [v for v in valores_unicos if v not in todos_valores_texto]

# Pular se já totalmente mapeado
if valores_texto and not valores_originais:
    campos_ja_mapeados.append(campo)
    continue
```

### 2. Problema: Variações de Representação Numérica
**Desafio**: Valores decimais como "1.0" precisavam ser tratados como equivalentes a "1".

**Solução**:
- Utilizamos uma abordagem de duas vias que combina correspondência exata e verificação de equivalência numérica
- Implementamos um método seguro de manipulação de strings para remover '.0' dos valores

```python
mascara = (
    df[campo].astype(str).str.strip() == str(codigo).strip()
) | (
    df[campo].apply(
        lambda x: str(x).replace('.0', '') == str(codigo).strip() 
        if pd.notnull(x) else False
    )
)
```

### 3. Problema: Carregamento de Arquivos em Diferentes Formatos
**Desafio**: Os arquivos CSV vinham com diferentes encodings, separadores e estruturas.

**Solução**:
- Sistema de fallback de múltiplas tentativas para carregamento de CSV
- Detecção automática de compressão de arquivo
- Sistema de diagnóstico que mostra as primeiras linhas em caso de falha

```python
# Sistema sequencial de tentativas com diferentes configurações
configs = [
    {'encoding': 'latin1', 'sep': ';', 'low_memory': False},
    {'encoding': 'latin1', 'sep': ',', 'low_memory': False},
    {'encoding': 'utf-8', 'sep': ';', 'low_memory': False},
    {'encoding': 'latin1', 'sep': None, 'engine': 'python', 'low_memory': False}
]
```

### 4. Problema: Prevenção de Erros em Processamento em Lote
**Desafio**: O processamento não podia falhar completamente devido a erros em campos individuais.

**Solução**:
- Blocos try/except granulares em torno de cada operação importante
- Reporting detalhado de campos processados, pulados ou com erro
- Código defensivo que verifica existência de colunas antes de processá-las

### 5. Problema: Otimização para Grandes Volumes de Dados
**Desafio**: Os datasets completos chegam a milhões de registros, exigindo uso eficiente de memória.

**Solução**:
- Implementação opcional do PyArrow para carregar arquivos grandes
- Remoção proativa de colunas desnecessárias
- Processamento em chunks para arquivos muito grandes
- Minimização de cópias de DataFrames em memória

## Fluxo de Trabalho

O projeto foi desenvolvido para seguir um fluxo de trabalho em etapas:

1. **Unificação das Bases**
   - Execute `unificacao.py` para combinar múltiplos arquivos de dados
   - Cria o arquivo `SRAG_Unificado.csv` contendo todos os registros

2. **Processamento e Enriquecimento**
   - Execute `processar_srag.py` para processar e enriquecer os dados
   - Transforma códigos em descrições conforme o dicionário
   - Cria o arquivo `dados_srag_tratados.csv` com os dados processados

3. **Filtragem de Registros**
   - Execute `filtrar_dados_srag.py` para remover registros problemáticos
   - Cria o arquivo `dados_srag_filtrados.csv` com dados de alta qualidade

4. **Análise e Visualização**
   - Realiza análises estatísticas e prepara visualizações

## Métricas e Validação dos Resultados

Após o processamento, o script gera relatórios com:

- Total de registros processados
- Contagem de campos já mapeados, mapeados durante o processamento, e não mapeados
- Distribuição de valores em colunas-chave como sexo, raça, evolução e classificação final

Estas métricas permitem validar a qualidade do processamento e identificar possíveis anomalias nos dados.

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

### Filtragem de Registros Problemáticos

```bash
python filtrar_dados_srag.py
```

Opções disponíveis:
- `--arquivo` ou `-a`: Caminho para o arquivo a ser filtrado
- `--saida` ou `-s`: Caminho para o arquivo de saída filtrado
- `--sobrescrever` ou `-o`: Sobrescreve o arquivo original (cria backup automático)

## Melhores Práticas e Dicas

- **Arquivos Grandes**: Para arquivos muito grandes, considere aumentar a memória disponível para o Python
- **Performance**: A instalação do PyArrow melhora significativamente o desempenho ao trabalhar com arquivos CSV grandes
- **Modificações**: Ao adicionar novos campos, consulte o dicionário SIVEP-Gripe para garantir a correta interpretação

## Resultados e Benefícios

- **Dados Interpretáveis**: Transformação de códigos numéricos em informações de fácil compreensão
- **Consolidação Temporal**: Unificação de dados de múltiplos anos em uma base coerente
- **Enriquecimento**: Campos calculados que facilitam análises epidemiológicas
- **Padronização**: Formato consistente que facilita integrações com outras ferramentas

## Lições Aprendidas

O desenvolvimento deste projeto ofereceu importantes aprendizados sobre processamento de dados epidemiológicos:

1. **Validação Rigorosa**: É essencial verificar a correspondência exata com o dicionário oficial
2. **Tratamento Defensivo**: Sempre assumir que os dados podem ter inconsistências
3. **Otimização Progressiva**: Começar com código funcional e otimizar conforme necessário
4. **Diagnóstico Detalhado**: Implementar sistemas de log que facilitem a depuração

## Limitações Conhecidas

- O processamento de arquivos muito grandes pode requerer otimizações adicionais de memória
- Alguns campos específicos podem não ter mapeamentos completos se não estiverem no dicionário oficial

## Contribuições e Desenvolvimento Futuro

Ideias para aprimoramento:
- Implementação de ferramentas de visualização integradas
- Módulos de análise estatística avançada
- Integração com sistemas de BI e dashboards

## Conclusão

O panorama apresentado evidencia tanto os desafios quanto as oportunidades no enfrentamento da SRAG no Brasil. Embora avanços tenham sido feitos no manejo clínico dos casos graves – como indicado pela redução do tempo médio de internação – ainda há lacunas significativas na prevenção primária, especialmente relacionadas à vacinação contra COVID-19.

As desigualdades observadas entre grupos raciais e sexos reforçam a necessidade urgente de políticas públicas mais inclusivas e equitativas. Além disso, o declínio na adesão vacinal ao longo do tempo destaca a importância da comunicação clara sobre os benefícios contínuos das doses subsequentes.

Por fim, o fortalecimento da vigilância epidemiológica e da infraestrutura hospitalar será essencial para mitigar os impactos futuros da SRAG e outras doenças respiratórias graves no Brasil. Este projeto serve como base para orientar gestores públicos na tomada de decisões estratégicas voltadas à proteção da saúde coletiva no país.

## Agradecimentos

Este projeto utiliza dados públicos do SIVEP-Gripe (Sistema de Informação de Vigilância Epidemiológica da Gripe) do Ministério da Saúde do Brasil.

---

Este projeto foi realizado por Argus Cordeiro Sales Portal como atividade avaliativa do curso de Especialização em Tecnologias Emergentes e Imersivas para Saúde Digital - UFG