# 📋 Changelog

Wszystkie ważne zmiany w tym projekcie będą dokumentowane w tym pliku.

Format bazuje na [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
a projekt używa [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-06-24

### 📝 Dokumentacja i finalizacja
- Dodano spis treści do pliku `app.py` i `README.md`
- Uzupełniono docstringi i sekcje w kodzie
- Zwiększono numer wersji aplikacji do 2.1
- Uporządkowano sekcje dokumentacyjne
- Finalizacja projektu i przygotowanie do prezentacji

## [2.0.0] - 2025-06-22

### ✨ Dodane
- **Modularna architektura**: Przepisano kod na modułową strukturę z `src/utils/`
- **Testy jednostkowe**: Dodano kompleksowe testy z pytest
- **CI/CD**: GitHub Actions z automatycznymi testami
- **Quality tools**: Black, flake8, mypy, pre-commit hooks
- **Lepsze UI**: Przeprojektowano interfejs użytkownika
- **Advanced logging**: Dodano profesjonalne logowanie
- **Caching**: Optymalizacja wydajności z `@st.cache_resource`
- **Error handling**: Robustna obsługa błędów
- **Configuration**: Centralna konfiguracja w `config.py`
- **Type hints**: Dodano type annotations
- **Dokumentacja**: Znacznie rozszerzone README.md

### 🔧 Zmienione
- **Walidacja danych**: Przepisano funkcje walidacji
- **OpenAI integration**: Lepsza obsługa API z fallbackiem
- **Visualizations**: Ulepszone wykresy Plotly
- **Session state**: Lepsie zarządzanie stanem aplikacji
- **Requirements**: Aktualizacja zależności do najnowszych wersji

### 🐛 Naprawione
- Błędy parsowania danych wejściowych
- Problemy z cache'owaniem modelu
- Responsywność na urządzeniach mobilnych
- Obsługa edge cases w regex

## [1.1.0] - 2025-05-24

### Zmieniono
- Zaktualizowano model z GPT-3.5 na GPT-4
- Poprawiono błędy w walidacji danych
- Ulepszono obsługę błędów w aplikacji
- Dodano informację o statusie przetwarzania w interfejsie

### Naprawiono
- Błędy w formatowaniu kodu
- Problem z wyświetlaniem przykładu po obliczeniu wyniku
- Poprawiono obsługę nieprawidłowych danych wejściowych

### Techniczne
- Refaktoryzacja kodu i dodanie sekcji komentarzy
- Aktualizacja dokumentacji
- Optymalizacja przetwarzania danych

## [1.0.0] - 2025-05-22

### Dodano
- Pierwsza publiczna wersja
- Przewidywanie czasu półmaratonu na podstawie wieku, płci i tempa na 5km
- Interaktywne wykresy z rozkładem czasów
- Inteligentna analiza tekstu przez GPT
- Walidacja danych wejściowych
- Interfejs użytkownika w Streamlit
- Dokumentacja w języku polskim

Autor: Alan Steinbarth (alan.steinbarth@gmail.com)
GitHub: https://github.com/AlanSteinbarth
