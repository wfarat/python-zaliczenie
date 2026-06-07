import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from typing import Tuple
from .visualization_strategy import VisualizationStrategy


class TopSuppliersStrategy(VisualizationStrategy):
    """
    Strategia: Analiza wolumenu i profilu asortymentowego partnerów biznesowych.
    Heurystyka wykrywa czy analizujemy Dostawców czy Kurierów.
    Dolny wykres 100% Stacked Bar Chart pokazuje uniwersalne zależności dla każdego zbioru danych.
    """

    def _detect_entity(self, df: pd.DataFrame) -> dict:
        """Heurystyka odporna na wielkość liter i spacje."""
        if 'SUPPLIER' not in df.columns:
            return {"plural": "Dostawców", "singular": "Dostawca", "instrumental": "dostawcami"}

        unique_vals = set(df['SUPPLIER'].dropna().astype(str).str.strip().str.upper().unique())
        couriers = {'UPS', 'FEDEX', 'DHL', 'ROYAL MAIL'}

        if couriers.intersection(unique_vals):
            return {"plural": "Kurierów", "singular": "Kurier", "instrumental": "kurierami"}

        return {"plural": "Dostawców", "singular": "Dostawca", "instrumental": "dostawcami"}

    def generate_plot(self, df: pd.DataFrame) -> plt.Figure:
        entity = self._detect_entity(df)

        fig, axes = plt.subplots(2, 1, figsize=(14, 12))

        if 'SUPPLIER' in df.columns and 'RETAIL SALES' in df.columns and 'ITEM TYPE' in df.columns:
            df_plot = df.copy()
            transfers = df_plot['RETAIL TRANSFERS'] if 'RETAIL TRANSFERS' in df_plot.columns else 0
            df_plot['TOTAL VOLUME'] = df_plot['RETAIL SALES'] + df_plot['WAREHOUSE SALES'] + transfers

            top_10_df = df_plot.groupby('SUPPLIER')['TOTAL VOLUME'].sum().nlargest(10).reset_index()
            top_10_suppliers = top_10_df['SUPPLIER'].tolist()

            sns.barplot(data=top_10_df, x='TOTAL VOLUME', y='SUPPLIER', ax=axes[0], palette='mako')
            axes[0].set_title(f"Makro-perspektywa: Top 10 {entity['plural']} wg Całkowitego Wolumenu", fontsize=14)
            axes[0].set_xlabel("Całkowity Obrót / Koszt (Wolumen)")
            axes[0].set_ylabel(entity['singular'])


            top_data = df_plot[df_plot['SUPPLIER'].isin(top_10_suppliers)]

            pivot_df = top_data.pivot_table(index='SUPPLIER', columns='ITEM TYPE', values='TOTAL VOLUME', aggfunc='sum',
                                            fill_value=0)

            pivot_percent = pivot_df.div(pivot_df.sum(axis=1), axis=0)
            pivot_percent = pivot_percent.reindex(top_10_suppliers)

            pivot_percent.plot(kind='barh', stacked=True, ax=axes[1], colormap='tab20', width=0.7)

            axes[1].set_title(
                f"Profil Asortymentowy: Jakie produkty napędzają wolumen danego {entity['singular'].lower()}?",
                fontsize=14)
            axes[1].set_xlabel("Struktura procentowa (100% = Cały wolumen partnera)")
            axes[1].set_ylabel(entity['singular'])

            axes[1].xaxis.set_major_formatter(mtick.PercentFormatter(1.0))

            axes[1].legend(title="Kategoria (ITEM TYPE)", bbox_to_anchor=(1.02, 1), loc='upper left')

        else:
            axes[0].text(0.5, 0.5, 'Brak wymaganych kolumn', ha='center', fontsize=12)
            axes[1].axis('off')

        plt.tight_layout(pad=4.0)
        return fig

    def generate_ai_context(self, df: pd.DataFrame) -> Tuple[str, str]:
        entity = self._detect_entity(df)

        system_prompt = (
            f"Jesteś ekspertem ds. strategii operacyjnej. "
            f"Przeanalizuj listę największych {entity['plural'].lower()} pod kątem generowanego przez nich wolumenu "
            f"oraz ich profilu produktowego (jakie kategorie dominują w ich obsłudze). "
            "Zwróć odpowiedź w rygorystycznym formacie:\n"
            f"PODSUMOWANIE:\n[Napisz 2-3 zdania wniosków oceniających jak silnie jesteśmy uzależnieni "
            f"od liderów oraz które kategorie produktów są dla nich kluczowe]\n"
            "PYTANIA:\n[Napisz dokładnie 3 analityczne pytania pogłębiające "
            f"dotyczące optymalizacji współpracy z tymi {entity['instrumental']}, każde w nowej linii, zaczynając od myślnika '-']"
        )

        df_copy = df.copy()
        transfers = df_copy['RETAIL TRANSFERS'] if 'RETAIL TRANSFERS' in df_copy.columns else 0
        df_copy['TOTAL VOLUME'] = df_copy['RETAIL SALES'] + df_copy['WAREHOUSE SALES'] + transfers

        top_10 = df_copy.groupby('SUPPLIER')['TOTAL VOLUME'].sum().nlargest(10).index
        top_data = df_copy[df_copy['SUPPLIER'].isin(top_10)]

        ai_stats = top_data.groupby(['SUPPLIER', 'ITEM TYPE'])['TOTAL VOLUME'].sum().reset_index()
        ai_stats = ai_stats.sort_values(['SUPPLIER', 'TOTAL VOLUME'], ascending=[True, False]).groupby(
            'SUPPLIER').first().reset_index()
        ai_stats = ai_stats.rename(columns={'ITEM TYPE': 'TOP CATEGORY'})
        ai_stats = ai_stats.sort_values(by='TOTAL VOLUME', ascending=False)

        data_summary = f"Statystyki Top 10 {entity['plural']} (Całkowity Wolumen i ich Najsilniejsza Kategoria):\n{ai_stats.to_string()}"
        return system_prompt, data_summary