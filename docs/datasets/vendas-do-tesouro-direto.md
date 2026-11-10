---
dataset:
  id: "vendas-do-tesouro-direto"
  fonte: "tesouro-direto"
  titulo: "Vendas do Tesouro Direto"
  resumo: "Volume diário de vendas de títulos no Tesouro Direto, por título, vencimento e data de liquidação."
  orgao: "Tesouro Nacional (STN/MF), Coordenação-Geral do Tesouro Direto (COTED), via Tesouro Transparente"
  pagina_oficial: "https://www.tesourotransparente.gov.br/ckan/dataset/vendas-do-tesouro-direto"
  licenca: "Licença Aberta para Bases de Dados (ODbL) do Open Data Commons, declarada no catálogo do Tesouro Transparente: http://www.opendefinition.org/licenses/odc-odbl"
  periodicidade: "diária, com dados até dois dias antes da extração (quando o dado é considerado consolidado)"
  cobertura: {inicio: "2002-01", fim: "em-curso"}
  unidade: "venda de um título (tipo e vencimento) liquidada em um dia, por faixa de preço"
  granularidade: {espacial: "Brasil", temporal: "dia"}
  formato_bruto: "CSV em UTF-8, separador ponto e vírgula, decimal com vírgula, datas DD/MM/AAAA; um único arquivo com toda a série"
  lake: {estado: convertido, particoes: [], chave: [], colunas: 6}
  unidades_de_medida:
    pu: "R$ por título"
    quantidade: "títulos"
    valor: "R$"
  dados_pessoais: "nenhum"
  eras: []
  revisado_em: "2026-11-10"
  versao_fetcher: "5.0.0"
---

# Vendas do Tesouro Direto

## Resumo

Vendas dos títulos do Tesouro Direto: o volume financeiro vendido a investidores por dia de liquidação, tipo de título e vencimento. Serve para acompanhar a captação do programa. Para a visão por investidor, veja `operacoes-do-tesouro-direto`.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `tesouro-direto/vendas-do-tesouro-direto` |
| Órgão | Tesouro Nacional (STN/MF), Coordenação-Geral do Tesouro Direto (COTED), via Tesouro Transparente |
| Página oficial | https://www.tesourotransparente.gov.br/ckan/dataset/vendas-do-tesouro-direto |
| Licença | Licença Aberta para Bases de Dados (ODbL) do Open Data Commons, declarada no catálogo do Tesouro Transparente: http://www.opendefinition.org/licenses/odc-odbl |
| Periodicidade | diária, com dados até dois dias antes da extração (quando o dado é considerado consolidado) |
| Cobertura | 2002-01 a em-curso |
| Unidade (uma linha) | venda de um título (tipo e vencimento) liquidada em um dia, por faixa de preço |
| Granularidade | espacial: Brasil; temporal: dia |
| Formato bruto | CSV em UTF-8, separador ponto e vírgula, decimal com vírgula, datas DD/MM/AAAA; um único arquivo com toda a série |
| Estado no lake | convertido |
| Partições | — |
| Chave | — |
| Colunas | 6 |
| Unidades de medida | `pu`: R$ por título; `quantidade`: títulos; `valor`: R$ |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 5.0.0 |

## Origem e coleta

- O fetcher consulta o catálogo CKAN do Tesouro Transparente (conjunto `vendas-do-tesouro-direto`) e baixa o recurso CSV (`vendastesourodireto.csv`).
- A fonte gera o arquivo todo dia, com a série inteira desde 2002 até dois dias antes da extração, a partir do Sistema Integrado da Dívida Pública (SID). No bruto: `vendas-do-tesouro-direto@AAAAMMDDTHHMMSS.csv`. O Drive tinha 27 versões em 2026-11-10; o lake converte a mais recente.

## Conteúdo

- Uma linha por tipo, vencimento, data de liquidação e PU: a mesma combinação de título e dia pode aparecer em mais de uma linha, com PUs diferentes (112 linhas em chaves repetidas na amostra, por exemplo o IGPM+ 01/01/2031 em 01/11/2002).
- Cobertura real (versão `@20261109`, conferido em 2026-11-10): 6.145 dias de liquidação, de 2002-01-04 a 2026-11-06; 101.923 linhas; vencimentos de 2002-06 a 2084-12.
- Soma anual do valor (R$ bilhões, conferido em 2026-11-10): 0,08 em 2002; 4,99 em 2014; 30,88 em 2019; 89,28 em 2025; 118,0 até 2026-11-06.

