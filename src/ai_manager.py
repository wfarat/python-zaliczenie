import os
from llama_cpp import Llama


class AIManager:
    """
    Klasa Singleton do zarządzania komunikacją z lokalnym modelem AI.
    """
    _instance = None
    is_ready = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AIManager, cls).__new__(cls)

            try:
                cls._instance._initialize_model()
            except Exception as e:
                print(f"Krytyczny błąd podczas inicjalizacji AI: {e}")
                cls._instance.is_ready = False
        return cls._instance

    def _initialize_model(self):
        """Prywatna metoda inicjalizująca model GGUF."""
        self.is_ready = False  # Upewniamy się, że startujemy z poziomu False

        self.model_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'models', 'qwen2.5-3b-instruct-q4_k_m.gguf'))

        if not os.path.exists(self.model_path):
            print(f"Błąd: Nie znaleziono modelu w ścieżce: {self.model_path}")
            return

        print("Ładowanie modelu AI do pamięci...")

        # 3. ZMIANA: Przechwytujemy błędy samej biblioteki llama.cpp
        try:
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=2048,  # Zostawiamy 2048
                n_batch=2048,  # NOWE: Zmusza silnik do zjedzenia całego promptu na raz!
                n_gpu_layers=0,
                chat_format="chatml",  # Przywracamy, Qwen tego potrzebuje
                verbose=False  # Wyłączamy logi, żeby nie śmieciły w konsoli
            )
            self.is_ready = True
            print("Zainicjalizowano model AI pomyślnie.")
        except Exception as e:
            print(f"Błąd silnika Llama: {e}")
            self.is_ready = False

    def get_insights(self, data_summary: str, system_prompt: str) -> str:
        """Zwraca wnioski biznesowe na podstawie podsumowania danych i dedykowanego promptu."""
        if not self.is_ready:
            return "Błąd: Model AI nie jest gotowy."

        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"Oto podsumowanie wyselekcjonowanych danych:\n{data_summary}\n\nWygeneruj wnioski biznesowe."
            }
        ]
        try:
            response = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=300,
                temperature=0.3
            )

            generated_text = response["choices"][0]["message"]["content"]
            return generated_text.strip()

        except Exception as e:
            return f"Wystąpił błąd podczas generowania wniosków: {e}"

    def get_follow_up_answer(self, data_summary: str, question: str) -> str:
        """Odpowiada na konkretne pytanie pogłębiające zadane przez użytkownika, wspierając się tabelą."""
        if not self.is_ready:
            return "Błąd: Model AI nie jest gotowy."

        messages = [
            {
                "role": "system",
                "content": (
                    "Jesteś starszym analitykiem danych. Odpowiedz na zadane pytanie bazując wyłącznie "
                    "na dostarczonym podsumowaniu danych. "
                    "Wymóg krytyczny: Oprócz krótkiego tekstu (max 3 zdania), MUSISZ zilustrować swoją odpowiedź "
                    "małą, czytelną tabelą w formacie Markdown. Tabela ma pokazywać tylko te liczby, "
                    "które bezpośrednio dotyczą pytania."
                )
            },
            {
                "role": "user",
                "content": f"Oto dane:\n{data_summary}\n\nPytanie: {question}"
            }
        ]

        try:
            # Zwiększamy max_tokens, bo tabela zajmuje trochę miejsca w kontekście
            response = self.llm.create_chat_completion(messages=messages, max_tokens=250, temperature=0.3)
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Błąd generowania odpowiedzi: {e}"