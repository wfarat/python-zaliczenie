Oto propozycja kompleksowego dokumentu projektowego (Design Doc), który łączy Twoją wizję z wymogami postawionymi w zadaniu zaliczeniowym.

Dokument ten posłuży Ci jako mapa drogowa do implementacji oraz baza do stworzenia ostatecznego pliku README, który jest wymagany do zaliczenia.

---

# Design Document: System Analizy Danych Sprzedażowych i Magazynowych z Asystentem AI

## 1. Cel i Opis Projektu

Celem projektu jest stworzenie interaktywnej aplikacji do analizy i wizualizacji danych sprzedażowych oraz magazynowych z wykorzystaniem bibliotek NumPy, Pandas, Matplotlib oraz Seaborn. Aplikacja, oparta o interfejs Streamlit, pozwoli użytkownikowi na wczytywanie danych, ich eksplorację oraz wyciąganie wniosków biznesowych ("insights"). Wnioski te, dotyczące m.in. optymalizacji zamówień u dostawców czy predykcji braków magazynowych, będą dodatkowo wspomagane przez lokalny model AI, komunikujący oparte na danych rekomendacje. Projekt zostanie zrealizowany zgodnie z paradygmatem programowania obiektowego.

## 2. Architektura Systemu i Użyte Technologie

* 
**Interfejs Użytkownika:** Streamlit (zastępuje proste sterowanie klawiaturą, oferując nowoczesny interfejs webowy).


* 
**Przetwarzanie Danych:** Pandas, NumPy (manipulacja, sortowanie, filtrowanie, konwersja typów).


* 
**Wizualizacja:** Matplotlib, Seaborn.


* **AI (LLM):** Lokalny model AI (np. poprzez Ollama lub Llama.cpp) integrowany za pomocą biblioteki `requests` lub dedykowanego klienta w Pythonie.

3. Zastosowane Wzorce Projektowe 

Projekt będzie w pełni obiektowy i wykorzysta wzorce projektowe w celu zwiększenia czytelności, elastyczności i optymalizacji działania:

* **Singleton (Wzorzec Kreacyjny):** * *Zastosowanie:* `AIModelManager`.
* *Cel:* Komunikacja z lokalnym modelem AI wymaga zarządzania zasobami (inicjalizacja klienta, utrzymanie połączenia). Wzorzec ten gwarantuje, że w aplikacji istnieje tylko jedna instancja menedżera AI, co zapobiega wielokrotnemu ładowaniu modelu do pamięci RAM/VRAM i optymalizuje zużycie zasobów.




* **Strategy (Wzorzec Behawioralny):** * *Zastosowanie:* Klasy `VisualizationStrategy` (np. `BarChartStrategy`, `TimeSeriesStrategy`, `HeatmapStrategy`).
* *Cel:* W zależności od tego, czy użytkownik chce analizować trendy sprzedaży w czasie, czy porównywać wydajność dostawców, system wybierze inną strategię wizualizacji. Ułatwia to dodawanie nowych typów wykresów w przyszłości bez modyfikowania głównego kodu logiki.


* **Observer (Wzorzec Behawioralny):** * *Zastosowanie:* `DataState` (Subject) oraz `UIComponents` (Observers).
* *Cel:* Gdy użytkownik załaduje nowy plik CSV, zaaplikuje filtry (np. wybierze konkretnego dostawcę) lub dokona manipulacji danymi, główny obiekt przechowujący stan danych (Subject) powiadomi wszystkie podpięte komponenty widoku (Observers - np. wykresy, tabele, sekcję wniosków AI), aby zaktualizowały swój stan i przerenderowały się w interfejsie Streamlit.



4. Analiza i Uzasadnienie Metod 

Wymagane jest uzasadnienie dlaczego wybrane metody i wykresy pasują do danych. W projekcie zastosujemy następujące podejście:

* **Trendy w czasie (Time Series):** Do analizy historycznej sprzedaży użyjemy wykresów liniowych (Line Plots) z biblioteki Seaborn/Matplotlib. Są one optymalne do ukazywania ciągłości i sezonowości popytu.
* 
**Porównanie Dostawców/Produktów:** Wykorzystamy wykresy słupkowe (Bar Charts), które najlepiej sprawdzają się przy danych kategorycznych. Pozwolą one szybko zidentyfikować, który dostawca realizuje najwięcej zamówień lub generuje najwięcej braków.


