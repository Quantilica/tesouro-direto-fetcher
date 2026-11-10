---
dataset:
  id: "investidores-do-tesouro-direto"
  fonte: "tesouro-direto"
  titulo: "Investidores do Tesouro Direto"
  resumo: "Cadastro de investidores do Tesouro Direto, uma linha por código de investidor e instituição, com perfil (idade, sexo, estado civil, profissão, cidade) e situação."
  orgao: "Tesouro Nacional (STN/MF), Coordenação-Geral do Tesouro Direto (COTED), via Tesouro Transparente"
  pagina_oficial: "https://www.tesourotransparente.gov.br/ckan/dataset/investidores-do-tesouro-direto"
  licenca: "Licença Aberta para Bases de Dados (ODbL) do Open Data Commons, declarada no catálogo do Tesouro Transparente: http://www.opendefinition.org/licenses/odc-odbl"
  periodicidade: "mensal (arquivo gerado todo mês; divulgação em geral até o quinto dia útil do mês seguinte)"
  cobertura: {inicio: "2002-01", fim: "em-curso"}
  unidade: "cadastro de um investidor em uma instituição financeira"
  granularidade: {espacial: "município (cidade e UF)", temporal: "data de adesão"}
  formato_bruto: "CSV em UTF-8, separador ponto e vírgula, datas DD/MM/AAAA; um CSV por período de adesão (até 2017 e um por ano a partir de 2018)"
  lake: {estado: convertido, particoes: [periodo], chave: [], colunas: 11}
  dados_pessoais:
  - coluna: "codigo_do_investidor"
    categoria: "identificador pseudonimizado do investidor (código numérico da fonte)"
  - coluna: "data_de_adesao"
    categoria: "data (data de adesão ao programa)"
  - coluna: "estado_civil"
    categoria: "estado civil"
  - coluna: "genero"
    categoria: "sexo"
  - coluna: "profissao"
    categoria: "profissão"
  - coluna: "idade_do_investidor"
    categoria: "idade"
  - coluna: "uf_do_investidor"
    categoria: "localização (UF)"
  - coluna: "cidade_do_investidor"
    categoria: "localização (cidade)"
  - coluna: "pais_do_investidor"
    categoria: "localização (país)"
  eras:
  - {desde: "2018-01", mudanca: "os arquivos passam a ser separados por ano de adesão (antes, um único arquivo até 2017)"}
  revisado_em: "2026-11-10"
  versao_fetcher: "5.0.0"
---

# Investidores do Tesouro Direto

## Resumo

Lista de investidores cadastrados no Tesouro Direto, com dados de perfil (data de adesão, estado civil, sexo, profissão, idade, cidade e UF) e indicadores de situação da conta (ativa ou desativada) e se operou nos últimos 12 meses. Um investidor com cadastro em mais de uma instituição financeira aparece em mais de uma linha, com o mesmo código.

São dados individuais, mas o código é um identificador numérico sem nome nem CPF. Neste repositório não se reproduzem valores reais de investidores.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `tesouro-direto/investidores-do-tesouro-direto` |
| Órgão | Tesouro Nacional (STN/MF), Coordenação-Geral do Tesouro Direto (COTED), via Tesouro Transparente |
| Página oficial | https://www.tesourotransparente.gov.br/ckan/dataset/investidores-do-tesouro-direto |
| Licença | Licença Aberta para Bases de Dados (ODbL) do Open Data Commons, declarada no catálogo do Tesouro Transparente: http://www.opendefinition.org/licenses/odc-odbl |
| Periodicidade | mensal (arquivo gerado todo mês; divulgação em geral até o quinto dia útil do mês seguinte) |
| Cobertura | 2002-01 a em-curso |
| Unidade (uma linha) | cadastro de um investidor em uma instituição financeira |
| Granularidade | espacial: município (cidade e UF); temporal: data de adesão |
| Formato bruto | CSV em UTF-8, separador ponto e vírgula, datas DD/MM/AAAA; um CSV por período de adesão (até 2017 e um por ano a partir de 2018) |
| Estado no lake | convertido |
| Partições | `periodo` |
| Chave | — |
| Colunas | 11 |
| Unidades de medida | — |
| Dados pessoais | `codigo_do_investidor` (identificador pseudonimizado do investidor (código numérico da fonte)); `data_de_adesao` (data (data de adesão ao programa)); `estado_civil` (estado civil); `genero` (sexo); `profissao` (profissão); `idade_do_investidor` (idade); `uf_do_investidor` (localização (UF)); `cidade_do_investidor` (localização (cidade)); `pais_do_investidor` (localização (país)) |
| Eras | 2018-01: os arquivos passam a ser separados por ano de adesão (antes, um único arquivo até 2017) |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 5.0.0 |

