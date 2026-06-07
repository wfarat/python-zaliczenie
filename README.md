# System Analizy Danych Sprzedażowych i Magazynowych z AI

Rozbudowana aplikacja analityczna (Dashboard) zbudowana w bibliotece **Streamlit**, służąca do interaktywnej eksploracji danych sprzedażowo-logistycznych. Projekt integruje tradycyjne techniki Data Science (Pandas, Seaborn) z **lokalnym modelem sztucznej inteligencji (LLM)**, który pełni rolę wirtualnego analityka, generując wnioski biznesowe całkowicie offline.

---

## Główne funkcjonalności

* **Wizualizacja Danych:** Trzy interaktywne moduły analityczne (Trendy w czasie, Dywersyfikacja Dostawców/Kurierów, Analiza Sezonowości Asortymentu).
* **Lokalne AI (Privacy-First):** Wykorzystanie modelu w formacie GGUF operującego wyłącznie w pamięci maszyny lokalnej, bez wysyłania wrażliwych danych do chmury.
* **Deep Dive AI:** Interaktywny interfejs pozwalający na zadawanie pytań pogłębiających, na które AI odpowiada za pomocą tekstowych analiz oraz tabel w formacie Markdown.
* **Smart Adapter:** Aplikacja automatycznie wykrywa strukturę pliku CSV. Potrafi w locie dostosować nowe zbiory danych (np. e-commerce) do swojego silnika, zmieniając nawet odpowiednio słownictwo na wykresach (np. z "Dostawców" na "Kurierów").

---

## 🏛Architektura i Wzorce Projektowe

Projekt został zaprojektowany z rygorystycznym zachowaniem paradygmatów programowania obiektowego (OOP) oraz zasad SOLID. Poniżej znajduje się uzasadnienie kluczowych decyzji architektonicznych:

### 1. Wzorzec Wzmocnionej Strategii (Strategy Pattern)
* **Gdzie:** Klasa bazowa `VisualizationStrategy` oraz jej implementacje (np. `TopSuppliersStrategy`, `SalesTrendStrategy`).
* **Uzasadnienie:** Moduł wizualizacji jest najbardziej podatnym na zmiany elementem systemu. Zamiast budować gigantyczną instrukcję `if-else` w interfejsie, zastosowano wzorzec Strategii. Każda strategia hermetyzuje dwa obowiązki: sposób rysowania wykresów (`generate_plot`) oraz sposób kompresowania danych pod "wąski" kontekst modelu AI (`generate_ai_context`). Dzięki temu dodanie nowej analizy do systemu nie wymaga modyfikacji już istniejącego kodu (spełnienie *Open/Closed Principle*).

### 2. Wzorzec Singleton z Leniwą Inicjalizacją (Lazy Singleton)
* **Gdzie:** Klasa `AIManager`.
* **Uzasadnienie:** Modele językowe (np. Qwen2.5-3B) rezerwują gigantyczne ilości pamięci RAM (ok. 3-4 GB). Środowisko Streamlit ma tendencję do wielokrotnego przeładowywania skryptu przy każdej interakcji użytkownika. Zastosowanie wzorca Singleton gwarantuje, że ciężki silnik LLM (`llama.cpp`) zostanie zainicjalizowany w systemie **tylko raz**. Zapobiega to wyciekom pamięci i krytycznym błędom *Out Of Memory (OOM)*.

### 3. Wzorzec Fasady (Facade)
* **Gdzie:** Klasa `SalesAndInventoryManager` (lub `InventoryManager`).
* **Uzasadnienie:** Interfejs użytkownika w `app.py` jest całkowicie odcięty od złożoności biblioteki Pandas, transformacji danych oraz komunikacji z LLM. Fasada udostępnia prosty interfejs (np. `load_data()`, `change_strategy()`, `get_ai_insights()`), co drastycznie zwiększa czytelność warstwy prezentacji.

