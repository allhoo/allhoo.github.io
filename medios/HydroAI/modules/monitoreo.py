
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================

def mostrar_monitoreo(df):

    st.title("Monitoreo de Calidad del Agua")

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

    # =========================================================
    # FILTRO PUNTO
    # =========================================================

    posibles_puntos = [
        "Punto de Muestreo",
        "Punto de Toma",
        "Lugar"
    ]

    columna_punto = None

    for c in posibles_puntos:
        if c in df.columns:
            columna_punto = c
            break

    if columna_punto:

        puntos = sorted(
            df[columna_punto]
            .dropna()
            .astype(str)
            .unique()
        )

        punto = st.sidebar.selectbox(
            "Punto",
            ["Todos"] + list(puntos)
        )

        if punto != "Todos":

            df = df[
                df[columna_punto].astype(str) == punto
            ]

    # =========================================================
    # COLUMNAS NUMÉRICAS
    # =========================================================

    df_num = df.select_dtypes(include="number")

    # =========================================================
    # KPIs PRINCIPALES
    # =========================================================

    st.subheader("Indicadores Principales")

    col1, col2, col3, col4 = st.columns(4)

    # -------------------------
    # IRCA
    # -------------------------

    irca_prom = None

    if "IRCA (%)" in df.columns:

        irca_prom = round(
            df["IRCA (%)"].mean(),
            2
        )

        with col1:

            st.metric(
                label="IRCA promedio",
                value=f"{irca_prom}%"
            )

    # -------------------------
    # pH
    # -------------------------

    ph_prom = None

    if "pH" in df.columns:

        ph_prom = round(
            df["pH"].mean(),
            2
        )

        with col2:

            st.metric(
                label="pH promedio",
                value=ph_prom
            )

    # -------------------------
    # CLORO
    # -------------------------

    posibles_cloro = [
        "Cloro residual libre",
        "Cloro Residual Libre",
        "Cloro residual",
        "Cloro Residual"
    ]

    columna_cloro = None

    for c in posibles_cloro:
        if c in df.columns:
            columna_cloro = c
            break

    if columna_cloro:

        cloro_prom = round(
            df[columna_cloro].mean(),
            2
        )

        with col3:

            st.metric(
                label="Cloro residual",
                value=cloro_prom
            )

    # -------------------------
    # MUESTRAS
    # -------------------------

    with col4:

        st.metric(
            label="Muestras",
            value=len(df)
        )

    # =========================================================
    # KPIs SECUNDARIOS
    # =========================================================

    st.subheader("Indicadores Secundarios")

    col5, col6, col7, col8 = st.columns(4)

    # -------------------------
    # TURBIDEZ
    # -------------------------

    if "Turbidez" in df.columns:

        turbidez = round(
            df["Turbidez"].mean(),
            2
        )

        with col5:

            st.metric(
                "Turbidez promedio",
                turbidez
            )

    # -------------------------
    # CONDUCTIVIDAD
    # -------------------------

    if "Conductividad" in df.columns:

        conductividad = round(
            df["Conductividad"].mean(),
            2
        )

        with col6:

            st.metric(
                "Conductividad",
                conductividad
            )

    # -------------------------
    # E. COLI
    # -------------------------

    posibles_ecoli = [
        "E. coli",
        "E.coli",
        "Escherichia coli"
    ]

    ecoli_col = None

    for c in posibles_ecoli:
        if c in df.columns:
            ecoli_col = c
            break

    if ecoli_col:

        ecoli_detectado = (
            df[ecoli_col]
            .fillna(0)
            .astype(float)
            .gt(0)
            .sum()
        )

        with col7:

            st.metric(
                "Muestras con E. coli",
                ecoli_detectado
            )

    # -------------------------
    # RIESGO DOMINANTE
    # -------------------------

    if "Nivel de Riesgo" in df.columns:

        riesgo = (
            df["Nivel de Riesgo"]
            .mode()
            .iloc[0]
        )

        with col8:

            st.metric(
                "Riesgo dominante",
                riesgo
            )

    # =========================================================
    # ALERTAS
    # =========================================================

    st.subheader("Estado del Sistema")

    if irca_prom is not None:

        if irca_prom <= 5:

            st.success(
                "Estado general: SIN RIESGO"
            )

        elif irca_prom <= 14:

            st.warning(
                "Estado general: RIESGO BAJO"
            )

        elif irca_prom <= 35:

            st.warning(
                "Estado general: RIESGO MEDIO"
            )

        else:

            st.error(
                "Estado general: RIESGO ALTO"
            )

    # =========================================================
    # GAUGES
    # =========================================================

    st.subheader("Gauges")

    g1, g2 = st.columns(2)

    # =========================================================
    # GAUGE IRCA
    # =========================================================

    if irca_prom is not None:

        with g1:

            fig_irca = go.Figure(go.Indicator(

                mode="gauge+number",

                value=irca_prom,

                title={
                    "text": "IRCA (%)"
                },

                gauge={

                    "axis": {
                        "range": [0, 100]
                    },

                    "steps": [

                        {
                            "range": [0, 5],
                            "color": "green"
                        },

                        {
                            "range": [5, 14],
                            "color": "yellow"
                        },

                        {
                            "range": [14, 35],
                            "color": "orange"
                        },

                        {
                            "range": [35, 100],
                            "color": "red"
                        }
                    ]
                }
            ))

            st.plotly_chart(
                fig_irca,
                use_container_width=True
            )

    # =========================================================
    # GAUGE pH
    # =========================================================

    if ph_prom is not None:

        with g2:

            fig_ph = go.Figure(go.Indicator(

                mode="gauge+number",

                value=ph_prom,

                title={
                    "text": "pH"
                },

                gauge={

                    "axis": {
                        "range": [0, 14]
                    },

                    "steps": [

                        {
                            "range": [0, 6.5],
                            "color": "red"
                        },

                        {
                            "range": [6.5, 8.5],
                            "color": "green"
                        },

                        {
                            "range": [8.5, 14],
                            "color": "orange"
                        }
                    ]
                }
            ))

            st.plotly_chart(
                fig_ph,
                use_container_width=True
            )

    # =========================================================
    # SERIES TEMPORALES
    # =========================================================

    st.subheader("Series Temporales")

    columnas_numericas = list(df_num.columns)

    if len(columnas_numericas) > 0:

        variable = st.selectbox(
            "Seleccionar variable",
            columnas_numericas
        )

        if (
            "Fecha de Muestreo" in df.columns
            and variable in df.columns
        ):

            fig = px.line(
                df,
                x="Fecha de Muestreo",
                y=variable,
                title=f"{variable} en el tiempo",
                markers=True
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # =========================================================
    # HISTOGRAMA
    # =========================================================

    st.subheader("Distribución de Variables")

    if len(columnas_numericas) > 0:

        variable_hist = st.selectbox(
            "Variable distribución",
            columnas_numericas,
            key="histograma"
        )

        fig_hist = px.histogram(
            df,
            x=variable_hist,
            nbins=30,
            title=f"Distribución de {variable_hist}"
        )

        st.plotly_chart(
            fig_hist,
            use_container_width=True
        )

    # =========================================================
    # TABLA FINAL
    # =========================================================

    with st.expander("Ver datos"):

        st.dataframe(
            df,
            use_container_width=True
        )