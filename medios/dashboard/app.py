import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression

# ======================
# CARGA DE DATOS
# ======================

url = "https://raw.githubusercontent.com/USUARIO/REPO/main/resultados_Cacota_2010_2025_procesados.csv"
df = pd.read_csv(url)

# ajustar fecha (cambia el nombre si es diferente)
df["Fecha de Muestreo"] = pd.to_datetime(df["Fecha de Muestreo"])

# ======================
# INTERFAZ
# ======================

st.title("Dashboard Calidad del Agua - IRCA")

modo = st.sidebar.selectbox(
    "Seleccionar módulo",
    ["Series temporales", "Correlación", "Predicción"]
)

# ======================
# 1. SERIES TEMPORALES
# ======================

if modo == "Series temporales":

    columnas = df.select_dtypes(include="number").columns

    variable = st.selectbox("Variable", columnas)

    fig = px.line(
        df,
        x="Fecha de Muestreo",
        y=variable,
        title=f"{variable} en el tiempo"
    )

    st.plotly_chart(fig)

# ======================
# 2. CORRELACIÓN
# ======================

elif modo == "Correlación":

    metodo = st.selectbox(
        "Método",
        ["pearson", "spearman"]
    )

    df_num = df.select_dtypes(include="number")

    corr = df_num.corr(method=metodo)

    fig = px.imshow(
        corr,
        text_auto=True,
        title=f"Correlación ({metodo})"
    )

    st.plotly_chart(fig)

# ======================
# 3. PREDICCIÓN IRCA
# ======================

elif modo == "Predicción":

    df_num = df.select_dtypes(include="number").dropna()

    if "IRCA (%)" not in df_num.columns:
        st.error("No se encontró la columna IRCA (%)")
    else:
        X = df_num.drop(columns=["IRCA (%)"])
        y = df_num["IRCA (%)"]

        model = LinearRegression()
        model.fit(X, y)

        y_pred = model.predict(X)

        fig = px.scatter(
            x=y,
            y=y_pred,
            labels={"x": "IRCA real", "y": "IRCA predicho"},
            title="Modelo de regresión múltiple"
        )

        st.plotly_chart(fig)

        st.write("R² del modelo:", model.score(X, y))