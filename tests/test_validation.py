# =============================================================================  
# TESTY JEDNOSTKOWE
# Testy dla funkcji walidacji i przetwarzania danych
# =============================================================================

import pytest
import sys
import os

# Dodanie głównego katalogu do ścieżki
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.validation import is_valid_age, is_valid_tempo, is_valid_gender, validate_user_data
from src.utils.model_utils import calculate_5km_time


class TestValidation:
    """Testy funkcji walidacji."""
    
    def test_is_valid_age(self):
        """Test walidacji wieku."""
        # Prawidłowe wieku
        assert is_valid_age(25)
        assert is_valid_age("30")
        assert is_valid_age(50.0)
        
        # Nieprawidłowe wieku
        assert not is_valid_age(5)
        assert not is_valid_age(105)
        assert not is_valid_age("abc")
        assert not is_valid_age(None)
        assert not is_valid_age(-10)
    
    def test_is_valid_tempo(self):
        """Test walidacji tempa."""
        # Prawidłowe tempa
        assert is_valid_tempo(4.5)
        assert is_valid_tempo("5.0")
        assert is_valid_tempo(8)
        
        # Nieprawidłowe tempa
        assert not is_valid_tempo(2.0)
        assert not is_valid_tempo(15.0)
        assert not is_valid_tempo("abc")
        assert not is_valid_tempo(None)
    
    def test_is_valid_gender(self):
        """Test walidacji płci."""
        assert is_valid_gender("M")
        assert is_valid_gender("K")
        assert not is_valid_gender("X")
        assert not is_valid_gender("")
        assert not is_valid_gender(None)
    
    def test_validate_user_data(self):
        """Test kompletnej walidacji danych użytkownika."""
        # Prawidłowe dane
        valid_data = {
            'Wiek': 25,
            'Płeć': 'M',
            '5 km Tempo': 4.5
        }
        is_valid, errors = validate_user_data(valid_data)
        assert is_valid
        assert len(errors) == 0
        
        # Brakujące pola
        incomplete_data = {
            'Wiek': 25,
            'Płeć': 'M'
        }
        is_valid, errors = validate_user_data(incomplete_data)
        assert not is_valid
        assert len(errors) > 0
        
        # Nieprawidłowe dane
        invalid_data = {
            'Wiek': 5,  # za młody
            'Płeć': 'X',  # nieprawidłowa płeć
            '5 km Tempo': 15.0  # za wolno
        }
        is_valid, errors = validate_user_data(invalid_data)
        assert not is_valid
        assert len(errors) == 3


class TestModelUtils:
    """Testy funkcji modelowych."""
    
    def test_calculate_5km_time(self):
        """Test obliczania czasu 5km."""
        # 5 min/km * 5km * 60s/min = 1500s
        assert calculate_5km_time(5.0) == 1500.0
        
        # 4.5 min/km * 5km * 60s/min = 1350s  
        assert calculate_5km_time(4.5) == 1350.0
        
        # Test z stringiem
        assert calculate_5km_time("6.0") == 1800.0


# Uruchomienie testów
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
