# =============================================================================
# KALKULATOR CZASU PÓŁMARATONU - WERSJA 2.1
# Aplikacja do przewidywania czasu ukończenia półmaratonu na podstawie wieku,
# płci i tempa na 5km, wykorzystująca model uczenia maszynowego.
# 
# Autor: Alan Steinbarth
# Email: alan.steinbarth@gmail.com
# GitHub: https://github.com/AlanSteinbarth/Kalkulator-dla-biegaczy
# =============================================================================
#
# 🗂️ SPIS TREŚCI
# 1. Importy i konfiguracja pakietów
# 2. Konfiguracja strony i stylów
# 3. Konfiguracja globalna i zmienne
# 4. Funkcje pomocnicze (walidacja, model, dane, ekstrakcja)
# 5. Obsługa klucza OpenAI API (status, sidebar)
# 6. Interfejs użytkownika (główny widok)
# 7. Footer
# =============================================================================

import streamlit as st
import pandas as pd
import datetime
import logging
import json
import re
import os
from dotenv import load_dotenv
from openai import OpenAI

# Próba importu opcjonalnych pakietów z fallback'ami
try:
    from pycaret.regression import load_model as pycaret_load_model, predict_model as pycaret_predict_model
    PYCARET_AVAILABLE = True
      # Bezpośrednie przypisanie oryginalnych funkcji PyCaret
    load_model = pycaret_load_model
    predict_model = pycaret_predict_model  # type: ignore[assignment]
    
except ImportError:
    PYCARET_AVAILABLE = False
    
    # Fallback funkcje gdy PyCaret nie jest dostępny - kompatybilne z oryginalnym API
    def load_model(model_name, platform=None, authentication=None, verbose=True):  # noqa: ARG001
        """Fallback funkcja gdy PyCaret nie jest dostępny."""
        # Parametry zachowane dla kompatybilności z PyCaret API
        _ = platform, authentication, verbose  # Jawne oznaczenie nieużywanych parametrów
        st.error("❌ PyCaret nie jest zainstalowany. Zainstaluj go komendą: pip install pycaret")
        logger.error("PyCaret nie jest dostępny - model %s nie może być załadowany", model_name)
        return None

    def predict_model(estimator, data=None, round_digits=4, verbose=True):  # noqa  # type: ignore
        """Fallback funkcja gdy PyCaret nie jest dostępny.""" 
        # Parametry zachowane dla kompatybilności z PyCaret API
        _ = estimator, data, round_digits, verbose  # Jawne oznaczenie nieużywanych parametrów  
        st.error("❌ PyCaret nie jest zainstalowany. Nie można wykonać przewidywania.")
        logger.error("PyCaret nie jest dostępny - przewidywanie niemożliwe")
        return None
    
# Sprawdzenie dostępności opcjonalnych pakietów
PLOTLY_AVAILABLE = False
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:    
    # Zaślepka dla px i figur plotly
    class PlotlyFigure:
        def add_vline(self, *_args, **_kwargs):
            return self
        
        def add_trace(self, *_args, **_kwargs):
            return self
        
        def update_layout(self, *_args, **_kwargs):
            return self
            
        def update_xaxes(self, *_args, **_kwargs):
            return self
            
        def update_yaxes(self, *_args, **_kwargs):
            return self
            
    class PlotlyExpress:
        def __getattr__(self, _name):
            def method(*_args, **_kwargs):
                return PlotlyFigure()
            return method
    
    class PlotlyGraphObjects:
        def __getattr__(self, _name):
            def method(*_args, **_kwargs):
                return PlotlyFigure()
            return method
            
    px = PlotlyExpress()
    go = PlotlyGraphObjects()

