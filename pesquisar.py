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
    raw_found_in = get_field(paper, data, "found_in") or get_field(
        paper, data, "databases"
    )
    found_in_list = normalize_list(raw_found_in)

    found_in_normalized = sorted(
        {str(db).strip().lower() for db in found_in_list if db}
    )

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
        str(x["title"]).lower() if x["title"] else "",
    )
)


# ============================================================
# EXPORTAÇÕES CUSTOMIZADAS
# ============================================================

# 1 — JSON COMPLETO TRATADO
json_file = OUTPUT_DIR / "artigos.json"
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(
        {
            "metadata": {
                "search_date": SEARCH_DATE,
                "search_duration": search_duration,
                "search_duration_seconds": round(elapsed_seconds, 2),
                "python_version": PYTHON_VERSION,
                "findpapers_version": FINDPAPERS_VERSION,
            },
            "query": QUERY,
            "databases": DATABASES,
            "total_papers": total_papers,
            "database_counts": database_counts,
            "papers": paper_data,
        },
        f,
        ensure_ascii=False,
        indent=2,
        default=str,
    )

# 2 — CSV TRATADO
csv_file = OUTPUT_DIR / "artigos.csv"
csv_fields = [
    "title",
    "authors",
    "publication_date",
    "doi",
    "url",
    "pdf_url",
    "language",
    "paper_type",
    "keywords",
    "found_in",
    "database_count",
    "citations",
    "is_open_access",
    "is_retracted",
    "reference_count",
    "cited_by_count",
    "abstract",
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