## Origem e coleta

- O fetcher consulta o catálogo CKAN do Tesouro Transparente (conjunto `investidores-do-tesouro-direto`) e baixa os recursos em CSV: um arquivo "até 2017" e um por ano de adesão de 2018 em diante. Os recursos ZIP, a base completa em GZ e o PDF de metadados não são baixados.
- No bruto: `investidores-do-tesouro-direto-ate-2017@…csv` e `investidores-do-tesouro-direto-de-AAAA@…csv`, com carimbo de data de modificação do recurso. O lake converte a versão mais recente de cada período.
- Os dados chegam do MF/STN a partir de arquivos enviados pela B3. A fonte gera o arquivo todo mês.

## Conteúdo

- Uma linha por código de investidor e cadastro. Na amostra converti três arquivos (`ate-2017`, `2018` e `2026`): 10.176.339 linhas, 7.857.386 códigos distintos; 1.555.335 códigos aparecem em mais de uma linha, e 137.400 linhas são cópias exatas de outras (conferido em 2026-11-10, só nesses três arquivos).
- O período do arquivo é o **ano de adesão**: cada arquivo contém só adesões do seu ano (`2018`: de 2018-01-01 a 2018-12-31; `2026`: de 2026-01-01 a 2026-09-30; `ate-2017`: de 1900-01-01 a 2017-12-31).
- Cobertura nominal: a fonte anuncia dados desde jan/2002; a primeira adesão real vista foi em 2002-01-03. Há ainda adesões com data `1900` (821.380 das 3.261.185 linhas do arquivo `ate-2017`): a fonte atribui 1900 a pessoas jurídicas cadastradas (nota do dicionário oficial), mas não explica por que o volume é tão grande, e este documento não verifica a explicação.
- Disponibilidade no bruto (2026-11-10): `ate-2017` e 2018 a 2026; o arquivo de 2021 tem versão de maio de 2026, as demais de setembro e outubro de 2026.

## Variáveis

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `codigo_do_investidor` | Codigo do Investidor | texto | Código identificador do investidor (pode repetir quando o investidor tem cadastro em mais de uma instituição) | até 10 posições | todo |
| `data_de_adesao` | Data de Adesao | texto | Data de adesão ao programa | DD/MM/AAAA; `1900` é atribuído a pessoas jurídicas | todo |
| `estado_civil` | Estado Civil | texto | Estado civil | Solteiro(a), Desquitado(a), Viúvo(a), Divorciado(a), Casado(a) com brasileiro(a) nato(a), Casado(a) com brasileiro(a) naturalizado(a), Casado(a) com estrangeiro(a), União estável, Separado judic., Não se aplica (instituições de caridade) | todo |
| `genero` | Genero | texto | Sexo do investidor | M, F, N (não se aplica; instituições de caridade) | todo |
| `profissao` | Profissao | texto | Profissão (texto livre padronizado pela fonte) | até 70 posições; Não se aplica para instituições de caridade | todo |
| `idade_do_investidor` | Idade | texto | Idade do investidor, com três dígitos e zeros à esquerda; registros `00*` têm erro de cadastro, segundo a fonte (o conversor renomeia `Idade` para `idade_do_investidor`) | anos, ex.: `061` | todo |
| `uf_do_investidor` | UF do Investidor | texto | UF do investidor | sigla | todo |
| `cidade_do_investidor` | Cidade do Investidor | texto | Cidade do investidor | até 30 posições, sem acento | todo |
| `pais_do_investidor` | Pais do Investidor | texto | País do investidor | até 50 posições (`BRASIL` em todas as linhas da amostra) | todo |
| `situacao_da_conta` | Situacao da Conta | texto | Situação da conta | A (ativo), D (desativado) | todo |
| `operou_12_meses` | Operou 12 Meses | texto | Indicador de operação nos últimos 12 meses | S (sim), N (não) | todo |

