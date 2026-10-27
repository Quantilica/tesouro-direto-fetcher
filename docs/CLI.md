# tesouro-direto-fetcher CLI Documentation

## Overview

The `tesouro-direto-fetcher` command-line interface (CLI) provides a
convenient way to download, inspect, and convert Brazilian Tesouro Direto data
from the official CKAN API. The CLI exposes three commands: `sync` (download),
`convert` (CSV → Parquet lake) and `pipeline` (sync → convert chained).

## Installation

The CLI is included with the `tesouro-direto-fetcher` package. Install it using
one of the following methods:

**Minimal installation (download only):**
```bash
pip install "git+https://github.com/Quantilica/tesouro-direto-fetcher#egg=tesouro-direto-fetcher"
```

**Full installation (with analysis features):**
```bash
pip install "git+https://github.com/Quantilica/tesouro-direto-fetcher#egg=tesouro-direto-fetcher[analysis]"
```

The `analysis` extras are required for the `convert` and `pipeline` commands.

## General Usage

```bash
tesouro-direto-fetcher <command> [options]
```

### Available Commands

- `sync` - Sync datasets from the Tesouro Transparente CKAN API
- `convert` - Convert downloaded investor and operation CSVs to a Hive-partitioned Parquet lake (requires analysis extras)
- `pipeline` - Run the full pipeline: sync → convert

### Global Options

- `-h, --help` - Show help message and exit
- `--version` - Show the package version and exit
- `--verbose` - Exibir logs detalhados em vez de barra de progresso

## Commands

### `sync`

Sync one or more datasets to a local directory. The download is idempotent —
files already up-to-date (per CKAN `Last-Modified`) are skipped.

**Syntax:**
```bash
tesouro-direto-fetcher sync [-o OUTPUT_DIR] [--dataset DATASET] [--dry-run]
```

**Options:**

- `-o OUTPUT_DIR, --output OUTPUT_DIR`
  - Output directory for downloaded files
  - Type: Path
  - Default: `/data/tesouro-direto`

- `--dataset DATASET`
  - Dataset to sync
  - Choices: `prices`, `operations`, `investors`, `stock`, `buybacks`,
    `sales`, `all`
  - Default: `all` (syncs every dataset sequentially)

- `--dry-run`
  - List the files that would be downloaded (resources, sizes, modification
    dates, and whether each file is up-to-date) without writing anything.

**Examples:**

```bash
# Sync every dataset (default)
tesouro-direto-fetcher sync -o ./data

# Sync a single dataset
tesouro-direto-fetcher sync --dataset prices -o ./data

# Preview what would be downloaded, without downloading
tesouro-direto-fetcher sync --dataset prices --dry-run -o ./data

# Verbose logs instead of the progress bar
tesouro-direto-fetcher sync --verbose -o ./data
```

Files are saved with timestamps in their filenames (e.g.,
`taxas-dos-titulos-ofertados-pelo-tesouro-direto@20251230T102010.csv`).

### `convert`

Convert the most recent investor and operation CSVs under a data directory tree
into a Hive-partitioned Parquet lake. This command is only available when the
`analysis` optional dependencies are installed.

**Syntax:**
```bash
tesouro-direto-fetcher convert [-i INPUT] [--lake LAKE] [--dataset DATASET]... [--force]
```

**Options:**

- `-i INPUT, --input INPUT` — directory with the downloaded CSVs (root of the
  `<dataset_id>/` tree produced by `sync`)
- `--lake LAKE` (aliases `-o`, `--output`) — lake root (default: the
  `QUANTILICA_LAKE_DIR` environment variable)
- `--dataset DATASET` — convert only this dataset; repeatable. Accepts
  `investidores-do-tesouro-direto` / `investidores` and
  `operacoes-do-tesouro-direto` / `operacoes`
- `--force` — reconvert even if the file's `sha256` is already in the lake
- `--verbose` — detailed logs

**Examples:**

```bash
tesouro-direto-fetcher convert -i ./data --lake ./lake
tesouro-direto-fetcher convert -i ./data --lake ./lake --dataset operacoes --force
```

Output layout, one Parquet per CSV, partitioned by the period in the file name:

```text
<lake>/tesouro-direto/<dataset_id>/_dataset.json
<lake>/tesouro-direto/<dataset_id>/periodo=<2019|ate-2017>/<file>.parquet
```

Already converted files are skipped; files whose header lacks the expected
columns (e.g. an HTML error page saved as CSV) are rejected and listed in the
final report, and the command exits with code 1.

### `pipeline`

Run the full pipeline in one command: `sync` followed by `convert`. Use
`--lake` to choose the lake root (default: `QUANTILICA_LAKE_DIR`).

**Syntax:**
```bash
tesouro-direto-fetcher pipeline [-o OUTPUT_DIR] [--dataset DATASET]
```

**Options:**

- `-o OUTPUT_DIR, --output OUTPUT_DIR` — output directory (default:
  `/data/tesouro-direto`)
- `--dataset DATASET` — dataset to sync (default: `all`)

**Example:**

```bash
tesouro-direto-fetcher pipeline -o ./data
```

## Dataset Types

The following dataset types are supported:

- `prices` - Daily price rates for all Tesouro Direto bonds
- `operations` - Individual buy/sell operations by investors
- `investors` - Demographic data about Tesouro Direto investors
- `stock` - Current stock/holdings of Tesouro Direto bonds
- `buybacks` - Bond redemption/buyback operations
- `sales` - Bond sales data

## Error Handling

### Exit Codes

- `0` - Success
- `1` - Error (invalid arguments, file not found, network issues, etc.)
- `130` - Interrupted (Ctrl+C)

### Common Errors

**Convert command not available:**
```
Erro: convert requer extras de análise: quantilica install td --extra analysis
```
**Solution:** Install with analysis extras: `pip install "git+https://github.com/Quantilica/tesouro-direto-fetcher#egg=tesouro-direto-fetcher[analysis]"`

**Invalid dataset:**
```
Erro: dataset inválido 'invalid'. Opções: prices, operations, investors, stock, buybacks, sales, all
```
**Solution:** Use one of the valid dataset choices listed in the error message.

## See Also

- [README.md](../README.md) - General package documentation
- [Tesouro Transparente CKAN API](https://www.tesourotransparente.gov.br/ckan/) - Official data source
