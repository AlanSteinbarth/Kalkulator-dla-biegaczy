# 🔧 INSTRUKCJA NAPRAWY VS CODE

## Problem: VS Code nie rozpoznaje importów (streamlit, pandas, dotenv, openai)

### ✅ **ROZWIĄZANIE KROK PO KROK:**

1. **RESTART VS CODE**
   - Zamknij VS Code całkowicie
   - Otwórz ponownie projekt

2. **WYBIERZ WŁAŚCIWY INTERPRETER**
   - Naciśnij `Cmd+Shift+P` (macOS) lub `Ctrl+Shift+P` (Windows/Linux)
   - Wpisz: `Python: Select Interpreter`
   - Wybierz: `/Users/alansteinbarth/Desktop/od_zera_do_ai/Projekty na GitHub/Kalkulator-dla-biegaczy/venv/bin/python`

3. **PRZEŁADUJ OKNO** (opcjonalnie)
   - `Cmd+Shift+P` → `Developer: Reload Window`

4. **SPRAWDŹ STATUS BAR**
   - W dolnym pasku VS Code powinieneś zobaczyć: `Python 3.13.5 ('venv': venv)`

### 🛠️ **ALTERNATYWNE ROZWIĄZANIA:**

**Opcja A: Manualny wybór interpretera**
```
Cmd+Shift+P → "Python: Select Interpreter" → "Enter interpreter path..." 
→ Wpisz: /Users/alansteinbarth/Desktop/od_zera_do_ai/Projekty na GitHub/Kalkulator-dla-biegaczy/venv/bin/python
```

**Opcja B: Restart Pylance**
```
Cmd+Shift+P → "Python: Restart Language Server"
```

**Opcja C: Sprawdź czy pakiety są zainstalowane**
```bash
cd "/Users/alansteinbarth/Desktop/od_zera_do_ai/Projekty na GitHub/Kalkulator-dla-biegaczy"
source venv/bin/activate
python -c "import streamlit, pandas, openai; print('OK')"
```

### 📁 **PLIKI KONFIGURACYJNE UTWORZONE:**

- `.vscode/settings.json` - Konfiguracja interpretera Python
- `.vscode/launch.json` - Konfiguracja debugowania
- `.vscode/tasks.json` - Zadania do uruchamiania aplikacji
- `.vscode/extensions.json` - Rekomendowane rozszerzenia
- `pyrightconfig.json` - Konfiguracja Pylance
- `.env` - Zmienne środowiskowe

### ✅ **SPRAWDZENIE CZY DZIAŁA:**

Po wykonaniu kroków powyżej:
1. Otwórz `app.py` w VS Code
2. Linia `import streamlit as st` nie powinna pokazywać błędu
3. Można uruchomić aplikację zadaniem: `Cmd+Shift+P` → "Tasks: Run Task" → "Uruchom aplikację Streamlit"

### 🚨 **JEŚLI NADAL NIE DZIAŁA:**

1. Sprawdź czy masz zainstalowane rozszerzenia Python:
   - Python (ms-python.python)
   - Pylance (ms-python.vscode-pylance)

2. Upewnij się, że środowisko wirtualne jest aktywne:
   ```bash
   which python
   # Powinno zwrócić: /Users/alansteinbarth/Desktop/od_zera_do_ai/Projekty na GitHub/Kalkulator-dla-biegaczy/venv/bin/python
   ```

3. W ostateczności - usuń folder `.vscode` i pozwól VS Code utworzyć go ponownie.

---
**Utworzono:** 23 czerwca 2025  
**Status:** Wszystkie pakiety są zainstalowane i działają - problem tylko w konfiguracji VS Code
