import streamlit as st
st.set_page_config(page_title="Kalkulator półmaratonu", layout="wide")
import pandas as pd
import datetime
from pycaret.regression import load_model, predict_model
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import plotly.express as px

load_dotenv()

# OpenAI setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_user_data(user_input):
    prompt = f"""
    Extract the following information from the user input:
    - Age (as a number)
    - Gender (M or K)
    - 5km pace (as a float number)
    Return the data in JSON format with keys: 'Wiek', 'Płeć', '5 km Tempo'
    
    User input: {user_input}
    """
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return None

def calculate_5km_time(tempo):
    """Convert 5km tempo (min/km) to total seconds for 5km"""
    minutes_per_km = float(tempo)
    return minutes_per_km * 5 * 60

def is_valid_age(age):
    try:
        age = int(age)
        return 10 <= age <= 100
    except:
        return False

def is_valid_tempo(tempo):
    try:
        tempo = float(tempo)
        return 3.0 <= tempo <= 10.0
    except:
        return False

# Wczytaj dane referencyjne do wykresów
@st.cache_data
def load_reference_data():
    df = pd.read_csv("df_cleaned.csv")
    return df

reference_df = load_reference_data()

st.title("🏃‍♂️ Kalkulator czasu półmaratonu")
st.markdown("""
Wprowadź swoje dane, a aplikacja oszacuje Twój czas ukończenia półmaratonu na podstawie wytrenowanego modelu uczenia maszynowego.

*Podaj wiek, płeć oraz tempo na 5km w dowolnej formie tekstowej.*
""")

if 'user_input' not in st.session_state:
    st.session_state['user_input'] = "Np.: Mam 28 lat, jestem mężczyzną i biegam 5km w tempie 4.45 min/km"

# --- STYLOWANIE PRZYCISKÓW ---
st.markdown("""
    <style>
    div.stButton > button {
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(44, 62, 80, 0.15);
        margin-bottom: 0px !important;
        margin-top: 0px !important;
        font-weight: 600;
        font-size: 1.1em;
    }
    </style>
""", unsafe_allow_html=True)

# --- POLE TEKSTOWE Z NOWYM PLACEHOLDEREM ---
user_input = st.text_area(
    "Przedstaw się i podaj swoje dane (wiek, płeć, tempo na 5km):",
    st.session_state['user_input'],
    key="user_input_area",
    placeholder="Wpisz: Mam 35 lat, jestem kobietą, tempo 5km: 5.10 min/km"
)

# --- PRZYCISKI BEZPOŚREDNIO POD POLEM TEKSTOWYM ---
col1, col2 = st.columns([1, 1], gap="small")
with col1:
    oblicz = st.button("Oblicz przewidywany czas", use_container_width=True)
with col2:
    wyczysc = st.button("Wyczyść dane", use_container_width=True)

if wyczysc:
    st.session_state['user_input'] = ""
    st.rerun()