## No lake

- Dataset `tesouro-direto/investidores-do-tesouro-direto`, particionado por `periodo`: `periodo=ate-2017`, `periodo=2018`, … `periodo=2026`, um Parquet por arquivo.
- O valor da partição vem do **nome do arquivo** (`…-de-2019@…csv` vira `periodo=2019`; `…-ate-2017@…csv` vira `periodo=ate-2017`), nunca do conteúdo. Como `ate-2017` não é número, a partição é texto neste dataset.
- Renomeação: `Idade` vira `idade_do_investidor`. As demais colunas só têm o cabeçalho normalizado.
- Todas as colunas são texto. Nulos na amostra de três arquivos: `uf_do_investidor` com 1 vazio (o texto `  `), `cidade_do_investidor` com 8 vazios.
- Não há chave: o mesmo código se repete (ver Conteúdo).

## Cuidados de uso

- **Dados individuais.** Cada linha é um investidor. O código é numérico e a fonte não traz nome nem CPF, mas a combinação de cidade, idade, profissão e data de adesão pode ser identificadora; trate como dado pessoal.
- **Tudo é texto.** O conversor não converte tipos: datas continuam `DD/MM/AAAA`, números usam vírgula decimal (`18168,832736`). Converta antes de ordenar ou somar; ordenar as datas como texto não segue o calendário (`data_de_adesao` em `DD/MM/AAAA`).
- **Linhas repetidas.** O mesmo código aparece em mais de uma linha (1.555.335 códigos na amostra de três arquivos), e há linhas idênticas (137.400). Para contar investidores, conte códigos distintos, não linhas.
- **Data 1900 e idade 000.** 821.380 linhas do arquivo `ate-2017` têm adesão em 1900; 3.230 têm idade `000` (conferido em 2026-11-10). A fonte documenta o 1900 (pessoas jurídicas) e a idade com `00*` (erro de cadastro).
- **Idades implausíveis.** 81 linhas têm idade acima de 110 anos.
- **Situação e período.** `situacao_da_conta` e `operou_12_meses` refletem a data da extração, não a do ano de adesão.
- **Período = ano de adesão**, não ano do dado. O arquivo `ate-2017` junta quase duas décadas.
- **Revisões.** O Tesouro Nacional informa que os valores podem ser revistos por alteração da base primária, estornos ou erros de consolidação. O lake guarda só a versão mais recente de cada arquivo.

## Exemplos

Número de investidores distintos que aderiram por ano nos arquivos convertidos (contagem por código, sem listar nenhum investidor):

```python
import polars as pl

inv = pl.scan_parquet("lake/tesouro-direto/investidores-do-tesouro-direto/**/*.parquet", hive_partitioning=True)
por_periodo = (
    inv.group_by("periodo")
    .agg(pl.col("codigo_do_investidor").n_unique().alias("investidores"))
    .sort("periodo")
    .collect()
)
```

## Referências

- Conjunto no Tesouro Transparente: https://www.tesourotransparente.gov.br/ckan/dataset/investidores-do-tesouro-direto
- Metadados em PDF: https://www.tesourotransparente.gov.br/ckan/dataset/48a7fd9d-78e5-43cb-bcba-6e7dcaf2d741/resource/9243a43c-31cd-4984-8129-55768fb780f5/download/investidoresdotesourodireto-metadados.pdf
