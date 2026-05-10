import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression

# =====================
# DATOS
# =====================

@st.cache_data
def cargar_datos():

    url = "https://raw.githubusercontent.com/allhoo/allhoo.github.io/refs/heads/main/medios/dashboard/resultados_Cacota_2010_2025_procesados.csv"

    df = pd.read_csv(url)

    df["Fecha de Muestreo"] = pd.to_datetime(
        df["Fecha de Muestreo"]
    )

    return df

df = cargar_datos()

# =====================
# MENU
# =====================

st.sidebar.title("Opciones")

modo = st.sidebar.selectbox(
    "Módulo",
    [
        "Series temporales",
        "Correlación",
        "Regresión múltiple"
    ]
)

# =====================
# SERIES TEMPORALES
# =====================

if modo == "Series temporales":

    columnas = df.select_dtypes(include="number").columns

    variable = st.selectbox(
        "Seleccionar variable",
        columnas
    )

    fig = px.line(
        df,
        x="Fecha de Muestreo",
        y=variable,
        title=f"{variable} en el tiempo"
    )

    st.plotly_chart(fig)

# =====================
# CORRELACIÓN
# =====================

elif modo == "Correlación":

    metodo = st.radio(
        "Método",
        ["pearson", "spearman"]
    )

    df_num = df.select_dtypes(include="number")

    corr = df_num.corr(method=metodo)

    fig = px.imshow(
        corr,
        text_auto=True
    )

    st.plotly_chart(fig)

    st.dataframe(corr)

# =====================
# REGRESIÓN MÚLTIPLE
# =====================

elif modo == "Regresión múltiple":

    df_num = df.select_dtypes(include="number").dropna()

    objetivo = st.selectbox(
        "Variable objetivo",
        df_num.columns
    )

    predictoras = st.multiselect(
        "Variables predictoras",
        df_num.columns.drop(objetivo),
        default=list(df_num.columns.drop(objetivo)[:3])
    )

    if len(predictoras) > 0:

        X = df_num[predictoras]
        y = df_num[objetivo]

        model = LinearRegression()

        model.fit(X, y)

        y_pred = model.predict(X)

        st.write(
            "R²:",
            model.score(X, y)
        )

        fig = px.scatter(
            x=y,
            y=y_pred,
            labels={
                "x":"Real",
                "y":"Predicho"
            }
        )

        st.plotly_chart(fig)