if oblicz:
    if not user_input or user_input.strip() == "":
        st.warning("⚠️ Proszę wprowadzić dane.")
    else:
        user_data = extract_user_data(user_input)
        if user_data is None:
            st.error("❌ Nie udało się przetworzyć danych. Upewnij się, że podałeś wszystkie wymagane informacje.")
        else:
            missing_fields = []
            required_fields = ['Wiek', 'Płeć', '5 km Tempo']
            for field in required_fields:
                if field not in user_data:
                    missing_fields.append(field)
            if missing_fields:
                st.warning(f"⚠️ Brakuje następujących danych: {', '.join(missing_fields)}")
            else:
                # Walidacja wieku i tempa
                if not is_valid_age(user_data['Wiek']):
                    st.warning("⚠️ Wiek powinien być liczbą z zakresu 10-100 lat.")
                elif not is_valid_tempo(user_data['5 km Tempo']):
                    st.warning("⚠️ Tempo na 5km powinno być liczbą z zakresu 3.0-10.0 min/km.")
                else:
                    try:
                        model_path = "huber_model_halfmarathon_time"
                        model = load_model(model_path)
                        prediction_data = pd.DataFrame({
                            'Wiek': [user_data['Wiek']],
                            'Płeć': [user_data['Płeć']],
                            '5 km Tempo': [float(user_data['5 km Tempo'])],
                            '5 km Czas': [calculate_5km_time(user_data['5 km Tempo'])]
                        })
                        prediction = predict_model(model, data=prediction_data)
                        predicted_seconds = round(prediction["prediction_label"].iloc[0], 2)
                        predicted_time = str(datetime.timedelta(seconds=int(predicted_seconds)))
                        st.success(f"✅ Przewidywany czas ukończenia półmaratonu: {predicted_time}")
                        # --- WIZUALIZACJA: rozkład czasów tej samej płci ---
                        user_gender = user_data['Płeć']
                        user_age = int(user_data['Wiek'])
                        df_gender = reference_df[reference_df['Płeć'] == user_gender]
                        group_count_gender = len(df_gender)
                        avg_gender = df_gender['Czas'].mean()
                        fig1 = px.histogram(
                            df_gender, x='Czas', nbins=40,
                            title=f"Rozkład czasów ukończenia półmaratonu dla płci: {user_gender}",
                            labels={"Czas": "Czas ukończenia (sekundy)"},
                            color_discrete_sequence=['#636EFA'],
                            width=500, height=500,
                            hover_data={'Czas':':.0f'}
                        )
                        fig1.add_vline(x=predicted_seconds, line_dash="dash", line_color="red",
                            annotation_text="Twój wynik", annotation_position="top right")
                        fig1.add_vline(x=avg_gender, line_dash="dot", line_color="green",
                            annotation_text="Średnia", annotation_position="bottom right")
                        fig1.update_traces(hovertemplate='Czas: %{x:.0f} sek<br>Liczba osób: %{y}')
                        fig1.update_layout(xaxis_title="Czas ukończenia (sekundy)", yaxis_title="Liczba uczestników")
                        st.markdown(f"Twój wynik na tle <b>{group_count_gender}</b> osób tej samej płci.", unsafe_allow_html=True)
                        st.plotly_chart(fig1)
                        # --- WIZUALIZACJA: rozkład czasów tego samego wieku (±1 rok) ---
                        df_age = reference_df[reference_df['Wiek'].between(user_age-1, user_age+1)]
                        group_count_age = len(df_age)
                        avg_age = df_age['Czas'].mean()
                        fig2 = px.histogram(
                            df_age, x='Czas', nbins=40,
                            title=f"Rozkład czasów ukończenia półmaratonu dla wieku: {user_age} ±1 rok",
                            labels={"Czas": "Czas ukończenia (sekundy)"},
                            color_discrete_sequence=['#00CC96'],
                            width=500, height=500,
                            hover_data={'Czas':':.0f'}
                        )
                        fig2.add_vline(x=predicted_seconds, line_dash="dash", line_color="red",
                            annotation_text="Twój wynik", annotation_position="top right")
                        fig2.add_vline(x=avg_age, line_dash="dot", line_color="green",
                            annotation_text="Średnia", annotation_position="bottom right")
                        fig2.update_traces(hovertemplate='Czas: %{x:.0f} sek<br>Liczba osób: %{y}')
                        fig2.update_layout(xaxis_title="Czas ukończenia (sekundy)", yaxis_title="Liczba uczestników")
                        st.markdown(f"Twój wynik na tle <b>{group_count_age}</b> osób w tej grupie wiekowej.", unsafe_allow_html=True)
                        st.plotly_chart(fig2)
                    except Exception as e:
                        st.error(f"❌ Wystąpił błąd podczas generowania przewidywania: {str(e)}")

# Info z przykładem tylko jeśli nie ma wyniku
if not (oblicz and user_data and not missing_fields and is_valid_age(user_data['Wiek']) and is_valid_tempo(user_data['5 km Tempo'])):
    st.info("ℹ️ Przykład: 'Mam 28 lat, jestem mężczyzną i biegam 5km w tempie 4.45 min/km'")

# --- LEWA ROZWIJANA ZAKŁADKA Z FAQ ---
with st.sidebar:
    with st.expander("ℹ️ Jak to działa? (FAQ)", expanded=False):
        st.markdown("""
        **Jak działa kalkulator?**  
        Twój czas półmaratonu jest szacowany na podstawie wieku, płci i tempa na 5km. Model został wytrenowany na rzeczywistych wynikach biegaczy z Wrocławia z lat 2023-2024.  
        Wykorzystujemy model uczenia maszynowego (PyCaret, regresja Huber), a dane wejściowe są automatycznie rozpoznawane przez AI (OpenAI GPT-3.5).  

        **Jak interpretować wykresy?**  
        Na wykresach możesz zobaczyć, jak Twój przewidywany czas wypada na tle innych osób tej samej płci i wieku. Czerwona linia to Twój wynik, zielona linia to średnia w danej grupie.
        """)
