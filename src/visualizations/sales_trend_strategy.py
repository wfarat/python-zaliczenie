import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple
from .visualization_strategy import VisualizationStrategy


class SalesTrendStrategy(VisualizationStrategy):
    """
    Strategia: Analiza trendów czasowych (Makro i Mikro).
    Uzasadnienie: Górny wykres liniowy idealnie ukazuje makro-sezonowość kanałów sprzedaży.
    Dolny wykres warstwowy komplementuje go, pokazując, z jakich kategorii produktów (mikro)
    składa się ten całkowity wolumen i co napędza ewentualne piki sprzedażowe.
    """

    def generate_plot(self, df: pd.DataFrame) -> plt.Figure:
        fig, axes = plt.subplots(2, 1, figsize=(14, 12))

        if 'YEAR' in df.columns and 'MONTH' in df.columns:
            df_plot = df.copy()
            df_plot['Date'] = pd.to_datetime(df_plot['YEAR'].astype(str) + '-' + df_plot['MONTH'].astype(str) + '-01',
                                             errors='coerce')
            df_plot = df_plot.dropna(subset=['Date']).sort_values('Date')

            monthly_sales = df_plot.groupby('Date')[['RETAIL SALES', 'WAREHOUSE SALES']].sum().reset_index()

            sns.lineplot(data=monthly_sales, x='Date', y='RETAIL SALES', ax=axes[0], marker='o', linewidth=2,
                         label='Sprzedaż Detaliczna')
            sns.lineplot(data=monthly_sales, x='Date', y='WAREHOUSE SALES', ax=axes[0], marker='s', linewidth=2,
                         label='Sprzedaż Magazynowa')

            axes[0].set_title("Makro-trend: Miesięczna Sprzedaż Detaliczna vs Magazynowa", fontsize=14)
            axes[0].set_ylabel("Suma sprzedaży")
            axes[0].set_xlabel("Data")
            axes[0].grid(True, linestyle='--', alpha=0.6)
            axes[0].legend()

            if 'ITEM TYPE' in df.columns:
                df_plot['TOTAL VOLUME'] = df_plot['RETAIL SALES'] + df_plot['WAREHOUSE SALES'] + df_plot[
                    'RETAIL TRANSFERS']

                top_5_cats = df_plot.groupby('ITEM TYPE')['TOTAL VOLUME'].sum().nlargest(5).index

                trend_data = df_plot[df_plot['ITEM TYPE'].isin(top_5_cats)]

                pivot_trend = trend_data.pivot_table(index='Date', columns='ITEM TYPE', values='TOTAL VOLUME',
                                                     aggfunc='sum', fill_value=0)

                pivot_trend.plot.area(ax=axes[1], colormap='tab10', alpha=0.8)

                axes[1].set_title("Mikro-trend: Struktura wolumenu Top 5 Kategorii w czasie", fontsize=14)
                axes[1].set_ylabel("Całkowity Wolumen")
                axes[1].set_xlabel("Data")
                axes[1].grid(True, linestyle='--', alpha=0.6)
                axes[1].legend(title="Typ Produktu", loc='upper left')
            else:
                axes[1].text(0.5, 0.5, 'Brak kolumny ITEM TYPE do analizy struktury', ha='center', fontsize=12)

        else:
            axes[0].text(0.5, 0.5, 'Brak wymaganych kolumn (YEAR, MONTH)', ha='center', fontsize=12)
            axes[1].axis('off')

        plt.tight_layout(pad=4.0)
        return fig

    def generate_ai_context(self, df: pd.DataFrame) -> Tuple[str, str]:
        system_prompt = (
            "Jesteś analitykiem trendów rynkowych. Przeanalizuj podane dane sprzedaży w czasie. "
            "Zwróć odpowiedź w rygorystycznym formacie:\n"
            "PODSUMOWANIE:\n[Napisz 2-3 zdania podsumowania ogólnego makro-trendu, "
            "zwracając szczególną uwagę na ewidentną sezonowość, wzrosty i spadki popytu]\n"
            "PYTANIA:\n[Napisz dokładnie 3 ciekawe, analityczne pytania pogłębiające "
            "dotyczące zmian tych trendów w czasie, każde w nowej linii, zaczynając od myślnika '-']"
        )

        df_copy = df.copy()
        df_copy['Date'] = df_copy['YEAR'].astype(str) + '-' + df_copy['MONTH'].astype(str).str.zfill(2)

        monthly_sales = df_copy.groupby('Date')[['RETAIL SALES', 'WAREHOUSE SALES']].sum().tail(12)

        data_summary = f"Miesięczna sprzedaż z podziałem na kanały (ostatnie 12 m-cy):\n{monthly_sales.to_string()}"
        return system_prompt, data_summary