# 🏃‍♂️ Kalkulator dla biegaczy v2.1

[![Tests](https://github.com/AlanSteinbarth/Kalkulator-dla-biegaczy/actions/workflows/tests.yml/badge.svg)](https://github.com/AlanSteinbarth/Kalkulator-dla-biegaczy/actions/workflows/tests.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?logo=openai&logoColor=white)](https://openai.com)

> **Profesjonalna aplikacja webowa** do przewidywania czasu ukończenia półmaratonu przy użyciu **uczenia maszynowego** i **sztucznej inteligencji**.

---
## 📑 Spis treści
1. [Cel projektu](#-cel-projektu)
2. [Kluczowe funkcjonalności](#-kluczowe-funkcjonalności)
3. [Demo na żywo](#-demo-na-żywo)
4. [Dane i model](#-dane-i-model)
5. [Instalacja i uruchomienie](#-instalacja-i-uruchomienie)
6. [Obsługa klucza OpenAI](#obsługa-klucza-openai)
7. [Changelog](#-changelog)
8. [Licencja](#licencja)

---

## 🎯 Cel projektu

Projekt został stworzony jako **showcase umiejętności** w obszarze:
- **Machine Learning** (PyCaret, Scikit-learn)
- **AI Integration** (OpenAI GPT-4) 
- **Data Visualization** (Plotly)
- **Web Development** (Streamlit)
- **Software Engineering** (testy, CI/CD, clean code)

## ✨ Kluczowe funkcjonalności

### 🤖 Inteligentna analiza danych
- Automatyczne rozpoznawanie danych przez **GPT-4**
- Fallback na **regex** w przypadku problemów z API
- Obsługa różnych formatów wejściowych

### 📊 Zaawansowane wizualizacje
- Interaktywne wykresy porównawcze (Plotly)
- Analiza na tle grup demograficznych
- Responsywny design

### 🔧 Profesjonalne narzędzia
- **Testy jednostkowe** (pytest)
- **CI/CD** (GitHub Actions)
- **Code quality** (Black, flake8)
- **Type hints** i dokumentacja

## 🚀 Demo na żywo

**[👉 Wypróbuj aplikację na Streamlit Cloud](https://twoj-link-do-aplikacji.streamlit.app)**

## 📊 Dane i model

### Zbiór danych
- **Źródło**: Maraton Wrocławski 2023-2024
- **Rozmiar**: 1,247 rekordów
- **Cechy**: wiek, płeć, tempo 5km, czas półmaratonu

### Model ML
- **Algorytm**: Huber Regression (odporny na outliers)
- **R² Score**: 0.85
- **MAE**: 12.3 minuty
- **Framework**: PyCaret

## �️ Instalacja i uruchomienie

### Wymagania
- Python 3.9+
- Klucz API OpenAI

### Szybki start
```bash
# 1. Sklonuj repozytorium
git clone https://github.com/AlanSteinbarth/Kalkulator-dla-biegaczy.git
cd Kalkulator-dla-biegaczy

# 2. Zainstaluj zależności
pip install -r requirements.txt

# 3. Skonfiguruj zmienne środowiskowe
echo "OPENAI_API_KEY=your_api_key_here" > .env

# 4. Uruchom aplikację
streamlit run app.py
```

### Rozwój (development)
```bash
# Zainstaluj zależności deweloperskie
pip install -r requirements.txt
pip install -e ".[dev]"

# Skonfiguruj pre-commit
pre-commit install

# Uruchom testy
pytest

# Sprawdź jakość kodu
black .
flake8 .
```
   streamlit run app.py
   ```

## 📁 Struktura projektu

```
kalkulator-dla-biegaczy/
├── 📱 app.py                    # Główna aplikacja Streamlit
├── ⚙️ config.py                 # Konfiguracja aplikacji  
├── 📊 df_cleaned.csv            # Dane treningowe
├── 🤖 huber_model_*.pkl         # Wytrenowany model ML
├── 📋 requirements.txt          # Zależności Python
├── 🔧 pyproject.toml           # Konfiguracja projektu
├── 📚 README.md                # Dokumentacja
├── 📄 CHANGELOG.md             # Historia zmian
├── src/utils/                   # Moduły pomocnicze
│   ├── validation.py           # Walidacja danych
│   ├── model_utils.py          # Funkcje ML
│   ├── data_processing.py      # Przetwarzanie danych
│   └── visualization.py        # Wizualizacje
├── tests/                      # Testy jednostkowe
│   └── test_validation.py
├── .github/workflows/          # CI/CD GitHub Actions
│   └── tests.yml
└── dane/                       # Surowe dane
    ├── halfmarathon_2023.csv
    └── halfmarathon_2024.csv
```

## 🧪 Testy i jakość kodu

### Uruchamianie testów
```bash
# Wszystkie testy
pytest

# Z pokryciem kodu
pytest --cov=src

# Tylko konkretny plik
pytest tests/test_validation.py -v
```

### Sprawdzenie jakości
```bash
# Formatowanie kodu
black . --check

# Linting
flake8 .

# Type checking
mypy src/
```

## 🚀 Deployment na Streamlit Cloud

### Automatyczny deployment
1. **Fork** tego repozytorium
2. Połącz z **[Streamlit Cloud](https://share.streamlit.io)**
3. Dodaj **secrets** w ustawieniach:
   ```toml
   OPENAI_API_KEY = "your_api_key_here"
   ```
4. Deploy automatycznie się uruchomi! 🎉

### Konfiguracja production
```toml
# .streamlit/config.toml
[server]
headless = true
port = $PORT

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
```

## 📈 Roadmap i przyszłe funkcjonalności

- [ ] **Więcej dystansów**: 10km, maraton
- [ ] **Analiza pogody**: wpływ warunków atmosferycznych  
- [ ] **Historia treningów**: tracking postępów
- [ ] **API REST**: integracja z innymi aplikacjami
- [ ] **Mobile app**: wersja mobilna
- [ ] **Social features**: porównywanie z przyjaciółmi

## 🤝 Wkład w projekt (Contributing)

Zachęcam do współpracy! 

### Jak zacząć:
1. **Fork** repozytorium
2. Utwórz **feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit** zmiany: `git commit -m 'Add amazing feature'`
4. **Push** do brancha: `git push origin feature/amazing-feature`
5. Otwórz **Pull Request**

### Zasady:
- ✅ Wszystkie testy muszą przechodzić
- ✅ Kod musi być sformatowany (Black)
- ✅ Dodaj testy dla nowych funkcjonalności
- ✅ Aktualizuj dokumentację

## 📊 Metryki projektu

![GitHub stars](https://img.shields.io/github/stars/AlanSteinbarth/Kalkulator-dla-biegaczy?style=social)
![GitHub forks](https://img.shields.io/github/forks/AlanSteinbarth/Kalkulator-dla-biegaczy?style=social)
![GitHub issues](https://img.shields.io/github/issues/AlanSteinbarth/Kalkulator-dla-biegaczy)
![GitHub last commit](https://img.shields.io/github/last-commit/AlanSteinbarth/Kalkulator-dla-biegaczy)

## 👨‍💻 Autor

**Alan Steinbarth**
- 🐙 GitHub: [@AlanSteinbarth](https://github.com/AlanSteinbarth)
- 📧 Email: alan.steinbarth@gmail.com
- 💼 LinkedIn: [Alan Steinbarth](https://linkedin.com/in/alan-steinbarth)

## 📄 Licencja

Ten projekt jest licencjonowany na licencji MIT - szczegóły w pliku [LICENSE](LICENSE).

## 🙋‍♂️ FAQ

**Q: Czy aplikacja działa offline?**  
A: Nie, wymaga połączenia z internetem do OpenAI API.

**Q: Jakie są koszty korzystania?**  
A: Aplikacja jest darmowa, ale wymaga klucza API OpenAI (~$0.01 za zapytanie).

**Q: Czy mogę dodać swoje dane treningowe?**  
A: Tak! Sprawdź sekcję Contributing powyżej.

**Q: Na ile dokładny jest model?**  
A: Model ma R² = 0.85, średni błąd to ~12 minut.

---

<div align="center">

**⭐ Jeśli projekt Ci się podoba, zostaw gwiazdkę! ⭐**

*Stworzony z ❤️ dla społeczności biegaczy*

</div>

## 🔑 Obsługa klucza OpenAI API

### Status klucza w aplikacji
Aplikacja wyświetla szczegółowe informacje o statusie klucza OpenAI w sidebarze:

- ✅ **Klucz prawidłowy** - AI jest aktywne, zaawansowana analiza tekstu włączona
- ❌ **Klucz nieprawidłowy** - Problemy z weryfikacją klucza
- ⚠️ **Brak klucza** - Używany jest prostszy tryb analizy (regex)

### Konfiguracja klucza

#### Opcja 1: Plik .env (zalecana)
```bash
# Utwórz plik .env w głównym katalogu
echo "OPENAI_API_KEY=sk-proj-twoj_klucz_tutaj" > .env
```

#### Opcja 2: Tymczasowo w aplikacji
1. Uruchom aplikację bez klucza w .env
2. W sidebarze kliknij **"🔧 Wprowadź klucz tymczasowo"**
3. Wpisz klucz i kliknij **"✅ Aktywuj"**
4. Klucz będzie aktywny tylko w bieżącej sesji

### Komunikaty dla użytkownika
- **🔍 Sprawdź** - weryfikuje poprawność klucza bez aktywacji
- **🧪 Testuj klucz z .env** - testuje klucz z pliku konfiguracyjnego
- **🔄 Ponownie sprawdź klucz** - weryfikuje aktywny klucz
- **🔴 Wyłącz AI** - dezaktywuje tryb AI

### Rozwiązywanie problemów
- **Nieprawidłowy format**: Klucz musi zaczynać się od 'sk-'
- **Klucz wygasł**: Sprawdź na [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Problemy z rozliczeniami**: Sprawdź [platform.openai.com/usage](https://platform.openai.com/usage)
- **Bez klucza**: Aplikacja działa w trybie podstawowym (analiza regex)
