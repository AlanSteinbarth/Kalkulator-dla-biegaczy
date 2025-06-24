# =============================================================================
# FUNKCJE WALIDACJI DANYCH
# Moduł zawierający funkcje do walidacji danych wejściowych
# =============================================================================

import re
from typing import Union, Optional
from config import config


def is_valid_age(age: Union[int, str, float, None]) -> bool:
    """
    Sprawdza, czy podany wiek jest prawidłowy.
    
    Args:
        age: Wiek do sprawdzenia (może być liczbą lub stringiem)
        
    Returns:
        bool: True jeśli wiek jest w przedziale MIN_AGE-MAX_AGE
        
    Example:
        >>> is_valid_age(25)
        True
        >>> is_valid_age("abc")
        False
        >>> is_valid_age(5)
        False
    """
    if age is None:
        return False
    try:
        age_int = int(age)
        return config.MIN_AGE <= age_int <= config.MAX_AGE
    except (ValueError, TypeError):
        return False


def is_valid_tempo(tempo: Union[float, str, int, None]) -> bool:
    """
    Sprawdza, czy podane tempo jest prawidłowe.
    
    Args:
        tempo: Tempo do sprawdzenia (min/km)
        
    Returns:
        bool: True jeśli tempo jest w przedziale MIN_TEMPO-MAX_TEMPO
        
    Example:
        >>> is_valid_tempo(4.5)
        True
        >>> is_valid_tempo("abc")
        False
        >>> is_valid_tempo(15.0)
        False
    """
    if tempo is None:
        return False
    try:
        tempo_float = float(tempo)
        return config.MIN_TEMPO <= tempo_float <= config.MAX_TEMPO
    except (ValueError, TypeError):
        return False


def is_valid_gender(gender: Optional[str]) -> bool:
    """
    Sprawdza, czy płeć jest prawidłowa.
    
    Args:
        gender: Płeć do sprawdzenia
        
    Returns:
        bool: True jeśli płeć to 'M' lub 'K'
    """
    if gender is None:
        return False
    return gender in ['M', 'K']


def validate_user_data(data: dict) -> tuple[bool, list[str]]:
    """
    Waliduje kompletny zestaw danych użytkownika.
    
    Args:
        data: Słownik z danymi użytkownika
        
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    errors = []
    
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


def extract_data_with_regex(user_input: str) -> Optional[dict]:
    """
    Fallback function: ekstraktuje dane przy użyciu wyrażeń regularnych.
    
    Args:
        user_input: Tekst wprowadzony przez użytkownika
        
    Returns:
        dict lub None: Wyekstraktowane dane lub None w przypadku błędu
    """
    try:
        # Rozszerzone wyrażenia regularne
        age_match = re.search(r'(\d{1,3})\s*(?:lat|l\b|roku|years?)', user_input.lower())
        gender_match = re.search(r'(?:jestem\s+)?(kobiet[ąaę]|kobieta|mężczyzn[ąaę]|mężczyzna|k\b|m\b|facet|chłop)', user_input.lower())
        
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
            pace_match = re.search(pattern, user_input.lower())
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
