# 🏃‍♂️ Kalkulator dla biegaczy

Aplikacja webowa do szacowania przewidywanego czasu ukończenia półmaratonu na podstawie wieku, płci i tempa na 5km.

## 📋 Opis

Aplikacja wykorzystuje:
- Model uczenia maszynowego (regresja Huber, PyCaret)
- Rzeczywiste dane biegaczy z Maratonu Wrocławskiego (2023-2024)
- GPT-4 do inteligentnej analizy danych wejściowych
- Interaktywne wykresy do wizualizacji wyników

## ✨ Funkcjonalności

1. **Wprowadzanie danych** – w dowolnej formie tekstowej
   ```
   Np.: "Mam 35 lat, jestem kobietą, tempo 5km: 5.10 min/km"
   ```

2. **Inteligentna analiza** – automatyczne rozpoznawanie danych przez GPT-4

3. **Walidacja danych**
   - Wiek: 10-100 lat
   - Tempo: 3.0-10.0 min/km

4. **Wizualizacje**
   - Rozkład czasów dla tej samej płci
   - Rozkład czasów dla grupy wiekowej (±1 rok)
   - Interaktywne tooltipy i wykresy

## 🚀 Instalacja

1. Sklonuj repozytorium:
   ```bash
   git clone https://github.com/AlanSteinbarth/Kalkulator-dla-biegaczy.git
   cd Kalkulator-dla-biegaczy
   ```

2. Zainstaluj zależności:
   ```bash
   pip install -r requirements.txt
   ```

3. Utwórz plik `.env` i dodaj klucz API OpenAI:
   ```
   OPENAI_API_KEY=twój_klucz_api
   ```

4. Uruchom aplikację:
   ```bash
   streamlit run app.py
   ```

## 📊 Przykład użycia

1. Wprowadź swoje dane w dowolnej formie
2. Kliknij "Oblicz przewidywany czas"
3. Zobacz przewidywany czas i porównaj go z innymi biegaczami na wykresach

## 🛠️ Technologie

- Python 3.8+
- Streamlit
- PyCaret
- OpenAI GPT-4
- Plotly
- Pandas

## 📝 Licencja

Ten projekt jest dostępny na licencji MIT. Szczegóły w pliku [LICENSE](LICENSE).

## 👥 Kontrybucje

Zachęcamy do kontrybucji! Zobacz [CONTRIBUTING.md](CONTRIBUTING.md) po szczegóły.

## 📋 Changelog

Zobacz [CHANGELOG.md](CHANGELOG.md) po historię zmian.

## 🤝 Autor

Alan Steinbarth
- Email: alan.steinbarth@gmail.com
- GitHub: https://github.com/AlanSteinbarth

---
Data ostatniej aktualizacji: 2025-05-24
