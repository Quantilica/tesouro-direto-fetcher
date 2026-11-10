---
dataset:
  id: "operacoes-do-tesouro-direto"
  fonte: "tesouro-direto"
  titulo: "Operações do Tesouro Direto"
  resumo: "Operações (compra, venda, depósito e retirada de títulos) realizadas por investidores no Tesouro Direto, uma linha por operação, desde 2014."
  orgao: "Tesouro Nacional (STN/MF), Coordenação-Geral do Tesouro Direto (COTED), via Tesouro Transparente"
  pagina_oficial: "https://www.tesourotransparente.gov.br/ckan/dataset/operacoes-do-tesouro-direto"
  licenca: "Licença Aberta para Bases de Dados (ODbL) do Open Data Commons, declarada no catálogo do Tesouro Transparente: http://www.opendefinition.org/licenses/odc-odbl"
  periodicidade: "mensal (arquivo gerado todo mês; divulgação em geral até o quinto dia útil do mês seguinte); os metadados declaram dados diários"
  cobertura: {inicio: "2014-01", fim: "em-curso"}
  unidade: "operação de um investidor com um título em um dia"
  granularidade: {espacial: "Brasil", temporal: "dia"}
  formato_bruto: "CSV em UTF-8, separador ponto e vírgula, decimal com vírgula, datas DD/MM/AAAA; um CSV por ano de operação"
  lake: {estado: convertido, particoes: [periodo], chave: [], colunas: 9}
  unidades_de_medida:
    quantidade: "títulos"
    valor_do_titulo: "R$ por título"
    valor_da_operacao: "R$"
  dados_pessoais:
  - coluna: "codigo_do_investidor"
    categoria: "identificador pseudonimizado do investidor (código numérico da fonte)"
  - coluna: "data_da_operacao"
    categoria: "movimentação financeira individual (data)"
  - coluna: "valor_da_operacao"
    categoria: "movimentação financeira individual (valor)"
  - coluna: "quantidade"
    categoria: "movimentação financeira individual (quantidade)"
  eras: []
  revisado_em: "2026-11-10"
  versao_fetcher: "5.0.0"
---

# Operações do Tesouro Direto

## Resumo

Cada linha é uma operação de um investidor com um título do Tesouro Direto: data, tipo e vencimento do título, quantidade, preço, valor, tipo de operação e canal. Permite medir captação, resgates e o perfil das operações. O código do investidor liga as operações ao cadastro em `investidores-do-tesouro-direto`.

São dados individuais com identificador numérico, sem nome nem CPF. Os exemplos deste repositório não reproduzem operações reais.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `tesouro-direto/operacoes-do-tesouro-direto` |
| Órgão | Tesouro Nacional (STN/MF), Coordenação-Geral do Tesouro Direto (COTED), via Tesouro Transparente |
| Página oficial | https://www.tesourotransparente.gov.br/ckan/dataset/operacoes-do-tesouro-direto |
| Licença | Licença Aberta para Bases de Dados (ODbL) do Open Data Commons, declarada no catálogo do Tesouro Transparente: http://www.opendefinition.org/licenses/odc-odbl |
| Periodicidade | mensal (arquivo gerado todo mês; divulgação em geral até o quinto dia útil do mês seguinte); os metadados declaram dados diários |
| Cobertura | 2014-01 a em-curso |
| Unidade (uma linha) | operação de um investidor com um título em um dia |
| Granularidade | espacial: Brasil; temporal: dia |
| Formato bruto | CSV em UTF-8, separador ponto e vírgula, decimal com vírgula, datas DD/MM/AAAA; um CSV por ano de operação |
| Estado no lake | convertido |
| Partições | `periodo` |
| Chave | — |
| Colunas | 9 |
| Unidades de medida | `quantidade`: títulos; `valor_do_titulo`: R$ por título; `valor_da_operacao`: R$ |
| Dados pessoais | `codigo_do_investidor` (identificador pseudonimizado do investidor (código numérico da fonte)); `data_da_operacao` (movimentação financeira individual (data)); `valor_da_operacao` (movimentação financeira individual (valor)); `quantidade` (movimentação financeira individual (quantidade)) |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 5.0.0 |

## Origem e coleta

- O fetcher consulta o catálogo CKAN do Tesouro Transparente (conjunto `operacoes-do-tesouro-direto`) e baixa os recursos CSV, um por ano (2014 a 2026). Os ZIP, a base completa em GZ e o PDF de metadados não são baixados.
- No bruto: `operacoes-do-tesouro-direto-de-AAAA@AAAAMMDDTHHMMSS.csv`, com a data de modificação do recurso no catálogo. O lake converte a versão mais recente de cada ano, escolhida pelo carimbo no nome.
- Os dados chegam do MF/STN a partir de arquivos enviados pela B3.

## Conteúdo

- Uma linha por operação. Cobertura nominal: operações desde janeiro de 2014 (metadados), arquivos de 2014 a 2026 no bruto em 2026-11-10 (listagem do bruto).
- Amostra convertida: o ano de 2014, com 554.363 linhas, 248 dias de 2014-01-02 a 2014-12-30, 97.576 códigos de investidor distintos. Para 2019, o arquivo completo tem 7.884.807 linhas (conferido em 2026-11-10; ver Cuidados de uso). Não converti os demais anos.
- Tipos de operação em 2014: `C` 475.438, `V` 69.520, `D` 4.815 e `R` 4.590 linhas; os canais `D` e `R` só aparecem pelo `S` (site).

