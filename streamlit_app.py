"""
streamlit_app.py – Główny plik dashboardu Space.

Uruchomienie:
    streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta

from dashboard.nasa_client import NASAClient
from dashboard.iss_client import ISSClient
from dashboard.charts import neo_scatter_chart, neo_bar_chart, iss_map

# ---------------------------------------------------------------------------
# Konfiguracja strony
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="🚀 Space Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ciemny styl pasujący do kosmosu
st.markdown("""
<style>
    .stMetric { background-color: #1a1a2e; border-radius: 8px; padding: 10px; }
    .stMetric label { color: #9CA3AF !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🚀 Space Dashboard")
    st.caption("Dane na żywo z NASA & Open Notify API")
    st.divider()

    nasa_key = st.text_input(
        "NASA API Key (opcjonalnie)",
        value="DEMO_KEY",
        help="Darmowy klucz: https://api.nasa.gov | DEMO_KEY działa bez rejestracji",
        type="password",
    )

    st.divider()
    page = st.radio(
        "Sekcja",
        options=["🌌 Zdjęcie Dnia", "☄️ Asteroidy", "🛸 ISS Tracker", "🔴 Mars Rover"],
    )

    st.divider()
    st.caption("Źródła danych:")
    st.caption("• [NASA Open APIs](https://api.nasa.gov)")
    st.caption("• [Open Notify](http://open-notify.org)")

# Inicjalizacja klientów
nasa = NASAClient(api_key=nasa_key)
iss = ISSClient()


# ===========================================================================
# SEKCJA 1: APOD – Astronomiczne Zdjęcie Dnia
# ===========================================================================
if page == "🌌 Zdjęcie Dnia":
    st.title("🌌 Astronomiczne Zdjęcie Dnia")
    st.caption("NASA Astronomy Picture of the Day (APOD)")

    col_date, col_btn = st.columns([3, 1])
    with col_date:
        selected_date = st.date_input(
            "Data",
            value=date.today(),
            min_value=date(1995, 6, 16),  # Pierwsze APOD
            max_value=date.today(),
        )
    with col_btn:
        st.write("")
        load_btn = st.button("📡 Załaduj", use_container_width=True)

    if "apod_data" not in st.session_state or load_btn:
        with st.spinner("Pobieranie zdjęcia dnia..."):
            try:
                st.session_state.apod_data = nasa.get_apod(selected_date.isoformat())
            except Exception as e:
                st.error(f"Błąd API: {e}")
                st.stop()

    apod = st.session_state.apod_data

    st.subheader(apod.get("title", ""))
    st.caption(f"📅 {apod.get('date', '')} · {apod.get('copyright', 'NASA')}")

    if apod.get("media_type") == "image":
        st.image(apod["url"], use_container_width=True)
    elif apod.get("media_type") == "video":
        st.video(apod["url"])

    with st.expander("📖 Opis (NASA)", expanded=True):
        st.write(apod.get("explanation", "Brak opisu."))

    if apod.get("hdurl"):
        st.link_button("🔍 Pełna rozdzielczość", apod["hdurl"])


# ===========================================================================
# SEKCJA 2: Asteroidy (NEO)
# ===========================================================================
elif page == "☄️ Asteroidy":
    st.title("☄️ Asteroidy bliskie Ziemi")
    st.caption("NASA Near Earth Object Web Service (NeoWs) · kolejne 7 dni")

    with st.spinner("Pobieranie danych o asteroidach..."):
        try:
            neo_data = nasa.get_neo(days=7)
        except Exception as e:
            st.error(f"Błąd API: {e}")
            st.stop()

    asteroids = neo_data["asteroids"]
    hazardous = [a for a in asteroids if a["hazardous"]]

    # Metryki
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Łącznie asteroid", neo_data["element_count"])
    col2.metric("Potencjalnie niebezpiecznych", len(hazardous), delta=None)
    col3.metric("Najbliższa (km)", f"{asteroids[0]['miss_distance_km']:,}" if asteroids else "—")
    col4.metric("Najszybsza (km/h)", f"{max(a['velocity_kmh'] for a in asteroids):,}" if asteroids else "—")

    st.divider()

    tab1, tab2, tab3 = st.tabs(["📊 Wykres odległość/prędkość", "📏 Największe", "📋 Tabela"])

    with tab1:
        st.plotly_chart(neo_scatter_chart(asteroids), use_container_width=True)

    with tab2:
        st.plotly_chart(neo_bar_chart(asteroids), use_container_width=True)

    with tab3:
        df = pd.DataFrame(asteroids)
        if not df.empty:
            df["hazardous"] = df["hazardous"].map({True: "⚠️ Tak", False: "✅ Nie"})
            df = df.rename(columns={
                "name": "Nazwa",
                "diameter_min_m": "Śr. min (m)",
                "diameter_max_m": "Śr. max (m)",
                "hazardous": "Niebezpieczna",
                "velocity_kmh": "Prędkość (km/h)",
                "miss_distance_km": "Odległość (km)",
                "close_approach_date": "Data zbliżenia",
            })
            st.dataframe(df, use_container_width=True, hide_index=True)


# ===========================================================================
# SEKCJA 3: ISS Tracker
# ===========================================================================
elif page == "🛸 ISS Tracker":
    st.title("🛸 ISS – Międzynarodowa Stacja Kosmiczna")
    st.caption("Dane na żywo · Open Notify API · odświeżaj co 10 sekund")

    col_refresh, col_auto = st.columns([2, 4])
    with col_refresh:
        if st.button("🔄 Odśwież pozycję", use_container_width=True):
            if "iss_position" in st.session_state:
                del st.session_state.iss_position

    with st.spinner("Pobieranie pozycji ISS..."):
        try:
            if "iss_position" not in st.session_state:
                st.session_state.iss_position = iss.get_position()
                st.session_state.astronauts = iss.get_astronauts()
        except Exception as e:
            st.error(f"Błąd API: {e}")
            st.stop()

    pos = st.session_state.iss_position
    people = st.session_state.astronauts

    # Pozycja
    col1, col2, col3 = st.columns(3)
    col1.metric("🌍 Szerokość (lat)", f"{pos['latitude']:.4f}°")
    col2.metric("🌍 Długość (lon)", f"{pos['longitude']:.4f}°")
    col3.metric("👨‍🚀 Osób na orbicie", len(people))

    # Mapa
    st.plotly_chart(iss_map(pos["latitude"], pos["longitude"]), use_container_width=True)

    # Astronauci
    if people:
        st.subheader("👨‍🚀 Załoga w kosmosie")
        iss_crew = [p for p in people if p.get("craft") == "ISS"]
        other_crew = [p for p in people if p.get("craft") != "ISS"]

        if iss_crew:
            st.caption("🛸 Na pokładzie ISS:")
            cols = st.columns(min(len(iss_crew), 4))
            for i, person in enumerate(iss_crew):
                cols[i % 4].info(f"👤 **{person['name']}**")

        if other_crew:
            st.caption("🚀 Inne statki:")
            for person in other_crew:
                st.caption(f"• {person['name']} ({person.get('craft', '?')})")


# ===========================================================================
# SEKCJA 4: Mars Rover
# ===========================================================================
elif page == "🔴 Mars Rover":
    st.title("🔴 Zdjęcia z Marsa")
    st.caption("NASA Mars Rover Photos API")

    col1, col2 = st.columns(2)
    with col1:
        rover = st.selectbox("Łazik", ["curiosity", "perseverance"], index=0)
    with col2:
        sol = st.number_input("Sol (dzień marsjański)", min_value=1, max_value=4000, value=1000)

    if st.button("📡 Załaduj zdjęcia", use_container_width=False):
        with st.spinner(f"Pobieranie zdjęć z {rover.capitalize()} (sol {sol})..."):
            try:
                photos = nasa.get_mars_photos(rover=rover, sol=sol)
                st.session_state.mars_photos = photos
                st.session_state.mars_rover = rover
                st.session_state.mars_sol = sol
            except Exception as e:
                st.error(f"Błąd API: {e}")

    if "mars_photos" in st.session_state:
        photos = st.session_state.mars_photos
        if not photos:
            st.warning(f"Brak zdjęć dla {st.session_state.mars_rover} sol {st.session_state.mars_sol}. Spróbuj innego sola.")
        else:
            st.success(f"Znaleziono {len(photos)} zdjęć · {photos[0]['earth_date']}")

            # Galeria
            cols_per_row = 3
            for i in range(0, len(photos), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, photo in enumerate(photos[i:i + cols_per_row]):
                    with cols[j]:
                        st.image(photo["img_src"], caption=photo["camera"], use_container_width=True)
    else:
        st.info("👆 Wybierz łazika i sola, a następnie kliknij 'Załaduj zdjęcia'")
        st.caption("Sol to marsjański dzień od lądowania łazika. Curiosity wylądował 6 sierpnia 2012.")
