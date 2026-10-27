# tesouro-direto-fetcher

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square) ![Python](https://img.shields.io/badge/python-3.12+-blue.svg?style=flat-square) [![Tests](https://github.com/Quantilica/tesouro-direto-fetcher/actions/workflows/run-tests.yml/badge.svg)](https://github.com/Quantilica/tesouro-direto-fetcher/actions/workflows/run-tests.yml)

Biblioteca Python para download, leitura e visualização de dados históricos do Tesouro Direto via API CKAN (Tesouro Transparente). Fornece leitores especializados por tipo de dataset e gráficos prontos com Altair.

Para a documentação completa, visite [https://docs.quantilica.com](https://docs.quantilica.com).

## Instalação

Pela CLI unificada (recomendado):

```bash
quantilica install td
# com o extra de análise (comandos convert e pipeline):
quantilica install td --extra analysis
```

Como biblioteca num projeto, a partir do índice próprio (este pacote não é publicado no PyPI):

```bash
uv add tesouro-direto-fetcher --index https://index.quantilica.com/simple/
# com o extra de análise:
uv add 'tesouro-direto-fetcher[analysis]' --index https://index.quantilica.com/simple/
```

## Uso Rápido

```python
import asyncio
from pathlib import Path
from tesouro_direto_fetcher import downloader, reader

# Download dos dados de preços/taxas
asyncio.run(
    downloader.download(
        dest_dir=Path("./dados"),
        dataset_id="taxas-dos-titulos-ofertados-pelo-tesouro-direto",
    )
)

# Leitura
df_precos = reader.read_prices(
    Path("./dados/taxas-dos-titulos-ofertados-pelo-tesouro-direto@20251230T102010.csv")
)
```

## CLI

Consulte [docs/CLI.md](docs/CLI.md) para a referência completa de comandos, opções e exemplos.

## API Python

### Download assíncrono

```python
import asyncio
from pathlib import Path
from tesouro_direto_fetcher import downloader

asyncio.run(
    downloader.download(
        dest_dir=Path("./dados"),
        dataset_id="taxas-dos-titulos-ofertados-pelo-tesouro-direto",
        max_concurrency=3,
    )
)
```

### Leitura

```python
from pathlib import Path
from tesouro_direto_fetcher import reader

df_precos      = reader.read_prices(Path("./dados/taxas-...@....csv"))
df_estoque     = reader.read_stock(Path("./dados/estoque-...@....csv"))
df_investidores = reader.read_investors(Path("./dados/investidores-...@....csv"))
```

### Conversão para o lake (Parquet)

Com o extra `analysis`, os microdados de **investidores** e **operações** são convertidos para um lake de arquivos Parquet particionado no estilo Hive (`chave=valor/`), legível diretamente por DuckDB, Polars, PyArrow e Spark:

```bash
tesouro-direto-fetcher convert -i ./dados --lake ./lake
# apenas um dataset (nome completo ou alias: investidores, operacoes):
tesouro-direto-fetcher convert -i ./dados --lake ./lake --dataset operacoes
# baixar e converter em sequência:
tesouro-direto-fetcher pipeline -o ./dados --lake ./lake
```

- `-i/--input`: diretório dos CSVs baixados (a árvore `<dataset_id>/` criada por `sync`).
- `--lake`: raiz do lake (padrão: variável de ambiente `QUANTILICA_LAKE_DIR`).
- `--dataset`: limita a conversão a um ou mais datasets (repetível).
- `--force`: reconverte mesmo que o arquivo já esteja no lake.

Layout gerado — um Parquet por CSV, com a partição `periodo` derivada do nome do arquivo (`...-de-2019` → `periodo=2019`; `...-ate-2017` → `periodo=ate-2017`):

```text
lake/tesouro-direto/investidores-do-tesouro-direto/
  _dataset.json
  periodo=ate-2017/investidores-do-tesouro-direto-ate-2017.parquet
  periodo=2019/investidores-do-tesouro-direto-de-2019.parquet
lake/tesouro-direto/operacoes-do-tesouro-direto/
  periodo=2019/operacoes-do-tesouro-direto-de-2019.parquet
```

As colunas são gravadas como texto, com nomes normalizados (`Código do Investidor` → `codigo_do_investidor`; `idade` → `idade_do_investidor` em investidores). A coluna `periodo` não fica dentro do Parquet: o leitor a obtém do nome do diretório.

A conversão é idempotente: um CSV cujo `sha256` já está no lake é pulado, e uma nova publicação do mesmo período substitui o Parquet anterior em vez de acumular arquivos. CSVs sem as colunas esperadas (por exemplo, uma página HTML de erro salva como CSV) são recusados e listados no relatório final, e o comando sai com código 1.

```python
import polars as pl

df = pl.scan_parquet(
    "lake/tesouro-direto/operacoes-do-tesouro-direto/**/*.parquet",
    hive_partitioning=True,
).collect()
```

> **Mudança na versão 4.0:** a saída de `convert` deixou de ser um `.parquet` ao lado de cada CSV. Veja o [CHANGELOG](CHANGELOG.md).

### Visualização

```python
from tesouro_direto_fetcher import plot

plot.plot_prices(df_precos, bond_type="Tesouro Selic").save("precos.html")
plot.plot_stock(df_estoque, by_bond_type=True).save("estoque.html")
plot.plot_investors_population_pyramid(df_investidores).save("piramide.html")
```

Helpers disponíveis: `plot_investors_evolution`, `plot_operations`, `plot_sales`, `plot_buybacks`, `plot_maturities`, `plot_interest_coupons`. Veja [docs/PLOTS.md](docs/PLOTS.md).

## Fontes de Dados

Todos os dados são obtidos via [API CKAN do Tesouro Transparente](https://www.tesourotransparente.gov.br/ckan/):

| Dataset | ID CKAN |
| :--- | :--- |
| Preços / Taxas | `taxas-dos-titulos-ofertados-pelo-tesouro-direto` |
| Estoque | `estoque-do-tesouro-direto` |
| Investidores | `investidores-do-tesouro-direto` |
| Operações | `operacoes-do-tesouro-direto` |
| Vendas | `vendas-do-tesouro-direto` |
| Recompras | `recompras-do-tesouro-direto` |

## Desenvolvimento

```bash
git clone https://github.com/Quantilica/tesouro-direto-fetcher.git
cd tesouro-direto-fetcher
uv sync --dev
uv run pytest
```

## Licença

MIT — veja [LICENSE](LICENSE).
