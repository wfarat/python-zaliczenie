import pytest
import pandas as pd
from src.visualizations import TopSuppliersStrategy

@pytest.fixture
def dummy_sales_data():
    """Mały, w pełni kontrolowany DataFrame do testowania obliczeń matematycznych."""
    return pd.DataFrame({
        'SUPPLIER': ['UPS', 'UPS', 'FedEx', 'Lokalna Winiarnia'],
        'RETAIL SALES': [100, 50, 200, 300],
        'WAREHOUSE SALES': [20, 30, 10, 0],
        'RETAIL TRANSFERS': [0, 0, 0, 0],
        'ITEM TYPE': ['Electronics', 'Apparel', 'Electronics', 'Wino']
    })

def test_detect_entity_heuristics(dummy_sales_data):
    """Testuje czy heurystyka poprawnie wykrywa kurierów vs dostawców."""
    strategy = TopSuppliersStrategy()

    entity_courier = strategy._detect_entity(dummy_sales_data)
    assert entity_courier['plural'] == 'Kurierów'
    assert entity_courier['singular'] == 'Kurier'

    traditional_data = pd.DataFrame({'SUPPLIER': ['Browar X', 'Winiarnia Y']})
    entity_supplier = strategy._detect_entity(traditional_data)
    assert entity_supplier['plural'] == 'Dostawców'
    assert entity_supplier['singular'] == 'Dostawca'


def test_top_suppliers_computations(dummy_sales_data):
    """
    Testuje poprawność agregacji matematycznych wewnątrz strategii (bez rysowania wykresu).
    Sprawdza, czy Total Volume i grupowanie działają poprawnie.
    """
    strategy = TopSuppliersStrategy()

    system_prompt, data_summary = strategy.generate_ai_context(dummy_sales_data)

    assert "PODSUMOWANIE:" in system_prompt
    assert "PYTANIA:" in system_prompt

    assert "200" in data_summary
    assert "210" in data_summary
    assert "300" in data_summary

    assert "Wino" in data_summary


def test_missing_columns_graceful_handling():
    """Testuje czy podanie błędnych danych nie wysadza aplikacji w powietrze."""
    strategy = TopSuppliersStrategy()
    bad_df = pd.DataFrame({'ZLA_KOLUMNA': [1, 2, 3]})

    fig = strategy.generate_plot(bad_df)

    assert fig is not None
    axes = fig.get_axes()
    texts = [t.get_text() for t in axes[0].texts]
    assert any("Brak wymaganych kolumn" in text for text in texts)