## Variáveis

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `codigo_do_investidor` | Codigo do Investidor | texto | Código identificador do investidor (mesmo código do cadastro de investidores) | até 10 posições | todo |
| `data_da_operacao` | Data da Operacao | texto | Data em que ocorreu a operação | DD/MM/AAAA | todo |
| `tipo_titulo` | Tipo Titulo | texto | Nome do tipo de título | Selic, Prefixado, Prefixado com Juros Semestrais, IPCA+, IPCA+ com Juros Semestrais, IGPM+ com Juros Semestrais, EducA+, RendA+ | todo |
| `vencimento_do_titulo` | Vencimento do Titulo | texto | Data de vencimento do título | DD/MM/AAAA | todo |
| `quantidade` | Quantidade | texto | Quantidade de títulos da operação | títulos, vírgula decimal | todo |
| `valor_do_titulo` | Valor do Titulo | texto | Valor unitário do título | R$, duas casas, vírgula decimal | todo |
| `valor_da_operacao` | Valor da Operacao | texto | Valor total da operação (quantidade vezes valor unitário) | R$, duas casas, vírgula decimal | todo |
| `tipo_da_operacao` | Tipo da Operacao | texto | Tipo da operação | C = compra, V = venda, R = retirada, D = depósito (ver o cuidado sobre C e V) | todo |
| `canal_da_operacao` | Canal da Operacao | texto | Canal da operação | S = site, H = homebroker | todo |

## No lake

- Dataset `tesouro-direto/operacoes-do-tesouro-direto`, particionado por `periodo` (o ano, tirado do nome do arquivo: `…-de-2019@…csv` vira `periodo=2019`), um Parquet por ano.
- Todas as colunas são texto; só o cabeçalho é normalizado. Não há renomeação.
- Nulos: nenhum no arquivo de 2014 (amostra).
- Não há chave: as linhas são operações, sem identificador próprio.
- O conversor só confere que o cabeçalho tem `codigo_do_investidor`, `data_da_operacao` e `valor_da_operacao`; não confere se o arquivo termina inteiro.

## Cuidados de uso

- **Download truncado passa pelo conversor.** Um download do arquivo de 2019 feito em 2026-11-02 veio incompleto: 314.966.191 bytes em vez de 556.661.638, terminando no meio de uma linha e seguido de uma página HTML de erro (`Server Error`). Convertido, esse arquivo gera 4.462.070 linhas, 11 delas lixo, contra 7.884.807 do arquivo completo. O conversor não detecta o caso, porque só confere o cabeçalho. O lake publicado usa o arquivo completo de 2019, com 7.884.807 linhas (conferido em 2026-11-10). Quem converter por conta própria deve comparar o tamanho do arquivo com o `size_bytes` do manifesto.
- **C e V estão invertidos em relação ao dicionário.** O dicionário oficial define venda como título vendido ao investidor e compra como recompra pelo Tesouro. Nos dados de 2014, porém, a soma de `C` (R$ 4,993 bilhões) é praticamente a de `vendas-do-tesouro-direto` em 2014 (R$ 4,991 bilhões) e a de `V` (R$ 1,689 bilhão) é próxima à de `recompras-do-tesouro-direto` (R$ 1,703 bilhão). Na prática `C` é compra pelo investidor e `V` é venda pelo investidor (conferido em 2026-11-10).
- **`D` e `R` não são compra nem venda.** São depósito e retirada de títulos do ambiente do Tesouro Direto; a retirada não é permitida desde maio de 2015, salvo correções por ordem da B3 (dicionário oficial). Não conte como captação.
- **Tudo é texto.** O conversor não converte tipos: datas continuam `DD/MM/AAAA`, números usam vírgula decimal (`18168,832736`). Converta antes de ordenar ou somar; ordenar as datas como texto não segue o calendário (`DD/MM/AAAA`).
- **Valor unitário zero.** Em 2014, 4 linhas têm `valor_do_titulo` igual a `0,00` (conferido em 2026-11-10).
- **Dados individuais.** O código liga ao cadastro de investidores; evite cruzamentos que identifiquem pessoas.
- **Revisões.** O Tesouro Nacional informa que os valores podem ser revistos por alteração da base primária, estornos ou erros de consolidação. O lake guarda só a versão mais recente de cada arquivo.

## Exemplos

Valor anual de compras de títulos por investidores (`C`), por tipo de título, sem listar investidores:

```python
import polars as pl

ops = pl.scan_parquet("lake/tesouro-direto/operacoes-do-tesouro-direto/**/*.parquet", hive_partitioning=True)
compras = (
    ops.filter(pl.col("tipo_da_operacao") == "C")
    .with_columns(pl.col("valor_da_operacao").str.replace(",", ".").cast(pl.Float64).alias("valor_rs"))
    .group_by("periodo", "tipo_titulo")
    .agg((pl.col("valor_rs").sum() / 1e9).alias("bi"))
    .sort("periodo", "bi", descending=[False, True])
    .collect()
)
```

## Referências

- Conjunto no Tesouro Transparente: https://www.tesourotransparente.gov.br/ckan/dataset/operacoes-do-tesouro-direto
- Metadados em PDF: https://www.tesourotransparente.gov.br/ckan/dataset/78739a33-4d2f-4e35-88fd-65f1ccbe81c4/resource/89640be3-450b-4de1-8135-02194c8a8ada/download/operacoesdotesourodireto-metadados.pdf
