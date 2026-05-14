import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# =========================================================
# FUNCIÓN PDF
# =========================================================

def generar_pdf(df, resumen):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    elementos = []

    estilos = getSampleStyleSheet()

    # =====================================================
    # TÍTULO
    # =====================================================

    titulo = Paragraph(
        "Reporte de Calidad del Agua",
        estilos["Title"]
    )

    elementos.append(titulo)

    elementos.append(
        Spacer(1, 20)
    )

    # =====================================================
    # RESUMEN
    # =====================================================

    subtitulo = Paragraph(
        "Resumen Estadístico",
        estilos["Heading2"]
    )

    elementos.append(subtitulo)

    elementos.append(
        Spacer(1, 10)
    )

    # =====================================================
    # TABLA RESUMEN
    # =====================================================

    datos_tabla = [
        ["Indicador", "Valor"]
    ]

    for k, v in resumen.items():

        datos_tabla.append([
            str(k),
            str(v)
        ])

    tabla = Table(datos_tabla)

    tabla.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.grey
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.whitesmoke
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                1,
                colors.black
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            )
        ])
    )

    elementos.append(tabla)

    elementos.append(
        Spacer(1, 20)
    )

    # =====================================================
    # DATOS
    # =====================================================

    subtitulo2 = Paragraph(
        "Primeras muestras",
        estilos["Heading2"]
    )

    elementos.append(subtitulo2)

    elementos.append(
        Spacer(1, 10)
    )

    # =====================================================
    # TABLA DATOS
    # =====================================================

    muestra = df.head(10)

    datos = [
        list(muestra.columns)
    ]

    for _, row in muestra.iterrows():

        datos.append(
            [str(x) for x in row.values]
        )

    tabla2 = Table(datos)

    tabla2.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightblue
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                1,
                colors.black
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            )
        ])
    )

    elementos.append(tabla2)

    # =====================================================
    # CONSTRUIR PDF
    # =====================================================

    doc.build(elementos)

    buffer.seek(0)

    return buffer


# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================

def mostrar_reportes(df):

    st.title("Reportes")

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
    # FILTROS
    # =========================================================

    st.sidebar.subheader("Filtros")

    # =========================================================
    # AÑO
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
    # COLUMNAS NUMÉRICAS
    # =========================================================

    df_num = df.select_dtypes(include="number")

    # =========================================================
    # RESUMEN
    # =========================================================

    st.subheader("Resumen General")

    resumen = {}

    resumen["Muestras"] = len(df)

    resumen["Variables Numéricas"] = len(
        df_num.columns
    )

    # =========================================================
    # IRCA
    # =========================================================

    posibles_irca = [
        "IRCA (%)",
        "IRCA"
    ]

    for c in posibles_irca:

        if c in df.columns:

            resumen["IRCA Promedio"] = round(
                df[c].mean(),
                2
            )

            resumen["IRCA Máximo"] = round(
                df[c].max(),
                2
            )

            break

    # =========================================================
    # pH
    # =========================================================

    if "pH" in df.columns:

        resumen["pH Promedio"] = round(
            df["pH"].mean(),
            2
        )

    # =========================================================
    # KPIs
    # =========================================================

    col1, col2, col3, col4 = st.columns(4)

    valores = list(resumen.values())
    claves = list(resumen.keys())

    for i, col in enumerate([
        col1,
        col2,
        col3,
        col4
    ]):

        if i < len(valores):

            with col:

                st.metric(
                    claves[i],
                    valores[i]
                )

    # =========================================================
    # ESTADÍSTICA
    # =========================================================

    st.subheader("Estadística Descriptiva")

    descripcion = df_num.describe().T

    st.dataframe(
        descripcion,
        use_container_width=True
    )

    # =========================================================
    # VARIABLE
    # =========================================================

    st.subheader("Visualización")

    if len(df_num.columns) > 0:

        variable = st.selectbox(
            "Variable",
            df_num.columns
        )

        # =====================================================
        # HISTOGRAMA
        # =====================================================

        fig = px.histogram(

            df,

            x=variable,

            nbins=30,

            title=f"Distribución de {variable}"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # =====================================================
        # TEMPORAL
        # =====================================================

        if "Fecha de Muestreo" in df.columns:

            fig2 = px.line(

                df,

                x="Fecha de Muestreo",

                y=variable,

                markers=True,

                title=f"{variable} en el tiempo"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

    # =========================================================
    # EXPORTAR CSV
    # =========================================================

    st.subheader("Exportar Datos")

    csv = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(

        label="Descargar CSV",

        data=csv,

        file_name="reporte.csv",

        mime="text/csv"
    )

    # =========================================================
    # EXPORTAR EXCEL
    # =========================================================

    excel_buffer = BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Datos"
        )

        descripcion.to_excel(
            writer,
            sheet_name="Estadistica"
        )

    excel_buffer.seek(0)

    st.download_button(

        label="Descargar Excel",

        data=excel_buffer,

        file_name="reporte.xlsx",

        mime="""
        application/vnd.openxmlformats-officedocument
        .spreadsheetml.sheet
        """
    )

    # =========================================================
    # EXPORTAR PDF
    # =========================================================

    pdf = generar_pdf(
        df,
        resumen
    )

    st.download_button(

        label="Descargar PDF",

        data=pdf,

        file_name="reporte.pdf",

        mime="application/pdf"
    )

    # =========================================================
    # DATOS
    # =========================================================

    with st.expander("Ver datos"):

        st.dataframe(
            df,
            use_container_width=True
        )