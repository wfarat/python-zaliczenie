from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import pandas as pd
from typing import Tuple

class VisualizationStrategy(ABC):
    """
    Abstrakcyjna klasa bazowa dla wzorca Strategy.
    Każda konkretna strategia musi zaimplementować metodę generate_plot.
    """
    @abstractmethod
    def generate_plot(self, df: pd.DataFrame) -> plt.Figure:
        pass
    @abstractmethod
    def generate_ai_context(self, df: pd.DataFrame) -> Tuple[str, str]:
        """
        Zwraca krotkę (system_prompt, data_summary) dostosowaną do danej strategii.
        """
        pass