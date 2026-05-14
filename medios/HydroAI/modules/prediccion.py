import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error
)

import statsmodels.api as sm


# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================

def mostrar_prediccion(df):

    st.title("Predicción - Regresión Lineal Múltiple")

    # =========================================================
    # VALIDACIÓN
    # =========================================================

    if df.empty:

        st.warning("No hay datos disponibles")

        return

    # =========================================================
    # COPIA SEGURA
    # =========================================================

    df = df.copy()

    # =========================================================
    # COLUMNAS NUMÉRICAS
    # =========================================================

    df_num = df.select_dtypes(include="number")

    # =========================================================
    # ELIMINAR COLUMNAS VACÍAS
    # =========================================================

    df_num = df_num.dropna(
        axis=1,
        how="all"
    )

    # =========================================================
    # VALIDACIÓN COLUMNAS
    # =========================================================

    if len(df_num.columns) < 2:

        st.error(
            "No hay suficientes variables numéricas"
        )

        return

    # =========================================================
    # SELECCIÓN VARIABLE OBJETIVO
    # =========================================================

    st.subheader("Configuración del Modelo")

    columnas = list(df_num.columns)

    objetivo = st.selectbox(
        "Variable objetivo",
        columnas,
        index=0
    )

    # =========================================================
    # VARIABLES PREDICTORAS
    # =========================================================

    predictoras = st.multiselect(
        "Variables predictoras",
        [c for c in columnas if c != objetivo],

        default=[
            c for c in columnas
            if c != objetivo
        ][:3]
    )

    # =========================================================
    # VALIDACIÓN
    # =========================================================

    if len(predictoras) == 0:

        st.warning(
            "Seleccione variables predictoras"
        )

        return

    # =========================================================
    # DATOS
    # =========================================================

    datos_modelo = df_num[
        predictoras + [objetivo]
    ].dropna()

    # =========================================================
    # VALIDACIÓN
    # =========================================================

    if len(datos_modelo) < 5:

        st.error(
            "No hay suficientes datos válidos"
        )

        return

    # =========================================================
    # MATRICES
    # =========================================================

    X = datos_modelo[predictoras]

    y = datos_modelo[objetivo]

    # =========================================================
    # TRAIN / TEST
    # =========================================================

    X_train, X_test, y_train, y_test = train_test_split(

        X,
        y,

        test_size=0.2,

        random_state=42
    )

    # =========================================================
    # MODELO
    # =========================================================

    modelo = LinearRegression()

    modelo.fit(
        X_train,
        y_train
    )

    # =========================================================
    # PREDICCIÓN
    # =========================================================

    y_pred = modelo.predict(X_test)

    # =========================================================
    # MÉTRICAS
    # =========================================================

    r2 = r2_score(
        y_test,
        y_pred
    )

    mae = mean_absolute_error(
        y_test,
        y_pred
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            y_pred
        )
    )

    # =========================================================
    # KPIs
    # =========================================================

    st.subheader("Indicadores del Modelo")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "R²",
            round(r2, 4)
        )

    with col2:

        st.metric(
            "MAE",
            round(mae, 4)
        )

    with col3:

        st.metric(
            "RMSE",
            round(rmse, 4)
        )

    # =========================================================
    # REAL VS PREDICHO
    # =========================================================

    st.subheader("Valores Reales vs Predichos")

    resultados = pd.DataFrame({

        "Real": y_test,

        "Predicho": y_pred
    })

    fig_real = px.scatter(

        resultados,

        x="Real",

        y="Predicho",

        trendline="ols",

        title="Real vs Predicho"
    )

    fig_real.add_trace(

        go.Scatter(

            x=[
                resultados["Real"].min(),
                resultados["Real"].max()
            ],

            y=[
                resultados["Real"].min(),
                resultados["Real"].max()
            ],

            mode="lines",

            name="Ideal"
        )
    )

    st.plotly_chart(
        fig_real,
        use_container_width=True
    )

    # =========================================================
    # RESIDUOS
    # =========================================================

    st.subheader("Análisis de Residuos")

    residuos = y_test - y_pred

    fig_res = px.scatter(

        x=y_pred,

        y=residuos,

        labels={

            "x": "Predicción",

            "y": "Residuo"
        },

        title="Residuos del Modelo"
    )

    fig_res.add_hline(
        y=0
    )

    st.plotly_chart(
        fig_res,
        use_container_width=True
    )

    # =========================================================
    # HISTOGRAMA RESIDUOS
    # =========================================================

    fig_hist = px.histogram(

        residuos,

        nbins=20,

        title="Distribución de Residuos"
    )

    st.plotly_chart(
        fig_hist,
        use_container_width=True
    )

    # =========================================================
    # COEFICIENTES
    # =========================================================

    st.subheader("Coeficientes del Modelo")

    coeficientes = pd.DataFrame({

        "Variable": predictoras,

        "Coeficiente": modelo.coef_
    })

    coeficientes = coeficientes.sort_values(
        by="Coeficiente",
        ascending=False
    )

    st.dataframe(
        coeficientes,
        use_container_width=True
    )

    # =========================================================
    # GRÁFICA COEFICIENTES
    # =========================================================

    fig_coef = px.bar(

        coeficientes,

        x="Variable",

        y="Coeficiente",

        title="Importancia de Variables"
    )

    st.plotly_chart(
        fig_coef,
        use_container_width=True
    )

    # =========================================================
    # MODELO ESTADÍSTICO
    # =========================================================

    st.subheader("Resumen Estadístico")

    X_sm = sm.add_constant(X)

    modelo_sm = sm.OLS(
        y,
        X_sm
    ).fit()

    st.text(
        modelo_sm.summary()
    )

    # =========================================================
    # ECUACIÓN
    # =========================================================

    st.subheader("Ecuación del Modelo")

    ecuacion = f"{objetivo} = "

    ecuacion += str(
        round(modelo.intercept_, 4)
    )

    for var, coef in zip(
        predictoras,
        modelo.coef_
    ):

        ecuacion += f" + ({round(coef,4)} × {var})"

    st.code(ecuacion)

    # =========================================================
    # DATOS
    # =========================================================

    with st.expander("Ver datos utilizados"):

        st.dataframe(
            datos_modelo,
            use_container_width=True
        )