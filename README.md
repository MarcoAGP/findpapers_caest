# Busca bibliográfica multibase com Findpapers

Pesquisa sobre **Instagram, marketing digital e assuntos estudantis**, com consulta multilíngue e exportação de metadados para análise acadêmica.

Este guia documenta o script `pesquisar.py`. O fluxo foi organizado para uso pelo Terminal no **macOS Intel, sem Homebrew**, e pode apoiar o levantamento bibliográfico de pesquisas sobre Centros de Assuntos Estudantis (CAEST).

> Este é um fluxo de pesquisa baseado no [Findpapers](https://github.com/jonatasgrosman/findpapers), não o repositório oficial da biblioteca. O script coleta e organiza registros; a decisão de inclusão na revisão depende de avaliação metodológica e leitura dos estudos.

## Sumário

- [Objetivo e funcionalidades](#objetivo-e-funcionalidades)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Bases e credenciais](#bases-e-credenciais)
- [Configuração segura](#configuração-segura)
- [Estratégia de busca](#estratégia-de-busca)
- [Preparação e execução](#preparação-e-execução)
- [Arquivos de saída](#arquivos-de-saída)
- [Dicionário dos dados](#dicionário-dos-dados)
- [Interpretação dos resultados](#interpretação-dos-resultados)
- [Personalização](#personalização)
- [Reprodutibilidade](#reprodutibilidade)
- [Solução de problemas](#solução-de-problemas)
- [Publicação no GitHub](#publicação-no-github)
- [Limitações e melhorias](#limitações-e-melhorias)
- [Contribuições, créditos e licença](#contribuições-créditos-e-licença)
- [Referências](#referências)
- [Apêndice: script completo](#apêndice-script-completo)

## Objetivo e funcionalidades

Automatizar o levantamento inicial de trabalhos que relacionem Instagram, marketing/comunicação e serviços ou assuntos estudantis, utilizando termos em português, inglês e espanhol.

O script fornecido:

- Executa uma consulta booleana em sete bases configuradas.
- Utiliza a consolidação e deduplicação disponibilizadas pelo Findpapers.
- Normaliza autores, palavras-chave e identificação das bases.
- Exporta registros em CSV, JSON, BibTeX e texto legível.
- Tenta preservar o resultado bruto em JSON.
- Registra consulta, bases, data, duração da busca e versões do ambiente.
- Ordena registros por número de bases, citações e título.

Não estão implementados neste script: tradução automática, classificação semântica, triagem de elegibilidade, dashboard, download de PDFs ou execução de snowballing. O preenchimento de `pdf_url` não equivale a baixar o artigo.

## Requisitos

| Item                               | Uso                                             |
| ---------------------------------- | ----------------------------------------------- |
| Python 3.11 ou superior            | Execução e ambiente virtual                     |
| Git                                | Instalação da dependência diretamente do GitHub |
| Conexão à internet                 | Instalação e consultas às APIs                  |
| Findpapers                         | Biblioteca externa de busca e consolidação      |
| Credenciais das bases selecionadas | Acesso conforme as condições de cada provedor   |

O script utiliza também `csv`, `json`, `sys`, `time`, `pathlib` e `datetime`, que fazem parte da biblioteca padrão do Python. Não é necessário instalar pandas, NumPy, PyTorch ou Gemini para este fluxo.

**Compatibilidade:** confira se o instalador do Python escolhido suporta sua versão do macOS. A exigência de Python 3.11+ não significa que qualquer versão recente de Python funcione em qualquer macOS antigo.

## Instalação

### 1. Verificar o ambiente

```bash
uname -m
python3 --version
command -v python3
git --version
```

Em um Mac Intel, `uname -m` normalmente retorna `x86_64`. Se o Python for anterior a 3.11, instale uma versão compatível pelo [site oficial do Python](https://www.python.org/downloads/macos/). Se o Git não estiver disponível, instale as ferramentas de linha de comando da Apple:

```bash
xcode-select --install
```

### 2. Criar a pasta e o ambiente virtual

```bash
mkdir -p ~/findpapers
cd ~/findpapers
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

Se houver vários interpretadores, substitua `python3` pelo executável compatível escolhido, por exemplo `python3.11`. Confirme o ambiente ativo:

```bash
python -c "import sys; print(sys.executable); print(sys.version)"
```

### 3. Instalar e verificar o Findpapers

```bash
python -m pip install git+https://github.com/jonatasgrosman/findpapers.git
python -c "import findpapers; print('Findpapers instalado com sucesso!')"
python -m pip check
```

A instalação acompanha o código disponível no GitHub. Como a branch `main` pode mudar, registre a revisão instalada antes de executar uma coleta destinada à pesquisa.

## Bases e credenciais

| Base             | Identificador em `DATABASES` | Credencial no fluxo documentado                                          |
| ---------------- | ---------------------------- | ------------------------------------------------------------------------ |
| arXiv            | `arxiv`                      | Sem chave                                                                |
| IEEE Xplore      | `ieee`                       | Chave necessária                                                         |
| OpenAlex         | `openalex`                   | Opcional segundo a documentação do Findpapers consultada                 |
| PubMed           | `pubmed`                     | Opcional segundo a documentação do Findpapers consultada                 |
| Scopus           | `scopus`                     | Chave necessária; permissões dependem do acesso contratado               |
| Semantic Scholar | `semantic_scholar`           | Opcional segundo a documentação do Findpapers consultada                 |
| Web of Science   | `wos`                        | Chave necessária; permissões dependem do plano                           |
| CrossRef         | Não incluído                 | Enriquecimento/referências; não é fonte de `Engine.search()` neste fluxo |

A documentação geral menciona oito integrações, mas o script configura **sete fontes de busca**. O script não chama explicitamente operações de enriquecimento ou snowballing; essas possibilidades da biblioteca não devem ser confundidas com etapas implementadas aqui.

Solicite credenciais nos portais de [IEEE](https://developer.ieee.org/), [Elsevier](https://dev.elsevier.com/) e [Clarivate](https://developer.clarivate.com/). Consulte as políticas de cada provedor para as demais bases. Quotas, elegibilidade, acesso institucional e limites podem mudar; possuir uma chave não garante acesso irrestrito.

## Configuração segura

O `findpapers.Engine()` do script utiliza a configuração por variáveis de ambiente. Não insira chaves reais no Python, no README ou em arquivos versionados.

### 1. Criar um arquivo local

Na pasta do projeto, crie `.env`:

```bash
nano .env
```

Preencha somente as variáveis que utilizar, substituindo os exemplos:

```bash
FINDPAPERS_IEEE_API_TOKEN='SUBSTITUA_PELA_CHAVE_IEEE'
FINDPAPERS_SCOPUS_API_TOKEN='SUBSTITUA_PELA_CHAVE_SCOPUS'
FINDPAPERS_WOS_API_TOKEN='SUBSTITUA_PELA_CHAVE_WOS'
FINDPAPERS_OPENALEX_API_TOKEN='SUBSTITUA_PELA_CHAVE_OPENALEX'
FINDPAPERS_SEMANTIC_SCHOLAR_API_TOKEN='SUBSTITUA_PELA_CHAVE_SEMANTIC_SCHOLAR'
FINDPAPERS_EMAIL='seu-email@exemplo.com'
```

Remova linhas de chaves que não possuir. Não deixe valores fictícios ativos. Proteja o arquivo e carregue as variáveis:

```bash
chmod 600 .env
set -a
source .env
set +a
```

**O script original não carrega `.env` automaticamente.** Execute esses comandos em cada nova sessão antes da busca. O arquivo deve conter apenas atribuições confiáveis: `source` interpreta seu conteúdo como comandos do shell.

Como alternativa, variáveis com `export` podem ser configuradas em `~/.zshrc` para Zsh ou no arquivo de inicialização apropriado do Bash. Evite manter configurações conflitantes em vários locais.

### 2. Verificar sem revelar as chaves

```bash
python - <<'PYTHON'
import os
for name in (
    'FINDPAPERS_IEEE_API_TOKEN',
    'FINDPAPERS_SCOPUS_API_TOKEN',
    'FINDPAPERS_WOS_API_TOKEN',
    'FINDPAPERS_OPENALEX_API_TOKEN',
    'FINDPAPERS_SEMANTIC_SCHOLAR_API_TOKEN',
    'FINDPAPERS_EMAIL',
):
    print(f"{name}: {'configurada' if os.getenv(name) else 'ausente'}")
PYTHON
```

Esse teste verifica apenas a presença da variável, não a validade da credencial.

## Estratégia de busca

A consulta combina três blocos obrigatórios por `AND`. Dentro de cada bloco, sinônimos são associados por `OR`:

| Bloco                          | Exemplos presentes no script                                                                                                            |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| Plataforma                     | `Instagram`                                                                                                                             |
| Marketing e comunicação        | `digital marketing`, `marketing digital`, `promotion`, `communication`, `engagement`, `outreach`                                        |
| Assuntos e serviços estudantis | `Centro de Assuntos Estudantis`, `Student Affairs`, `Student Services`, `Servicios Estudiantiles`, `Student Support`, `Vida Estudantil` |

A consulta integral está na variável `QUERY` do apêndice. A sintaxe utiliza termos entre colchetes e agrupamentos entre parênteses.

**Cuidados metodológicos:** termos como `Student Engagement`, `Student Development` e `communication` ampliam a recuperação, mas também podem trazer estudos sobre ensino ou comportamento estudantil sem relação direta com a atuação de um CAEST. A presença dos termos não comprova elegibilidade.

Os sinônimos em três idiomas não impõem um filtro de idioma. O script também não define intervalo de publicação, tipo documental ou limite de resultados. Registre qualquer alteração na consulta como uma nova estratégia de coleta.

## Preparação e execução

### 1. Criar o script

Copie o código do [apêndice](#apêndice-script-completo) para um arquivo chamado `pesquisar.py` na pasta `~/findpapers`. O apêndice preserva o código da seção “Versão Melhorada” do material de origem ou baixe o arquivo [pesquisar.py](https://github.com/MarcoAGP/findpapers_caest/blob/MarcoAGP/pesquisar.py) diretamente do repositório.

### 2. Escolher as bases

Se não tiver as credenciais obrigatórias, edite `DATABASES` para conter apenas as bases disponíveis. Um conjunto inicial previsto pela documentação do Findpapers é:

```python
DATABASES = ['arxiv', 'openalex', 'pubmed', 'semantic_scholar']
```

Confira também as regras vigentes dos provedores. Não apresente uma execução reduzida como consulta às sete bases.

### 3. Executar

```bash
cd ~/findpapers
source .venv/bin/activate
set -a
source .env
set +a
python -m py_compile pesquisar.py
python pesquisar.py
```

O comando de compilação verifica sintaxe, sem executar a pesquisa. Caso não use `.env`, omita as três linhas de carregamento e configure as variáveis pelo método escolhido.

Ao terminar:

```bash
ls -lh resultados/
cat resultados/resumo_busca.txt
```

O diretório `resultados` é relativo à pasta de execução, e não necessariamente à localização do script. Execute a partir da raiz do projeto. Uma nova execução reutiliza os mesmos nomes e pode sobrescrever resultados anteriores; preserve-os antes de repetir a coleta.

Para sair do ambiente virtual:

```bash
deactivate
```

## Arquivos de saída

| Arquivo                                 | Conteúdo e finalidade                                                                |
| --------------------------------------- | ------------------------------------------------------------------------------------ |
| `resultados/findpapers_raw_search.json` | Resultado bruto serializado pela biblioteca; criação tentada e status registrado     |
| `resultados/artigos.json`               | Registros normalizados, metadados da execução, consulta, bases e contagens           |
| `resultados/artigos.csv`                | Tabela de 17 colunas para análise em Excel, Python ou ferramentas de BI              |
| `resultados/artigos.bib`                | Exportação BibTeX dos objetos retornados; criação tentada e status registrado        |
| `resultados/artigos_completos.txt`      | Listagem legível de metadados e resumos; **não contém o texto integral dos artigos** |
| `resultados/resumo_busca.txt`           | Relatório da execução, ordenação, contagens e status das exportações                 |

O CSV utiliza vírgula como delimitador e `UTF-8 com BOM` (`utf-8-sig`). Se o Excel abrir tudo em uma coluna, importe por **Dados → De Texto/CSV**, selecionando UTF-8 e delimitador vírgula. Valores múltiplos dentro de uma célula usam ponto e vírgula.

O JSON tratado inclui `metadata`, `query`, `databases`, `total_papers`, `database_counts` e `papers`. O JSON bruto é importante porque a normalização exporta apenas parte dos campos disponíveis.

## Dicionário dos dados

| Coluna             | Significado                             | Observações                                           |
| ------------------ | --------------------------------------- | ----------------------------------------------------- |
| `title`            | Título                                  | Pode estar ausente                                    |
| `authors`          | Autores                                 | Nomes separados por `;`                               |
| `publication_date` | Data de publicação                      | Formato e precisão dependem da fonte                  |
| `doi`              | Identificador DOI                       | Pode estar ausente                                    |
| `url`              | Endereço do registro                    | Não garante acesso ao texto integral                  |
| `pdf_url`          | Endereço de PDF                         | Pode estar ausente ou indisponível                    |
| `language`         | Idioma informado                        | Não é tradução nem detecção local                     |
| `paper_type`       | Tipo documental                         | Conforme metadados retornados                         |
| `keywords`         | Palavras-chave                          | Valores separados por `;`                             |
| `found_in`         | Bases associadas ao artigo              | Nomes normalizados em minúsculas                      |
| `database_count`   | Quantidade de bases em `found_in`       | Não é contagem de duplicatas removidas                |
| `citations`        | Citações informadas                     | Pode variar entre fontes e datas                      |
| `is_open_access`   | Indicador de acesso aberto              | Ausência de valor não significa `False`               |
| `is_retracted`     | Indicador de retratação                 | Ausência de valor não comprova ausência de retratação |
| `reference_count`  | Tamanho da lista `references` retornada | Zero pode indicar dados não recuperados               |
| `cited_by_count`   | Tamanho da lista `cited_by` retornada   | Não necessariamente igual a `citations`               |
| `abstract`         | Resumo                                  | Pode estar ausente; não é texto integral              |

O script converte muitos valores ausentes em string vazia. As listas de referências e citações recebidas não são preservadas no JSON tratado: somente suas contagens. Consulte o bruto quando essas listas forem necessárias.

## Interpretação dos resultados

`total_papers` representa a quantidade de objetos em `result.papers`, após a consolidação da biblioteca. Ainda é recomendável revisar duplicatas residuais, principalmente quando faltam DOI ou metadados consistentes.

As contagens por base são calculadas a partir de `found_in` dos registros consolidados. Um artigo encontrado em três bases contribui uma vez para o total único e uma vez para cada uma dessas bases. **Somar as contagens por base não produz o total de artigos únicos.** Esses números também não equivalem aos totais brutos recuperados antes da deduplicação.

A ordenação aplicada é:

1. Maior `database_count`.
2. Maior `citations`, com valores ausentes ou inválidos tratados como zero apenas para ordenar.
3. Título em ordem alfabética.

Essa ordenação não mede qualidade metodológica nem aderência ao tema. A frequência em bases e o número de citações não substituem critérios de inclusão.

## Personalização

Edite as constantes e a chamada de busca no próprio `pesquisar.py`; o script não implementa argumentos de linha de comando.

| Configuração         | Local                | Efeito                                    |
| -------------------- | -------------------- | ----------------------------------------- |
| Termos e combinações | `QUERY`              | Define a estratégia temática              |
| Bases                | `DATABASES`          | Define os provedores solicitados          |
| Diretório            | `OUTPUT_DIR`         | Define onde os arquivos serão gravados    |
| Paralelismo          | `num_workers=4`      | Define o número de trabalhadores da busca |
| Mensagens            | `verbose=True`       | Habilita detalhes da execução             |
| Progresso            | `show_progress=True` | Habilita a indicação de progresso         |

Para gravar perto do script, substitua a definição do diretório por:

```python
OUTPUT_DIR = Path(__file__).resolve().parent / 'resultados'
```

Para separar execuções, use, antes de `OUTPUT_DIR.mkdir(...)`:

```python
OUTPUT_DIR = Path(__file__).resolve().parent / 'resultados' / datetime.now().strftime('%Y%m%d_%H%M%S')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
```

Nesse caso, substitua também a chamada original de `mkdir`. Para filtros temporais ou outros parâmetros, consulte a API da versão instalada antes de alterar `engine.search()`.

## Reprodutibilidade

Além dos arquivos gerados, preserve a versão exata do script, a revisão da dependência, as bases efetivamente acessíveis e eventuais falhas das APIs.

```bash
python --version
python -m pip show findpapers
python -m pip freeze > requirements-lock.txt
```

O arquivo de dependências registra o ambiente instalado; revise seu conteúdo antes de publicá-lo. A instalação a partir de Git deve registrar uma revisão identificável. Depois de obter e validar o hash, é possível fixá-lo no comando de instalação, substituindo `HASH_DO_COMMIT`:

```bash
python -m pip install 'git+https://github.com/jonatasgrosman/findpapers.git@HASH_DO_COMMIT'
```

O campo `findpapers_version` do script usa `__version__` e pode aparecer como `Desconhecida`. `pip show` e o registro da revisão complementam essa informação.

A duração registrada mede a chamada de busca, não todo o processamento e as exportações. A data usa o relógio local sem registrar o fuso horário. Informe o fuso separadamente no protocolo da pesquisa.

Para uso em revisão acadêmica, registre também os critérios de inclusão/exclusão, decisões de triagem e motivos de exclusão. O relatório gerado, sozinho, não constitui um protocolo completo de revisão sistemática.

## Solução de problemas

| Problema                          | Verificação e ação                                                                          |
| --------------------------------- | ------------------------------------------------------------------------------------------- |
| `python3` antigo ou incorreto     | Confira `command -v python3`; recrie o ambiente com o interpretador compatível              |
| `ModuleNotFoundError: findpapers` | Ative `.venv` e instale usando `python -m pip` no mesmo ambiente                            |
| Git ausente na instalação         | Verifique `git --version` e instale as ferramentas da Apple                                 |
| Erro 401 ou 403                   | Confira variável, validade da chave, permissões e acesso institucional                      |
| Erro 429                          | Aguarde a liberação da quota e reduza concorrência se necessário                            |
| Timeout ou erro 5xx               | Verifique conexão e disponibilidade do provedor; preserve a execução antes de repetir       |
| Nenhum resultado                  | Teste uma base e consulta menores; confira sintaxe, credenciais e restrição dos três blocos |
| `TypeError` em `Engine.search()`  | Compare os parâmetros com a API da revisão instalada                                        |
| JSON bruto ou BibTeX ausente      | Leia o status no terminal e em `resumo_busca.txt`; o script captura essas falhas            |
| CSV em uma coluna                 | Importe com delimitador vírgula e codificação UTF-8                                         |
| Resumos ou DOI vazios             | Confira o bruto; metadados podem não ter sido disponibilizados pela fonte                   |
| Resultados fora da pasta esperada | Confira o diretório atual com `pwd` ou use caminho baseado em `__file__`                    |
| Contagem zero em uma base         | Investigue logs; zero não distingue ausência de resultados de falha de acesso               |
| Erro de certificado SSL           | Confira data/hora, certificados do Python e configuração de rede; mantenha a validação TLS  |

As exportações CSV, JSON tratado e TXT não possuem tratamento individual de exceções. Falta de permissão ou espaço em disco pode interromper a execução. Uma mensagem final de conclusão também não comprova, por si só, que todos os provedores responderam integralmente.

## Publicação no GitHub

Salve este documento como **`README.md`**, na raiz do repositório. O nome convencional é `README.md`, sem ponto antes de `README`.

Organização sugerida, a ser criada pelo responsável:

| Caminho                 | Finalidade                         | Versionar?                                    |
| ----------------------- | ---------------------------------- | --------------------------------------------- |
| `README.md`             | Documentação                       | Sim                                           |
| `pesquisar.py`          | Código do apêndice                 | Sim                                           |
| `.gitignore`            | Exclusões de arquivos locais       | Sim                                           |
| `.env.example`          | Modelo sem segredos                | Sim                                           |
| `.env`                  | Credenciais reais                  | Não                                           |
| `requirements-lock.txt` | Ambiente validado                  | Sim, após revisão                             |
| `LICENSE`               | Licença escolhida pelo responsável | Após definição                                |
| `resultados/`           | Saídas da pesquisa                 | Somente após avaliar permissões e necessidade |

Crie `.gitignore` com:

```gitignore
.venv/
__pycache__/
*.py[cod]
.env
.env.*
!.env.example
.DS_Store
resultados/
*.log
```

Em `.env.example`, inclua apenas nomes de variáveis com valores vazios ou marcadores fictícios. Se uma chave já tiver sido enviada ao GitHub, adicionar `.gitignore` não a remove do histórico: revogue a credencial exposta e substitua-a.

Antes do commit, revise os arquivos e o conteúdo preparado:

```bash
git status
git diff --cached
```

A criação do README não implica publicação automática de um repositório.

## Limitações e melhorias

### Limitações identificadas no material

- A busca depende das APIs, permissões e metadados disponíveis no momento da coleta.
- Termos amplos aumentam a necessidade de triagem humana.
- Campos ausentes não são diferenciados de todos os tipos de erro de recuperação.
- `found_in` é usado para contagens consolidadas, sem relatório próprio de duplicatas removidas.
- Resultados de execuções sucessivas podem ser sobrescritos.
- O relatório lista bases solicitadas, sem um diagnóstico estruturado de sucesso por provedor.
- Exportações opcionais podem falhar sem interromper todo o fluxo.

### Melhorias propostas, ainda não implementadas

- Criar pastas por execução e registrar horário com fuso.
- Adicionar argumentos para consulta, bases, datas e diretório.
- Validar credenciais antes da coleta e registrar status por base.
- Preservar listas completas de referências no JSON tratado.
- Diferenciar valor ausente, zero e falha de recuperação.
- Criar testes com dados simulados, sem consumir quotas.
- Adicionar protocolo de triagem, sem confundir relevância temática com elegibilidade.

**Validação desta documentação:** análise estática do script e revisão de sua estrutura; não foi realizada busca real com credenciais nem validação ponta a ponta das APIs.

## Contribuições, créditos e licença

Para propor mudanças, descreva o problema, a versão do ambiente, o comportamento esperado e uma reprodução mínima sem segredos. Alterações de consulta ou critérios metodológicos devem explicar seu impacto sobre a recuperação dos estudos.

O motor de busca utilizado é o [Findpapers, de Jonatas Grosman e colaboradores](https://github.com/jonatasgrosman/findpapers). Consulte o projeto original para autoria, licença e orientações de citação.

O material fornecido não define uma licença para este projeto derivado. O responsável deve escolher e adicionar um arquivo `LICENSE` antes de declarar permissões de reutilização. A licença da dependência não define automaticamente a licença do script ou da documentação.

Ao citar a pesquisa, identifique seu repositório e versão, registre a data da coleta e cite também o Findpapers conforme as orientações do projeto original. Não foram atribuídos autor, DOI ou endereço de repositório próprios sem confirmação.

## Referências

- Material de origem: **02 Instalação e Configuração FindPaper**, fornecido com o script “Versão Melhorada”.
- [Findpapers — repositório e instalação](https://github.com/jonatasgrosman/findpapers).
- [Findpapers — bases de dados](https://github.com/jonatasgrosman/findpapers/blob/main/docs/databases.md).
- [Findpapers — configuração](https://github.com/jonatasgrosman/findpapers/blob/main/docs/configuration.md).
- [Findpapers — sintaxe de consulta](https://github.com/jonatasgrosman/findpapers/blob/main/docs/query-syntax.md).
- [Python — instaladores para macOS](https://www.python.org/downloads/macos/).

Documentação preparada em **15 de novembro de 2026**. Regras de acesso e APIs devem ser conferidas antes de novas coletas.

## Apêndice: script completo

Copie somente o conteúdo do bloco Python para `pesquisar.py`. O código abaixo foi preservado do material de origem; as melhorias propostas acima não foram aplicadas silenciosamente.

<details>
<summary>Expandir código de pesquisar.py</summary>

```python
import csv
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

import findpapers

# ============================================================
# CONFIGURAÇÃO DA PESQUISA
# ============================================================

QUERY = """
[Instagram] AND
(
    [digital marketing] OR
    [online marketing] OR
    [social media marketing] OR
    [marketing digital] OR
    [marketing nas redes sociais] OR
    [marketing em mídias sociais] OR
    [marketing en redes sociales] OR
    [marketing de redes sociales] OR
    [promotion] OR
    [communication] OR
    [engagement] OR
    [outreach] OR
    [digital communication] OR
    [social media strategy]
)
AND
(
    [Centro de Assuntos Estudantis] OR
    [Assuntos Estudantis] OR
    [Student Affairs Center] OR
    [Student Affairs] OR
    [Student Services] OR
    [Centro de Asuntos Estudiantiles] OR
    [Asuntos Estudiantiles] OR
    [Servicios Estudiantiles] OR
    [Student Support] OR
    [Student Support Services] OR
    [Student Engagement] OR
    [Student Life] OR
    [Student Development] OR
    [Student Welfare] OR
    [Apoio Estudantil] OR
    [Vida Estudantil] OR
    [Apoyo Estudiantil] OR
    [Vida Estudiantil]
)
"""

DATABASES = [
    "arxiv",
    "ieee",
    "openalex",
    "pubmed",
    "scopus",
    "semantic_scholar",
    "wos",
]

# ============================================================
# CONFIGURAÇÕES E AMBIENTE
# ============================================================

OUTPUT_DIR = Path("resultados")
OUTPUT_DIR.mkdir(exist_ok=True)

SEARCH_DATE = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
RAW_SEARCH_JSON = OUTPUT_DIR / "findpapers_raw_search.json"

PYTHON_VERSION = sys.version.split(" ")[0]
FINDPAPERS_VERSION = getattr(findpapers, "__version__", "Desconhecida")


# ============================================================
# FUNÇÕES AUXILIARES SEGURAS
# ============================================================

def safe(value, default=""):
    if value is None:
        return default
    return value

def get_field(paper, data_dict, field, default=""):
    value = getattr(paper, field, None)
    if value is None and isinstance(data_dict, dict):
        value = data_dict.get(field)
    return safe(value, default)

def normalize_list(value):
    if not value:
        return []
    if isinstance(value, str):
        return [value]
    try:
        return list(value)
    except TypeError:
        return [value]

def get_authors(paper, data_dict=None):
    authors = getattr(paper, "authors", None)
    if authors is None and isinstance(data_dict, dict):
        authors = data_dict.get("authors")

    if not authors:
        return ""

    if isinstance(authors, str):
        return authors.strip()

    names = []
    for author in normalize_list(authors):
        if isinstance(author, dict):
            name = author.get("name", "")
        else:
            name = getattr(author, "name", str(author))

        if name:
            names.append(str(name).strip())

    return "; ".join(names)

def paper_to_dict(paper):
    data = {}
    try:
        dict_data = paper.to_dict()
        if isinstance(dict_data, dict):
            data = dict_data
    except Exception:
        pass
    return data


# ============================================================
# INICIALIZAÇÃO E BUSCA
# ============================================================

print("\n" + "=" * 80)
print("FINDPAPERS — BUSCA BIBLIOGRÁFICA MULTIBASE")
print("=" * 80)
print(f"\nData da pesquisa: {SEARCH_DATE}")
print(f"Versão Python: {PYTHON_VERSION}")
print(f"Versão Findpapers: {FINDPAPERS_VERSION}\n")
print("BASES:")
for database in DATABASES:
    print(f"  ✓ {database}")
print("\nCONSULTA:\n", QUERY)
print("\n" + "=" * 80 + "\nINICIANDO BUSCA...\n" + "=" * 80 + "\n")

engine = findpapers.Engine()
start_time = time.perf_counter()

try:
    result = engine.search(
        QUERY,
        databases=DATABASES,
        num_workers=4,
        verbose=True,
        show_progress=True,
    )
except Exception as e:
    print(f"ERRO CRÍTICO durante a pesquisa: {type(e).__name__}: {e}")
    sys.exit(1)

elapsed_seconds = time.perf_counter() - start_time
search_duration = str(timedelta(seconds=round(elapsed_seconds)))


# ============================================================
# PERSISTÊNCIA DO RAW ORIGINAL
# ============================================================

raw_status = ""
try:
    findpapers.save_to_json(result, str(RAW_SEARCH_JSON))
    raw_status = "OK"
except Exception as e:
    raw_status = f"{type(e).__name__}: {e}"
    print(f"AVISO: não foi possível salvar o resultado bruto: {raw_status}")

papers = result.papers
total_papers = len(papers)


# ============================================================
# PROCESSAMENTO DE RESULTADOS
# ============================================================

print("\n\n" + "=" * 80 + "\nRESULTADOS\n" + "=" * 80)
print(f"\nTempo de busca: {search_duration}")
print(f"Total de artigos únicos consolidados: {total_papers}")

database_counts = {database: 0 for database in DATABASES}
paper_data = []

for paper in papers:
    data = paper_to_dict(paper)

    # Extração de campos complexos normalizados (priorizando found_in)
    raw_found_in = get_field(paper, data, "found_in") or get_field(paper, data, "databases")
    found_in_list = normalize_list(raw_found_in)

    found_in_normalized = sorted({str(db).strip().lower() for db in found_in_list if db})

    for db_name in found_in_normalized:
        if db_name in database_counts:
            database_counts[db_name] += 1

    keywords_list = normalize_list(get_field(paper, data, "keywords"))
    references_list = normalize_list(get_field(paper, data, "references"))
    cited_by_list = normalize_list(get_field(paper, data, "cited_by"))

    record = {
        "title": get_field(paper, data, "title"),
        "authors": get_authors(paper, data),
        "publication_date": get_field(paper, data, "publication_date"),
        "doi": get_field(paper, data, "doi"),
        "url": get_field(paper, data, "url"),
        "pdf_url": get_field(paper, data, "pdf_url"),
        "abstract": get_field(paper, data, "abstract"),
        "keywords": "; ".join(str(k) for k in keywords_list),
        "language": get_field(paper, data, "language"),
        "paper_type": get_field(paper, data, "paper_type"),
        "found_in": "; ".join(found_in_normalized),
        "database_count": len(found_in_normalized),
        "citations": get_field(paper, data, "citations"),
        "is_open_access": get_field(paper, data, "is_open_access"),
        "is_retracted": get_field(paper, data, "is_retracted"),
        "reference_count": len(references_list),
        "cited_by_count": len(cited_by_list),
    }
    paper_data.append(record)

print("\nARTIGOS ÚNICOS IDENTIFICADOS POR BASE:")
for database, count in database_counts.items():
    print(f"  {database:20} {count:>5} artigos")


# ============================================================
# ORDENAÇÃO
# ============================================================

def citation_value(record):
    try:
        return int(float(record.get("citations") or 0))
    except (ValueError, TypeError):
        return 0

paper_data.sort(
    key=lambda x: (
        -x["database_count"],
        -citation_value(x),
        str(x["title"]).lower() if x["title"] else ""
    )
)


# ============================================================
# EXPORTAÇÕES CUSTOMIZADAS
# ============================================================

# 1 — JSON COMPLETO TRATADO
json_file = OUTPUT_DIR / "artigos.json"
with open(json_file, "w", encoding="utf-8") as f:
    json.dump({
        "metadata": {
            "search_date": SEARCH_DATE,
            "search_duration": search_duration,
            "search_duration_seconds": round(elapsed_seconds, 2),
            "python_version": PYTHON_VERSION,
            "findpapers_version": FINDPAPERS_VERSION
        },
        "query": QUERY,
        "databases": DATABASES,
        "total_papers": total_papers,
        "database_counts": database_counts,
        "papers": paper_data,
    }, f, ensure_ascii=False, indent=2, default=str)

# 2 — CSV TRATADO
csv_file = OUTPUT_DIR / "artigos.csv"
csv_fields = [
    "title", "authors", "publication_date", "doi", "url", "pdf_url",
    "language", "paper_type", "keywords", "found_in", "database_count",
    "citations", "is_open_access", "is_retracted", "reference_count",
    "cited_by_count", "abstract"
]
with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(paper_data)

# 3 — BIBTEX
bib_file = OUTPUT_DIR / "artigos.bib"
bib_status = ""
try:
    findpapers.save_to_bibtex(papers, str(bib_file))
    bib_status = "OK"
except Exception as e:
    bib_status = f"{type(e).__name__}: {e}"

# 4 — TEXTO COMPLETO (READABLE)
txt_file = OUTPUT_DIR / "artigos_completos.txt"
with open(txt_file, "w", encoding="utf-8") as f:
    f.write("=" * 80 + "\nARTIGOS ENCONTRADOS — FINDPAPERS\n" + "=" * 80 + "\n\n")
    f.write(f"Data da busca: {SEARCH_DATE}\n")
    f.write(f"Tempo de execução: {search_duration}\n")
    f.write(f"Total de artigos únicos consolidados: {total_papers}\n\n")
    f.write("CONSULTA:\n" + QUERY + "\n\n")
    f.write("=" * 80 + "\n\n")

    for i, record in enumerate(paper_data, start=1):
        title = record.get("title") or "Sem título"
        f.write(f"{i}. {title}\n")
        f.write(f"Autores: {record.get('authors')}\n")
        f.write(f"Data: {record.get('publication_date')}\n")
        f.write(f"DOI: {record.get('doi')}\n")
        f.write(f"URL: {record.get('url')}\n")
        f.write(f"PDF: {record.get('pdf_url')}\n")
        f.write(f"Idioma: {record.get('language')}\n")
        f.write(f"Tipo: {record.get('paper_type')}\n")
        f.write(f"Palavras-chave: {record.get('keywords')}\n")
        f.write(f"Encontrado em: {record.get('found_in')}\n")
        f.write(f"Número de bases: {record.get('database_count')}\n")
        f.write(f"Citações: {record.get('citations')}\n")
        f.write(f"Acesso aberto: {record.get('is_open_access')}\n")
        f.write(f"Retratado: {record.get('is_retracted')}\n")
        f.write(f"\nRESUMO:\n{record.get('abstract')}\n\n")
        f.write("-" * 80 + "\n\n")

# 5 — RELATÓRIO DA BUSCA
summary_file = OUTPUT_DIR / "resumo_busca.txt"
with open(summary_file, "w", encoding="utf-8") as f:
    f.write("RELATÓRIO DA BUSCA BIBLIOGRÁFICA\n")
    f.write("=" * 70 + "\n\n")
    f.write(f"Data: {SEARCH_DATE}\n")
    f.write(f"Tempo de execução: {search_duration}\n")
    f.write(f"Python version: {PYTHON_VERSION}\n")
    f.write(f"Findpapers version: {FINDPAPERS_VERSION}\n")
    f.write(f"\nTotal de artigos únicos consolidados: {total_papers}\n\n")

    f.write("BASES CONSULTADAS:\n")
    for database in DATABASES:
        f.write(f"- {database}\n")
    f.write("\n")

    f.write("ARTIGOS ÚNICOS IDENTIFICADOS POR BASE:\n")
    for database, count in database_counts.items():
        f.write(f"{database}: {count} artigos\n")

    f.write("\nCRITÉRIO DE ORDENAÇÃO DOS RESULTADOS:\n")
    f.write("1. Maior número de bases em que o artigo foi identificado\n")
    f.write("2. Maior número de citações\n")
    f.write("3. Título em ordem alfabética\n\n")

    f.write(f"\nCONSULTA UTILIZADA:\n{QUERY}\n")

    f.write("\n" + "=" * 70 + "\n")
    f.write("ARQUIVOS GERADOS\n")
    f.write("=" * 70 + "\n\n")
    f.write(f"RAW: {RAW_SEARCH_JSON} — {raw_status}\n")
    f.write(f"CSV: {csv_file}\n")
    f.write(f"JSON tratado: {json_file}\n")
    f.write(f"BibTeX: {bib_file} — {bib_status}\n")
    f.write(f"Texto completo: {txt_file}\n")
    f.write(f"Relatório da busca: {summary_file}\n")


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 80 + "\nPESQUISA FINALIZADA\n" + "=" * 80)
print(f"\nTempo total de busca: {search_duration}")
print(f"Total de artigos únicos: {total_papers}\n\nARQUIVOS GERADOS:")

if raw_status == "OK":
    print(f"  ✓ {RAW_SEARCH_JSON} (RAW original)")
else:
    print(f"  ✗ {RAW_SEARCH_JSON} não gerado. Erro: {raw_status}")

print(f"  ✓ {csv_file}")
print(f"  ✓ {json_file}")
print(f"  ✓ {txt_file}")
print(f"  ✓ {summary_file}")

if bib_status == "OK":
    print(f"  ✓ {bib_file}")
else:
    print(f"  ✗ {bib_file} não gerado. Erro: {bib_status}")
```

</details>
