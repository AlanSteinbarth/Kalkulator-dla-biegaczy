import streamlit as st
import pandas as pd
import os
from openai import OpenAI
import boto3
from pycaret.regression import load_model, predict_model
from io import BytesIO

# Walidacja zmiennych środowiskowych
required_env = ['OPENAI_API_KEY', 'DO_SPACES_KEY', 'DO_SPACES_SECRET', 'DO_SPACES_REGION', 'DO_SPACES_NAME']
missing = [var for var in required_env if var not in os.environ]
if missing:
    raise EnvironmentError(f"Brakujące zmienne środowiskowe: {', '.join(missing)}")

# Inicjalizacja klienta OpenAI
openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Funkcja do pobierania modelu z DO Spaces z cache
@st.cache_resource
def load_remote_model(bucket: str, key: str):
    session = boto3.session.Session()
    client = session.client(
        's3',
        region_name=os.environ['DO_SPACES_REGION'],
        endpoint_url=f"https://{os.environ['DO_SPACES_REGION']}.digitaloceanspaces.com",
        aws_access_key_id=os.environ['DO_SPACES_KEY'],
        aws_secret_access_key=os.environ['DO_SPACES_SECRET']
    )
    data = client.get_object(Bucket=bucket, Key=key)['Body'].read()
    # Zapisujemy w pamięci
    buffer = BytesIO(data)
    # PyCaret wymaga pliku na dysku, więc zapisujemy tymczasowo
    tmp_path = '/tmp/model.pkl'
    with open(tmp_path, 'wb') as f:
        f.write(buffer.getbuffer())
    return load_model(tmp_path)

# Ładowanie modelu
bucket = os.environ['DO_SPACES_NAME']
model_key = 'models/huber_model_halfmarathon_time.pkl'
model = load_remote_model(bucket, model_key)

# Konwersja sekund na HH:MM:SS
@st.cache_data
def format_time(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"

# Streamlit UI
st.set_page_config(page_title='Biegowy Prognozator', layout='centered')
st.title('🏅 Biegowy Prognozator')
st.markdown('Podaj dane wejściowe, aby oszacować czas ukończenia półmaratonu.')

with st.form('predict'):
    gender = st.radio('Płeć', ['Kobieta', 'Mężczyzna'])
    age = st.number_input('Wiek', min_value=0, max_value=120, value=30)
    pace = st.text_input('Tempo na 5 km (MM:SS)', '06:00')
    time5 = st.text_input('Czas na 5 km (MM:SS)', '35:00')
    submit = st.form_submit_button('Oblicz czas')

if submit:
    # Walidacja formatu
    for field, label in [(pace, 'Tempo'), (time5, 'Czas na 5 km')]:
        if ':' not in field:
            st.error(f"{label} musi być w formacie MM:SS")
            st.stop()
    try:
        m1, s1 = map(int, pace.split(':'))
        m2, s2 = map(int, time5.split(':'))
    except ValueError:
        st.error('Niepoprawne wartości liczbowe.')
        st.stop()
    pace_sec = m1 * 60 + s1
    time5_sec = m2 * 60 + s2
    df_input = pd.DataFrame({
        'Wiek': [age],
        'Płeć': [0 if gender == 'Kobieta' else 1],
        'Tempo_5km': [pace_sec],
        'Czas_5km': [time5_sec]
    })
    try:
        with st.spinner('Przewidywanie...'):
            res = predict_model(model, data=df_input)
            pred_sec = int(res['prediction_label'].iloc[0])
            pred_hms = format_time(pred_sec)
            st.success(f'Czas ukończenia półmaratonu: {pred_hms}')
    except Exception as e:
        st.error(f'Błąd podczas predykcji: {e}')
