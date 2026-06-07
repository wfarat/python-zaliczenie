import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from .visualization_strategy import VisualizationStrategy
from typing import Tuple


class ItemTypeDistributionStrategy(VisualizationStrategy):
    """
    Strategia: Wykres słupkowy rozkładu typów produktów oraz struktury ich sprzedaży.
    Uzasadnienie: Wykres z lewej pozwala szybko zidentyfikować liderów wolumenu (najlepsze kategorie).
    Wykres z prawej (skumulowany) precyzyjnie pokazuje, przez jakie kanały (detal, magazyn, transfery)
    dana kategoria rotuje, co pomaga w lepszym alokowaniu zapasów.
    """

    def generate_plot(self, df: pd.DataFrame) -> plt.Figure:
        fig, axes = plt.subplots(2, 1, figsize=(14, 14))

        if 'ITEM TYPE' in df.columns and 'MONTH' in df.columns:
            df_plot = df.copy()
            df_plot['TOTAL VOLUME'] = df_plot['RETAIL SALES'] + df_plot['WAREHOUSE SALES'] + df_plot['RETAIL TRANSFERS']

            top_10_df = df_plot.groupby('ITEM TYPE')['TOTAL VOLUME'].sum().nlargest(10).reset_index()
            top_10_categories = top_10_df['ITEM TYPE'].tolist()

            channel_distribution = df_plot[df_plot['ITEM TYPE'].isin(top_10_categories)].groupby('ITEM TYPE')[
                ['RETAIL SALES', 'WAREHOUSE SALES', 'RETAIL TRANSFERS']].sum()
            channel_distribution = channel_distribution.loc[top_10_categories]

            channel_distribution.plot(kind='bar', stacked=True, ax=axes[0], colormap='viridis', alpha=0.85)

            axes[0].set_title("Struktura Dystrybucji dla Top 10 Kategorii", fontsize=14)
            axes[0].set_xlabel("Typ Produktu")
            axes[0].set_ylabel("Suma sprzedaży w kanale")
            axes[0].tick_params(axis='x', rotation=0)
            axes[0].legend(title="Kanał dystrybucji")

            heatmap_data = df_plot[df_plot['ITEM TYPE'].isin(top_10_categories)]

            pivot_table = heatmap_data.pivot_table(
                values='TOTAL VOLUME',
                index='ITEM TYPE',
                columns='MONTH',
                aggfunc='sum',
                fill_value=0
            )

            pivot_table = pivot_table.reindex(top_10_categories)

            pivot_normalized = pivot_table.div(pivot_table.sum(axis=1), axis=0).fillna(0)

            sns.heatmap(
                pivot_normalized,
                cmap="YlGnBu",
                ax=axes[1],
                annot=True,
                fmt=".0%",
                linewidths=.5,
                cbar_kws={'label': 'Procentowy udział w roku'}
            )

            axes[1].set_title("Sezonowość (Kiedy dany produkt sprzedaje się najlepiej w ciągu roku?)", fontsize=14)
            axes[1].set_xlabel("Miesiąc (1-12)")
            axes[1].set_ylabel("Typ Produktu")

        else:
            axes[0].text(0.5, 0.5, 'Brak wymaganych kolumn (ITEM TYPE, MONTH)', ha='center', fontsize=12)
            axes[1].axis('off')

        plt.tight_layout(pad=4.0)
        return fig
    def generate_ai_context(self, df: pd.DataFrame) -> Tuple[str, str]:
        system_prompt = (
            "Jesteś ekspertem od zarządzania asortymentem (category manager). "
            "Przeanalizuj podany rozkład sprzedaży kategorii produktów. "
            "Zwróć odpowiedź w rygorystycznym formacie:\n"
            "PODSUMOWANIE:\n[Napisz 2-3 zdania podsumowania: co rotuje najlepiej i z czego ewentualnie można by zrezygnować]\n"
            "PYTANIA:\n[Napisz dokładnie 3 ciekawe, analityczne pytania pogłębiające temat, "
            "każde w nowej linii, zaczynając od myślnika '-']"
        )

        df_copy = df.copy()
        df_copy['TOTAL VOLUME'] = df_copy['RETAIL SALES'] + df_copy['WAREHOUSE SALES'] + df_copy['RETAIL TRANSFERS']

        summary_data = df_copy.groupby('ITEM TYPE')[
            ['RETAIL SALES', 'WAREHOUSE SALES', 'RETAIL TRANSFERS', 'TOTAL VOLUME']].sum().sort_values(
            by='TOTAL VOLUME', ascending=False).head(10)

        data_summary = f"Top 10 Kategorii Produktów wraz z podziałem na kanały:\n{summary_data.to_string()}"
        return system_prompt, data_summary