import streamlit as st
import pandas as pd
import pydeck as pdk


# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================

def mostrar_mapas(df):

    st.title("Mapas de Calidad del Agua")

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
    # COORDENADAS
    # =========================================================

    coordenadas = {

        "Punto 1": {
            "Latitud": 7.271090,
            "Longitud": -72.641962
        },

        "Punto 2": {
            "Latitud": 7.265819,
            "Longitud": -72.640164
        },

        "Punto 3": {
            "Latitud": 7.264164,
            "Longitud": -72.641296
        },

        "Punto 4": {
            "Latitud": 7.268910,
            "Longitud": -72.644666
        },

        "Punto 5": {
            "Latitud": 7.271786,
            "Longitud": -72.646355
        }
    }

    # =========================================================
    # ASIGNAR COORDENADAS
    # =========================================================

    posibles_puntos = [
        "Punto de Toma",
        "Punto de Muestreo",
        "Lugar"
    ]

    columna_punto = None

    for c in posibles_puntos:

        if c in df.columns:
            columna_punto = c
            break

    if columna_punto is None:

        st.error(
            "No se encontró columna de puntos"
        )

        return

    # =========================================================
    # MAPEO
    # =========================================================

    df["Latitud"] = df[columna_punto].map(
        lambda x: coordenadas.get(
            str(x).strip(),
            {}
        ).get("Latitud")
    )

    df["Longitud"] = df[columna_punto].map(
        lambda x: coordenadas.get(
            str(x).strip(),
            {}
        ).get("Longitud")
    )

    # =========================================================
    # LIMPIEZA
    # =========================================================

    df = df.dropna(
        subset=["Latitud", "Longitud"]
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

    columnas_numericas = list(
        df.select_dtypes(include="number").columns
    )

    columnas_excluir = [
        "Latitud",
        "Longitud"
    ]

    columnas_numericas = [

        c for c in columnas_numericas

        if c not in columnas_excluir
    ]

    # =========================================================
    # SELECTOR VARIABLE
    # =========================================================

    st.subheader("Visualización Espacial")

    variable = st.selectbox(
        "Seleccionar variable",
        columnas_numericas
    )

    # =========================================================
    # NORMALIZACIÓN
    # =========================================================

    df[variable] = pd.to_numeric(
        df[variable],
        errors="coerce"
    )

    df = df.dropna(
        subset=[variable]
    )

    # =========================================================
    # COLORES AUTOMÁTICOS
    # =========================================================

    vmin = df[variable].min()
    vmax = df[variable].max()

    if vmax == vmin:
        vmax = vmin + 1

    df["norm"] = (
        (df[variable] - vmin)
        /
        (vmax - vmin)
    )

    # =========================================================
    # ESCALA DE COLOR
    # =========================================================

    df["color_r"] = (
        df["norm"] * 255
    ).astype(int)

    df["color_g"] = (
        150 - (df["norm"] * 100)
    ).clip(0, 255).astype(int)

    df["color_b"] = (
        255 - (df["norm"] * 255)
    ).astype(int)

    # =========================================================
    # RADIO
    # =========================================================

    radio = st.slider(
        "Tamaño de puntos",
        100,
        3000,
        800
    )

    # =========================================================
    # CENTRO MAPA
    # =========================================================

    lat_media = df["Latitud"].mean()
    lon_media = df["Longitud"].mean()

    # =========================================================
    # CAPA
    # =========================================================

    layer = pdk.Layer(

        "ScatterplotLayer",

        data=df,

        get_position="[Longitud, Latitud]",

        get_fill_color="""
        [color_r, color_g, color_b, 180]
        """,

        get_radius=radio,

        pickable=True,

        auto_highlight=True
    )

    # =========================================================
    # TOOLTIP
    # =========================================================

    tooltip = {

        "html": f"""

        <b>Punto:</b> {{{columna_punto}}} <br/>

        <b>{variable}:</b>
        {{{variable}}}

        """,

        "style": {

            "backgroundColor": "steelblue",

            "color": "white"
        }
    }

    # =========================================================
    # VIEW STATE
    # =========================================================

    view_state = pdk.ViewState(

        latitude=lat_media,

        longitude=lon_media,

        zoom=13,

        pitch=40
    )

    # =========================================================
    # MAPA
    # =========================================================

    deck = pdk.Deck(

        map_style="mapbox://styles/mapbox/light-v9",

        initial_view_state=view_state,

        layers=[layer],

        tooltip=tooltip
    )

    # =========================================================
    # MOSTRAR
    # =========================================================

    st.pydeck_chart(
        deck,
        use_container_width=True
    )

    # =========================================================
    # KPIs ESPACIALES
    # =========================================================

    st.subheader("Indicadores Espaciales")

    col1, col2, col3 = st.columns(3)

    # =========================================================
    # PUNTOS
    # =========================================================

    with col1:

        st.metric(
            "Puntos",
            len(df)
        )

    # =========================================================
    # PROMEDIO
    # =========================================================

    with col2:

        promedio = round(
            df[variable].mean(),
            2
        )

        st.metric(
            f"Promedio {variable}",
            promedio
        )

    # =========================================================
    # MÁXIMO
    # =========================================================

    with col3:

        maximo = round(
            df[variable].max(),
            2
        )

        st.metric(
            f"Máximo {variable}",
            maximo
        )

    # =========================================================
    # TABLA
    # =========================================================

    with st.expander("Ver datos geográficos"):

        columnas_mostrar = [

            columna_punto,

            "Latitud",

            "Longitud",

            variable
        ]

        st.dataframe(
            df[columnas_mostrar],
            use_container_width=True
        )