import streamlit as st
import pandas as pd
import os
import boto3
from io import BytesIO
from pycaret.regression import load_model, predict_model
from langfuse.client import LangfuseClient

# Walidacja zmiennych środowiskowych
env_required = ['DO_SPACES_KEY', 'DO_SPACES_SECRET', 'DO_SPACES_REGION', 'DO_SPACES_NAME', 'LANGFUSE_API_KEY']
env_missing = [v for v in env_required if v not in os.environ]

st.set_page_config(page_title='Biegowy Prognozator', layout='centered')
st.title('🏅 Biegowy Prognozator')
if env_missing:
    st.error(f"Brakujące zmienne środowiskowe: {', '.join(env_missing)}. Ustaw je w App Platform.")
    st.stop()

# Inicjalizacja Langfuse
lf = LangfuseClient(api_key=os.environ['LANGFUSE_API_KEY'])

# Funkcja do pobierania modelu z DigitalOcean Spaces i cache
@st.cache_resource
def load_model_spaces():
    session = boto3.session.Session()
    client = session.client(
        's3',
        region_name=os.environ['DO_SPACES_REGION'],
        endpoint_url=f"https://{os.environ['DO_SPACES_REGION']}.digitaloceanspaces.com",
        aws_access_key_id=os.environ['DO_SPACES_KEY'],
        aws_secret_access_key=os.environ['DO_SPACES_SECRET']
    )
    data = client.get_object(Bucket=os.environ['DO_SPACES_NAME'], Key='models/huber_model_halfmarathon_time.pkl')['Body'].read()
    tmp_path = '/tmp/model.pkl'
    with open(tmp_path, 'wb') as f:
        f.write(data)
    return load_model(tmp_path)

model = load_model_spaces()

# Format czasu sekund na HH:MM:SS
def to_hms(seconds: int) -> str:
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hrs:02}:{mins:02}:{secs:02}"

# Główna logika UI
st.write('Podaj dane, aby obliczyć przewidywany czas ukończenia półmaratonu:')
with st.form('input_form'):
    gender = st.radio('Płeć', ['Kobieta', 'Mężczyzna'])
    age = st.number_input('Wiek', min_value=0, max_value=120, value=30)
    pace = st.text_input('Tempo na 5 km (MM:SS)', '06:00')
    time5 = st.text_input('Czas na 5 km (MM:SS)', '35:00')
    submitted = st.form_submit_button('Oblicz czas')

if submitted:
    # Walidacja formatu
    if ':' not in pace or ':' not in time5:
        st.error('Tempo i czas muszą być w formacie MM:SS')
        st.stop()
    try:
        p_min, p_sec = map(int, pace.split(':'))
        t_min, t_sec = map(int, time5.split(':'))
    except ValueError:
        st.error('Niepoprawne wartości liczb w polach tempo lub czas.')
        st.stop()
    pace_sec = p_min * 60 + p_sec
    time5_sec = t_min * 60 + t_sec
    df_input = pd.DataFrame({
        'Wiek': [age],
        'Płeć': [0 if gender == 'Kobieta' else 1],
        'Tempo_5km': [pace_sec],
        'Czas_5km': [time5_sec]
    })
    # Logowanie i predykcja przez Langfuse
    lf.log_start('predict', input=df_input.to_dict(orient='records'))
    try:
        res = predict_model(model, data=df_input)
        eta_sec = int(res['prediction_label'].iloc[0])
        lf.log_success('predict', output={'eta_sec': eta_sec})
        st.success(f'Przewidywany czas półmaratonu: {to_hms(eta_sec)}')
    except Exception as e:
        lf.log_failure('predict', error=str(e))
        st.error(f'Błąd predykcji: {e}')
