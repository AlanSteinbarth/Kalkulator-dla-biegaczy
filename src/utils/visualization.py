# =============================================================================
# FUNKCJE WIZUALIZACJI
# Moduł zawierający funkcje do tworzenia wykresów i wizualizacji
# =============================================================================

import pandas as pd
import plotly.express as px
import streamlit as st
import sys
import os
from typing import Tuple

# Dodanie głównego katalogu do ścieżki
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.model_utils import get_model_metrics


def create_gender_comparison_chart(reference_df: pd.DataFrame, user_gender: str, 
                                 predicted_minutes: float) -> Tuple[object, int, float]:
    """
    Tworzy wykres porównawczy dla danej płci.
    
    Args:
        reference_df: DataFrame z danymi referencyjnymi
        user_gender: Płeć użytkownika ('M' lub 'K')
        predicted_minutes: Przewidywany czas w minutach
        
    Returns:
        Tuple: (figura_plotly, liczba_osób, średnia_w_minutach)
    """
    df_gender = reference_df[reference_df['Płeć'] == user_gender].copy()
    group_count_gender = len(df_gender)
    
    if group_count_gender == 0:
        return None, 0, 0
    
    avg_gender = df_gender['Czas'].mean()
    df_gender['Czas_minuty'] = df_gender['Czas'] / 60
    avg_gender_minutes = avg_gender / 60
    
    gender_display = "Mężczyzna" if user_gender == "M" else "Kobieta"
    
    fig = px.histogram(
        df_gender, 
        x='Czas_minuty', 
        nbins=40,
        title=f"Rozkład czasów ukończenia półmaratonu dla płci: {gender_display}",
        labels={"Czas_minuty": "Czas ukończenia (minuty)", "count": "Liczba uczestników"},
        color_discrete_sequence=['#636EFA'],
        width=500, 
        height=500
    )
    
    # Dodanie linii referencyjnych
    fig.add_vline(
        x=predicted_minutes, 
        line_dash="dash", 
        line_color="red",
        annotation_text="Twój wynik", 
        annotation_position="top right"
    )
    
    fig.add_vline(
        x=avg_gender_minutes, 
        line_dash="dot", 
        line_color="green",
        annotation_text="Średnia", 
        annotation_position="bottom right"
    )
    
    fig.update_traces(hovertemplate='Czas: %{x:.1f} min<br>Liczba osób: %{y}<extra></extra>')
    fig.update_layout(
        xaxis_title="Czas ukończenia (minuty)", 
        yaxis_title="Liczba uczestników",
        showlegend=False
    )
    
    return fig, group_count_gender, avg_gender_minutes


def create_age_comparison_chart(reference_df: pd.DataFrame, user_age: int, 
                              predicted_minutes: float) -> Tuple[object, int, float]:
    """
    Tworzy wykres porównawczy dla danej grupy wiekowej.
    
    Args:
        reference_df: DataFrame z danymi referencyjnymi
        user_age: Wiek użytkownika
        predicted_minutes: Przewidywany czas w minutach
        
    Returns:
        Tuple: (figura_plotly, liczba_osób, średnia_w_minutach)
    """
    df_age = reference_df[reference_df['Wiek'].between(user_age-1, user_age+1)].copy()
    group_count_age = len(df_age)
    
    if group_count_age == 0:
        return None, 0, 0
    
    df_age['Czas_minuty'] = df_age['Czas'] / 60
    avg_age_minutes = df_age['Czas'].mean() / 60
    
    fig = px.histogram(
        df_age, 
        x='Czas_minuty', 
        nbins=40,
        title=f"Rozkład czasów ukończenia półmaratonu dla wieku: {user_age} ±1 rok",
        labels={"Czas_minuty": "Czas ukończenia (minuty)", "count": "Liczba uczestników"},
        color_discrete_sequence=['#00CC96'],
        width=500, 
        height=500
    )
    
    # Dodanie linii referencyjnych
    fig.add_vline(
        x=predicted_minutes, 
        line_dash="dash", 
        line_color="red",
        annotation_text="Twój wynik", 
        annotation_position="top right"
    )
    
    fig.add_vline(
        x=avg_age_minutes, 
        line_dash="dot", 
        line_color="green",
        annotation_text="Średnia", 
        annotation_position="bottom right"
    )
    
    fig.update_traces(hovertemplate='Czas: %{x:.1f} min<br>Liczba osób: %{y}<extra></extra>')
    fig.update_layout(
        xaxis_title="Czas ukończenia (minuty)", 
        yaxis_title="Liczba uczestników",
        showlegend=False
    )
    
    return fig, group_count_age, avg_age_minutes


def display_model_metrics():
    """Wyświetla metryki modelu w sidebar."""
    metrics = get_model_metrics()
    
    st.sidebar.markdown("### 📈 Metryki modelu")
    
    for metric, value in metrics.items():
        if isinstance(value, float):
            st.sidebar.metric(metric, f"{value:.2f}")
        else:
            st.sidebar.metric(metric, value)


def display_examples_sidebar():
    """Wyświetla przykłady w sidebar."""
    st.sidebar.markdown("### 💡 Przykłady danych")
    
    examples = [
        "Mam 28 lat, jestem kobietą, tempo 5km: 4:45",
        "35 lat, mężczyzna, biegam 5km w 5:20", 
        "Kobieta, 42 lata, mój czas na 5km to 6:10",
        "Facet, 30 lat, 5 kilometrów w 4.5 minuty na km"
    ]
    
    for i, example in enumerate(examples, 1):
        if st.sidebar.button(f"Przykład {i}", key=f"example_{i}", use_container_width=True):
            st.session_state['user_input'] = example
            st.rerun()


def display_usage_stats():
    """Wyświetla statystyki użytkowania w sidebar."""
    import time
    
    # Inicjalizacja statystyk w session state
    if 'usage_stats' not in st.session_state:
        st.session_state['usage_stats'] = {
            'predictions_made': 0,
            'start_time': time.time()
        }
    
    st.sidebar.markdown("### 📊 Statystyki sesji")
    
    predictions_count = st.session_state['usage_stats']['predictions_made']
    session_duration = time.time() - st.session_state['usage_stats']['start_time']
    
    st.sidebar.metric("Przewidywania wykonane", predictions_count)
    st.sidebar.metric("Czas sesji", f"{session_duration/60:.1f} min")


def increment_prediction_counter():
    """Zwiększa licznik przewidywań."""
    if 'usage_stats' in st.session_state:
        st.session_state['usage_stats']['predictions_made'] += 1
