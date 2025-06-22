# 🤝 Contributing Guide

Dziękuję za zainteresowanie wkładem w projekt **Kalkulator dla biegaczy**! 

## 🚀 Szybki start dla developerów

### Setup środowiska
```bash
# Fork i sklonuj
git clone https://github.com/YOUR_USERNAME/Kalkulator-dla-biegaczy.git
cd Kalkulator-dla-biegaczy

# Wirtualne środowisko
python -m venv venv
source venv/bin/activate

# Instalacja z narzędziami dev
pip install -r requirements.txt
pip install pytest black flake8

# Pre-commit hooks
pre-commit install
```

### Standardy kodu
- **Formatowanie**: Black (`black .`)
- **Linting**: flake8 (`flake8 .`)
- **Testy**: pytest (`pytest`)
- **Type hints**: Dodawaj tam gdzie to możliwe

### Workflow
1. **Fork** → **Branch** → **Code** → **Test** → **PR**
2. Branch naming: `feature/nazwa`, `fix/nazwa`, `docs/nazwa`
3. Commit messages: `feat:`, `fix:`, `docs:`, `test:`

## 🐛 Zgłaszanie błędów

**Szablon Issue:**
```markdown
**Opis:** Krótko o problemie
**Kroki:** 1. Krok 1 2. Krok 2  
**Oczekiwane:** Co powinno się stać
**Środowisko:** OS, Python, Streamlit wersja
```

## ✨ Propozycje funkcjonalności

**Priorytetowe obszary:**
- Więcej dystansów (10km, maraton)
- Integracja z Strava API
- Mobile optimization
- Performance improvements

## 📞 Kontakt

- GitHub Issues: Pytania techniczne
- Email: alan.steinbarth@gmail.com
- Discussions: Ogólne dyskusje

**Dziękuję za wkład! 🙏**
