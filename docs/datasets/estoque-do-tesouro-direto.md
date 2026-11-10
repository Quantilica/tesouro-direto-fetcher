---
dataset:
  id: "estoque-do-tesouro-direto"
  fonte: "tesouro-direto"
  titulo: "Estoque do Tesouro Direto"
  resumo: "Estoque mensal de títulos públicos do Tesouro Direto, por título e vencimento, em quantidade e volume financeiro."
  orgao: "Tesouro Nacional (STN/MF), Coordenação-Geral do Tesouro Direto (COTED), via Tesouro Transparente"
  pagina_oficial: "https://www.tesourotransparente.gov.br/ckan/dataset/estoque-do-tesouro-direto"
  licenca: "Licença Aberta para Bases de Dados (ODbL) do Open Data Commons, declarada no catálogo do Tesouro Transparente: http://www.opendefinition.org/licenses/odc-odbl"
  periodicidade: "mensal (a fonte também declara periodicidade diária nos metadados; o arquivo tem um registro por mês). Divulgação, em geral, no primeiro dia do segundo mês depois do mês de referência"
  cobertura: {inicio: "2002-01", fim: "em-curso"}
  unidade: "estoque de um título (tipo e vencimento) em um mês"
  granularidade: {espacial: "Brasil", temporal: "mês"}
  formato_bruto: "CSV em UTF-8, separador ponto e vírgula, decimal com vírgula, datas DD/MM/AAAA; um único arquivo com toda a série"
  lake: {estado: convertido, particoes: [], chave: [tipo_titulo, vencimento_do_titulo, mes_estoque], colunas: 6}
  unidades_de_medida:
    pu: "R$ por título"
    quantidade: "títulos"
    valor_estoque: "R$"
  dados_pessoais: "nenhum"
  eras: []
  revisado_em: "2026-11-10"
  versao_fetcher: "5.0.0"
---

# Estoque do Tesouro Direto

## Resumo

O estoque do Tesouro Direto é o volume de títulos públicos federais mantidos por investidores pessoa física no programa, mês a mês, por tipo de título e vencimento. Serve para acompanhar o tamanho e a composição da carteira do programa.

O estoque usa a metodologia do estoque da Dívida Pública Federal: os juros são acumulados pela taxa de emissão de cada título, de modo que o valor **não** é marcado a mercado (fonte: metadados do conjunto).

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `tesouro-direto/estoque-do-tesouro-direto` |
| Órgão | Tesouro Nacional (STN/MF), Coordenação-Geral do Tesouro Direto (COTED), via Tesouro Transparente |
| Página oficial | https://www.tesourotransparente.gov.br/ckan/dataset/estoque-do-tesouro-direto |
| Licença | Licença Aberta para Bases de Dados (ODbL) do Open Data Commons, declarada no catálogo do Tesouro Transparente: http://www.opendefinition.org/licenses/odc-odbl |
| Periodicidade | mensal (a fonte também declara periodicidade diária nos metadados; o arquivo tem um registro por mês). Divulgação, em geral, no primeiro dia do segundo mês depois do mês de referência |
| Cobertura | 2002-01 a em-curso |
| Unidade (uma linha) | estoque de um título (tipo e vencimento) em um mês |
| Granularidade | espacial: Brasil; temporal: mês |
| Formato bruto | CSV em UTF-8, separador ponto e vírgula, decimal com vírgula, datas DD/MM/AAAA; um único arquivo com toda a série |
| Estado no lake | convertido |
| Partições | — |
| Chave | `tipo_titulo`, `vencimento_do_titulo`, `mes_estoque` |
| Colunas | 6 |
| Unidades de medida | `pu`: R$ por título; `quantidade`: títulos; `valor_estoque`: R$ |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 5.0.0 |

## Origem e coleta

- O fetcher consulta o catálogo CKAN do Tesouro Transparente (conjunto `estoque-do-tesouro-direto`) e baixa o recurso em CSV. Os recursos em PDF (metadados) não são baixados.
- O arquivo da fonte (`estoquetesourodireto.csv`) traz a série inteira. No bruto, o fetcher grava `estoque-do-tesouro-direto@AAAAMMDDTHHMMSS.csv`, em que o carimbo é a data de última modificação do recurso no catálogo; versões sucessivas convivem na pasta e o lake converte a mais recente.
- Valores no Drive em 2026-11-10: duas versões (`@20260916` e `@20261016`).

## Conteúdo

