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

    st.subheader("Modelo de regresión múltiple")

    # =========================
    # SOLO COLUMNAS NUMÉRICAS
    # =========================

    df_num = df.select_dtypes(include=["number"]).copy()

    # =========================
    # ELIMINAR COLUMNAS VACÍAS
    # =========================

    df_num = df_num.dropna(axis=1, how="all")

    # =========================
    # VARIABLE OBJETIVO
    # =========================

    objetivo = st.selectbox(
        "Variable objetivo",
        df_num.columns
    )

    # =========================
    # VARIABLES PREDICTORAS
    # =========================

    predictoras = st.multiselect(
        "Variables predictoras",
        [c for c in df_num.columns if c != objetivo],
        default=[c for c in df_num.columns if c != objetivo][:3]
    )

    # =========================
    # VALIDACIÓN
    # =========================

    if len(predictoras) == 0:

        st.warning("Seleccione al menos una variable predictora")

    else:

        # =========================
        # DATOS
        # =========================

        datos_modelo = df_num[predictoras + [objetivo]].dropna()

        X = datos_modelo[predictoras]
        y = datos_modelo[objetivo]

        # =========================
        # VALIDACIÓN EXTRA
        # =========================

        if len(X) < 2:

            st.error("No hay suficientes datos válidos")

        else:

            # =========================
            # MODELO
            # =========================

            model = LinearRegression()

            model.fit(X, y)

            y_pred = model.predict(X)

            # =========================
            # RESULTADOS
            # =========================

            st.write("R²:", round(model.score(X, y), 4))

            resultados = pd.DataFrame({
                "Real": y,
                "Predicho": y_pred
            })

            fig = px.scatter(
                resultados,
                x="Real",
                y="Predicho",
                trendline="ols",
                title="Valores reales vs predichos"
            )

            st.plotly_chart(fig)

            # =========================
            # COEFICIENTES
            # =========================

            coef = pd.DataFrame({
                "Variable": predictoras,
                "Coeficiente": model.coef_
            })

            st.dataframe(coef)

     
