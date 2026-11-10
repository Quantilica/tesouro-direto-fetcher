---
dataset:
  id: "taxas-dos-titulos-ofertados-pelo-tesouro-direto"
  fonte: "tesouro-direto"
  titulo: "Taxas dos títulos ofertados pelo Tesouro Direto"
  resumo: "Taxas e preços diários de compra e venda dos títulos ofertados no Tesouro Direto, por título e vencimento."
  orgao: "Tesouro Nacional (STN/MF), CODIP, via Tesouro Transparente"
  pagina_oficial: "https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto"
  licenca: "Licença Aberta para Bases de Dados (ODbL) do Open Data Commons, declarada no catálogo do Tesouro Transparente: http://www.opendefinition.org/licenses/odc-odbl"
  periodicidade: "diária; divulgação no primeiro dia útil depois do fechamento do mercado secundário"
  cobertura: {inicio: "2004-12", fim: "em-curso"}
  unidade: "taxas e preços de um título (tipo e vencimento) em um dia"
  granularidade: {espacial: "Brasil", temporal: "dia"}
  formato_bruto: "CSV em UTF-8, separador ponto e vírgula, decimal com vírgula, datas DD/MM/AAAA; um único arquivo com toda a série"
  lake: {estado: convertido, particoes: [], chave: [tipo_titulo, data_vencimento, data_base], colunas: 8}
  unidades_de_medida:
    taxa_compra_manha: "% ao ano"
    taxa_venda_manha: "% ao ano"
    pu_compra_manha: "R$ por título"
    pu_venda_manha: "R$ por título"
    pu_base_manha: "R$ por título"
  dados_pessoais: "nenhum"
  eras:
  - {desde: "2023-01", mudanca: "entra o Tesouro RendA+ (grafado Tesouro Renda+ Aposentadoria Extra neste arquivo)"}
  - {desde: "2023-08", mudanca: "entra o Tesouro EducA+"}
  revisado_em: "2026-11-10"
  versao_fetcher: "5.0.0"
---

# Taxas dos títulos ofertados pelo Tesouro Direto

## Resumo

As taxas e os preços dos títulos ofertados pelo Tesouro Direto refletem o mercado secundário de títulos públicos federais: para cada título e vencimento, a taxa e o preço unitário (PU) pelos quais o investidor pode comprar ou vender naquele dia. É a base para curvas de juros dos títulos do Tesouro Direto.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `tesouro-direto/taxas-dos-titulos-ofertados-pelo-tesouro-direto` |
| Órgão | Tesouro Nacional (STN/MF), CODIP, via Tesouro Transparente |
| Página oficial | https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto |
| Licença | Licença Aberta para Bases de Dados (ODbL) do Open Data Commons, declarada no catálogo do Tesouro Transparente: http://www.opendefinition.org/licenses/odc-odbl |
| Periodicidade | diária; divulgação no primeiro dia útil depois do fechamento do mercado secundário |
| Cobertura | 2004-12 a em-curso |
| Unidade (uma linha) | taxas e preços de um título (tipo e vencimento) em um dia |
| Granularidade | espacial: Brasil; temporal: dia |
| Formato bruto | CSV em UTF-8, separador ponto e vírgula, decimal com vírgula, datas DD/MM/AAAA; um único arquivo com toda a série |
| Estado no lake | convertido |
| Partições | — |
| Chave | `tipo_titulo`, `data_vencimento`, `data_base` |
| Colunas | 8 |
| Unidades de medida | `taxa_compra_manha`: % ao ano; `taxa_venda_manha`: % ao ano; `pu_compra_manha`: R$ por título; `pu_venda_manha`: R$ por título; `pu_base_manha`: R$ por título |
| Dados pessoais | nenhum |
| Eras | 2023-01: entra o Tesouro RendA+ (grafado Tesouro Renda+ Aposentadoria Extra neste arquivo); 2023-08: entra o Tesouro EducA+ |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 5.0.0 |

## Origem e coleta

- O fetcher consulta o catálogo CKAN do Tesouro Transparente (conjunto `taxas-dos-titulos-ofertados-pelo-tesouro-direto`) e baixa o recurso em CSV (`precotaxatesourodireto.csv`). O PDF de metadados não é baixado.
- O arquivo traz a série inteira e é atualizado todo dia útil. No bruto: `taxas-dos-titulos-ofertados-pelo-tesouro-direto@AAAAMMDDTHHMMSS.csv`, com a data de modificação do recurso no catálogo. O bruto tinha 28 versões em 2026-11-10; o lake converte a mais recente.

## Conteúdo

- Uma linha por tipo de título, vencimento e data-base.
- Cobertura real (versão `@20261109`, conferido em 2026-11-10): 5.454 datas-base de 2004-12-31 a 2026-11-06; 178.304 linhas; vencimentos de 2005-01 a 2084-12. A fonte anuncia início em dez/2004.
- Eras: o Tesouro IPCA+ aparece a partir de 2005-07-18, o RendA+ a partir de 2023-01-30 e o EducA+ a partir de 2023-08-01.
- Os metadados descrevem as colunas como valores da **manhã** (taxas e PUs calculados na abertura): compra para o investidor comprar, venda para revender ao Tesouro.

