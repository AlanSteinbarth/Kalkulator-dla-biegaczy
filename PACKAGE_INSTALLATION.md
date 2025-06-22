# INSTRUKCJE INSTALACJI BRAKUJĄCYCH PAKIETÓW

## Problemy z pakietami Python

Aplikacja wymaga następujących pakietów, które nie są obecnie zainstalowane:

### 1. PyCaret
```bash
pip install pycaret
```

### 2. Plotly
```bash
pip install plotly
```

### 3. Scikit-learn (zależność PyCaret)
```bash
pip install scikit-learn
```

### 4. Inne zależności (opcjonalne)
```bash
pip install seaborn matplotlib
```

## Instalacja w środowisku Conda

Jeśli używasz Conda, spróbuj:

```bash
# Dla plotly
conda install -c conda-forge plotly

# Dla PyCaret (może wymagać pip)
pip install pycaret

# Lub utwórz nowe środowisko
conda create -n kalkulator python=3.11
conda activate kalkulator
pip install -r requirements.txt
```

## Rozwiązanie problemów

1. **Jeśli instalacja się nie powiedzie**: Upewnij się, że masz aktywne środowisko wirtualne
2. **Dla macOS**: Może być potrzebne `brew install python` lub aktualizacja Xcode tools
3. **Dla Windows**: Upewnij się, że Python jest w PATH

## Status naprawy błędów lintera

✅ **NAPRAWIONE**:
- Broad exception handling - zastąpiono specific exceptions
- Variable redefinition - zmieniono nazwy zmiennych na unikalne
- Błędy składni - wszystkie naprawione
- Import errors - pozostają tylko dla brakujących pakietów

❌ **WYMAGAJĄ INSTALACJI PAKIETÓW**:
- `pycaret.regression` - wymaga instalacji PyCaret
- `plotly.express` - wymaga instalacji Plotly

Wszystkie inne błędy zostały naprawione i kod jest gotowy do uruchomienia po zainstalowaniu brakujących pakietów.
