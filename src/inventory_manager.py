import pandas as pd
import matplotlib.pyplot as plt
from .data_processor import DataProcessor
from .ai_manager import AIManager
from .visualizations.visualization_strategy import VisualizationStrategy

class InventoryManager:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.ai_manager = AIManager()
        self.current_strategy: VisualizationStrategy = None

    def load_data(self, file_path_or_buffer) -> bool:
        return self.data_processor.load_csv(file_path_or_buffer)

    def change_strategy(self, strategy: VisualizationStrategy):
        self.current_strategy = strategy

    def generate_visualization(self) -> plt.Figure:
        if self.current_strategy is None:
            raise ValueError("Nie ustawiono strategii wizualizacji!")

        if self.data_processor.df is None or self.data_processor.df.empty:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, 'Brak danych do wizualizacji', ha='center')
            return fig

        return self.current_strategy.generate_plot(self.data_processor.df)

    def get_ai_insights(self) -> str:
        """Pobiera wnioski z AI na podstawie obecnych danych i aktywnej strategii."""
        if self.current_strategy is None:
            return "Wybierz najpierw strategię analizy (wykres), aby uzyskać dedykowane wnioski."

        if self.data_processor.df is None or self.data_processor.df.empty:
            return "Brak danych do analizy."

        system_prompt, data_summary = self.current_strategy.generate_ai_context(self.data_processor.df)

        return self.ai_manager.get_insights(data_summary, system_prompt)

    def get_ai_follow_up(self, question: str) -> str:
        if self.current_strategy is None or self.data_processor.df is None:
            return "Brak danych."
        _, data_summary = self.current_strategy.generate_ai_context(self.data_processor.df)
        return self.ai_manager.get_follow_up_answer(data_summary, question)

    def get_raw_data(self) -> pd.DataFrame:
        return self.data_processor.df