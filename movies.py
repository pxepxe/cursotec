
import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import json
import altair as alt

key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="cursotec-c0222")

dbmovies =db.collection("movies")

# Cargar datos desde la colección 'movies'
@st.cache_data
def load_data():
    docs = list(db.collection(u'movies').stream())
    data_dicts = [doc.to_dict() for doc in docs]
    return pd.DataFrame(data_dicts)

# Cargar datos una vez
data_load_state = st.text('Cargando datos...')
data = load_data()
data_load_state.text("¡Listo!")

# ======================
# Filtros por título
@st.cache_data
def load_data_by_title(title):
    return data[data["name"].str.contains(title, case=False)]

# Filtros por director
@st.cache_data
def load_data_by_director(director):
    return data[data["director"] == director]

# ======================
# Interfaz de usuario
# ======================

# Mostrar todos los filmes
if st.sidebar.checkbox("Mostrar todos los filmes"):
    st.subheader("Conjunto de datos completo")
    st.dataframe(data)

# Buscar por título
movie_title = st.sidebar.text_input("Buscar por título:")
if movie_title:
    filtered_by_title = load_data_by_title(movie_title)
    st.write(f"Películas encontradas: {filtered_by_title.shape[0]}")
    st.dataframe(filtered_by_title)

# Buscar por director
selected_director = st.sidebar.selectbox("Selecciona un director", data["director"].dropna().unique())
if st.sidebar.button("Filtrar por director"):
    filtered_by_director = load_data_by_director(selected_director)
    st.write(f"Películas encontradas: {filtered_by_director.shape[0]}")
    st.dataframe(filtered_by_director)

# ==============================
# Sección para nuevo registro
# ==============================

st.sidebar.header("Agregar nueva película")

new_name = st.sidebar.text_input("Nombre de la película:")
new_company = st.sidebar.text_input("Compañía:")
new_director = st.sidebar.text_input("Director:")
new_genre = st.sidebar.text_input("Género:")
submit = st.sidebar.button("Crear nuevo registro")

# Validación e inserción
if new_name and new_company and new_director and new_genre and submit:
    # Se utiliza el nombre como ID del documento (no se recomienda en producción)
    doc_ref = db.collection("movies").document(new_name)
    doc_ref.set({
        "name": new_name,
        "company": new_company,
        "director": new_director,
        "genre": new_genre
    })
    st.sidebar.success("¡Registro insertado correctamente!")
    st.cache_data.clear()
    st.rerun()
