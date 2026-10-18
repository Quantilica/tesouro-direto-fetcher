import unittest
from pathlib import Path

from tesouro_direto_fetcher import _HAS_ANALYSIS

if not _HAS_ANALYSIS:
    raise unittest.SkipTest("Analysis extras required.")

from tesouro_direto_fetcher import reader
from tesouro_direto_fetcher.converter import _get_reader_function


class TestConverterInference(unittest.TestCase):
    def test_inference(self):
        cases = [
            (
                "taxas-dos-titulos-ofertados-pelo-tesouro-direto@20260101.csv",
                reader.read_prices,
            ),
            ("estoque-do-tesouro-direto@20260101.csv", reader.read_stock),
            (
                "investidores-do-tesouro-direto-de-2024@20260101.csv",
                reader.read_investors,
            ),
            (
                "operacoes-do-tesouro-direto-de-2024@20260101.csv",
                reader.read_operations,
            ),
            ("vendas-do-tesouro-direto@20260101.csv", reader.read_sales),
            ("resgates-do-tesouro-direto@20260101.csv", reader.read_buybacks),
            ("recompras-do-tesouro-direto@20260728T102003.csv", reader.read_buybacks),
            ("vencimentos-do-tesouro-direto@20260101.csv", reader.read_maturities),
            (
                "pagamento-de-cupom-de-juros-do-tesouro-direto@20260101.csv",
                reader.read_interest_coupons,
            ),
        ]

        for filename, expected_reader in cases:
            with self.subTest(filename=filename):
                func = _get_reader_function(Path(filename), "infer")
                self.assertEqual(func, expected_reader)

    def test_explicit_type(self):
        func = _get_reader_function(Path("random_name.csv"), "buybacks")
        self.assertEqual(func, reader.read_buybacks)

    def test_inference_failure(self):
        with self.assertRaises(ValueError):
            _get_reader_function(Path("unknown-file-type.csv"), "infer")


class TestReaderSales(unittest.TestCase):
    def test_read_sales_alternative_header(self):
        import datetime
        import tempfile

        from tesouro_direto_fetcher.constants import Column as C

        # Create a temporary CSV file with "Data de Liquidacao da Venda" header
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
            csv_path = Path(f.name)
            header = (
                "Tipo Titulo;Vencimento do Titulo;"
                "Data de Liquidacao da Venda;PU;Quantidade;Valor\n"
            )
            row_data = (
                "Tesouro IPCA+ com Juros Semestrais;15/08/2024;"
                "11/06/2004;1087,18;8,20;8914,93\n"
            )
            f.write(header + row_data)

        try:
            df = reader.read_sales(csv_path)
            self.assertIn(C.SALE_DATE.value, df.columns)
            self.assertEqual(df[C.SALE_DATE.value][0], datetime.date(2004, 6, 11))
            self.assertEqual(
                df[C.BOND_TYPE.value][0], "Tesouro IPCA+ com Juros Semestrais"
            )
        finally:
            csv_path.unlink()


class TestMetadataInjection(unittest.TestCase):
    def test_convert_to_parquet_injects_quantilica_metadata(self):
        import tempfile

        import polars as pl
        from quantilica.core.manifests import DownloadManifest

        from tesouro_direto_fetcher import converter

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            csv_path = tmp_path / "dados.csv"
            csv_path.write_text("a,b\n1,2\n", encoding="utf-8")

            manifest = DownloadManifest(
                source_id="tesouro-direto",
                dataset_id="prices",
                url="https://example.com/dados.csv",
                fetched_at="2026-01-01T00:00:00+00:00",
                sha256="a" * 64,
                size_bytes=csv_path.stat().st_size,
            )
            csv_path.with_name(csv_path.name + ".manifest.json").write_text(
                manifest.to_json(), encoding="utf-8"
            )

            original = converter._get_reader_function
            converter._get_reader_function = lambda *a, **k: pl.read_csv
            try:
                parquet_path = tmp_path / "dados.parquet"
                converter.convert_to_parquet(csv_path, parquet_path)
            finally:
                converter._get_reader_function = original

            metadata = pl.read_parquet_metadata(parquet_path)
            self.assertEqual(metadata["quantilica.dataset_id"], "prices")
            self.assertEqual(metadata["quantilica.source_id"], "tesouro-direto")


if __name__ == "__main__":
    unittest.main()
