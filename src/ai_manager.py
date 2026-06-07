import os
from llama_cpp import Llama

from llama_cpp import Llama


class AIManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AIManager, cls).__new__(cls)
            cls._instance.llm = None
            cls._instance.is_ready = False
        return cls._instance

    def load_model(self):
        """Pobiera i ładuje model do pamięci na wyraźne żądanie użytkownika."""
        if self.is_ready:
            return

        try:
            self.llm = Llama.from_pretrained(
                repo_id="Qwen/Qwen2.5-3B-Instruct-GGUF",
                filename="qwen2.5-3b-instruct-q4_k_m.gguf",
                n_ctx=2048,
                n_batch=2048,
                n_gpu_layers=0,
                chat_format="chatml",
                verbose=False
            )
            self.is_ready = True
            print("Model AI wczytany i gotowy do pracy.")
        except Exception as e:
            print(f"Błąd inicjalizacji modelu AI: {e}")
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