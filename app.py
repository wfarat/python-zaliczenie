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
    st.header("⚙️ Ustawienia i Filtry")

    uploaded_file = st.file_uploader("Wgraj własny plik CSV (opcjonalnie)", type=['csv'])
    if uploaded_file is not None:
        with st.spinner("Ładowanie danych..."):
            success = st.session_state.manager.load_data(uploaded_file)
            if success:
                st.success("Plik załadowany poprawnie!")
            else:
                st.error("Błąd podczas ładowania pliku.")

    st.divider()

    st.subheader("Wybierz typ analizy:")

    strategies = {
        "Trendy Sprzedaży (Linia czasu)": SalesTrendStrategy(),
        "Najlepsi Dostawcy (Wykres słupkowy)": TopSuppliersStrategy(),
        "Rozkład Typów Produktów": ItemTypeDistributionStrategy()
    }

    selected_strategy_name = st.radio("Dostępne wykresy:", list(strategies.keys()))

    st.session_state.manager.change_strategy(strategies[selected_strategy_name])
manager = st.session_state.manager

if manager.data_processor.df is not None and not manager.data_processor.df.empty:

    # GŁÓWNY PANEL: Wykresy (lewo) i Panel AI (prawo)
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

        if "ai_raw_response" not in st.session_state:
            st.session_state.ai_raw_response = None
            st.session_state.ai_answer = None
            st.session_state.clicked_question = None  # Zapamiętujemy, jakie pytanie kliknięto

        if st.button("Generuj analizę i pytania", type="primary"):
            if not manager.ai_manager.is_ready:
                st.error("Model AI nie jest gotowy.")
            else:
                with st.spinner("AI analizuje dane..."):
                    st.session_state.ai_raw_response = manager.get_ai_insights()
                    st.session_state.ai_answer = None
                    st.session_state.clicked_question = None
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
                    if st.button(q, use_container_width=True):
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

    st.divider()

    with st.expander("🔍 Podgląd wczytanych danych (pierwsze 100 wierszy)"):
        st.dataframe(manager.get_raw_data().head(100), width='stretch')

else:
    st.warning(
        "Brak danych do analizy. Proszę upewnić się, że plik 'warehouse_and_retail_sales.csv' znajduje się w folderze 'data' lub wgrać własny plik w panelu bocznym.")