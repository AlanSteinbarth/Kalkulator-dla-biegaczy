# app.py

import os
import socket
import streamlit as st
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.request_timeout = (5, 60)

# Quick network & key check
st.write("OPENAI_API_KEY:", openai.api_key)
try:
    sock = socket.create_connection(("api.openai.com", 443), timeout=5)
    sock.close()
    st.success("Sieć OK: api.openai.com:443 osiągalne")
except Exception as e:
    st.error(f"Problem z siecią/API: {e}")

def get_training_advice(wiek, płeć, tempo, czas):
    prompt = (
        f"Udziel porady treningowej osobie w wieku {wiek}, płci {płeć}, "
        f"która biega tempem {tempo} i osiągnęła czas {czas}."
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
            temperature=0
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"AI error: {e}")
        return "Przepraszam, nie mogę teraz wygenerować porady."

st.title("Porady Treningowe")

wiek = st.selectbox("Wiek", ["<18", "18-24", "25-34", "35-44", "45-54", "55-64", ">=65"])
płeć = st.radio("Płeć", ["Mężczyzna", "Kobieta"])
tempo = st.text_input("Twoje tempo (min/km)", "5:00")
czas = st.text_input("Twój czas (hh:mm:ss)", "00:25:00")

if st.button("Generuj poradę"):
    porada = get_training_advice(wiek, płeć, tempo, czas)
    st.markdown("**Porada od AI:**")
    st.write(porada)
