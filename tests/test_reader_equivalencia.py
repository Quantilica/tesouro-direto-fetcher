"""Os leitores passam pelo ``read_csv_resilient`` sem mudar a saída.

``data/golden_reader.json`` foi gerado com o ``pl.read_csv``/``pl.scan_csv`` direto
que o leitor usava (esquema e linhas de cada DataFrame, leitura inteira e em
blocos, numa amostra de fixture).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from tesouro_direto_fetcher import _HAS_ANALYSIS

if not _HAS_ANALYSIS:
    raise unittest.SkipTest("Analysis extras required.")

import polars as pl

from tesouro_direto_fetcher import reader

GOLDEN = Path(__file__).parent / "data" / "golden_reader.json"

_CASES = {
    "prices": (
        reader.read_prices,
        "Data Base;Tipo Titulo;Data Vencimento;Taxa Compra Manha;Taxa Venda Manha;"
        "PU Compra Manha;PU Venda Manha;PU Base Manha\n"
        "02/01/2020;Tesouro Prefixado;01/01/2025;4,5;4,6;800,12;799,5;800,1\n"
        "03/01/2020;Tesouro IPCA+;15/05/2035;3,1;3,2;2.100,00;2.099,0;2.100,5\n"
        "04/01/2020;Tesouro Selic;01/03/2025;0,01;0,02;9.000,5;9.001,0;9.000,7\n",
    ),
    "stock": (
        reader.read_stock,
        "Tipo Titulo;Vencimento do Titulo;Mes Estoque;PU;Quantidade;Valor Estoque\n"
        "Tesouro Prefixado;01/01/2025;01/2020;800,12;10,5;8401,26\n"
        "Tesouro IPCA+;15/05/2035;02/2020;2100,0;3,25;6825,0\n",
    ),
    "investors": (
        reader.read_investors,
        "Codigo do Investidor;Data de Adesao;Estado Civil;Genero;Profissao;Idade;"
        "UF do Investidor;Cidade do Investidor;Pais do Investidor;Situacao da Conta;"
        "Operou 12 Meses\n"
        "1;01/02/2015;Solteiro;M;Engenheiro Civil Ação;35;SP;São Paulo;Brasil;A;S\n"
        "2;15/08/2018;Casado;F;Professora;41;MG;Belo Horizonte;Brasil;D;N\n",
    ),
    "sales": (
        reader.read_sales,
        "Tipo Titulo;Vencimento do Titulo;Data Venda;PU;Quantidade;Valor\n"
        "Tesouro IPCA+ com Juros Semestrais;15/08/2024;11/06/2004;"
        "1087,18;8,20;8914,93\n"
        "Tesouro Prefixado;01/01/2025;12/06/2004;800,0;1,0;800,0\n",
    ),
}


def _frame(df: pl.DataFrame) -> dict:
    return {
        "schema": [[c, str(t)] for c, t in df.schema.items()],
        "rows": [json.dumps(r, ensure_ascii=False, default=str) for r in df.to_dicts()],
    }


def snapshot(tmp: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for name, (func, text) in _CASES.items():
        path = tmp / f"{name}.csv"
        path.write_text(text, encoding="utf-8")
        out[name] = _frame(func(path))
        # Em blocos: as linhas de todos os blocos, na ordem.
        batches = list(func(path, chunksize=1))
        out[f"{name}-chunked"] = _frame(pl.concat(batches))
        out[f"{name}-chunked"]["n_batches"] = len(batches)
    return out


class TestReaderEquivalencia(unittest.TestCase):
    def test_reader_output_matches_golden(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            got = snapshot(Path(tmp))
        self.assertEqual(got, json.loads(GOLDEN.read_text(encoding="utf-8")))

    def test_latin1_file_is_read_instead_of_failing(self):
        import tempfile

        func, text = _CASES["investors"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "investors-latin1.csv"
            path.write_bytes(text.encode("latin-1", errors="replace"))
            df = func(path)
        self.assertEqual(df["city"][0], "São Paulo")
        self.assertEqual(df["profession"][0], "Engenheiro Civil Ação")


if __name__ == "__main__":  # pragma: no cover - gera o golden com o leitor atual
    import sys
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        GOLDEN.parent.mkdir(exist_ok=True)
        GOLDEN.write_text(
            json.dumps(snapshot(Path(tmp)), ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )
    sys.stdout.write(f"golden gravado em {GOLDEN}\n")
