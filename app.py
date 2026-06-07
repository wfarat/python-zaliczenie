import streamlit as st
from src.inventory_manager import InventoryManager

from src.visualizations import (
    SalesTrendStrategy,
    TopSuppliersStrategy,
    ItemTypeDistributionStrategy
)

st.set_page_config(page_title="Analiza Sprzedaży i Magazynu", layout="wide", page_icon="📊")

if 'manager' not in st.session_state:
    st.session_state.manager = InventoryManager()
    st.session_state.manager.load_data("warehouse_and_retail_sales.csv")

st.title("📊 System Analizy Danych Sprzedażowych i Magazynowych z AI")
st.markdown("Wczytuj, eksploruj i generuj wnioski z danych wspomagane przez lokalny model AI.")
with st.sidebar:
    st.header("⚙️ Ustawienia i Dane")

    st.subheader("Wybierz zestaw danych:")

    available_datasets = {
        "Tradycyjna Sprzedaż (Detal i Magazyn)": "Warehouse_and_Retail_Sales.csv",
        "E-commerce (Dostawy Kurierskie)": "online_sales_dataset.csv",
        "Alternatywny (Detal i magazyn)": "warehouse_sales_2017.csv"
    }

    selected_label = st.selectbox("Dostępne zbiory:", list(available_datasets.keys()))
    selected_filename = available_datasets[selected_label]

    if "current_loaded_file" not in st.session_state or st.session_state.current_loaded_file != selected_filename:
        with st.spinner(f"Ładowanie danych z {selected_filename}..."):
            success = st.session_state.manager.load_data(selected_filename)
            if success:
                st.session_state.current_loaded_file = selected_filename
                st.success("Dane załadowane pomyślnie!")
            else:
                st.error(f"Błąd! Upewnij się, że plik {selected_filename} istnieje w folderze 'data'.")

    st.divider()

    st.subheader("Wybierz typ analizy:")

    strategies = {
        "Trendy Sprzedaży (Linia czasu)": SalesTrendStrategy(),
        "Najlepsi Dostawcy / Kurierzy": TopSuppliersStrategy(),
        "Rozkład Typów Produktów": ItemTypeDistributionStrategy()
    }
    selected_strategy_name = st.radio("Dostępne wykresy:", list(strategies.keys()))
    st.session_state.manager.change_strategy(strategies[selected_strategy_name])
    st.divider()


    st.subheader("Silnik AI (LLM)")
    if not st.session_state.manager.ai_manager.is_ready:
        st.warning("Model AI nie jest jeszcze wczytany.")
        if st.button("Pobierz i uruchom lokalne AI", type="primary"):
            with st.status("Inicjalizacja silnika AI...", expanded=True) as status:
                st.write("Wyszukiwanie modelu w pamięci podręcznej...")
                st.write("Pobieranie plików z HuggingFace (to może potrwać kilka minut za pierwszym razem)...")
                st.write("Ładowanie wag modelu do pamięci RAM...")
                st.session_state.manager.ai_manager.load_model()

                if st.session_state.manager.ai_manager.is_ready:
                    status.update(label="Model AI gotowy do pracy!", state="complete", expanded=False)
                    st.rerun()
                else:
                    status.update(label="Błąd inicjalizacji modelu.", state="error", expanded=True)
    else:
        st.success("Lokalny model AI jest aktywny i gotowy do pracy.")

manager = st.session_state.manager

if manager.data_processor.df is not None and not manager.data_processor.df.empty:

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"📈 Wykres: {selected_strategy_name}")
        try:
            fig = manager.generate_visualization()
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Wystąpił błąd podczas generowania wykresu: {e}")

    with col2:
        st.subheader("🤖 Interaktywne Wnioski AI")

        if "ai_loading" not in st.session_state:
            st.session_state.ai_loading = False
            st.session_state.ai_raw_response = None
            st.session_state.ai_answer = None
            st.session_state.clicked_question = None

        button_placeholder = st.empty()
        is_disabled = st.session_state.ai_loading

        if button_placeholder.button("Generuj analizę i pytania", type="primary", disabled=is_disabled):
            st.session_state.ai_loading = True
            st.rerun()

        if st.session_state.ai_loading:
            button_placeholder.button("Generowanie...", disabled=True)  # UI: informacja o pracy

            if not manager.ai_manager.is_ready:
                with st.status("Inicjalizacja silnika AI...", expanded=True) as status:
                    st.write("Wczytywanie modelu (to może potrwać)...")
                    manager.ai_manager.load_model()
                    if not manager.ai_manager.is_ready:
                        status.update(label="Błąd ładowania.", state="error")
                        st.session_state.ai_loading = False
                        st.stop()
                    status.update(label="Model wczytany!", state="complete")

            with st.spinner("AI analizuje dane..."):
                st.session_state.ai_raw_response = manager.get_ai_insights()
                st.session_state.ai_answer = None
                st.session_state.clicked_question = None
                st.session_state.ai_loading = False
                st.rerun()

        if st.session_state.ai_raw_response:
            raw_text = st.session_state.ai_raw_response
            if "PYTANIA:" in raw_text:
                parts = raw_text.split("PYTANIA:")
                summary = parts[0].replace("PODSUMOWANIE:", "").strip()
                questions = [q.strip("- ").strip() for q in parts[1].split("\n") if q.strip().startswith("-")]
            else:
                summary = raw_text
                questions = []

            st.info(summary)

            if questions:
                st.write("**Wybierz pytanie pogłębiające:**")
                for q in questions[:3]:
                    if st.button(q, key=q, use_container_width=True):  # Dodano key=q, aby przyciski były unikalne
                        st.session_state.clicked_question = q
                        with st.spinner("AI myśli..."):
                            st.session_state.ai_answer = manager.get_ai_follow_up(q)
                        st.rerun()

    if st.session_state.ai_answer:
        st.divider()
        st.subheader("🔍 Szczegółowa Analiza (Deep Dive)")
        with st.container(border=True):
            st.markdown(f"**Twoje pytanie:** *{st.session_state.clicked_question}*")
            st.markdown(st.session_state.ai_answer)