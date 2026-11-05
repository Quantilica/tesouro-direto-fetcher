import unittest
from pathlib import Path

from tesouro_direto_fetcher import _HAS_ANALYSIS

if not _HAS_ANALYSIS:
    raise unittest.SkipTest("Analysis extras required.")

from tesouro_direto_fetcher import reader


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


if __name__ == "__main__":
    unittest.main()
