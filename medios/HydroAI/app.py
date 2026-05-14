import streamlit as st
import pandas as pd

# ==========================================
# IMPORTAR MÓDULOS
# ==========================================

from modules.monitoreo import mostrar_monitoreo
from modules.mapas import mostrar_mapas
from modules.prediccion import mostrar_prediccion
from modules.analisis import mostrar_analisis
from modules.alertas import mostrar_alertas
from modules.reportes import mostrar_reportes
from modules.iot import mostrar_iot

# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="Dashboard IRCA",
    layout="wide"
)

import os

def cargar_css():

    base_dir = os.path.dirname(__file__)

    css_path = os.path.join(
        base_dir,
        "assets",
        "estilos.css"
    )

    with open(css_path) as f:

        st.markdown(

            f"<style>{f.read()}</style>",

            unsafe_allow_html=True
        )


import json

BASE_DIR = os.path.dirname(__file__)

config_path = os.path.join(
    BASE_DIR,
    "data",
    "config.json"
)

with open(config_path) as f:

    config = json.load(f)

# ==========================================
# CARGA DE DATOS
# ==========================================

@st.cache_data
def cargar_datos():

    url = "https://raw.githubusercontent.com/allhoo/allhoo.github.io/refs/heads/main/medios/dashboard/resultados_Cacota_2010_2025_procesados.csv"

    df = pd.read_csv(url)

    return df

df = cargar_datos()

# ==========================================
# SIDEBAR
# ==========================================

BASE_DIR = os.path.dirname(__file__)

logo_path = os.path.join(
    BASE_DIR,
    "assets",
    "logo.png"
)

if os.path.exists(logo_path):

    st.sidebar.image(
        logo_path,
        use_container_width=True
    )

else:

    st.sidebar.warning(
        f"No se encontró logo.png"
    )

st.sidebar.title("Sistema IRCA")

modulo = st.sidebar.selectbox(
    "Seleccionar módulo",
    [
        "Monitoreo",
        "Mapas",
        "Predicción",
        "Análisis químico",
        "Alertas",
        "Reportes",
        "IoT"
    ]
)

# ==========================================
# NAVEGACIÓN
# ==========================================

if modulo == "Monitoreo":
    mostrar_monitoreo(df)

elif modulo == "Mapas":
    mostrar_mapas(df)

elif modulo == "Predicción":
    mostrar_prediccion(df)

elif modulo == "Análisis químico":
    mostrar_analisis(df)

elif modulo == "Alertas":
    mostrar_alertas(df)

elif modulo == "Reportes":
    mostrar_reportes(df)

#elif modulo == "IoT":
    mostrar_iot(df)
