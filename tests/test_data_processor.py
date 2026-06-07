import pytest
import io
from src.data_processor import DataProcessor


@pytest.fixture
def sample_csv_data():
    """Tworzy symulowany plik CSV w pamięci z celowymi błędami (duplikaty, braki)."""
    csv_content = """Date,Supplier,Product,Quantity,Price
2023-01-01,Dostawca A,Produkt X,10,15.5
2023-01-02,Dostawca B,Produkt Y,,20.0
2023-01-01,Dostawca A,Produkt X,10,15.5
2023-01-03,Dostawca A,Produkt Z,5,
"""
    return io.StringIO(csv_content)


def test_load_and_clean_data(sample_csv_data):
    """Testuje ładowanie danych, usuwanie duplikatów i uzupełnianie braków z rzędu."""
    processor = DataProcessor()
    success = processor.load_csv(sample_csv_data)

    assert success is True
    assert processor.df is not None


    assert len(processor.df) == 3

    processor.df.reset_index(drop=True, inplace=True)

    assert processor.df.loc[1, 'Quantity'] == 0.0
    assert processor.df.loc[2, 'Price'] == 0.0


def test_filter_by_supplier(sample_csv_data):
    """Testuje funkcję filtrowania danych po nazwie dostawcy."""
    processor = DataProcessor()
    processor.load_csv(sample_csv_data)

    df_filtered = processor.filter_by_supplier("Dostawca A")

    assert len(df_filtered) == 2
    assert all(df_filtered['Supplier'] == "Dostawca A")


def test_empty_file_handling():
    """Testuje, czy klasa poprawnie łapie błąd pustego pliku bez przerywania programu."""
    processor = DataProcessor()
    empty_csv = io.StringIO("")

    success = processor.load_csv(empty_csv)

    assert success is False