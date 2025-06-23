# =============================================================================
# KALKULATOR CZASU PÓŁMARATONU - WERSJA 2.0
# Aplikacja do przewidywania czasu ukończenia półmaratonu na podstawie wieku,
# płci i tempa na 5km, wykorzystująca model uczenia maszynowego.
# 
# Autor: Alan Steinbarth
# Email: alan.steinbarth@gmail.com
# GitHub: https://github.com/AlanSteinbarth/Kalkulator-dla-biegaczy
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
    from pycaret.regression import load_model, predict_model
    PYCARET_AVAILABLE = True
except ImportError:
    PYCARET_AVAILABLE = False
    
# Sprawdzenie dostępności opcjonalnych pakietów
PLOTLY_AVAILABLE = False
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:    # Zaślepka dla px i figur plotly
    class PlotlyFigure:
        def add_vline(self, *_args, **_kwargs):
            return self
        
        def update_layout(self, *_args, **_kwargs):
            return self
            
    class PlotlyExpress:
        def __getattr__(self, _name):
            def method(*_args, **_kwargs):
                return PlotlyFigure()
            return method
    px = PlotlyExpress()

# Konfiguracja strony
st.set_page_config(
    page_title="🏃‍♂️ Kalkulator dla biegaczy", 
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
try:
    client = OpenAI(api_key=config.OPENAI_API_KEY)
except (ValueError, KeyError, ImportError) as e:
    logger.error("Błąd inicjalizacji OpenAI: %s", str(e))
    st.error("❌ Błąd konfiguracji OpenAI API. Sprawdź zmienne środowiskowe.")

# =============================================================================
# FUNKCJE POMOCNICZE
# =============================================================================

def create_fallback_chart(title, message):
    """Tworzy prostą alternatywę dla wykresów plotly."""
    return f"""
    <div style='border: 2px dashed #ccc; padding: 20px; text-align: center; margin: 10px 0;'>
        <h4>{title}</h4>
        <p>{message}</p>
        <p><em>💡 Zainstaluj plotly aby zobaczyć wykresy: pip install plotly</em></p>
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
    
    Args:
        tempo (float): Tempo biegu w minutach na kilometr
        
    Returns:
        float: Całkowity czas w sekundach
    """
    return float(tempo) * 5 * 60


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
        gender_match = re.search(r'(?:jestem\s+)?(kobieta|mężczyzna|k\b|m\b|facet|chłop)', input_text.lower())
        
        # Szukanie tempa w różnych formatach
        pace_patterns = [
            r'(\d{1,2}[.,]\d{1,2})\s*(?:min(?:ut)?(?:y|ę)?(?:\s*(?:na|\/|\s+)\s*km)?)',
            r'(\d{1,2}:\d{2})\s*(?:min(?:ut)?(?:y|ę)?(?:\s*(?:na|\/|\s+)\s*km)?)',
            r'tempo[:\s]*(\d{1,2}[.,]\d{1,2})',
            r'biegam[^0-9]*(\d{1,2}[.,]\d{1,2})'
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
        gender = 'K' if gender_text in ['kobieta', 'k'] else 'M'
        
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
    Wykorzystuje OpenAI GPT-4 do analizy tekstu, z fallbackiem do regex.
    
    Args:
        input_text: Tekst wprowadzony przez użytkownika
        
    Returns:
        dict lub None: Słownik z danymi użytkownika (wiek, płeć, tempo) lub None w przypadku błędu
    """    # Walidacja wejścia
    if not input_text or not input_text.strip():
        logger.warning("Pusty tekst wejściowy")
        return None
    
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
    "Mężczyzna, 28 lat, 4:45/km" → {{"Wiek": 28, "Płeć": "M", "5 km Tempo": 4.75}}    Tekst do przeanalizowania: {input_text}    """
    
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
            logger.info("Otrzymana odpowiedź z OpenAI: %s", response)            # Próba parsowania JSON
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
            
    except (ValueError, ConnectionError, ImportError) as e:
        logger.error("Błąd OpenAI API: %s", str(e))
      # Fallback: użycie regex
    logger.info("Próba ekstrakcji danych przy użyciu regex")
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
    
    if 'usage_stats' not in st.session_state:
        import time
        st.session_state['usage_stats'] = {
            'predictions_made': 0,
            'start_time': time.time()
        }


def display_sidebar_content():
    """Wyświetla zawartość sidebara."""
    with st.sidebar:
        # Metryki modelu
        st.markdown("### 📈 Metryki modelu")
        metrics = {
            'R² Score': 0.85,
            'MAE (minuty)': 12.3,
            'Próbek treningowych': 1247,
            'Algorytm': 'Huber Regression'
        }
        
        for metric, value in metrics.items():
            if isinstance(value, float):
                st.metric(metric, f"{value:.2f}")
            else:
                st.metric(metric, value)
        
        st.divider()
        
        # Przykłady
        st.markdown("### 💡 Przykłady danych")
        examples = [
            "Mam 28 lat, jestem kobietą, tempo 5km: 4:45",
            "35 lat, mężczyzna, biegam 5km w 5:20", 
            "Kobieta, 42 lata, mój czas na 5km to 6:10",
            "Facet, 30 lat, 5 kilometrów w 4.5 minuty na km"
        ]
        
        for i, example in enumerate(examples, 1):
            if st.button(f"Przykład {i}", key=f"example_{i}", use_container_width=True):
                st.session_state['user_input'] = example
                st.rerun()
        
        st.divider()
        
        # Statystyki sesji
        st.markdown("### 📊 Statystyki sesji")
        predictions_count = st.session_state['usage_stats']['predictions_made']
        import time
        session_duration = time.time() - st.session_state['usage_stats']['start_time']
        
        st.metric("Przewidywania wykonane", predictions_count)
        st.metric("Czas sesji", f"{session_duration/60:.1f} min")
        
        # FAQ
        with st.expander("ℹ️ Jak to działa? (FAQ)", expanded=False):
            st.markdown("""        
            **Jak działa kalkulator?**  
            Twój czas półmaratonu jest szacowany na podstawie wieku, płci i tempa na 5 km. Model został wytrenowany na rzeczywistych wynikach biegaczy z Maratonu Wrocławskiego z lat 2023-2024.  
            Wykorzystujemy model uczenia maszynowego (PyCaret, regresja Huber), a dane wejściowe są automatycznie rozpoznawane przez AI (OpenAI GPT-4).

            **Jak interpretować wykresy?**  
            Na wykresach możesz zobaczyć, jak Twój przewidywany czas wypada na tle innych osób tej samej płci i wieku. Czerwona linia to Twój wynik, zielona linia to średnia w danej grupie.
            
            **Jakie są ograniczenia?**
            - Wiek: {config.MIN_AGE}-{config.MAX_AGE} lat
            - Tempo: {config.MIN_TEMPO}-{config.MAX_TEMPO} min/km
            - Model działa najlepiej dla biegaczy amatorów
            """)


# =============================================================================
# INTERFEJS UŻYTKOWNIKA - GŁÓWNY WIDOK
# =============================================================================

# Inicjalizacja
initialize_session_state()
reference_df = load_reference_data()

st.title("🏃‍♂️ Kalkulator dla biegaczy 🥇")
st.markdown("""
**Wersja 2.0** - Wprowadź swoje dane, a aplikacja oszacuje Twój czas ukończenia półmaratonu 
na podstawie wytrenowanego modelu uczenia maszynowego.
""")

# Stylowanie
st.markdown("""
    <style>
    div.stButton > button {
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(44, 62, 80, 0.15);
        margin-bottom: 0px !important;
        margin-top: 0px !important;
        font-weight: 600;
        font-size: 1.1em;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
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
        else:            # Walidacja danych
            is_valid, errors_list = validate_user_data(user_data)
            
            if not is_valid:
                st.warning("⚠️ Problemy z danymi:")
                for error in errors_list:
                    st.write(f"• {error}")
            else:
                with st.spinner('🏃‍♂️ Przewiduję czas...'):
                    result = make_prediction(user_data)
                
                if result:
                    predicted_seconds, predicted_time = result
                    
                    # Zwiększ licznik przewidywań
                    st.session_state['usage_stats']['predictions_made'] += 1
                    
                    # Wyświetl wynik
                    st.markdown(f"""
                    <div class="success-box">
                        <h3>✅ Przewidywany czas ukończenia półmaratonu: <strong>{predicted_time}</strong></h3>
                        <p>Wynik obliczony na podstawie: {user_data['Wiek']} lat, płeć: {'Kobieta' if user_data['Płeć'] == 'K' else 'Mężczyzna'}, tempo 5km: {user_data['5 km Tempo']} min/km</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Wykresy porównawcze
                    st.markdown("---")
                    st.markdown("## 📊 Analiza porównawcza")
                    
                    user_gender = user_data['Płeć']
                    user_age = int(user_data['Wiek'])
                    predicted_minutes = predicted_seconds / 60
                    
                    # Wykres dla płci
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        df_gender = reference_df[reference_df['Płeć'] == user_gender].copy()
                        if len(df_gender) > 0:
                            df_gender['Czas_minuty'] = df_gender['Czas'] / 60
                            avg_gender_minutes = df_gender['Czas'].mean() / 60                            
                            gender_display = "Mężczyzn" if user_gender == "M" else "Kobiet"
                            
                            # Sprawdzenie dostępności Plotly
                            if PLOTLY_AVAILABLE:
                                fig1 = px.histogram(
                                    df_gender, 
                                    x='Czas_minuty', 
                                    nbins=30,
                                    title=f"Rozkład czasów dla {gender_display.lower()}",
                                    labels={"Czas_minuty": "Czas (minuty)", "count": "Liczba"},
                                    color_discrete_sequence=['#636EFA']
                                )
                                fig1.add_vline(x=predicted_minutes, line_dash="dash", line_color="red",
                                    annotation_text="Twój wynik", annotation_position="top right")
                                fig1.add_vline(x=avg_gender_minutes, line_dash="dot", line_color="green",
                                    annotation_text="Średnia", annotation_position="bottom right")
                                
                                fig1.update_layout(showlegend=False, height=400)
                                st.plotly_chart(fig1, use_container_width=True)
                            else:
                                # Fallback gdy plotly nie jest dostępny
                                chart_html = create_fallback_chart(
                                    f"Rozkład czasów dla {gender_display.lower()}",
                                    f"Twój przewidywany czas: {predicted_minutes:.1f} min<br>Średnia grupy: {avg_gender_minutes:.1f} min"
                                )
                                st.markdown(chart_html, unsafe_allow_html=True)
                            
                            st.metric("Porównanie z grupą", f"{len(df_gender)} osób")
                    
                    with col2:
                        df_age = reference_df[reference_df['Wiek'].between(user_age-2, user_age+2)].copy()
                        if len(df_age) > 0:
                            df_age['Czas_minuty'] = df_age['Czas'] / 60
                            avg_age_minutes = df_age['Czas'].mean() / 60
                            
                            # Sprawdzenie dostępności Plotly
                            if PLOTLY_AVAILABLE:
                                fig2 = px.histogram(
                                    df_age, 
                                    x='Czas_minuty', 
                                    nbins=30,
                                    title=f"Rozkład czasów dla wieku {user_age}±2 lat",
                                    labels={"Czas_minuty": "Czas (minuty)", "count": "Liczba"},
                                    color_discrete_sequence=['#00CC96']
                                )
                                
                                fig2.add_vline(x=predicted_minutes, line_dash="dash", line_color="red",
                                    annotation_text="Twój wynik", annotation_position="top right")
                                fig2.add_vline(x=avg_age_minutes, line_dash="dot", line_color="green",
                                    annotation_text="Średnia", annotation_position="bottom right")
                                
                                fig2.update_layout(showlegend=False, height=400)
                                st.plotly_chart(fig2, use_container_width=True)
                            else:
                                # Fallback gdy plotly nie jest dostępny
                                chart_html = create_fallback_chart(
                                    f"Rozkład czasów dla wieku {user_age}±2 lat",
                                    f"Twój przewidywany czas: {predicted_minutes:.1f} min<br>Średnia grupy: {avg_age_minutes:.1f} min"
                                )
                                st.markdown(chart_html, unsafe_allow_html=True)
                            
                            st.metric("Porównanie z grupą wiekową", f"{len(df_age)} osób")
                    
                    st.session_state['last_result_success'] = True
                else:
                    st.session_state['last_result_success'] = False

# Wyświetl sidebar
display_sidebar_content()

# Info tylko jeśli nie ma wyniku
if not oblicz or not st.session_state.get('last_result_success', False):
    st.info("💡 **Wskazówka:** Możesz pisać w dowolnym stylu - AI rozpozna Twoje dane automatycznie!")
    st.info("📝 **Przykład:** 'Mam 28 lat, jestem kobietą i biegam 5 km w tempie 4.45 min/km'")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🏃‍♂️ Kalkulator dla biegaczy v2.0 | Stworzony przez <a href='https://github.com/AlanSteinbarth'>Alan Steinbarth</a></p>
    <p>Model wytrenowany na danych z Maratonu Wrocławskiego 2023-2024</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# FALLBACK FUNKCJE DLA BRAKUJĄCYCH PAKIETÓW
# =============================================================================

def fallback_load_model(_model_path):  # noqa: ARG001
    """Fallback funkcja gdy PyCaret nie jest dostępny."""
    st.error("❌ PyCaret nie jest zainstalowany. Zainstaluj go komendą: pip install pycaret")
    logger.error("PyCaret nie jest dostępny - model nie może być załadowany")
    return None

def fallback_predict_model(_model, data=None, **_kwargs):  # noqa: ARG001
    """Fallback funkcja gdy PyCaret nie jest dostępny."""
    st.error("❌ PyCaret nie jest zainstalowany. Nie można wykonać przewidywania.")
    logger.error("PyCaret nie jest dostępny - przewidywanie niemożliwe")
    return None

# Ustawienie funkcji w zależności od dostępności pakietów
if not PYCARET_AVAILABLE:
    load_model = fallback_load_model
    predict_model = fallback_predict_model

# =============================================================================
