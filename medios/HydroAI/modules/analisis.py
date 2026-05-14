import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from scipy.stats import (
    pearsonr,
    spearmanr
)


# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================

def mostrar_analisis(df):

    st.title("Análisis Químico y Estadístico")

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
    # FECHA
    # =========================================================

    if "Fecha de Muestreo" in df.columns:

        df["Fecha de Muestreo"] = pd.to_datetime(
            df["Fecha de Muestreo"],
            errors="coerce"
        )

    # =========================================================
    # COLUMNAS NUMÉRICAS
    # =========================================================

    df_num = df.select_dtypes(include="number")

    # =========================================================
    # VALIDACIÓN
    # =========================================================

    if len(df_num.columns) < 2:

        st.error(
            "No hay suficientes variables numéricas"
        )

        return

    # =========================================================
    # SIDEBAR
    # =========================================================

    st.sidebar.subheader("Filtros")

    # =========================================================
    # FILTRO AÑO
    # =========================================================

    if "Fecha de Muestreo" in df.columns:

        años = sorted(
            df["Fecha de Muestreo"]
            .dt.year
            .dropna()
            .unique()
        )

        año = st.sidebar.selectbox(
            "Año",
            ["Todos"] + list(años)
        )

        if año != "Todos":

            df = df[
                df["Fecha de Muestreo"].dt.year == año
            ]

            df_num = df.select_dtypes(
                include="number"
            )

    # =========================================================
    # KPIs
    # =========================================================

    st.subheader("Indicadores Estadísticos")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Variables numéricas",
            len(df_num.columns)
        )

    with col2:

        st.metric(
            "Muestras",
            len(df_num)
        )

    with col3:

        st.metric(
            "Valores faltantes",
            int(df_num.isna().sum().sum())
        )

    with col4:

        st.metric(
            "Correlaciones posibles",
            int(
                (
                    len(df_num.columns)
                    *
                    (len(df_num.columns)-1)
                ) / 2
            )
        )

    # =========================================================
    # ANÁLISIS DESCRIPTIVO
    # =========================================================

    st.subheader("Estadística Descriptiva")

    descripcion = df_num.describe().T

    descripcion["CV (%)"] = (

        descripcion["std"]
        /
        descripcion["mean"]

    ) * 100

    st.dataframe(
        descripcion,
        use_container_width=True
    )

    # =========================================================
    # VARIABLE
    # =========================================================

    st.subheader("Distribución de Variables")

    variable = st.selectbox(
        "Seleccionar variable",
        df_num.columns
    )

    # =========================================================
    # HISTOGRAMA
    # =========================================================

    fig_hist = px.histogram(

        df_num,

        x=variable,

        nbins=30,

        title=f"Distribución de {variable}"
    )

    st.plotly_chart(
        fig_hist,
        use_container_width=True
    )

    # =========================================================
    # BOXPLOT
    # =========================================================

    fig_box = px.box(

        df_num,

        y=variable,

        title=f"Boxplot de {variable}"
    )

    st.plotly_chart(
        fig_box,
        use_container_width=True
    )

    # =========================================================
    # MATRIZ CORRELACIÓN
    # =========================================================

    st.subheader("Correlaciones")

    metodo = st.radio(

        "Método de correlación",

        [
            "pearson",
            "spearman"
        ],

        horizontal=True
    )

    # =========================================================
    # MATRIZ
    # =========================================================

    matriz_corr = df_num.corr(
        method=metodo
    )

    # =========================================================
    # HEATMAP
    # =========================================================

    fig_corr = px.imshow(

        matriz_corr,

        text_auto=True,

        aspect="auto",

        color_continuous_scale="RdBu_r",

        title=f"Correlación ({metodo})"
    )

    st.plotly_chart(
        fig_corr,
        use_container_width=True
    )

    # =========================================================
    # VARIABLES RELACIÓN
    # =========================================================

    st.subheader("Relación entre Variables")

    colx, coly = st.columns(2)

    with colx:

        x_var = st.selectbox(
            "Variable X",
            df_num.columns,
            key="xvar"
        )

    with coly:

        y_var = st.selectbox(
            "Variable Y",
            df_num.columns,
            index=1,
            key="yvar"
        )

    # =========================================================
    # DATOS LIMPIOS
    # =========================================================

    datos_relacion = df_num[
        [x_var, y_var]
    ].dropna()

    # =========================================================
    # CORRELACIÓN
    # =========================================================

    if metodo == "pearson":

        corr,
        pvalue = pearsonr(
            datos_relacion[x_var],
            datos_relacion[y_var]
        )

    else:

        corr,
        pvalue = spearmanr(
            datos_relacion[x_var],
            datos_relacion[y_var]
        )

    # =========================================================
    # KPIs CORRELACIÓN
    # =========================================================

    kc1, kc2 = st.columns(2)

    with kc1:

        st.metric(
            "Coeficiente",
            round(corr, 4)
        )

    with kc2:

        st.metric(
            "p-value",
            round(pvalue, 6)
        )

    # =========================================================
    # INTERPRETACIÓN
    # =========================================================

    if abs(corr) >= 0.8:

        st.success(
            "Correlación muy fuerte"
        )

    elif abs(corr) >= 0.6:

        st.info(
            "Correlación fuerte"
        )

    elif abs(corr) >= 0.4:

        st.warning(
            "Correlación moderada"
        )

    else:

        st.error(
            "Correlación débil"
        )

    # =========================================================
    # DISPERSIÓN
    # =========================================================

    fig_disp = px.scatter(

        datos_relacion,

        x=x_var,

        y=y_var,

        trendline="ols",

        title=f"{x_var} vs {y_var}"
    )

    st.plotly_chart(
        fig_disp,
        use_container_width=True
    )

    # =========================================================
    # SERIES TEMPORALES
    # =========================================================

    if "Fecha de Muestreo" in df.columns:

        st.subheader("Serie Temporal")

        variable_t = st.selectbox(
            "Variable temporal",
            df_num.columns,
            key="temporal"
        )

        fig_temp = px.line(

            df,

            x="Fecha de Muestreo",

            y=variable_t,

            markers=True,

            title=f"{variable_t} en el tiempo"
        )

        st.plotly_chart(
            fig_temp,
            use_container_width=True
        )

    # =========================================================
    # OUTLIERS
    # =========================================================

    st.subheader("Detección de Valores Atípicos")

    variable_out = st.selectbox(
        "Variable análisis outliers",
        df_num.columns,
        key="outliers"
    )

    q1 = df_num[
        variable_out
    ].quantile(0.25)

    q3 = df_num[
        variable_out
    ].quantile(0.75)

    iqr = q3 - q1

    limite_inf = q1 - 1.5 * iqr

    limite_sup = q3 + 1.5 * iqr

    outliers = df_num[
        (
            df_num[variable_out] < limite_inf
        )
        |
        (
            df_num[variable_out] > limite_sup
        )
    ]

    st.metric(
        "Outliers detectados",
        len(outliers)
    )

    fig_out = px.box(

        df_num,

        y=variable_out,

        points="all",

        title=f"Outliers en {variable_out}"
    )

    st.plotly_chart(
        fig_out,
        use_container_width=True
    )

    # =========================================================
    # TABLA CORRELACIONES
    # =========================================================

    st.subheader("Tabla de Correlaciones")

    st.dataframe(
        matriz_corr,
        use_container_width=True
    )

    # =========================================================
    # DATOS
    # =========================================================

    with st.expander("Ver datos"):

        st.dataframe(
            df,
            use_container_width=True
        )