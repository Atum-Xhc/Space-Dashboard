"""
dashboard/charts.py
Funkcje pomocnicze do tworzenia wykresów Plotly dla dashboardu.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def neo_scatter_chart(asteroids: list[dict]) -> go.Figure:
    """
    Wykres punktowy: odległość od Ziemi vs prędkość asteroidy.
    Rozmiar punktu = średnica. Kolor = potencjalnie niebezpieczna.

    Args:
        asteroids: Lista dict z get_neo()["asteroids"]

    Returns:
        Plotly Figure
    """
    if not asteroids:
        return go.Figure()

    df = pd.DataFrame(asteroids)
    df["diameter_avg_m"] = (df["diameter_min_m"] + df["diameter_max_m"]) / 2
    df["hazardous_label"] = df["hazardous"].map({True: "⚠️ Niebezpieczna", False: "✅ Bezpieczna"})
    df["miss_distance_mln_km"] = (df["miss_distance_km"] / 1_000_000).round(2)

    fig = px.scatter(
        df,
        x="miss_distance_mln_km",
        y="velocity_kmh",
        size="diameter_avg_m",
        color="hazardous_label",
        color_discrete_map={
            "⚠️ Niebezpieczna": "#FF4B4B",
            "✅ Bezpieczna": "#00CC96",
        },
        hover_name="name",
        hover_data={
            "diameter_avg_m": ":.0f",
            "close_approach_date": True,
            "hazardous_label": False,
        },
        labels={
            "miss_distance_mln_km": "Odległość od Ziemi (mln km)",
            "velocity_kmh": "Prędkość (km/h)",
            "diameter_avg_m": "Średnica (m)",
        },
        title="Asteroidy bliskie Ziemi – odległość vs prędkość",
        template="plotly_dark",
    )

    fig.update_layout(
        legend_title="Status",
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
    )

    return fig


def neo_bar_chart(asteroids: list[dict]) -> go.Figure:
    """
    Wykres słupkowy: Top 10 największych asteroid według średnicy.
    """
    if not asteroids:
        return go.Figure()

    df = pd.DataFrame(asteroids)
    df["diameter_avg_m"] = (df["diameter_min_m"] + df["diameter_max_m"]) / 2
    top10 = df.nlargest(10, "diameter_avg_m")

    colors = ["#FF4B4B" if h else "#636EFA" for h in top10["hazardous"]]

    fig = go.Figure(go.Bar(
        x=top10["name"],
        y=top10["diameter_avg_m"],
        marker_color=colors,
        text=top10["diameter_avg_m"].apply(lambda x: f"{x:.0f} m"),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Średnica: %{y:.0f} m<extra></extra>",
    ))

    fig.update_layout(
        title="Top 10 największych asteroid w pobliżu Ziemi",
        xaxis_title="Nazwa asteroidy",
        yaxis_title="Szacowana średnica (m)",
        template="plotly_dark",
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        xaxis_tickangle=-30,
    )

    return fig


def iss_map(latitude: float, longitude: float) -> go.Figure:
    """
    Mapa świata z aktualną pozycją ISS.

    Args:
        latitude: Szerokość geograficzna ISS
        longitude: Długość geograficzna ISS

    Returns:
        Plotly Figure z mapą
    """
    fig = go.Figure(go.Scattergeo(
        lon=[longitude],
        lat=[latitude],
        mode="markers+text",
        marker=dict(size=18, color="#FFD700", symbol="star"),
        text=["🛸 ISS"],
        textposition="top center",
        hovertemplate=(
            f"<b>ISS</b><br>"
            f"Lat: {latitude:.4f}°<br>"
            f"Lon: {longitude:.4f}°<extra></extra>"
        ),
    ))

    fig.update_layout(
        geo=dict(
            showland=True,
            landcolor="#1a1a2e",
            showocean=True,
            oceancolor="#16213e",
            showcoastlines=True,
            coastlinecolor="#374151",
            showframe=False,
            projection_type="natural earth",
            bgcolor="#0e1117",
        ),
        paper_bgcolor="#0e1117",
        margin=dict(l=0, r=0, t=0, b=0),
        height=400,
    )

    return fig
