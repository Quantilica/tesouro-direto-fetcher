# Tesouro Direto (`tesouro-direto`)

O `tesouro-direto-fetcher` coleta oito conjuntos de dados abertos do Tesouro Direto, programa do Tesouro Nacional (STN/MF) para venda de títulos públicos a pessoas físicas, e os converte para o lake em Parquet. Os dados são publicados no portal Tesouro Transparente, em conjuntos mantidos pela Coordenação-Geral do Tesouro Direto (COTED) e pela CODIP.

| Dataset | O que é | Origem (conjunto no Tesouro Transparente) | Período | Página |
|---|---|---|---|---|
| `taxas-dos-titulos-ofertados-pelo-tesouro-direto` | Taxas e preços diários de compra e venda, por título e vencimento | `taxas-dos-titulos-ofertados-pelo-tesouro-direto` | 2004-12 em diante | [taxas](datasets/taxas-dos-titulos-ofertados-pelo-tesouro-direto.md) |
| `estoque-do-tesouro-direto` | Estoque mensal de títulos, em quantidade e valor | `estoque-do-tesouro-direto` | 2002-01 em diante | [estoque](datasets/estoque-do-tesouro-direto.md) |
| `vendas-do-tesouro-direto` | Vendas diárias por título e vencimento | `vendas-do-tesouro-direto` | 2002-01 em diante | [vendas](datasets/vendas-do-tesouro-direto.md) |
| `pagamento-de-cupom-de-juros-do-tesouro-direto` | Pagamentos de cupons de juros | `resgates-do-tesouro-direto` | 2005-06 em diante | [cupom](datasets/pagamento-de-cupom-de-juros-do-tesouro-direto.md) |
| `recompras-do-tesouro-direto` | Títulos devolvidos antes do vencimento | `resgates-do-tesouro-direto` | 2005-01 em diante | [recompras](datasets/recompras-do-tesouro-direto.md) |
| `vencimentos-do-tesouro-direto` | Títulos pagos no vencimento | `resgates-do-tesouro-direto` | 2005-01 em diante | [vencimentos](datasets/vencimentos-do-tesouro-direto.md) |
| `investidores-do-tesouro-direto` | Cadastro de investidores (microdados) | `investidores-do-tesouro-direto` | adesões desde 2002 | [investidores](datasets/investidores-do-tesouro-direto.md) |
| `operacoes-do-tesouro-direto` | Operações dos investidores (microdados) | `operacoes-do-tesouro-direto` | 2014-01 em diante | [operações](datasets/operacoes-do-tesouro-direto.md) |

## Como o Tesouro Nacional publica

- Cada conjunto é um pacote do catálogo CKAN do Tesouro Transparente (`https://www.tesourotransparente.gov.br/ckan/`), com recursos em CSV e um PDF de metadados com o dicionário das colunas. O fetcher baixa só os recursos em CSV.
- Os arquivos de taxas, vendas e resgates são regerados todo dia, com a série inteira. Estoque, investidores e operações são mensais. Investidores e operações são divididos por ano (e, para investidores, um arquivo "até 2017").
- Cada arquivo vem com data de modificação, que o fetcher grava no nome do bruto (`<arquivo>@AAAAMMDDTHHMMSS.csv`). Versões sucessivas convivem; o lake converte a mais recente de cada arquivo.
- O catálogo declara a licença Open Data Commons Open Database License (ODbL) para os oito conjuntos.

## Como os conjuntos se relacionam

- **Vendas × operações.** O volume de vendas de um ano é próximo à soma das operações de compra do investidor (`C`) no mesmo ano. Em 2014, R$ 4,991 bilhões em vendas e R$ 4,993 bilhões em operações `C` (conferido em 2026-11-10). Veja o cuidado sobre `C` e `V` na [página de operações](datasets/operacoes-do-tesouro-direto.md).
- **Recompras × operações.** As recompras de 2014 (R$ 1,703 bilhão) ficam perto das operações `V` do mesmo ano (R$ 1,689 bilhão).
- **Investidores × operações.** `codigo_do_investidor` é o mesmo nos dois.
- **Estoque.** É um retrato mensal acumulado, pela taxa de emissão, e não é preço de mercado; as taxas e preços dos títulos ofertados são do mercado secundário.

## Quebras que valem para mais de um conjunto

| Desde | Mudança | Afeta |
|---|---|---|
| 2023-01 | Entra o Tesouro RendA+ (data conferida nas taxas; os tipos RendA+ e EducA+ também aparecem em estoque, vendas e recompras) | taxas e demais |
| 2023-08 | Entra o Tesouro EducA+ (idem) | taxas e demais |

O nome do título nem sempre é o mesmo entre arquivos: o RendA+ aparece como `Tesouro Renda+ Aposentadoria Extra` no arquivo de taxas e como `Tesouro RendA+` nos demais.

Todas as colunas chegam ao lake como texto, com datas `DD/MM/AAAA` e vírgula decimal; veja o cuidado de cada página.
