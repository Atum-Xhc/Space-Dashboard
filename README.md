# 🚀 Space Dashboard

Interaktywny dashboard astronomiczny z danymi na żywo z NASA i innych publicznych API.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io)
[![NASA API](https://img.shields.io/badge/Data-NASA%20API-blue.svg)](https://api.nasa.gov)

---

## Funkcjonalności

- 🌌 **APOD** – Astronomiczne Zdjęcie Dnia z NASA (z opisem i datą)
- ☄️ **Near Earth Objects** – asteroidy bliskie Ziemi z wykresem i tabelą
- 🛸 **ISS Tracker** – pozycja Międzynarodowej Stacji Kosmicznej na żywo na mapie
- 🔴 **Mars Rover** – najnowsze zdjęcia z łazika Curiosity/Perseverance

## Instalacja

```bash
git clone https://github.com/YOUR_USERNAME/space-dashboard.git
cd space-dashboard

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Opcjonalnie: wstaw własny klucz z https://api.nasa.gov
# Domyślny DEMO_KEY działa bez rejestracji
```

## Uruchomienie

```bash
streamlit run streamlit_app.py
```

## API używane w projekcie

| API | Dane | Klucz |
|-----|------|-------|
| [NASA APOD](https://api.nasa.gov) | Zdjęcie dnia | Darmowy (DEMO_KEY) |
| [NASA NeoWs](https://api.nasa.gov) | Asteroidy | Darmowy (DEMO_KEY) |
| [NASA Mars Rover](https://api.nasa.gov) | Zdjęcia z Marsa | Darmowy (DEMO_KEY) |
| [Open Notify](http://api.open-notify.org) | Pozycja ISS | Brak klucza |

## Architektura

```
dashboard/
├── nasa_client.py   # Klient NASA API (APOD, NEO, Mars Rover)
├── iss_client.py    # Klient Open Notify API (ISS)
└── charts.py        # Wykresy Plotly
```

## Testy

```bash
pytest tests/ -v
```

---

*Projekt portfolio Python AI/Data · NASA Open Data*