- Uma linha por tipo de título, vencimento e mês de referência (sem repetição na amostra: 9.134 linhas, 0 chaves repetidas).
- Cobertura real conferida em 2026-11-10 (versão `@20261016`): 296 meses, de 2002-01 a 2026-08; vencimentos de 2002-06 a 2084-12. A fonte anuncia início em jan/2002 e série em curso.
- Tipos de título presentes: nove (inclui `Tesouro Reserva`, só 7 linhas).
- Os metadados descrevem a **Quantidade** como títulos emitidos e não resgatados, e o **Valor Estoque** como PU multiplicado pela quantidade.

## Variáveis

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `tipo_titulo` | Tipo Titulo | texto | Denominação do título (define o indexador e a forma de pagamento) | Selic, Prefixado, Prefixado com Juros Semestrais, IPCA+, IPCA+ com Juros Semestrais, IGPM+ com Juros Semestrais, RendA+, EducA+, Reserva | todo |
| `vencimento_do_titulo` | Vencimento do Titulo | texto | Data de vencimento do título | DD/MM/AAAA | todo |
| `mes_estoque` | Mes Estoque | texto | Mês de referência do estoque | MM/AAAA | todo |
| `pu` | PU | texto | Preço unitário do título no estoque, pela taxa de emissão (não é preço de mercado) | R$, vírgula decimal | todo |
| `quantidade` | Quantidade | texto | Quantidade de títulos no estoque | títulos, vírgula decimal | todo |
| `valor_estoque` | Valor Estoque | texto | Volume financeiro do estoque: PU multiplicado pela quantidade | R$, vírgula decimal | todo |

## No lake

- Dataset `tesouro-direto/estoque-do-tesouro-direto`, sem partição: um Parquet `estoque-do-tesouro-direto.parquet`.
- Chave natural (conferida na amostra de 2026-11-10, 9.134 linhas, sem repetição): `tipo_titulo`, `vencimento_do_titulo`, `mes_estoque`.
- O conversor lê o CSV com o DuckDB, normaliza o cabeçalho (minúsculas, sem acento, `_`) e grava **todas as colunas como texto**. Não há renomeação neste dataset.
- Nulos: nenhum na amostra (0 vazios nas seis colunas).

## Cuidados de uso

- **Tudo é texto.** O conversor não converte tipos: datas continuam `DD/MM/AAAA`, números usam vírgula decimal (`18168,832736`). Converta antes de ordenar ou somar; ordenar as datas como texto não segue o calendário (conferido em 2026-11-10: o menor texto de `vencimento_do_titulo` do estoque é `01/01/2006`, o maior é `21/01/2004`).
- **O nome do título varia entre arquivos.** Neste arquivo o RendA+ aparece como `Tesouro RendA+` e o Educa+ como `Tesouro Educa+` (conferido em 2026-11-10). Uniformize antes de cruzar os datasets.
- **Estoque não é preço de mercado.** Valor calculado com os juros acumulados pela taxa de emissão; não use como valor de mercado da carteira.
- **O último mês pode estar defasado.** Em 2026-11-10 o arquivo ia até 2026-08, coerente com a divulgação no segundo mês seguinte.
- **Diferença residual.** Em 35 das 9.134 linhas o produto PU x quantidade difere do valor de estoque em mais de R$ 1 (conferido em 2026-11-10).
- **Revisões.** O Tesouro Nacional informa que os valores podem ser revistos por alteração da base primária, estornos ou erros de consolidação. O lake guarda só a versão mais recente de cada arquivo.

## Exemplos

Estoque total por mês (R$ bilhões), com conversão das colunas de texto:

```python
import polars as pl

estoque = pl.scan_parquet("lake/tesouro-direto/estoque-do-tesouro-direto/*.parquet")
serie = (
    estoque.with_columns(
        pl.col("mes_estoque").str.to_date("%m/%Y", strict=False).alias("mes"),
        (pl.col("valor_estoque").str.replace(",", ".").cast(pl.Float64) / 1e9).alias("bi"),
    )
    .group_by("mes")
    .agg(pl.col("bi").sum())
    .sort("mes")
    .collect()
)
```

## Referências

- Conjunto no Tesouro Transparente: https://www.tesourotransparente.gov.br/ckan/dataset/estoque-do-tesouro-direto
- Metadados em PDF (descrição das colunas): https://www.tesourotransparente.gov.br/ckan/dataset/4d4dac3b-96d2-4011-92c9-ddf7d8392622/resource/ca43792c-5580-47d4-9eb5-fae55dce0ce0/download/estoquedotesourodireto-metadados.pdf
- Tesouro Direto: https://www.tesourodireto.com.br
