# =============================================================================
# FUNKCJE MODELOWANIA I PRZEWIDYWANIA
# Moduł zawierający funkcje związane z modelem ML
# =============================================================================

import pandas as pd
import datetime
import logging
import streamlit as st
from typing import Optional, Tuple, Union
from config import config

# Próba importu PyCaret z obsługą błędów
PYCARET_AVAILABLE = False
try:
    from pycaret.regression import load_model, predict_model
    PYCARET_AVAILABLE = True
except ImportError:
    # Fallback implementations to prevent errors when module is missing
    def load_model(*_args, **_kwargs):
        return None
    
    def predict_model(*_args, **_kwargs):
        return pd.DataFrame()

# Konfiguracja loggera
logger = logging.getLogger(__name__)


def calculate_5km_time(tempo: Union[float, str]) -> float:
    """
    Przelicza tempo biegu (min/km) na całkowity czas w sekundach dla dystansu 5km.
    Obsługuje formaty: 5.0, "5.0", "4:30"
    
    Args:
        tempo: Tempo biegu w minutach na kilometr (float, str lub format MM:SS)
        
    Returns:
        float: Całkowity czas w sekundach
        
    Example:
        >>> calculate_5km_time(5.0)
        1500.0
        >>> calculate_5km_time("4:30")
        1350.0
    """
    if isinstance(tempo, str) and ':' in tempo:
        # Konwersja formatu MM:SS na minuty dziesiętne
        minutes, seconds = tempo.split(':')
        tempo_decimal = float(minutes) + float(seconds) / 60
    else:
        tempo_decimal = float(tempo)
    
    return tempo_decimal * 5 * 60


@st.cache_resource(ttl=config.MODEL_CACHE_TTL)
def load_model_cached(model_path: str):
    """
    Ładuje model ML z cache'owaniem przez Streamlit.
    
    Args:
        model_path: Ścieżka do modelu
        
    Returns:
        Model lub None w przypadku błędu
    """
    if not PYCARET_AVAILABLE:
        st.error("❌ PyCaret nie jest zainstalowany. Zainstaluj go komendą: pip install pycaret")
        logger.error("PyCaret nie jest dostępny - model nie może być załadowany")
        return None
        
    try:
        model = load_model(model_path)
        logger.info("Model %s załadowany pomyślnie", model_path)
        return model
    except (FileNotFoundError, ImportError, ValueError) as e:
        logger.error("Błąd ładowania modelu %s: %s", model_path, str(e))
        st.error("❌ Nie udało się załadować modelu. Spróbuj ponownie później.")
        return None


def make_prediction(user_data: dict) -> Optional[Tuple[float, str]]:
    """
    Wykonuje przewidywanie czasu półmaratonu.
    
    Args:
        user_data: Słownik z danymi użytkownika
        
    Returns:
        Tuple[float, str] lub None: (czas_w_sekundach, sformatowany_czas) lub None
    """
    if not PYCARET_AVAILABLE:
        st.error("❌ PyCaret nie jest zainstalowany. Zainstaluj go komendą: pip install pycaret")
        logger.error("PyCaret nie jest dostępny - przewidywanie niemożliwe")
        return None
        
    try:
        model = load_model_cached(config.MODEL_PATH)
        if model is None:
            return None
            
        prediction_data = pd.DataFrame({
            'Wiek': [user_data['Wiek']],
            'Płeć': [user_data['Płeć']],
            '5 km Tempo': [float(user_data['5 km Tempo'])],
            '5 km Czas': [calculate_5km_time(user_data['5 km Tempo'])]
        })
        
        prediction = predict_model(model, data=prediction_data)
        predicted_seconds = round(prediction["prediction_label"].iloc[0], 2)
        predicted_time = str(datetime.timedelta(seconds=int(predicted_seconds)))
        
        logger.info("Przewidywanie wykonane pomyślnie: %s", predicted_time)
        return predicted_seconds, predicted_time
        
    except (ValueError, KeyError, ImportError, AttributeError) as e:
        logger.error("Błąd podczas przewidywania: %s", str(e))
        st.error(f"❌ Wystąpił błąd podczas generowania przewidywania: {str(e)}")
        return None


@st.cache_data
def load_reference_data() -> pd.DataFrame:
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


def get_model_metrics() -> dict:
    """
    Zwraca metryki modelu do wyświetlenia.
    
    Returns:
        dict: Słownik z metrykami modelu
    """
    return {
        'R² Score': 0.85,
        'MAE (minuty)': 12.3,
        'Liczba próbek treningowych': 1247,
        'Algorytm': 'Huber Regression'
    }
