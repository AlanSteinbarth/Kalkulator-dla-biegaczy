README – Kalkulator czasu półmaratonu (Streamlit)

Opis aplikacji:
----------------
Aplikacja webowa stworzona w Streamlit służy do szacowania przewidywanego czasu ukończenia półmaratonu na podstawie danych użytkownika: wieku, płci oraz tempa na 5km. Wykorzystuje wytrenowany model uczenia maszynowego (regresja Huber, PyCaret) oraz rzeczywiste dane biegaczy z Wrocławia.

Funkcjonalności:
----------------
1. **Wprowadzanie danych** – użytkownik podaje wiek, płeć i tempo na 5km w dowolnej formie tekstowej (np. "Mam 35 lat, jestem kobietą, tempo 5km: 5.10 min/km").
2. **Ekstrakcja danych AI** – dane są automatycznie rozpoznawane przez model OpenAI GPT-3.5.
3. **Walidacja danych** – aplikacja sprawdza poprawność wieku (10-100 lat) i tempa (3.0-10.0 min/km).
4. **Szacowanie czasu** – po kliknięciu "Oblicz przewidywany czas" wyświetlany jest przewidywany czas ukończenia półmaratonu.
5. **Interaktywne wykresy** – dwa wykresy (Plotly):
   - rozkład czasów tej samej płci,
   - rozkład czasów tej samej grupy wiekowej (±1 rok),
   - na wykresach zaznaczony Twój wynik i średnia grupy, tooltipy z dokładnym czasem i liczbą osób.
6. **Informacja o pozycji** – pod wykresami wyświetlana jest liczba osób w danej grupie.
7. **Resetowanie danych** – przycisk "Wyczyść dane" pozwala szybko zacząć od nowa.
8. **Nowoczesny interfejs** – przyciski obok siebie, stylowanie CSS, czytelny layout, pole z przykładem znika po obliczeniu wyniku.
9. **FAQ** – sekcja "Jak to działa?" dostępna w rozwijanej zakładce w panelu bocznym.
10. **Cache danych** – szybkie ładowanie danych referencyjnych.

Wymagania:
----------
- Python 3.8+
- Streamlit
- PyCaret
- OpenAI
- Plotly
- Pandas

Uruchomienie:
-------------
1. Zainstaluj wymagane biblioteki: `pip install -r requirements.txt`
2. Ustaw klucz API OpenAI w pliku `.env` (OPENAI_API_KEY=...)
3. Uruchom aplikację: `streamlit run app.py`

Autor: Alan Steinbarth
Data: 2025-05-21
