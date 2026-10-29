# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [4.1.0] - 2026-10-29

### Adicionado
- O conversor do lake passa a cobrir estoque (`estoque`), taxas dos títulos ofertados
  (`taxas`), vendas (`vendas`) e, a partir da pasta de resgates, pagamento de cupom
  (`cupons`), recompras (`recompras`) e vencimentos (`vencimentos`), cada um como um
  retrato único, sem a partição `periodo`.

## [4.0.0] - 2026-10-27

### Alterado
- **Incompatível:** `convert` deixa de gravar um `.parquet` ao lado de cada CSV e passa a escrever num lake de Parquet particionado no estilo Hive: `<lake>/tesouro-direto/<dataset_id>/periodo=<periodo>/<arquivo>.parquet`. Só os microdados de investidores e de operações são convertidos; a partição `periodo` vem do nome do arquivo (`...-de-2019` → `periodo=2019`, `...-ate-2017` → `periodo=ate-2017`) e não é gravada dentro do Parquet. Cada dataset ganha um `_dataset.json` com o descritor, e cada Parquet leva os metadados de proveniência (`quantilica.*`). Não há modo de layout antigo; reconverta os CSVs no novo layout.
- **Incompatível:** `convert` e `pipeline` passam a usar os comandos padrão do ecossistema. Em vez do argumento posicional `<data_dir>`, `convert` recebe `-i/--input` (diretório dos CSVs), `--lake` (raiz do lake, com `-o/--output` como sinônimo; padrão `QUANTILICA_LAKE_DIR`), `--dataset` (repetível) e `--force`. `pipeline` ganha `--lake` (`--parquet-dir` segue aceito). O relatório final mostra arquivos convertidos, pulados e com erro, e o comando sai com código 1 se houver erro.
- As colunas do lake são gravadas como texto, com nomes normalizados; em investidores, `idade` é renomeada para `idade_do_investidor`.

### Adicionado
- `tesouro_direto_fetcher.lake` (requer o extra `analysis`): `converter.convert(input_dir, lake_dir, datasets=None, force=False)` devolve as contagens `converted` e `skipped` e a lista `errors`.
- Idempotência por `sha256`: um CSV já presente no lake com o mesmo `sha256` é pulado, e uma nova publicação do mesmo período substitui o Parquet anterior em vez de acumular arquivos.
- CSVs sem as colunas obrigatórias (por exemplo, uma página HTML de erro salva como CSV) são recusados sem interromper os demais arquivos.
- Ponto de entrada `quantilica.lake` (`tesouro-direto`), para ferramentas localizarem o conversor sem importar o pacote.
- Dependência `quantilica-core` atualizada para `>=0.13.0` e, no extra `analysis`, `quantilica-analytics` para `>=0.5.0`: são as primeiras versões com o contrato e o escritor do lake.

## [3.2.4] - 2026-10-20

### Corrigido
- Sem o extra `analysis`, importar `tesouro_direto_fetcher.reader`, `.analytics`, `.fast_returns`, `.plot` ou `.converter` levantava `ModuleNotFoundError` cru (ou, no `converter`, uma mensagem em inglês em outro formato). Agora todos levantam `ImportError` acionável no padrão do ecossistema: `<módulo> requer o extra 'analysis': uv add 'tesouro-direto-fetcher[analysis]' --index https://index.quantilica.com/simple/`. Com o extra instalado, nada muda.
- `make_plots.py`: linhas longas quebradas (E501).

## [3.2.3] - 2026-10-20

### Corrigido
- Injeção de metadados de proveniência (`quantilica.*`) no esquema Parquet em `to_parquet`.
- Remoção de duplicidades em `analytics.py`.
- `src/tesouro_direto_fetcher/py.typed` esvaziado conforme PEP 561.

### Alterado
- Dependências atualizadas: `quantilica-core>=0.12.0` e `quantilica-analytics>=0.4.0`.

## [3.2.2] - 2026-10-14

### Corrigido
- `plugin.py`: a dica de instalação do extra `analysis` mandava `pip install tesouro-direto-fetcher[analysis]`, que não funciona para fetchers do Fluxo B (fora do PyPI), e o Rich ainda engolia o `[analysis]` por tratá-lo como marcação, deixando só `pip install tesouro-direto-fetcher`. Agora a mensagem é `quantilica install td --extra analysis`.
- `cli.py`: mensagem do guard corrigida para `quantilica install td` (chave
  canônica do registro; `tesouro-direto` não resolve para a distribuição).

### Alterado
- `README.md`: a seção de instalação deixa de mandar `pip install` (fetchers do Fluxo B não estão no PyPI) e passa a mostrar `quantilica install td` (com `--extra analysis`) e `uv add --index` para uso como biblioteca.
- `cli.py` protege o import do plugin; sem o host a CLI standalone sai com código 1 e orienta `quantilica install td`.
- `cli.py`: removido `configure_cli_logging` do wrapper (o plugin já configura
  logging via `setup_rich_logging` em todos os comandos).

## [3.2.1] - 2026-08-31
### Corrigido
- Quitação de dívida de lint: E501 em docstrings/comentários, `zip()` agora com `strict=False` explícito (B905, sem mudança de comportamento), variável de loop não usada renomeada (B007).

## [3.2.0] - 2026-08-07
### Alterado
- Refatoração arquitetural: Remoção de dependências (`quantilica-cli` e `quantilica-catalog`) e limpeza de imports. Os fetchers agora são pacotes de extração puros, dependendo estritamente do `quantilica-core`.

## [3.0.2] - 2026-07-29

### Corrigido

- Correção de importação do conversor na ausência de extras de análise, lançando ImportError em vez de AttributeError.
- Adicionadas verificações SkipTest no unittest em testes que dependem de polars para evitar quebras em ambientes de CI onde extras de análise não estão instalados.

## [3.0.1] - 2026-07-29

### Corrigido

- Correção de inferência do dataset de recompras, mapeando a palavra-chave "recompras" no nome do arquivo para o leitor `read_buybacks`.
- Implementação de tratamento de fallback dinâmico para o diretório padrão de saída se `/data` não for gravável.
- Resiliência na renomeação de colunas do Polars no método `_process` do leitor e mapeamento da nova coluna de data de liquidação de venda (`"Data de Liquidacao da Venda"`).

## [3.0.0] - 2026-05-19

Primeira entrada em formato Keep a Changelog; documenta o estado do pacote nesta
versão.

### Adicionado

- Download assíncrono de dados históricos do Tesouro Direto via API CKAN (Tesouro
  Transparente), com leitores especializados por tipo de dataset.
- Gráficos prontos com Altair (extra opcional `[analysis]`, que adiciona Polars e
  Altair).

### Histórico anterior

Versões até a 3.0.0 antecedem a adoção deste changelog e estão registradas nas
tags do repositório: 2.1.1 (2026-02-09), 2.0.0 (2026-01-31), 1.1.2 (2026-01-07),
1.0.0 (2025-12-31), 0.2.2 (2024-03-09), 0.1.0 (2020-05-13).
