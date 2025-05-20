import streamlit as st
import pandas as pd
import os
from langfuse import LangfuseClient
import boto3
from pycaret.regression import load_model, predict_model
from io import BytesIO

# Walidacja zmiennych środowiskowych
required = ['DO_SPACES_KEY','DO_SPACES_SECRET','DO_SPACES_REGION','DO_SPACES_NAME','LANGFUSE_API_KEY']
missing = [v for v in required if v not in os.environ]
st.set_page_config(page_title='Biegowy Prognozator', layout='centered')
st.title('🏅 Biegowy Prognozator')
if missing:
    st.error(f"Brakujące zmienne środowiskowe: {', '.join(missing)}. Ustaw je w App Platform.")
    st.stop()

# Inicjalizacja Langfuse\ nlf = LangfuseClient(api_key=os.environ['LANGFUSE_API_KEY'])

# Wczytanie modelu z DO Spaces\ n@st.cache_resource
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
    tmp = '/tmp/model.pkl'
    with open(tmp, 'wb') as f:
        f.write(data)
    return load_model(tmp)
model = load_model_spaces()

# Format czasu
def to_hms(s):
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    return f"{h:02}:{m:02}:{sec:02}"

# UI i logika: ankieta
st.write('Podaj dane, aby obliczyć przewidywany czas ukończenia półmaratonu:')
with st.form('input_form'):
    gender = st.radio('Płeć', ['Kobieta', 'Mężczyzna'])
    age = st.number_input('Wiek', min_value=0, max_value=120, value=30)
    pace = st.text_input('Tempo na 5 km (MM:SS)', '06:00')
    time5 = st.text_input('Czas na 5 km (MM:SS)', '35:00')
    submit = st.form_submit_button('Oblicz czas')

if submit:
    # Walidacja formatów
    if ':' not in pace or ':' not in time5:
        st.error('Tempo i czas muszą być w formacie MM:SS')
        st.stop()
    try:
        m1, s1 = map(int, pace.split(':'))
        m2, s2 = map(int, time5.split(':'))
    except ValueError:
        st.error('Niepoprawne wartości liczb w polach tempo lub czas.')
        st.stop()
    pace_sec = m1*60 + s1
    time5_sec = m2*60 + s2
    df_input = pd.DataFrame({
        'Wiek': [age],
        'Płeć': [0 if gender == 'Kobieta' else 1],
        'Tempo_5km': [pace_sec],
        'Czas_5km': [time5_sec]
    })
    # Logowanie i predykcja
    lf.log_start('predict', input=df_input.to_dict(orient='records'))
    try:
        res = predict_model(model, data=df_input)
        eta = int(res['prediction_label'].iloc[0])
        lf.log_success('predict', output={'eta_sec': eta})
        st.success(f'Przewidywany czas półmaratonu: {to_hms(eta)}')
    except Exception as e:
        lf.log_failure('predict', error=str(e))
        st.error(f'Błąd predykcji: {e}')