### 4. Adapter w Locie (On-the-fly Adapter)
* **Gdzie:** Metoda `_detect_and_adapt_schema()` w klasie `DataProcessor`.
* **Uzasadnienie:** Aplikacja musiała obsłużyć nowy, niespodziewany zbiór danych (np. transakcje online), nie psując przy tym obecnych funkcjonalności. Adapter w locie bada nazwy kolumn i automatycznie wektoryzuje dane (przy użyciu `np.where`), mapując je do wewnętrznego schematu. Dzięki temu cały potężny silnik analityczny potrafi bez żadnych zmian obsłużyć zupełnie nowe formaty plików.

---

## Wybór Metod i Uzasadnienie Analityczne

W interfejsie postawiono na analizy komplementarne (Makro -> Mikro). 

1.  **Analiza Sezonowości Asortymentu:** Zrezygnowano z prostych wykresów słupkowych na rzecz **Znormalizowanej Mapy Cieplnej (Heatmap)**. Dzięki podziałowi każdej wartości przez sumę w wierszu, mapa cieplna ukazuje mikro-sezonowość każdego produktu niezależnie od jego ogólnego udziału w rynku.
2.  **Analiza Dostawców / Profilowanie:** Wykorzystano **100% Skumulowane Wykresy Horyzontalne (100% Stacked Bar Chart)**. Pozwala to na precyzyjną identyfikację, z czego składa się obrót danego partnera B2B. Zestawienie tego obok wykresu absolutnego wolumenu tworzy pełny obraz ryzyka w łańcuchu dostaw.
3.  **Biblioteki i Wydajność:** Użyto `pandas` do agregacji danych przed ich wysłaniem do Streamlit i AI. Zamiast iteracji w Pythonie, procesy transformacji i czyszczenia oparto na zwektoryzowanych metodach biblioteki `NumPy`, co pozwala na błyskawiczne procesowanie setek tysięcy wierszy.

---

## Integracja ze Sztuczną Inteligencją (Lokalny LLM)

Aby zachować pełną niezależność i bezpieczeństwo danych korporacyjnych, zrezygnowano z płatnych API (jak OpenAI) na rzecz modelu uruchamianego lokalnie.

* **Silnik:** Użyto bindów C++ czyli biblioteki `llama-cpp-python`. Gwarantuje ona bezkompromisową wydajność podczas pracy na CPU, wykorzystując zoptymalizowany format `.gguf`.
* **Model:** System zoptymalizowano pod modele z rodziny `Qwen2.5` (rekomendowany: `Qwen2.5-3B-Instruct`).
* **Prompt Engineering i Zarządzanie Kontekstem:** Aby uniknąć przepełnienia pamięci kontekstowej (okna) i "wymyślania" danych przez AI (halucynacje), aplikacja **nie wysyła** do modelu surowego DataFrame. Każda Strategia odpowiedzialna jest za przygotowanie wysoce skondensowanej "pigułki wiedzy" (tabeli z podsumowaniem) oraz dedykowanego promptu narzucającego rygorystyczny format odpowiedzi (PODSUMOWANIE + PYTANIA).

---

## Struktura Projektu

```text
├── app.py                      # Warstwa interfejsu użytkownika (Streamlit)
├── requirements.txt            # Lista zależności projektowych
├── data/                       # Katalog na pliki *.csv
│   └── warehouse_and_retail_sales.csv
├── models/                     # Miejsce na plik modelu (.gguf)
├── tests/                      # Moduł testów jednostkowych (pytest)
│   └── test_visualizations.py  
│   └── test_data_processor.py  
└── src/                        # Kod źródłowy (Backend)
    ├── __init__.py
    ├── ai_manager.py           # Komunikacja z Llama.cpp (Singleton)
    ├── data_processor.py       # Transformacje Pandas (Adapter)
    ├── inventory_manager.py    # Klasa integrująca (Fasada)
    └── visualizations.py       # Klasy rysujące (Strategie)