# =============================================================================
# FUNKCJE PRZETWARZANIA DANYCH
# Moduł zawierający funkcje do ekstrakcji i przetwarzania danych użytkownika
# =============================================================================

import datetime
import json
import logging
import os
import sys
from typing import Optional

from openai import OpenAI

# Dodanie głównego katalogu do ścieżki
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.validation import extract_data_with_regex, validate_user_data  # pylint: disable=wrong-import-position

# Konfiguracja loggera
logger = logging.getLogger(__name__)

# Inicjalizacja klienta OpenAI (opcjonalne - jeśli klucz API jest dostępny)
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None
except Exception:  # pylint: disable=broad-except
    client = None


def extract_user_data(user_input: str) -> Optional[dict]:
    """
    Ekstraktuje dane użytkownika z tekstu wprowadzonego w dowolnej formie.
    Wykorzystuje OpenAI GPT-4 do analizy tekstu, z fallbackiem do regex.

    Args:
        user_input: Tekst wprowadzony przez użytkownika

    Returns:
        dict lub None: Słownik z danymi użytkownika (wiek, płeć, tempo) lub None w przypadku błędu

    Example:
        >>> extract_user_data("Mam 28 lat, jestem kobietą, tempo 4:45")
        {'Wiek': 28, 'Płeć': 'K', '5 km Tempo': 4.75}
    """
    # Walidacja wejścia
    if not user_input or not user_input.strip():
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
    "Mężczyzna, 28 lat, 4:45/km" → {{"Wiek": 28, "Płeć": "M", "5 km Tempo": 4.75}}

    Tekst do przeanalizowania: {user_input}
    """

    try:
        # Próba użycia OpenAI API
        if client is not None:
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": ("Jesteś asystentem specjalizującym się w analizie danych "
                                   "biegowych. Twoje zadanie to dokładne wyodrębnienie wieku, "
                                   "płci i tempa biegu z tekstu, niezależnie od kolejności "
                                   "i formatu wprowadzania. Zawsze zwracaj poprawny JSON.")
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=200
            )

            response = completion.choices[0].message.content
        else:
            logger.warning("Brak klienta OpenAI, pomijanie zapytania do API.")
            response = None
        if response:
            response = response.strip()
            logger.info("Otrzymana odpowiedź z OpenAI: %s", response)

            # Próba parsowania JSON
            try:
                data = json.loads(response)
                is_valid, errors = validate_user_data(data)

                if is_valid:
                    logger.info("Dane wyekstraktowane pomyślnie przez OpenAI")
                    return data
                logger.warning("Dane z OpenAI nieprawidłowe: %s", errors)

            except json.JSONDecodeError as e:
                logger.warning("Błąd parsowania JSON z OpenAI: %s", str(e))

    except (ValueError, ConnectionError, ImportError) as e:
        logger.error("Błąd OpenAI API: %s", str(e))

    # Fallback: użycie regex
    logger.info("Próba ekstrakcji danych przy użyciu regex")
    data = extract_data_with_regex(user_input)

    if data:
        is_valid, errors = validate_user_data(data)
        if is_valid:
            logger.info("Dane wyekstraktowane pomyślnie przez regex")
            return data
        logger.warning("Dane z regex nieprawidłowe: %s", errors)

    logger.error("Nie udało się wyekstraktować danych")
    return None


def format_gender_display(gender: str) -> str:
    """
    Konwertuje skrót płci na pełną nazwę do wyświetlenia.

    Args:
        gender: 'M' lub 'K'

    Returns:
        str: 'Mężczyzna' lub 'Kobieta'
    """
    return "Mężczyzna" if gender == "M" else "Kobieta"


def format_time_display(seconds: float) -> str:
    """
    Formatuje czas z sekund na czytelny format.

    Args:
        seconds: Czas w sekundach

    Returns:
        str: Sformatowany czas (np. "1:23:45")
    """
    return str(datetime.timedelta(seconds=int(seconds)))