## Variáveis

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `tipo_titulo` | Tipo Titulo | texto | Nome do tipo de título | Selic, Prefixado, Prefixado com Juros Semestrais, IPCA+, IPCA+ com Juros Semestrais, IGPM+ com Juros Semestrais, RendA+, Educa+, Reserva | todo |
| `vencimento_do_titulo` | Vencimento do Titulo | texto | Data de vencimento do título | DD/MM/AAAA | todo |
| `data_de_liquidacao_da_venda` | Data de Liquidacao da Venda | texto | Data de liquidação da venda, no dia útil seguinte à operação do investidor | DD/MM/AAAA | todo |
| `pu` | PU | texto | Preço unitário médio do título na liquidação da venda; Valor dividido por Quantidade pode diferir do PU por truncamento (PU com 6 casas e quantidade com 1 casa) | R$, vírgula decimal | todo |
| `quantidade` | Quantidade | texto | Quantidade de títulos na liquidação da venda | títulos, vírgula decimal | todo |
| `valor` | Valor | texto | Volume financeiro da venda: PU multiplicado pela quantidade | R$, vírgula decimal | todo |

## No lake

- Dataset `tesouro-direto/vendas-do-tesouro-direto`, sem partição.
- Não há chave única: as linhas se repetem em (`tipo_titulo`, `vencimento_do_titulo`, `data_de_liquidacao_da_venda`) com PUs diferentes (112 repetições na amostra de 2026-11-10). Por isso o cabeçalho declara a chave vazia.
- Todas as colunas são texto; só o cabeçalho é normalizado. Sem nulos na amostra.

## Cuidados de uso

- **Tudo é texto.** O conversor não converte tipos: datas continuam `DD/MM/AAAA`, números usam vírgula decimal (`18168,832736`). Converta antes de ordenar ou somar; ordenar as datas como texto não segue o calendário (conferido em 2026-11-10: o menor texto de `vencimento_do_titulo` do estoque é `01/01/2006`, o maior é `21/01/2004`).
- **O nome do título varia entre arquivos.** Neste arquivo o RendA+ é `Tesouro RendA+` e o EducA+ é `Tesouro Educa+`; no arquivo de taxas o RendA+ é `Tesouro Renda+ Aposentadoria Extra` (conferido em 2026-11-10). Uniformize antes de cruzar os datasets.
- **Data é a de liquidação**, no dia útil seguinte ao da operação do investidor; não compare dia a dia com as operações (`data_da_operacao`).
- **Não é chave.** Somar `valor` por título e dia inclui todas as linhas; não deduplique.
- **Últimos dias incompletos.** A fonte consolida o dado só até dois dias antes da extração.
- **Revisões.** O Tesouro Nacional informa que os valores podem ser revistos por alteração da base primária, estornos ou erros de consolidação. O lake guarda só a versão mais recente de cada arquivo.

## Exemplos

Vendas anuais (R$ bilhões) por tipo de título em 2025:

```python
import polars as pl

vendas = pl.scan_parquet("lake/tesouro-direto/vendas-do-tesouro-direto/*.parquet")
por_titulo = (
    vendas.with_columns(
        pl.col("data_de_liquidacao_da_venda").str.to_date("%d/%m/%Y").alias("dia"),
        pl.col("valor").str.replace(",", ".").cast(pl.Float64).alias("valor_rs"),
    )
    .filter(pl.col("dia").dt.year() == 2025)
    .group_by("tipo_titulo")
    .agg((pl.col("valor_rs").sum() / 1e9).alias("bi"))
    .sort("bi", descending=True)
    .collect()
)
```

## Referências

- Conjunto no Tesouro Transparente: https://www.tesourotransparente.gov.br/ckan/dataset/vendas-do-tesouro-direto
- Metadados em PDF: https://www.tesourotransparente.gov.br/ckan/dataset/f0468ecc-ae97-4287-89c2-6d8139fb4343/resource/ab22ec7d-7ff9-4979-a3ed-fb234caae1f2/download/vendasdotesourodireto-metadados-revisado.pdf
