import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================

def mostrar_alertas(df):

    st.title("Sistema de Alertas")

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
    # SIDEBAR
    # =========================================================

    st.sidebar.subheader("Configuración de Alertas")

    # =========================================================
    # UMBRALES PERSONALIZADOS
    # =========================================================

    umbral_irca = st.sidebar.slider(
        "IRCA máximo permitido",
        0.0,
        100.0,
        5.0
    )

    umbral_ph_min = st.sidebar.slider(
        "pH mínimo",
        0.0,
        14.0,
        6.5
    )

    umbral_ph_max = st.sidebar.slider(
        "pH máximo",
        0.0,
        14.0,
        8.5
    )

    umbral_cloro = st.sidebar.slider(
        "Cloro residual mínimo",
        0.0,
        5.0,
        0.3
    )

    umbral_turbidez = st.sidebar.slider(
        "Turbidez máxima",
        0.0,
        100.0,
        2.0
    )

    # =========================================================
    # COLUMNAS DISPONIBLES
    # =========================================================

    columnas = list(df.columns)

    # =========================================================
    # DETECCIÓN COLUMNAS
    # =========================================================

    col_irca = None
    col_ph = None
    col_cloro = None
    col_turbidez = None

    # =========================================================
    # IRCA
    # =========================================================

    posibles_irca = [
        "IRCA (%)",
        "IRCA",
        "Irca"
    ]

    for c in posibles_irca:

        if c in columnas:

            col_irca = c
            break

    # =========================================================
    # pH
    # =========================================================

    posibles_ph = [
        "pH",
        "PH",
        "Ph"
    ]

    for c in posibles_ph:

        if c in columnas:

            col_ph = c
            break

    # =========================================================
    # CLORO
    # =========================================================

    posibles_cloro = [
        "Cloro residual libre",
        "Cloro Residual Libre",
        "Cloro residual",
        "Cloro Residual"
    ]

    for c in posibles_cloro:

        if c in columnas:

            col_cloro = c
            break

    # =========================================================
    # TURBIDEZ
    # =========================================================

    posibles_turbidez = [
        "Turbidez",
        "turbidez"
    ]

    for c in posibles_turbidez:

        if c in columnas:

            col_turbidez = c
            break

    # =========================================================
    # ALERTAS
    # =========================================================

    alertas = []

    # =========================================================
    # ALERTA IRCA
    # =========================================================

    if col_irca:

        datos_irca = df[
            df[col_irca] > umbral_irca
        ]

        for _, row in datos_irca.iterrows():

            alertas.append({

                "Tipo": "IRCA Alto",

                "Variable": col_irca,

                "Valor": row[col_irca],

                "Nivel": "Alta",

                "Fecha": row.get(
                    "Fecha de Muestreo",
                    None
                ),

                "Punto": row.get(
                    "Punto de Toma",
                    "N/A"
                )
            })

    # =========================================================
    # ALERTA pH
    # =========================================================

    if col_ph:

        datos_ph = df[
            (
                df[col_ph] < umbral_ph_min
            )
            |
            (
                df[col_ph] > umbral_ph_max
            )
        ]

        for _, row in datos_ph.iterrows():

            alertas.append({

                "Tipo": "pH fuera de rango",

                "Variable": col_ph,

                "Valor": row[col_ph],

                "Nivel": "Media",

                "Fecha": row.get(
                    "Fecha de Muestreo",
                    None
                ),

                "Punto": row.get(
                    "Punto de Toma",
                    "N/A"
                )
            })

    # =========================================================
    # ALERTA CLORO
    # =========================================================

    if col_cloro:

        datos_cloro = df[
            df[col_cloro] < umbral_cloro
        ]

        for _, row in datos_cloro.iterrows():

            alertas.append({

                "Tipo": "Cloro bajo",

                "Variable": col_cloro,

                "Valor": row[col_cloro],

                "Nivel": "Alta",

                "Fecha": row.get(
                    "Fecha de Muestreo",
                    None
                ),

                "Punto": row.get(
                    "Punto de Toma",
                    "N/A"
                )
            })

    # =========================================================
    # ALERTA TURBIDEZ
    # =========================================================

    if col_turbidez:

        datos_turbidez = df[
            df[col_turbidez] > umbral_turbidez
        ]

        for _, row in datos_turbidez.iterrows():

            alertas.append({

                "Tipo": "Turbidez alta",

                "Variable": col_turbidez,

                "Valor": row[col_turbidez],

                "Nivel": "Media",

                "Fecha": row.get(
                    "Fecha de Muestreo",
                    None
                ),

                "Punto": row.get(
                    "Punto de Toma",
                    "N/A"
                )
            })

    # =========================================================
    # DATAFRAME ALERTAS
    # =========================================================

    alertas_df = pd.DataFrame(alertas)

    # =========================================================
    # KPIs
    # =========================================================

    st.subheader("Indicadores de Alertas")

    col1, col2, col3, col4 = st.columns(4)

    total_alertas = len(alertas_df)

    alertas_altas = 0
    alertas_medias = 0

    if not alertas_df.empty:

        alertas_altas = len(
            alertas_df[
                alertas_df["Nivel"] == "Alta"
            ]
        )

        alertas_medias = len(
            alertas_df[
                alertas_df["Nivel"] == "Media"
            ]
        )

    # =========================================================
    # TOTAL
    # =========================================================

    with col1:

        st.metric(
            "Total Alertas",
            total_alertas
        )

    # =========================================================
    # ALTAS
    # =========================================================

    with col2:

        st.metric(
            "Alertas Altas",
            alertas_altas
        )

    # =========================================================
    # MEDIAS
    # =========================================================

    with col3:

        st.metric(
            "Alertas Medias",
            alertas_medias
        )

    # =========================================================
    # ESTADO
    # =========================================================

    with col4:

        if total_alertas == 0:

            st.metric(
                "Estado",
                "Normal"
            )

        else:

            st.metric(
                "Estado",
                "Atención"
            )

    # =========================================================
    # ESTADO GENERAL
    # =========================================================

    st.subheader("Estado General")

    if total_alertas == 0:

        st.success(
            "No se detectaron alertas"
        )

    elif alertas_altas > 0:

        st.error(
            "Existen alertas críticas"
        )

    else:

        st.warning(
            "Existen alertas moderadas"
        )

    # =========================================================
    # TABLA ALERTAS
    # =========================================================

    st.subheader("Listado de Alertas")

    if alertas_df.empty:

        st.info(
            "No hay alertas activas"
        )

    else:

        st.dataframe(
            alertas_df,
            use_container_width=True
        )

    # =========================================================
    # GRÁFICA ALERTAS
    # =========================================================

    if not alertas_df.empty:

        st.subheader("Distribución de Alertas")

        resumen = (

            alertas_df["Tipo"]

            .value_counts()

            .reset_index()
        )

        resumen.columns = [
            "Tipo",
            "Cantidad"
        ]

        fig_alertas = px.bar(

            resumen,

            x="Tipo",

            y="Cantidad",

            title="Cantidad de Alertas"
        )

        st.plotly_chart(
            fig_alertas,
            use_container_width=True
        )

    # =========================================================
    # ALERTAS TEMPORALES
    # =========================================================

    if (
        not alertas_df.empty
        and
        "Fecha" in alertas_df.columns
    ):

        st.subheader("Alertas en el Tiempo")

        alertas_df["Fecha"] = pd.to_datetime(
            alertas_df["Fecha"],
            errors="coerce"
        )

        alertas_tiempo = (

            alertas_df

            .groupby("Fecha")

            .size()

            .reset_index(name="Cantidad")
        )

        fig_time = px.line(

            alertas_tiempo,

            x="Fecha",

            y="Cantidad",

            markers=True,

            title="Evolución Temporal de Alertas"
        )

        st.plotly_chart(
            fig_time,
            use_container_width=True
        )

    # =========================================================
    # PIE CHART
    # =========================================================

    if not alertas_df.empty:

        st.subheader("Niveles de Riesgo")

        pie = (

            alertas_df["Nivel"]

            .value_counts()

            .reset_index()
        )

        pie.columns = [
            "Nivel",
            "Cantidad"
        ]

        fig_pie = px.pie(

            pie,

            names="Nivel",

            values="Cantidad",

            title="Distribución por Nivel"
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

    # =========================================================
    # EXPORTAR
    # =========================================================

    st.subheader("Exportar Alertas")

    if not alertas_df.empty:

        csv = alertas_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(

            label="Descargar CSV",

            data=csv,

            file_name="alertas.csv",

            mime="text/csv"
        )

    # =========================================================
    # DATOS
    # =========================================================

    with st.expander("Ver datos originales"):

        st.dataframe(
            df,
            use_container_width=True
        )