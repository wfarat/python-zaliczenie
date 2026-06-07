import pandas as pd
import numpy as np
import os


class DataProcessor:
    """
    Klasa odpowiedzialna za ładowanie, czyszczenie i transformację danych.
    """

    def __init__(self):
        self.df = None
        self.data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

    def load_csv(self, file_input) -> bool:
        """
        Wczytuje dane z pliku.
        """
        try:
            if isinstance(file_input, str):
                file_path = os.path.join(self.data_dir, file_input)
                if not os.path.exists(file_path):
                    print(f"Błąd: Plik nie istnieje -> {file_path}")
                    return False
                self.df = pd.read_csv(file_path)
            else:
                self.df = pd.read_csv(file_input)

            self._detect_and_adapt_schema()

            self._clean_data()
            return True

        except pd.errors.EmptyDataError:
            print("Błąd: Załadowany plik CSV jest pusty.")
            return False
        except pd.errors.ParserError:
            print("Błąd: Plik ma nieprawidłowy format lub uszkodzoną strukturę.")
            return False
        except Exception as e:
            print(f"Nieoczekiwany błąd podczas ładowania pliku: {e}")
            return False

    def _detect_and_adapt_schema(self):
        """
        Prywatna metoda (Adapter). Sprawdza schemat załadowanego DataFrame.
        Jeśli pasuje do nowego zbioru danych (Online Sales), transformuje go
        do struktury zrozumiałej dla naszego systemu (YEAR, MONTH, ITEM TYPE itd.).
        """
        if self.df is None or self.df.empty:
            return

        required_new_cols = {'InvoiceNo', 'Quantity', 'UnitPrice', 'InvoiceDate', 'Category', 'SalesChannel'}
        if required_new_cols.issubset(self.df.columns):
            print("Wykryto schemat 'Online Sales'. Uruchamiam Adapter w locie...")

            self.df['TotalAmount'] = self.df['Quantity'] * self.df['UnitPrice']

            self.df['InvoiceDate'] = pd.to_datetime(self.df['InvoiceDate'], errors='coerce')
            self.df.dropna(subset=['InvoiceDate'], inplace=True)
            self.df['YEAR'] = self.df['InvoiceDate'].dt.year
            self.df['MONTH'] = self.df['InvoiceDate'].dt.month

            self.df['ITEM TYPE'] = self.df['Category']
            self.df['SUPPLIER'] = self.df['ShipmentProvider'] if 'ShipmentProvider' in self.df.columns else 'Unknown'

            self.df['RETAIL SALES'] = np.where(self.df['SalesChannel'] == 'In-store', self.df['TotalAmount'], 0)
            self.df['WAREHOUSE SALES'] = np.where(self.df['SalesChannel'] == 'Online', self.df['TotalAmount'], 0)
            self.df['RETAIL TRANSFERS'] = 0

            final_cols = ['YEAR', 'MONTH', 'ITEM TYPE', 'SUPPLIER', 'RETAIL SALES', 'WAREHOUSE SALES',
                          'RETAIL TRANSFERS']
            self.df = self.df[final_cols].groupby(['YEAR', 'MONTH', 'ITEM TYPE', 'SUPPLIER']).sum().reset_index()
            print("Transformacja w locie zakończona sukcesem!")

    def _clean_data(self):
        if self.df is None or self.df.empty:
            return

        self.df.drop_duplicates(inplace=True)

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        self.df[numeric_cols] = self.df[numeric_cols].fillna(0)

        for col in self.df.columns:
            if 'date' in col.lower() or 'data' in col.lower():
                try:
                    self.df[col] = pd.to_datetime(self.df[col])
                except Exception:
                    pass

    def filter_by_supplier(self, supplier_name: str) -> pd.DataFrame:
        if self.df is None:
            return pd.DataFrame()

        col_name = next((col for col in self.df.columns if col.lower() in ['supplier', 'dostawca']), None)
        if col_name:
            return self.df[self.df[col_name] == supplier_name]
        return self.df