* **Wnioski AI (Insights):** Skrypty obliczeniowe przetworzą surowe dane (np. zidentyfikują produkty o najniższym stanie magazynowym i najwyższej rotacji). Agregaty te zostaną przekazane do lokalnego modelu AI, który wygeneruje tekstowe rekomendacje (np. "Zwiększ częstotliwość zamówień od dostawcy X dla produktu Y, aby uniknąć braków magazynowych").



## 5. Zapewnienie Jakości i Niezawodności

* 
**Obsługa Wyjątków:** Aplikacja musi zapewniać nieprzerwaną egzekucję. Interfejs Streamlit zostanie obudowany w bloki `try-except` (np. wyłapywanie błędów parsowania plików, braku wymaganych kolumn w załadowanym CSV, czy błędów połączenia z lokalnym AI), aby zamiast "crasha" wyświetlić użytkownikowi przyjazny komunikat o błędzie.


* 
**Testy Jednostkowe:** Zostanie użyta biblioteka `unittest` lub `pytest` do sprawdzania logiki obliczeniowej (np. czy funkcje agregujące sprzedaż lub konwertujące dane numeryczne zwracają poprawne wyniki).


* 
**Styl Kodu:** Cały kod będzie pisany zgodnie ze standardową konwencją PEP-8.



---

## 6. Plan Implementacji

Oto krok po kroku, jak powinieneś zaplanować pracę nad kodem:

**Etap 1: Przygotowanie środowiska i danych**

1. Znajdź odpowiedni zbiór danych (sprzedaż + magazyn) w formacie CSV, np. na portalu Kaggle.


2. Stwórz wirtualne środowisko i plik `requirements.txt` (zawierający m.in. `streamlit`, `pandas`, `numpy`, `matplotlib`, `seaborn`, `pytest`).



**Etap 2: Struktura Obiektowa i Wzorce (Backend)**

1. Zaimplementuj wzorzec **Singleton** do obsługi AI (`ai_manager.py`). Stwórz atrapę (mock), która zwraca statyczny tekst, a integrację z prawdziwym LLM podepnij na samym końcu.
2. Zaimplementuj silnik przetwarzania danych. Stwórz klasy odpowiedzialne za ładowanie danych, czyszczenie ich (np. zmiana typów danych na numeryczne) i sortowanie.


3. Napisz pierwsze testy jednostkowe dla funkcji analizujących (np. test liczenia średniej sprzedaży).



**Etap 3: Warstwa Prezentacji (Wzorce Strategy i Observer)**

1. Stwórz bazową klasę dla **Strategy** oraz konkretne implementacje generujące obiekty `Figure` z Matplotlib (`visualizations.py`).
2. Zbuduj podstawowy interfejs w Streamlit. Dodaj sekcję wgrywania plików CSV przez użytkownika.


3. Zaimplementuj uproszczony wzorzec **Observer** (lub wykorzystaj mechanizm `st.session_state` Streamlita) aby dynamicznie odświeżać wykresy po zmianie filtrów w pasku bocznym (sidebar).



**Etap 4: Integracja Wniosków (Insights) i AI**

1. Połącz statystyki wyliczone przez Pandas z modułem `AIAssistantManager`.
2. Wygeneruj podsumowania tekstowe, które aplikacja będzie czytelnie wyświetlać pod wykresami jako rekomendacje biznesowe.



**Etap 5: Stabilizacja i Dokumentacja (Krytyczne dla zaliczenia)**

1. Przetestuj ręcznie graniczne przypadki działania aplikacji i dodaj obsługę wyjątków (np. gdy użytkownik załaduje plik o złej strukturze).


2. Napisz obszerny plik `README.md`. Zgodnie z wymaganiami odpowiedz tam na pytania dotyczące wyboru metod, danych i uzasadnij strukturę klas oraz wzorce.


3. Upewnij się, że projekt działa samodzielnie (autonomicznie) i można go uruchomić z plikami testowymi.


4. Spakuj projekt do paczki i przygotuj do udostępnienia przez dysk Google.