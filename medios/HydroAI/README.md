# Dashboard IRCA

Sistema interactivo para monitoreo y análisis de calidad del agua.

## Características

- Monitoreo temporal
- KPIs
- Gauges
- Mapas interactivos
- Predicción mediante regresión múltiple
- Correlaciones Pearson y Spearman
- Sistema de alertas
- Exportación de reportes
- Arquitectura modular

---

# Estructura

```bash
dashboard-irca/
│
├── app.py
│
├── modules/
│   ├── monitoreo.py
│   ├── mapas.py
│   ├── prediccion.py
│   ├── analisis.py
│   ├── alertas.py
│   ├── reportes.py
│   └── iot.py
│
├── assets/
│
├── data/
│
├── requirements.txt
│
└── README.md