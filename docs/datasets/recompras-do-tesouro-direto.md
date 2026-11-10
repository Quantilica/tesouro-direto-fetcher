---
dataset:
  id: "recompras-do-tesouro-direto"
  fonte: "tesouro-direto"
  titulo: "Recompras do Tesouro Direto"
  resumo: "Títulos entregues pelo investidor antes do vencimento (recompras), por título, vencimento e data."
  orgao: "Tesouro Nacional (STN/MF), Coordenação-Geral do Tesouro Direto (COTED), via Tesouro Transparente"
  pagina_oficial: "https://www.tesourotransparente.gov.br/ckan/dataset/resgates-do-tesouro-direto"
  licenca: "Licença Aberta para Bases de Dados (ODbL) do Open Data Commons, declarada no catálogo do Tesouro Transparente: http://www.opendefinition.org/licenses/odc-odbl"
  periodicidade: "diária, com dados até dois dias antes da extração"
  cobertura: {inicio: "2005-01", fim: "em-curso"}
  unidade: "resgate de um título (tipo e vencimento) em uma data"
  granularidade: {espacial: "Brasil", temporal: "dia"}
  formato_bruto: "CSV em UTF-8, separador ponto e vírgula, decimal com vírgula, datas DD/MM/AAAA; um arquivo com toda a série"
  lake: {estado: convertido, particoes: [], chave: [tipo_titulo, vencimento_do_titulo, data_resgate], colunas: 5}
  unidades_de_medida:
    quantidade: "títulos"
    valor: "R$"
  dados_pessoais: "nenhum"
  eras: []
  revisado_em: "2026-11-10"
  versao_fetcher: "5.0.0"
---

# Recompras do Tesouro Direto

## Resumo

Títulos entregues pelo investidor antes do vencimento (recompras), por título, vencimento e data.

Os três arquivos de resgates (cupom, recompras e vencimentos) vêm do mesmo conjunto da fonte e são datasets separados no lake.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `tesouro-direto/recompras-do-tesouro-direto` |
| Órgão | Tesouro Nacional (STN/MF), Coordenação-Geral do Tesouro Direto (COTED), via Tesouro Transparente |
| Página oficial | https://www.tesourotransparente.gov.br/ckan/dataset/resgates-do-tesouro-direto |
| Licença | Licença Aberta para Bases de Dados (ODbL) do Open Data Commons, declarada no catálogo do Tesouro Transparente: http://www.opendefinition.org/licenses/odc-odbl |
| Periodicidade | diária, com dados até dois dias antes da extração |
| Cobertura | 2005-01 a em-curso |
| Unidade (uma linha) | resgate de um título (tipo e vencimento) em uma data |
| Granularidade | espacial: Brasil; temporal: dia |
| Formato bruto | CSV em UTF-8, separador ponto e vírgula, decimal com vírgula, datas DD/MM/AAAA; um arquivo com toda a série |
| Estado no lake | convertido |
| Partições | — |
| Chave | `tipo_titulo`, `vencimento_do_titulo`, `data_resgate` |
| Colunas | 5 |
| Unidades de medida | `quantidade`: títulos; `valor`: R$ |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 5.0.0 |

## Origem e coleta

- O fetcher consulta o catálogo CKAN do Tesouro Transparente (conjunto `resgates-do-tesouro-direto`), que reúne três recursos CSV: pagamento de cupom de juros, recompras e vencimentos. O bruto fica na pasta `resgates-do-tesouro-direto/` com os nomes `pagamento-de-cupom-de-juros-do-tesouro-direto@…`, `recompras-do-tesouro-direto@…` e `vencimentos-do-tesouro-direto@…`; o conversor separa os três pelo nome do arquivo e grava um dataset para cada.
- A fonte atualiza os arquivos todo dia, com dados até dois dias antes da extração, a partir do SID. No bruto, o carimbo `@AAAAMMDDTHHMMSS` é a data de modificação do recurso; o lake converte a versão mais recente. O Drive tinha 9 versões do cupom e 27 de recompras e de vencimentos em 2026-11-10.

## Conteúdo

- Uma linha por tipo de título, vencimento e data do resgate.
- Cobertura real (versão `@20261109`, conferido em 2026-11-10): 3.492 datas de 2005-01-06 a 2026-11-06, vencimentos de 2005-02 a 2084-12; 103.428 linhas, sem repetição da chave (0 repetições na amostra).
- A fonte anuncia: início das recompras em 06/01/2005 (metadados do conjunto). O arquivo de recompras não tem coluna de PU, diferente dos de cupom e vencimentos.

## Variáveis

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `tipo_titulo` | Tipo Titulo | texto | Nome do tipo de título | Selic, Prefixado, Prefixado com Juros Semestrais, IPCA+, IPCA+ com Juros Semestrais, IGPM+ com Juros Semestrais, EducA+ e outros | todo |
| `vencimento_do_titulo` | Vencimento do Titulo | texto | Data de vencimento do título | DD/MM/AAAA | todo |
| `data_resgate` | Data Resgate | texto | Data da recompra (resgate antecipado) | DD/MM/AAAA | todo |
| `quantidade` | Quantidade | texto | Quantidade de títulos do resgate | títulos, vírgula decimal | todo |
| `valor` | Valor | texto | Volume financeiro do resgate: PU multiplicado pela quantidade | R$, vírgula decimal | todo |

## No lake

- Dataset `tesouro-direto/recompras-do-tesouro-direto`, sem partição.
- Chave natural (amostra de 2026-11-10): `tipo_titulo`, `vencimento_do_titulo`, `data_resgate`, sem repetição.
- Todas as colunas são texto; só o cabeçalho é normalizado. Sem nulos na amostra.

## Cuidados de uso

- **Tudo é texto.** O conversor não converte tipos: datas continuam `DD/MM/AAAA`, números usam vírgula decimal (`18168,832736`). Converta antes de ordenar ou somar; ordenar as datas como texto não segue o calendário (conferido em 2026-11-10: o menor texto de `vencimento_do_titulo` do estoque é `01/01/2006`, o maior é `21/01/2004`).
- **Sem PU.** O arquivo de recompras só traz quantidade e valor; o PU implícito (valor sobre quantidade) é aproximado.
- **Resgate antecipado.** Não inclui o pagamento no vencimento (`vencimentos-do-tesouro-direto`) nem cupons.
- **Revisões.** O Tesouro Nacional informa que os valores podem ser revistos por alteração da base primária, estornos ou erros de consolidação. O lake guarda só a versão mais recente de cada arquivo.

## Exemplos

Recompras por ano (R$ bilhões):

```python
import polars as pl

recompras = pl.scan_parquet("lake/tesouro-direto/recompras-do-tesouro-direto/*.parquet")
por_ano = (
    recompras.with_columns(
        pl.col("data_resgate").str.to_date("%d/%m/%Y").dt.year().alias("ano"),
        pl.col("valor").str.replace(",", ".").cast(pl.Float64).alias("valor_rs"),
    )
    .group_by("ano")
    .agg((pl.col("valor_rs").sum() / 1e9).alias("bi"))
    .sort("ano")
    .collect()
)
```

## Referências

- Conjunto no Tesouro Transparente: https://www.tesourotransparente.gov.br/ckan/dataset/resgates-do-tesouro-direto
- Metadados em PDF: https://www.tesourotransparente.gov.br/ckan/dataset/f30db6e4-6123-416c-b094-be8dfc823601/resource/445e38cf-b3b3-4e08-879a-2724febcd861/download/resgatesdotesourodireto-metadados.pdf
