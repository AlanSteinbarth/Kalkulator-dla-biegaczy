import streamlit as st
import pandas as pd
import os
import boto3
from io import BytesIO
from pycaret.regression import load_model, predict_model
from langfuse import LangfuseClient

# --------------------------------------------------
# 1. ZAŁADOWANIE ZMIENNYCH ŚRODOWISKOWYCH
# --------------------------------------------------

# DigitalOcean Spaces (lub AWS S3) – obsługa różnych nazw
DO_KEY = os.getenv('DO_SPACES_KEY', os.getenv('AWS_ACCESS_KEY_ID'))
DO_SECRET = os.getenv('DO_SPACES_SECRET', os.getenv('AWS_SECRET_ACCESS_KEY'))
DO_REGION = os.getenv('DO_SPACES_REGION', os.getenv('AWS_REGION'))
DO_NAME = os.getenv('DO_SPACES_NAME', os.getenv('AWS_S3_BUCKET'))
# Endpoint DO (gdyby AWS_ENDPOINT_URL_S3 było puste, domyślnie region.digitaloceanspaces.com)
DO_ENDPOINT = os.getenv('AWS_ENDPOINT_URL_S3', f"https://{DO_REGION}.digitaloceanspaces.com")

# Langfuse – nowa wersja wymaga public_key i secret_key
LF_PUBLIC = os.getenv('LANGFUSE_PUBLIC_KEY')
LF_SECRET = os.getenv('LANGFUSE_SECRET_KEY')
LF_HOST = os.getenv('LANGFUSE_HOST', "https://cloud.langfuse.com")  # Domyślnie chmura EU

# Lista brakujących zmiennych
missing = [
    name for name, val in [
        ('DO_SPACES_KEY or AWS_ACCESS_KEY_ID', DO_KEY),
        ('DO_SPACES_SECRET or AWS_SECRET_ACCESS_KEY', DO_SECRET),
        ('DO_SPACES_REGION or AWS_REGION', DO_REGION),
        ('DO_SPACES_NAME or AWS_S3_BUCKET', DO_NAME),
        ('LANGFUSE_PUBLIC_KEY', LF_PUBLIC),
        ('LANGFUSE_SECRET_KEY', LF_SECRET)
    ] if not val
]

st.set_page_config(page_title='Biegowy Prognozator', layout='centered')
st.title('🏅 Biegowy Prognozator')

# Jeśli cokolwiek brakuje – pokazujemy błąd i zatrzymujemy działanie
if missing:
    st.error(
        'Brakujące zmienne środowiskowe:\n' +
        '\n'.join(missing) +
        '\n\nUstaw je w App Platform lub dodaj w GitHub Secrets.'
    )
    st.stop()

# --------------------------------------------------
# 2. INICJALIZACJA LANGFUSE
# --------------------------------------------------

lf = LangfuseClient(
    public_key=LF_PUBLIC,
    secret_key=LF_SECRET,
    host=LF_HOST
)

# --------------------------------------------------
# 3. POBRANIE I ZAŁADOWANIE MODELU Z DO SPACES
# --------------------------------------------------

def load_model_spaces():
    """
    Pobiera plik modelu (huber_model_halfmarathon_time.pkl) z DigitalOcean Spaces
    i zwraca obiekt modelu załadowany przez pycaret.load_model.
    """
    session = boto3.session.Session()
    client = session.client(
        's3',
        region_name=DO_REGION,
        endpoint_url=DO_ENDPOINT,
        aws_access_key_id=DO_KEY,
        aws_secret_access_key=DO_SECRET
    )
    obj = client.get_object(Bucket=DO_NAME, Key='models/huber_model_halfmarathon_time.pkl')
    data = obj['Body'].read()
    tmp_path = '/tmp/model.pkl'
    with open(tmp_path, 'wb') as f:
        f.write(data)
    return load_model(tmp_path)

model = load_model_spaces()

# --------------------------------------------------
# 4. FUNKCJE POMOCNICZE
# --------------------------------------------------

def to_hms(seconds: int) -> str:
    """
    Konwertuje czas w sekundach na format HH:MM:SS.
    """
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hrs:02}:{mins:02}:{secs:02}"

# --------------------------------------------------
# 5. INTERFEJS STREAMLIT
# --------------------------------------------------

st.write('Podaj dane, aby obliczyć przewidywany czas ukończenia półmaratonu:')

with st.form('input_form'):
    gender = st.radio('Płeć', ['Kobieta', 'Mężczyzna'])
    age = st.number_input('Wiek', min_value=0, max_value=120, value=30)
    pace = st.text_input('Tempo na 5 km (MM:SS)', '06:00')
    time5 = st.text_input('Czas na 5 km (MM:SS)', '35:00')
    submitted = st.form_submit_button('Oblicz czas')

if submitted:
    # 5.1 WALIDACJA FORMULARZA
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

    # --------------------------------------------------
    # 6. LOGOWANIE DO LANGFUSE (TRACE + GENERATION)
    # --------------------------------------------------

    # Tworzymy nowy trace o nazwie "predict" z wbudowanym inputem
    trace = lf.trace(
        name="predict",
        input=df_input.to_dict(orient='records')[0]  # pojedynczy rekord jako dict
    )

    try:
        # 6.1 WŁAŚCIWA PREDYKCJA MODELU
        res = predict_model(model, data=df_input)
        eta_sec = int(res['prediction_label'].iloc[0])

        # 6.2 Logujemy wynik jako Generation wewnątrz trace
        gen = trace.generation(
            name="prediction",
            model="huber_model_halfmarathon_time",
            input=df_input.to_dict(orient='records')[0]
        )
        gen.end(output={'eta_sec': eta_sec})

        # Kończymy trace
        trace.end()

        # 6.3 Wyświetlamy wynik w Streamlit
        st.success(f'Przewidywany czas półmaratonu: {to_hms(eta_sec)}')

    except Exception as e:
        # 6.4 W razie błędu – logujemy event ERROR i kończymy trace
        trace.event(
            name="predict_error",
            level="ERROR",
            status_message=str(e)
        )
        trace.end()

        st.error(f'Błąd predykcji: {e}')