# Konfiguracja strony
st.set_page_config(
    page_title="🏃‍♂️ Kalkulator dla biegaczy", 
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Wymuszenie poprawnego tytułu karty z emoji w Chrome i innych przeglądarkach
st.markdown("""
<script>
document.title = "🏃‍♂️ Kalkulator dla biegaczy 🏃‍♀️";
</script>
""", unsafe_allow_html=True)

# Poprawka tytułu karty (zakładki) w przeglądarce Chrome
st.markdown(
    """
    <script>
        document.title = "🏃‍♂️ Kalkulator dla biegaczy 🏃‍♀️";
    </script>
    """,
    unsafe_allow_html=True
)

# Wymuszenie ciemnego motywu
st.markdown("""
<style>
    /* GŁÓWNE TŁO APLIKACJI */
    .stApp {
        background-color: #0e1117 !important;
        color: #fafafa !important;
    }
    
    /* SUPER AGRESYWNE WYMUSZENIE CIEMNEGO MOTYWU DLA SIDEBARA */
    
    /* Wszystkie możliwe selektory dla sidebara */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] *,
    section[data-testid="stSidebar"] > *,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] > div,
    section[data-testid="stSidebar"] div[data-testid="stSidebarContent"],
    section[data-testid="stSidebar"] .st-emotion-cache-jx6q2s,
    section[data-testid="stSidebar"] .st-emotion-cache-1lqf7hx,
    section[data-testid="stSidebar"] .st-emotion-cache-1yiq2ps,
    section[data-testid="stSidebar"] .st-emotion-cache-bu46p3,
    section[data-testid="stSidebar"] .css-1d391kg,
    .st-emotion-cache-jx6q2s,
    .st-emotion-cache-1lqf7hx,
    .st-emotion-cache-1yiq2ps,
    .st-emotion-cache-bu46p3,
    .css-1d391kg {
        background-color: #0e1117 !important;
        background: #0e1117 !important;
        color: #fafafa !important;
    }
    
    /* Dodatkowe wymuszenie dla wszystkich elementów w sidebarze */
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stMarkdown *,
    section[data-testid="stSidebar"] .stButton,
    section[data-testid="stSidebar"] .stExpander,
    section[data-testid="stSidebar"] .stMetric,
    section[data-testid="stSidebar"] .stAlert,
    section[data-testid="stSidebar"] .stTextInput {
        background-color: #0e1117 !important;
        background: #0e1117 !important;
    }
    
    /* Globalne wymuszenie dla wszystkich divów w sidebarze */
    section[data-testid="stSidebar"] div[class*="st-emotion-cache"],
    section[data-testid="stSidebar"] div[class*="css-"] {
        background-color: #0e1117 !important;
        background: #0e1117 !important;
    }
    
    /* Dodatkowe selektory dla problematycznych elementów */
    .st-emotion-cache-1lqf7hx {
        background-color: #0e1117 !important;
        color: #fafafa !important;
    }
    
    /* Wszystkie divs w sidebarze */
    section[data-testid="stSidebar"] div[class*="st-emotion-cache"] {
        background-color: #0e1117 !important;
        color: #fafafa !important;
    }
    
    /* Specjalne selectory dla dynamicznych klas */
    div[class*="st-emotion-cache"]:has(section[data-testid="stSidebar"]) {
        background-color: #0e1117 !important;
    }
    
    /* Tło głównej zawartości */
    .main .block-container {
        background-color: #0e1117;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Stylowanie nagłówków */
    h1, h2, h3, h4, h5, h6 {
        color: #fafafa !important;
    }
      /* Stylowanie tekstu */
    p, div, span, li {
        color: #fafafa !important;
    }
    
    /* Tekst w sidebarze */
    section[data-testid="stSidebar"] * {
        color: #fafafa !important;
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] h4, 
    section[data-testid="stSidebar"] h5, 
    section[data-testid="stSidebar"] h6 {
        color: #ffffff !important;
    }
    
    /* Stylowanie inputów */
    .stTextArea > div > div > textarea {
        background-color: #262730 !important;
        color: #fafafa !important;
        border: 1px solid #4a4a4a !important;
    }
    
    /* Stylowanie przycisków */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
        font-weight: 600 !important;
        font-size: 1.1em !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }    /* Stylowanie przycisków w sidebarze */
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        width: 100% !important;
        margin-bottom: 8px !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(79, 172, 254, 0.3) !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4) !important;
    }
    
    /* Dodatkowe selektory dla przycisków w sidebarze */
    .css-1d391kg .stButton > button,
    .st-emotion-cache-1d391kg .stButton > button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        width: 100% !important;
        margin-bottom: 8px !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(79, 172, 254, 0.3) !important;
    }
    
    /* Stylowanie alertów w sidebarze */
    section[data-testid="stSidebar"] .stAlert {
        background-color: rgba(38, 39, 48, 0.8) !important;
        border: 1px solid #4a4a4a !important;
        border-radius: 8px !important;
    }
    
    /* Stylowanie inputów w sidebarze */
    section[data-testid="stSidebar"] .stTextInput input {
        background-color: #262730 !important;
        color: #fafafa !important;
        border: 1px solid #4a4a4a !important;
    }
    
    /* Stylowanie expanderów w sidebarze */
    section[data-testid="stSidebar"] .stExpander {
        background-color: rgba(38, 39, 48, 0.6) !important;
        border: 1px solid #4a4a4a !important;
        border-radius: 8px !important;
    }
    
    section[data-testid="stSidebar"] .stExpander summary {
        background-color: rgba(38, 39, 48, 0.8) !important;
        color: #fafafa !important;
    }
      /* Stylowanie metryk */
    .metric-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important;
        padding: 1rem !important;
        border-radius: 12px !important;
        margin: 0.5rem 0 !important;
        border: 1px solid #4a4a4a !important;
    }
    
    /* Stylowanie metryk w sidebarze */
    section[data-testid="stSidebar"] .stMetric {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important;
        padding: 0.8rem !important;
        border-radius: 8px !important;
        margin: 0.3rem 0 !important;
        border: 1px solid #4a4a4a !important;
    }
    
    section[data-testid="stSidebar"] .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: bold !important;
    }
      section[data-testid="stSidebar"] .stMetric [data-testid="stMetricLabel"] {
        color: #cbd5e0 !important;
    }
    
    /* Dodatkowe naprawy dla czarnego tła w sidebarze */
    section[data-testid="stSidebar"] [data-testid="stExpanderDetails"] {
        background-color: #0e1117 !important;
        color: #fafafa !important;
    }
    
    /* Naprawy dla paragrafów w sidebarze */
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] div[class*="st-emotion-cache"] p {
        background-color: transparent !important;
        color: #fafafa !important;
    }
    
    /* Success i warning messages w sidebarze */
    section[data-testid="stSidebar"] .stSuccess {
        background-color: rgba(17, 153, 142, 0.2) !important;
        color: #fafafa !important;
        border: 1px solid #11998e !important;
    }
    
    section[data-testid="stSidebar"] .stWarning {
        background-color: rgba(251, 146, 60, 0.2) !important;
        color: #fafafa !important;
        border: 1px solid #fb923c !important;
    }
    
    section[data-testid="stSidebar"] .stInfo {
        background-color: rgba(59, 130, 246, 0.2) !important;
        color: #fafafa !important;
        border: 1px solid #3b82f6 !important;
    }
    
    /* Naprawy dla wszystkich elementów w sidebarze - ostatnia deska ratunku */
    section[data-testid="stSidebar"] * {
        background-color: inherit !important;
    }
    
    /* Specjalne naprawy dla konkretnych klas które widzimy w CSS */
    .st-emotion-cache-qbgoph {
        background-color: transparent !important;
    }
      section[data-testid="stSidebar"] .st-emotion-cache-qbgoph {
        background-color: transparent !important;
        color: #fafafa !important;
    }
    
    /* ULTIMATE FIX - nadpisanie wszystkich możliwych klas CSS dla sidebara */
    section[data-testid="stSidebar"] [class*="st-emotion-cache"],
    section[data-testid="stSidebar"] [class*="css-"],
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        background-color: transparent !important;
        background: transparent !important;
    }
    
    /* Globalne nadpisanie tylko dla sidebara */
    section[data-testid="stSidebar"] {
        background: #0e1117 !important;
    }
    
    section[data-testid="stSidebar"] > * {
        background-color: #0e1117 !important;
    }
    
    /* Używamy ważności !important z bardzo wysoką specyficznością */
    html body div div section[data-testid="stSidebar"] * {
        background-color: inherit !important;
        background: inherit !important;
    }
    
    html body div div section[data-testid="stSidebar"] {
        background-color: #0e1117 !important;
        background: #0e1117 !important;
    }
    
    /* Stylowanie success box */
    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
        color: #000 !important;
        padding: 1.5rem !important;
        border-radius: 15px !important;
        border: none !important;
        box-shadow: 0 8px 25px rgba(17, 153, 142, 0.3) !important;
        margin: 1rem 0 !important;
    }
    
    .success-box h3 {
        color: #000 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .success-box p {
        color: #333 !important;
        margin-bottom: 0 !important;
    }
    
    /* Stylowanie kart informacyjnych */
    .stInfo {
        background-color: #1e3a8a !important;
        border-left: 4px solid #3b82f6 !important;
    }
    
    .stWarning {
        background-color: #92400e !important;
        border-left: 4px solid #f59e0b !important;
    }
    
    .stError {
        background-color: #991b1b !important;
        border-left: 4px solid #ef4444 !important;
    }
    
    /* Stylowanie expandera */
    .streamlit-expanderHeader {
        background-color: #262730 !important;
        color: #fafafa !important;
        border: 1px solid #4a4a4a !important;
        border-radius: 8px !important;
    }
    
    .streamlit-expanderContent {
        background-color: #1a1a1a !important;
        border: 1px solid #4a4a4a !important;
        border-top: none !important;
    }
    
    /* Stylowanie wykresów Plotly */
    .js-plotly-plot {
        background-color: #0e1117 !important;
    }
    
    /* Stylowanie dividerów */
    hr {
        border-color: #4a4a4a !important;
    }
    
    /* Stylowanie footera */
    .footer {
        background-color: #262730 !important;
        padding: 1rem !important;
        border-radius: 8px !important;
        margin-top: 2rem !important;
        border: 1px solid #4a4a4a !important;
    }
    
    /* Stylowanie tabeli (jeśli występuje) */
    .dataframe {
        background-color: #262730 !important;
        color: #fafafa !important;
    }
    
    /* Stylowanie spinnera */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Animacje */
    @keyframes glow {
        0% { box-shadow: 0 0 5px rgba(102, 126, 234, 0.5); }
        50% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.8); }
        100% { box-shadow: 0 0 5px rgba(102, 126, 234, 0.5); }
    }
      .stButton > button:focus {
        animation: glow 2s infinite !important;
    }
    
    /* =================================================================== */
    /* ULTIMATE SIDEBAR BACKGROUND FIX - NAJWYŻSZY PRIORYTET */
    /* =================================================================== */
    
    /* Super specyficzne selektory z najwyższą możliwą specyficznością */
    html body div#root div.stApp div.st-emotion-cache-13k62yr div.st-emotion-cache-1yiq2ps section[data-testid="stSidebar"],
    html body div#root div.stApp div.st-emotion-cache-13k62yr div.st-emotion-cache-1yiq2ps section[data-testid="stSidebar"] *,
    html body div#root div.stApp div.st-emotion-cache-13k62yr div.st-emotion-cache-1yiq2ps section[data-testid="stSidebar"] div,
    html body div.stApp section[data-testid="stSidebar"],
    html body div.stApp section[data-testid="stSidebar"] *,
    html body div.stApp section[data-testid="stSidebar"] div {
        background-color: #0e1117 !important;
        background: #0e1117 !important;
    }
    
    /* Wymuszenie na poziomie najbardziej ogólnym */
    * {
        --sidebar-background-color: #0e1117 !important;
    }
    
    /* Specjalne wymuszenie dla znanych klas */
    .st-emotion-cache-1lqf7hx,
    .st-emotion-cache-jx6q2s,
    .st-emotion-cache-1yiq2ps,
    .st-emotion-cache-qbgoph {
        background-color: #0e1117 !important;
        background: #0e1117 !important;
    }
    
    /* Absolutnie wszystko w sidebarze */
    section[data-testid="stSidebar"] {
        background-color: #0e1117 !important;
        background: #0e1117 !important;
    }
    
    section[data-testid="stSidebar"] > * {
        background-color: transparent !important;
        background: transparent !important;
    }
    
    /* Jeszcze bardziej agresywne wymuszenie */
    body section[data-testid="stSidebar"] *,
    body section[data-testid="stSidebar"] div,
    body section[data-testid="stSidebar"] p,
    body section[data-testid="stSidebar"] span,
    body section[data-testid="stSidebar"] [class*="st-emotion-cache"],
    body section[data-testid="stSidebar"] [class*="css-"] {
        background-color: inherit !important;
        background: inherit !important;
    }
</style>
""", unsafe_allow_html=True)

# Dodatkowy JavaScript do wymuszenia ciemnego motywu
st.markdown("""
<script>
    // JavaScript do wymuszenia ciemnego tła w sidebarze
    function forceDarkSidebar() {
        // Znajdź sidebar
        const sidebar = document.querySelector('section[data-testid="stSidebar"]');
        if (sidebar) {
            // Wymuś ciemne tło na sidebarze i wszystkich jego dzieciach
            sidebar.style.backgroundColor = '#0e1117';
            sidebar.style.background = '#0e1117';
            
            // Znajdź wszystkie elementy wewnątrz sidebara
            const sidebarElements = sidebar.querySelectorAll('*');
            sidebarElements.forEach(element => {
                // Nie zmieniaj tła dla konkretnych elementów zawartości, tylko kontenerów
                const computedStyle = window.getComputedStyle(element);
                if (computedStyle.backgroundColor === 'rgb(38, 39, 48)' || 
                    computedStyle.backgroundColor === 'rgb(33, 37, 41)' ||
                    computedStyle.backgroundColor.includes('262730')) {
                    element.style.backgroundColor = '#0e1117';
                    element.style.background = '#0e1117';
                }
            });
        }
    }
    
    // Uruchom natychmiast
    forceDarkSidebar();
    
    // Uruchom ponownie po krótkim opóźnieniu (gdy elementy się załadują)
    setTimeout(forceDarkSidebar, 100);
    setTimeout(forceDarkSidebar, 500);
    setTimeout(forceDarkSidebar, 1000);
    
    // Uruchom gdy DOM się zmieni
    const observer = new MutationObserver(forceDarkSidebar);
    observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# KONFIGURACJA I ZMIENNE GLOBALNE
# =============================================================================

load_dotenv()

class Config:
    """Klasa konfiguracyjna aplikacji."""
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_PATH = "huber_model_halfmarathon_time"
    DATA_PATH = "df_cleaned.csv" 
    MIN_AGE = 10
    MAX_AGE = 100
    MIN_TEMPO = 3.0
    MAX_TEMPO = 10.0

config = Config()

# Inicjalizacja klienta OpenAI
client = None
OPENAI_AVAILABLE = False

def verify_openai_key(api_key: str) -> tuple[bool, str]:
    """
    Weryfikuje klucz OpenAI API poprzez wysłanie testowego zapytania.
    
    Args:
        api_key: Klucz API do weryfikacji
        
    Returns:
        tuple: (czy_klucz_prawidlowy, wiadomosc_o_statusie)
    """
    if not api_key or not api_key.strip():
        return False, "Klucz API jest pusty"
    
    if not api_key.startswith("sk-"):
        return False, "Klucz API ma nieprawidłowy format (powinien zaczynać się od 'sk-')"
    
    try:
        test_client = OpenAI(api_key=api_key)        
        # Wysyłanie krótkiego testowego zapytania
        response = test_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=1,
            timeout=10
        )
        
        if response and response.choices:
            return True, "Klucz API jest prawidłowy i funkcjonalny"
        else:
            return False, "Otrzymano nieprawidłową odpowiedź z OpenAI"
            
    except (ValueError, TypeError, ConnectionError, TimeoutError) as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
            return False, "Klucz API jest nieprawidłowy lub wygasł"
        elif "quota" in error_msg.lower() or "billing" in error_msg.lower():
            return False, "Problem z rozliczeniami lub przekroczono limit"
        elif "timeout" in error_msg.lower():
            return False, "Przekroczono czas oczekiwania na odpowiedź"
        else:
            return False, f"Błąd weryfikacji: {error_msg}"

def initialize_openai_client(api_key: str | None = None) -> tuple[bool, str]:
    """
    Inicjalizuje klienta OpenAI z podanym kluczem.
    
    Args:
        api_key: Klucz API (opcjonalny, domyślnie z .env)
        
    Returns:
        tuple: (czy_inicjalizacja_udana, wiadomosc_o_statusie)
    """
    # Global jest potrzebne do modyfikacji stanu klienta OpenAI w całej aplikacji
    global client, OPENAI_AVAILABLE  # pylint: disable=global-statement
    
    # Użyj podanego klucza lub z .env
    key_to_use = api_key or config.OPENAI_API_KEY
    
    if not key_to_use or not key_to_use.strip():
        client = None
        OPENAI_AVAILABLE = False
        return False, "Brak klucza OpenAI API"
    
    try:        # Weryfikuj klucz przed inicjalizacją
        key_is_valid, init_message = verify_openai_key(key_to_use)
        
        if key_is_valid:
            client = OpenAI(api_key=key_to_use)
            OPENAI_AVAILABLE = True
            logger.info("OpenAI klient zainicjalizowany pomyślnie")
            return True, "OpenAI zostało pomyślnie zainicjalizowane"
        else:
            client = None
            OPENAI_AVAILABLE = False
            logger.warning("Nieprawidłowy klucz OpenAI: %s", init_message)
            return False, f"Błąd weryfikacji klucza: {init_message}"
            
    except (ValueError, TypeError, ImportError) as e:
        client = None
        OPENAI_AVAILABLE = False
        logger.error("Błąd inicjalizacji OpenAI: %s", str(e))
        return False, f"Błąd inicjalizacji: {str(e)}"

# Początkowa inicjalizacja klienta OpenAI z .env
initial_success, initial_message = initialize_openai_client()
if not initial_success:
    logger.warning("Początkowa inicjalizacja OpenAI nieudana: %s", initial_message)

# =============================================================================
# FUNKCJE POMOCNICZE
# =============================================================================

def create_fallback_chart(title, message):
    """Tworzy prostą alternatywę dla wykresów plotly z ciemnym motywem."""
    return f"""
    <div class='chart-fallback'>
        <h4>📊 {title}</h4>
        <p>{message}</p>
        <p><em>💡 Zainstaluj plotly aby zobaczyć interaktywne wykresy: pip install plotly</em></p>
    </div>
    """

# =============================================================================
# FUNKCJE POMOCNICZE - WALIDACJA
# =============================================================================

def is_valid_age(age):
    """
    Sprawdza, czy podany wiek jest prawidłowy.
    
    Args:
        age: Wiek do sprawdzenia
        
    Returns:
        bool: True jeśli wiek jest prawidłowy
    """
    try:
        age_int = int(age)
        return config.MIN_AGE <= age_int <= config.MAX_AGE
    except (ValueError, TypeError):
        return False


def is_valid_tempo(tempo):
    """
    Sprawdza, czy podane tempo jest prawidłowe.
    
    Args:
        tempo: Tempo do sprawdzenia
        
    Returns:
        bool: True jeśli tempo jest prawidłowe
    """
    try:
        tempo_float = float(tempo)
        return config.MIN_TEMPO <= tempo_float <= config.MAX_TEMPO
    except (ValueError, TypeError):
        return False


def is_valid_gender(gender):
    """Sprawdza, czy płeć jest prawidłowa."""
    return gender in ['M', 'K']


def validate_user_data(data):
    """
    Waliduje kompletny zestaw danych użytkownika.
    
    Args:        data: Słownik z danymi użytkownika
        
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    errors = []  # Zmieniona nazwa, by uniknąć konfliktu z outer scope
    
    # Sprawdzenie wymaganych pól
    required_fields = ['Wiek', 'Płeć', '5 km Tempo']
    for field in required_fields:
        if field not in data:
            errors.append(f"Brak pola: {field}")
    
    if errors:
        return False, errors
    
    # Walidacja poszczególnych pól
    if not is_valid_age(data['Wiek']):
        errors.append(f"Wiek powinien być liczbą z zakresu {config.MIN_AGE}-{config.MAX_AGE} lat")
    
    if not is_valid_gender(data['Płeć']):
        errors.append("Płeć powinna być określona jako 'M' lub 'K'")
    
    if not is_valid_tempo(data['5 km Tempo']):
        errors.append(f"Tempo na 5km powinno być liczbą z zakresu {config.MIN_TEMPO}-{config.MAX_TEMPO} min/km")
    
    return len(errors) == 0, errors


# =============================================================================
# FUNKCJE POMOCNICZE - MODEL I DANE
# =============================================================================

def calculate_5km_time(tempo):
    """
    Przelicza tempo biegu (min/km) na całkowity czas w sekundach dla dystansu 5km.
    Obsługuje formaty: 5.0, "5.0", "4:30"
    
    Args:
        tempo: Tempo biegu w minutach na kilometr (float, str lub format MM:SS)
        
    Returns:
        float: Całkowity czas w sekundach
    """
    if isinstance(tempo, str) and ':' in tempo:
        # Konwersja formatu MM:SS na minuty dziesiętne
        minutes, seconds = tempo.split(':')
        tempo_decimal = float(minutes) + float(seconds) / 60
    else:
        tempo_decimal = float(tempo)
    
    return tempo_decimal * 5 * 60


@st.cache_resource(ttl=3600)  # Cache na 1 godzinę
def load_model_cached(model_path):
    """
    Ładuje model ML z cache'owaniem przez Streamlit.
    
    Args:        model_path: Ścieżka do modelu
        
    Returns:
        Model lub None w przypadku błędu
    """
    try:
        model = load_model(model_path)
        logger.info("Model %s załadowany pomyślnie", model_path)
        return model
    except (FileNotFoundError, ImportError, ValueError) as e:
        logger.error("Błąd ładowania modelu %s: %s", model_path, str(e))
        st.error("❌ Nie udało się załadować modelu. Spróbuj ponownie później.")
        return None


@st.cache_data
def load_reference_data():
    """
    Wczytuje dane referencyjne z pliku CSV. Wynik jest cachowany przez Streamlit.
    
    Returns:
        DataFrame: Dane referencyjne z czasami biegaczy
    """
    try:
        df = pd.read_csv(config.DATA_PATH)
        logger.info("Dane referencyjne załadowane: %d rekordów", len(df))
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
        logger.error("Błąd ładowania danych referencyjnych: %s", str(e))
        st.error("❌ Nie udało się załadować danych referencyjnych.")
        return pd.DataFrame()


def extract_data_with_regex(input_text):
    """
    Fallback function: ekstraktuje dane przy użyciu wyrażeń regularnych.    
    Args:
        input_text: Tekst wprowadzony przez użytkownika
          Returns:
        dict lub None: Wyekstraktowane dane lub None w przypadku błędu
    """
    try:
        # Rozszerzone wyrażenia regularne
        age_match = re.search(r'(\d{1,3})\s*(?:lat|l\b|roku|years?)', input_text.lower())
        gender_match = re.search(r'(?:jestem\s+)?(kobiet[ąaę]|kobieta|mężczyzn[ąaę]|mężczyzna|k\b|m\b|facet|chłop)', input_text.lower())
        
        # Szukanie tempa w różnych formatach
        pace_patterns = [
            r'(\d{1,2}[.,]\d{1,2})\s*(?:min(?:ut)?(?:y|ę)?(?:\s*(?:na|\/|\s+)\s*km)?)',
            r'(\d{1,2}:\d{2})\s*(?:min(?:ut)?(?:y|ę)?(?:\s*(?:na|\/|\s+)\s*km)?)?',
            r'tempo[:\s]*(\d{1,2}[.,]\d{1,2})',
            r'tempo[:\s]*(\d{1,2}:\d{2})',
            r'biegam[^0-9]*(\d{1,2}[.,]\d{1,2})',
            r'(\d{1,2}:\d{2})(?!\d)',  # Format MM:SS bez wymagania słów kluczowych
            r'(\d{1,2}[.,]\d{1,2})(?!\d)'  # Format dziesiętny bez wymagania słów kluczowych
        ]
        
        pace_match = None
        for pattern in pace_patterns:
            pace_match = re.search(pattern, input_text.lower())
            if pace_match:
                break
        
        # Walidacja i konwersja
        if not age_match:
            return None
        age = int(age_match.group(1))
        
        if not gender_match:
            return None
        gender_text = gender_match.group(1).lower()
        # Bardziej rozbudowana logika rozpoznawania płci - sprawdzamy najpierw dłuższe wzorce
        if any(word in gender_text for word in ['kobiet']):
            gender = 'K'
        elif any(word in gender_text for word in ['mężczyzn', 'facet', 'chłop']):
            gender = 'M'
        elif gender_text.strip() == 'k':
            gender = 'K'
        elif gender_text.strip() == 'm':
            gender = 'M'
        else:
            gender = 'M'  # domyślnie
        
        if not pace_match:
            return None
        pace_str = pace_match.group(1).replace(',', '.')
        
        # Konwersja formatu MM:SS na minuty dziesiętne
        if ':' in pace_str:
            minutes, seconds = pace_str.split(':')
            pace = float(minutes) + float(seconds) / 60
        else:
            pace = float(pace_str)
        
        return {
            'Wiek': age,
            'Płeć': gender,
            '5 km Tempo': pace
        }
        
    except (ValueError, AttributeError, TypeError):
        return None


def extract_user_data(input_text):
    """
    Ekstraktuje dane użytkownika z tekstu wprowadzonego w dowolnej formie.
    Wykorzystuje OpenAI GPT-4 do analizy tekstu (jeśli dostępne), z fallbackiem do regex.
    
    Args:
        input_text: Tekst wprowadzony przez użytkownika
        
    Returns:
        dict lub None: Słownik z danymi użytkownika (wiek, płeć, tempo) lub None w przypadku błędu
    """
    # Walidacja wejścia
    if not input_text or not input_text.strip():
        logger.warning("Pusty tekst wejściowy")
        return None
    
    # Sprawdzenie dostępności OpenAI
    if OPENAI_AVAILABLE and client:
        prompt = f"""
        Przeanalizuj poniższy tekst i wyodrębnij następujące informacje niezależnie od ich kolejności:
        1. Wiek osoby (liczba całkowita)
        2. Płeć (zamień na 'M' dla mężczyzny lub 'K' dla kobiety)
        3. Tempo biegu na 5km (liczba z przecinkiem lub kropką, w minutach na kilometr)

        Zwróć dane w formacie JSON z kluczami: 'Wiek', 'Płeć', '5 km Tempo'
        Ignoruj dodatkowe informacje w tekście.
        
        Przykłady różnych formatów wejściowych:
        "Kobieta lat 35, biegam 5.30 min/km" → {{"Wiek": 35, "Płeć": "K", "5 km Tempo": 5.3}}
        "Tempo mam 6,20, jestem facetem i mam 42 lata" → {{"Wiek": 42, "Płeć": "M", "5 km Tempo": 6.2}}
        "Mężczyzna, 28 lat, 4:45/km" → {{"Wiek": 28, "Płeć": "M", "5 km Tempo": 4.75}}
        
        Tekst do przeanalizowania: {input_text}
        """        
        try:
            # Próba użycia OpenAI API
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": "Jesteś asystentem specjalizującym się w analizie danych biegowych. Twoje zadanie to dokładne wyodrębnienie wieku, płci i tempa biegu z tekstu, niezależnie od kolejności i formatu wprowadzania. Zawsze zwracaj poprawny JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=200
            )
            
            response = completion.choices[0].message.content
            if response:
                response = response.strip()
                logger.info("Otrzymana odpowiedź z OpenAI: %s", response)
                
                # Próba parsowania JSON
                try:
                    data = json.loads(response)
                    data_is_valid, data_errors = validate_user_data(data)
                    
                    if data_is_valid:
                        logger.info("Dane wyekstraktowane pomyślnie przez OpenAI")
                        return data
                    else:
                        logger.warning("Dane z OpenAI nieprawidłowe: %s", data_errors)
                        
                except json.JSONDecodeError as e:
                    logger.warning("Błąd parsowania JSON z OpenAI: %s", str(e))
                
        except (ValueError, TypeError, KeyError) as e:
            logger.error("Błąd OpenAI API: %s", str(e))
    
    # Fallback: użycie regex
    logger.info("Próba ekstrakcji danych przy użyciu regex (OpenAI niedostępne: %s)", not OPENAI_AVAILABLE)
    data = extract_data_with_regex(input_text)
    
    if data:
        data_is_valid, data_errors = validate_user_data(data)
        if data_is_valid:
            logger.info("Dane wyekstraktowane pomyślnie przez regex")
            return data
        else:
            logger.warning("Dane z regex nieprawidłowe: %s", data_errors)
    
    logger.error("Nie udało się wyekstraktować danych")
    return None


def make_prediction(prediction_data):
    """
    Wykonuje przewidywanie czasu półmaratonu.
    
    Args:
        prediction_data: Słownik z danymi użytkownika        
    Returns:
        tuple lub None: (czas_w_sekundach, sformatowany_czas) lub None
    """
    try:
        model = load_model_cached(config.MODEL_PATH)
        if model is None:
            return None
        
        # Sprawdzenie dostępności PyCaret
        if not PYCARET_AVAILABLE:
            st.error("❌ PyCaret nie jest zainstalowany. Zainstaluj go komendą: pip install pycaret")
            return None
            
        input_df = pd.DataFrame({
            'Wiek': [prediction_data['Wiek']],
            'Płeć': [prediction_data['Płeć']],
            '5 km Tempo': [float(prediction_data['5 km Tempo'])],
            '5 km Czas': [calculate_5km_time(prediction_data['5 km Tempo'])]
        })
        
        prediction = predict_model(model, data=input_df)
        if prediction is None:
            return None
            
        result_seconds = round(prediction["prediction_label"].iloc[0], 2)
        result_time = str(datetime.timedelta(seconds=int(result_seconds)))
        
        logger.info("Przewidywanie wykonane pomyślnie: %s", result_time)
        return result_seconds, result_time
        
    except (ValueError, KeyError, ImportError) as e:
        logger.error("Błąd podczas przewidywania: %s", str(e))
        st.error(f"❌ Wystąpił błąd podczas generowania przewidywania: {str(e)}")
        return None


def initialize_session_state():
    """Inicjalizuje stan sesji."""
    if 'user_input' not in st.session_state:
        st.session_state['user_input'] = "Np.: Mam 28 lat, jestem kobietą i biegam 5 km w tempie 4.45 min/km"


def display_openai_status():
    """Wyświetla szczegółowy status klucza OpenAI API."""
    if config.OPENAI_API_KEY and config.OPENAI_API_KEY.strip():
        # Sprawdź czy klucz jest prawidłowy
        if OPENAI_AVAILABLE:
            st.success("✅ **Klucz OpenAI prawidłowy**")
            st.info("🤖 **AI włączone** - Aplikacja korzysta z zaawansowanej analizy tekstu")
        else:
            # Klucz istnieje ale nie jest prawidłowy
            st.error("❌ **Klucz OpenAI nieprawidłowy**")
            st.warning("⚠️ **Problem z kluczem API:**")
            st.write("• Sprawdź czy klucz jest poprawny")
            st.write("• Upewnij się, że masz środki na koncie OpenAI")
            st.write("• Sprawdź czy klucz nie wygasł")
    else:
        # Brak klucza w .env
        st.warning("⚠️ **Brak klucza OpenAI**")
        st.info("💡 Bez klucza używany jest podstawowy tryb analizy")


def display_sidebar_content():
    """Wyświetla rozbudowaną zawartość sidebara z szczegółowym statusem OpenAI."""
    # Global jest potrzebne do modyfikacji stanu klienta OpenAI w sidebarze
    global client, OPENAI_AVAILABLE  # pylint: disable=global-statement
    
    with st.sidebar:
        st.markdown("### 🔑 Status OpenAI API")

        # Wyświetl szczegółowy status klucza
        display_openai_status()
        # Sekcja do wprowadzania klucza tymczasowego
        if not OPENAI_AVAILABLE:
            with st.expander("🔧 Wprowadź klucz tymczasowo", expanded=False):
                user_api_key = st.text_input(
                    "Klucz API", 
                    type="password", 
                    placeholder="sk-proj-...",
                    help="Klucz musi zaczynać się od 'sk-'"
                )

                if st.button("✅ Aktywuj", use_container_width=True):
                    if user_api_key:
                        with st.spinner("Aktywuję AI..."):
                            success, message = initialize_openai_client(user_api_key)
                        if success:
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.warning("⚠️ Wprowadź klucz API")

                st.markdown("---")
                st.markdown("**ℹ️ Informacje:**")
                st.write("• Klucz nie jest zapisywany na stałe")
                st.write("• Będzie aktywny tylko w tej sesji")
                st.write("• Aby zapisać na stałe, dodaj do `.env`")

                # Jeśli jest klucz w .env, pokaż opcję testowania
                if config.OPENAI_API_KEY and config.OPENAI_API_KEY.strip():
                    st.markdown("---")
                    st.markdown("**🔑 Klucz z pliku .env:**")
                    if st.button("🧪 Testuj klucz z .env", use_container_width=True):
                        with st.spinner("Testuję klucz z .env..."):
                            success, message = initialize_openai_client()
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
        else:
            # Jeśli AI jest aktywne
            with st.expander("🤖 Zarządzaj AI", expanded=False):
                # Opcja weryfikacji klucza ponownie
                if st.button("🔄 Ponownie sprawdź klucz", use_container_width=True):
                    with st.spinner("Weryfikuję klucz..."):
                        # Sprawdź aktualny klucz
                        current_key = config.OPENAI_API_KEY if client else None
                        if current_key:
                            key_is_valid, status_message = verify_openai_key(current_key)
                            if key_is_valid:
                                st.success(f"✅ {status_message}")
                            else:
                                st.error(f"❌ {status_message}")
                                # Dezaktywuj jeśli klucz nie działa
                                client = None
                                OPENAI_AVAILABLE = False
                                st.rerun()
                        else:
                            st.warning("⚠️ Nie można zweryfikować klucza")

                if st.button("🔴 Wyłącz AI", use_container_width=True):
                    client = None
                    OPENAI_AVAILABLE = False
                    st.info("🔌 OpenAI API zostało wyłączone")
                    st.rerun()

                st.markdown("---")
                st.markdown("**📊 Informacje o AI:**")
                st.write("• Model: GPT-3.5-turbo")
                st.write("• Funkcja: Analiza tekstu naturalnego")
                st.write("• Backup: Analiza regex")

        st.divider()

        # Tylko 2 przykłady
        st.markdown("### 💡 Przykłady")
        examples = [
            "28 lat, kobieta, tempo 4:45",
            "35 lat, mężczyzna, tempo 5:20"
        ]

        for i, example in enumerate(examples, 1):
            if st.button(f"Przykład {i}", key=f"example_{i}", use_container_width=True):
                st.session_state['user_input'] = example
                st.rerun()


# =============================================================================
# INTERFEJS UŻYTKOWNIKA - GŁÓWNY WIDOK
# =============================================================================

# Inicjalizacja
initialize_session_state()
reference_df = load_reference_data()

# Nagłówek z emoji i opisem
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <h1 style='color: #fafafa; font-size: 3em; margin-bottom: 0.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>
        🏃‍♂️ Kalkulator dla biegaczy 🏃‍♀️
    </h1>
    <h2 style='color: #667eea; font-size: 1.5em; margin-bottom: 1rem; font-weight: 300;'>
        Przewidywanie czasu półmaratonu za pomocą sztucznej inteligencji i uczenia maszynowego. 
        Analiza oparta na danych z Maratonu Wrocławskiego 2023-2024
    </h2>
</div>
""", unsafe_allow_html=True)

# Stylowanie - dodatkowe ulepszenia
st.markdown("""
    <style>
    /* Dodatkowe stylowanie dla lepszego wyglądu */
    .metric-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border: 1px solid #4a4a4a;
        box-shadow: 0 4px 15px rgba(30, 60, 114, 0.3);
    }
    
    /* Stylowanie kart z fallback dla wykresów */
    .chart-fallback {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
        color: #e2e8f0;
        box-shadow: 0 4px 15px rgba(45, 55, 72, 0.3);
    }
    
    .chart-fallback h4 {
        color: #667eea !important;
        margin-bottom: 10px;
    }
    
    .chart-fallback p {
        color: #cbd5e0 !important;
        margin: 5px 0;
    }
    
    .chart-fallback em {
        color: #90cdf4 !important;
        font-style: italic;
    }
    
    /* Animacje hover dla kart */
    .metric-container:hover, .chart-fallback:hover {
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    
    /* Lepsze stylowanie dla list */
    ul, ol {
        color: #fafafa !important;
    }
    
    li {
        color: #fafafa !important;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Pole tekstowe
user_input = st.text_area(
    "Przedstaw się i podaj swoje dane (wiek, płeć, tempo na 5km):",
    st.session_state['user_input'],
    key="user_input_area",
    placeholder="Wpisz: Mam 35 lat, jestem kobietą, tempo 5km: 5.10 min/km",
    height=100
)

# Przyciski
col1, col2 = st.columns([1, 1], gap="small")
with col1:
    oblicz = st.button("🚀 Oblicz przewidywany czas", use_container_width=True, type="primary")
with col2:
    wyczysc = st.button("🧹 Wyczyść dane", use_container_width=True)

if wyczysc:
    st.session_state['user_input'] = ""
    st.rerun()

# Logika główna
if oblicz:
    if not user_input or user_input.strip() == "":
        st.warning("⚠️ Proszę wprowadzić dane.")
    else:
        with st.spinner('🤖 Analizuję dane...'):
            user_data = extract_user_data(user_input)
            
        if user_data is None:
            st.error("❌ Nie udało się przetworzyć danych. Upewnij się, że podałeś wszystkie wymagane informacje.")
        else:
            # Walidacja danych
            valid_data, errors_list = validate_user_data(user_data)

            if not valid_data:
                st.warning("⚠️ Problemy z danymi:")
                for error in errors_list:
                    st.write(f"• {error}")
            else:
                with st.spinner('🏃‍♂️ Przewiduję czas...'):
                    result = make_prediction(user_data)
                
                if result:
                    predicted_seconds, predicted_time = result
                    
                    # Wyświetlenie wyniku
                    st.markdown(f"""
                    <div class="success-box">
                        <h3>✅ Przewidywany czas: <strong>{predicted_time}</strong></h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # =============================================================================
                    # SEKCJA ANALIZY PORÓWNAWCZEJ
                    # =============================================================================
                    
                    st.markdown("---")
                    st.markdown("### 📊 Analiza porównawcza")
                    
                    # Porównanie z danymi referencyjnymi
                    if not reference_df.empty:
                        # Filtrowanie danych dla podobnej grupy wiekowej i płci
                        age_range = 5
                        similar_data = reference_df[
                            (reference_df['Wiek'] >= user_data['Wiek'] - age_range) &
                            (reference_df['Wiek'] <= user_data['Wiek'] + age_range) &
                            (reference_df['Płeć'] == user_data['Płeć'])                        ]
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if len(similar_data) > 0:
                                avg_time = similar_data['Czas'].mean()
                                avg_time_formatted = str(datetime.timedelta(seconds=int(avg_time)))
                                delta = predicted_seconds - avg_time
                                delta_formatted = f"{'+' if delta > 0 else ''}{int(delta)} sek"
                                st.metric(
                                    "Średnia dla podobnych", 
                                    avg_time_formatted,
                                    delta_formatted
                                )
                            else:
                                st.metric("Średnia dla podobnych", "Brak danych", "")
                        
                        with col2:
                            percentile = 50
                            if len(reference_df) > 0:
                                percentile = (reference_df['Czas'] < predicted_seconds).mean() * 100
                            st.metric("Percentyl", f"{percentile:.0f}%", "")
                        
                        with col3:
                            if len(similar_data) > 0:
                                better_count = (similar_data['Czas'] > predicted_seconds).sum()
                                total_count = len(similar_data)
                                percentage = (better_count / total_count) * 100 if total_count > 0 else 0
                                st.metric("Lepszy od", f"{percentage:.0f}%", f"z {total_count} osób")
                            else:
                                st.metric("Lepszy od", "Brak danych", "")
                          # Wykres porównawczy
                        st.markdown("#### 📈 Rozkład czasów w Twojej grupie")
                        
                        if PLOTLY_AVAILABLE and len(similar_data) > 0:
                            try:
                                fig = go.Figure()
                                
                                # Histogram czasów podobnych biegaczy
                                fig.add_trace(go.Histogram(
                                    x=similar_data['Czas'] / 60,  # Konwersja na minuty
                                    nbinsx=20,
                                    name='Podobni biegacze',
                                    opacity=0.7,
                                    marker_color='lightblue'
                                ))
                                
                                # Linia dla przewidywanego czasu
                                fig.add_vline(
                                    x=predicted_seconds / 60,
                                    line_dash="dash",
                                    line_color="red",
                                    annotation_text="Twój przewidywany czas",
                                    annotation_position="top"
                                )
                                
                                fig.update_layout(
                                    title=f"Rozkład czasów półmaratonu ({user_data['Płeć']}, {user_data['Wiek']}±{age_range} lat)",
                                    xaxis_title="Czas (minuty)",
                                    yaxis_title="Liczba biegaczy",
                                    template="plotly_dark",
                                    showlegend=False
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                            except (ValueError, TypeError, KeyError, ImportError) as e:
                                logger.error("Błąd tworzenia wykresu: %s", str(e))
                                st.markdown(create_fallback_chart(
                                    "Rozkład czasów w Twojej grupie",
                                    f"Wykres porównujący Twój przewidywany czas z {len(similar_data)} podobnymi biegaczami"
                                ), unsafe_allow_html=True)
                        else:
                            st.markdown(create_fallback_chart(
                                "Rozkład czasów w Twojej grupie",
                                f"Analiza porównawcza z {len(similar_data)} podobnymi biegaczami" if len(similar_data) > 0 else "Brak danych do porównania"
                            ), unsafe_allow_html=True)
                        
                        # Analiza tempa vs czas
                        st.markdown("#### 🎯 Zależność tempo vs czas półmaratonu")
                        
                        if PLOTLY_AVAILABLE and len(reference_df) > 10:
                            try:                                # Scatter plot tempo vs czas półmaratonu
                                fig = px.scatter(
                                    reference_df, 
                                    x='5 km Tempo', 
                                    y='Czas',
                                    color='Płeć',
                                    title="Zależność między tempem na 5km a czasem półmaratonu",
                                    labels={
                                        '5 km Tempo': 'Tempo na 5km (min/km)',
                                        'Czas': 'Czas półmaratonu (sekundy)',
                                        'Płeć': 'Płeć'
                                    },
                                    template="plotly_dark"
                                )
                                
                                # Dodaj punkt użytkownika
                                fig.add_trace(go.Scatter(
                                    x=[user_data['5 km Tempo']],
                                    y=[predicted_seconds],
                                    mode='markers',
                                    marker=dict(size=15, color='red', symbol='star'),
                                    name='Twój wynik',
                                    showlegend=True
                                ))
                                
                                fig.update_layout(
                                    height=500,
                                    showlegend=True
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                            except (ValueError, TypeError, KeyError, ImportError) as e:
                                logger.error("Błąd tworzenia wykresu: %s", str(e))
                                st.markdown(create_fallback_chart(
                                    "Zależność tempo vs czas półmaratonu",
                                    "Wykres przedstawiający korelację między tempem na 5km a czasem półmaratonu"
                                ), unsafe_allow_html=True)
                        else:
                            st.markdown(create_fallback_chart(
                                "Zależność tempo vs czas półmaratonu",
                                "Analiza korelacji między tempem na 5km a czasem półmaratonu"
                            ), unsafe_allow_html=True)
                        
                        # Dodatkowe statystyki
                        st.markdown("#### 📋 Dodatkowe statystyki")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Twoje dane:**")
                            st.write(f"• Wiek: {user_data['Wiek']} lat")
                            st.write(f"• Płeć: {'Kobieta' if user_data['Płeć'] == 'K' else 'Mężczyzna'}")
                            st.write(f"• Tempo 5km: {user_data['5 km Tempo']:.2f} min/km")
                            st.write(f"• Przewidywany czas: {predicted_time}")
                        
                        with col2:
                            if len(similar_data) > 0:
                                st.markdown("**Statystyki grupy porównawczej:**")
                                st.write(f"• Liczba osób: {len(similar_data)}")
                                st.write(f"• Średnie tempo 5km: {similar_data['5 km Tempo'].mean():.2f} min/km")
                                st.write(f"• Średni czas półmaratonu: {str(datetime.timedelta(seconds=int(similar_data['Czas'].mean())))}")
                                best_time = similar_data['Czas'].min()
                                st.write(f"• Najlepszy czas: {str(datetime.timedelta(seconds=int(best_time)))}")
                    
                    st.session_state['last_result_success'] = True
                else:
                    st.session_state['last_result_success'] = False

# Wyświetl sidebar
display_sidebar_content()

# Footer
st.markdown("---")
st.markdown("""
<div class='footer' style='text-align: center; background: linear-gradient(135deg, #262730 0%, #1a1a1a 100%); padding: 1.5rem; border-radius: 12px; margin-top: 2rem; border: 1px solid #4a4a4a;'>
    <p style='color: #cbd5e0; font-size: 1.1em; margin-bottom: 0.5rem;'>🏃‍♂️ <strong>Kalkulator dla biegaczy v2.1</strong></p>
    <p style='color: #90cdf4; margin-bottom: 0.5rem;'>Stworzony przez <a href='https://github.com/AlanSteinbarth' style='color: #667eea; text-decoration: none;'>Alan Steinbarth</a></p>
    <p style='color: #a0aec0; font-size: 0.9em;'>Model wytrenowany na danych z Maratonu Wrocławskiego 2023-2024</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
