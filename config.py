# =============================================================================
# KONFIGURACJA APLIKACJI
# Centralne miejsce zarządzania konfiguracją aplikacji
# =============================================================================

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Klasa konfiguracyjna aplikacji."""
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Ścieżki plików
    MODEL_PATH: str = "huber_model_halfmarathon_time"
    DATA_PATH: str = "df_cleaned.csv"
    
    # Limity walidacji
    MIN_AGE: int = 10
    MAX_AGE: int = 100
    MIN_TEMPO: float = 3.0
    MAX_TEMPO: float = 10.0
    
    # Konfiguracja UI
    PAGE_TITLE: str = "Kalkulator dla biegaczy"
    PAGE_ICON: str = "🏃‍♂️"
    
    # Konfiguracja modelu
    MODEL_CACHE_TTL: int = 3600  # 1 godzina
    
    def validate(self) -> bool:
        """Waliduje konfigurację aplikacji."""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY nie jest ustawiony w zmiennych środowiskowych")
        
        if not os.path.exists(self.DATA_PATH):
            raise FileNotFoundError(f"Plik danych {self.DATA_PATH} nie istnieje")
            
        return True

# Globalna instancja konfiguracji
config = Config()