## Variáveis

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `tipo_titulo` | Tipo Titulo | texto | Tipo do título do Tesouro Direto | Selic, Prefixado, Prefixado com Juros Semestrais, IPCA+, IPCA+ com Juros Semestrais, IGPM+ com Juros Semestrais, Renda+ Aposentadoria Extra, Educa+ | todo |
| `data_vencimento` | Data Vencimento | texto | Data de vencimento do título | DD/MM/AAAA | todo |
| `data_base` | Data Base | texto | Data a que se referem os preços e taxas | DD/MM/AAAA | todo |
| `taxa_compra_manha` | Taxa Compra Manha | texto | Taxa disponível para o investidor comprar o título | % ao ano, duas casas, vírgula decimal | todo |
| `taxa_venda_manha` | Taxa Venda Manha | texto | Taxa disponível para o investidor revender o título ao Tesouro; é sempre um pouco maior que a de compra, para proteger o Tesouro das oscilações entre uma precificação e outra | % ao ano, duas casas, vírgula decimal | todo |
| `pu_compra_manha` | PU Compra Manha | texto | Preço do título pela taxa de compra da manhã, com liquidação em D+1; quanto maior a taxa, menor o preço | R$, vírgula decimal | todo |
| `pu_venda_manha` | PU Venda Manha | texto | Preço do título pela taxa de venda da manhã, com liquidação em D+1 | R$, vírgula decimal | todo |
| `pu_base_manha` | PU Base Manha | texto | Preço do título pela taxa de venda da manhã, com liquidação no mesmo dia (D0); usado para marcar a mercado os títulos adquiridos | R$, vírgula decimal | todo |

## No lake

- Dataset `tesouro-direto/taxas-dos-titulos-ofertados-pelo-tesouro-direto`, sem partição: um Parquet por arquivo de origem.
- Chave natural (amostra de 2026-11-10, 178.304 linhas, 0 repetições): `tipo_titulo`, `data_vencimento`, `data_base`.
- Todas as colunas são texto; só o cabeçalho é normalizado. Sem nulos na amostra.

## Cuidados de uso

- **Tudo é texto.** O conversor não converte tipos: datas continuam `DD/MM/AAAA`, números usam vírgula decimal (`18168,832736`). Converta antes de ordenar ou somar; ordenar as datas como texto não segue o calendário (conferido em 2026-11-10: o menor texto de `vencimento_do_titulo` do estoque é `01/01/2006`, o maior é `21/01/2004`).
- **O nome do título varia entre arquivos.** Na lista de taxas o RendA+ aparece como `Tesouro Renda+ Aposentadoria Extra`; nos demais arquivos, como `Tesouro RendA+` (conferido em 2026-11-10). Uniformize antes de cruzar os datasets.
- **Taxas negativas e zeradas.** 5.115 linhas têm taxa de compra negativa (mínimo -3,53) e 14 linhas têm taxa e PU de compra iguais a zero (por exemplo, o Prefixado com Juros Semestrais 01/01/2021 em março de 2010, com `0,00` no PU). São valores da fonte; filtre antes de calcular curvas (conferido em 2026-11-10).
- **Preços da manhã.** Não são as cotações de fechamento nem o PU de liquidação das operações.
- **Série diária contém muitos vencimentos por dia.** Para uma curva, escolha o título e o vencimento; somar ou fazer média entre vencimentos não tem sentido.
- **Revisões.** O Tesouro Nacional informa que os valores podem ser revistos por alteração da base primária, estornos ou erros de consolidação. O lake guarda só a versão mais recente de cada arquivo.

## Exemplos

Taxa de compra do Tesouro IPCA+ 2035 (vencimento 15/05/2035) ao longo do tempo, ignorando taxas negativas ou zeradas só quando o PU for zero:

```python
import polars as pl

taxas = pl.scan_parquet("lake/tesouro-direto/taxas-dos-titulos-ofertados-pelo-tesouro-direto/*.parquet")
ipca_2035 = (
    taxas.filter(
        (pl.col("tipo_titulo") == "Tesouro IPCA+") & (pl.col("data_vencimento") == "15/05/2035")
    )
    .with_columns(
        pl.col("data_base").str.to_date("%d/%m/%Y").alias("dia"),
        pl.col("taxa_compra_manha").str.replace(",", ".").cast(pl.Float64).alias("taxa"),
        pl.col("pu_compra_manha").str.replace(",", ".").cast(pl.Float64).alias("pu"),
    )
    .filter(pl.col("pu") > 0)
    .select("dia", "taxa", "pu")
    .sort("dia")
    .collect()
)
```

## Referências

- Conjunto no Tesouro Transparente: https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto
- Metadados em PDF: https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/1a8eb2e3-4902-4a38-a1eb-6410f23d90de/download/taxa.pdf
- Preços e taxas no site do Tesouro Direto: https://www.tesourodireto.com.br/produtos/precos-e-taxas
