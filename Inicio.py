import pandas as pd
import streamlit as st
from PIL import Image
from datetime import datetime

# =========================================================
# CONFIGURACIÓN DE LA PÁGINA
# =========================================================

st.set_page_config(
    page_title="Sistema de Monitoreo de Calidad del Aire",
    page_icon="🌫️",
    layout="wide"
)

# =========================================================
# ESTILOS CSS
# =========================================================

st.markdown("""
<style>

/* Fondo principal */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(to bottom right, #0f2027, #203a43, #2c5364);
    color: white;
}

/* Texto general */
html, body, [class*="css"]  {
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

/* Títulos */
h1, h2, h3 {
    color: #7CFC00;
}

/* Métricas */
[data-testid="metric-container"] {
    background-color: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 15px;
    border-radius: 12px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-size: 16px;
    padding: 10px;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    background-color: rgba(255,255,255,0.03);
}

/* Alertas */
.stAlert {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TÍTULO PRINCIPAL
# =========================================================

st.title("🌫️ Sistema de Monitoreo de Calidad del Aire")

st.markdown("""
Monitoreo y análisis de concentraciones de gases mediante sensores ESP32  
instalados en la Universidad EAFIT, Medellín.
""")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙️ Panel de Control")

st.sidebar.info("""
Proyecto de monitoreo ambiental usando sensores IoT.

Variables:
- Gas_PPM
- Gas_Raw
""")

# =========================================================
# MAPA
# =========================================================

eafit_location = pd.DataFrame({
    'lat': [6.2006],
    'lon': [-75.5783]
})

st.subheader("📍 Ubicación de la Estación de Monitoreo")
st.map(eafit_location, zoom=15)

# =========================================================
# CARGA DE ARCHIVO
# =========================================================

uploaded_file = st.file_uploader(
    "📂 Seleccione archivo CSV",
    type=["csv"]
)

# =========================================================
# PROCESAMIENTO
# =========================================================

if uploaded_file is not None:

    try:

        df1 = pd.read_csv(uploaded_file)

        # =====================================================
        # CONVERSIÓN DE FECHA
        # =====================================================

        if 'Time' in df1.columns:
            df1['Time'] = pd.to_datetime(df1['Time'])
            df1 = df1.set_index('Time')

        # =====================================================
        # VALIDACIÓN DE COLUMNAS
        # =====================================================

        expected_columns = ['Gas_PPM', 'Gas_Raw']

        missing_columns = [
            col for col in expected_columns
            if col not in df1.columns
        ]

        if missing_columns:
            st.error(f"❌ Faltan columnas en el CSV: {missing_columns}")
            st.stop()

        # =====================================================
        # MÉTRICAS PRINCIPALES
        # =====================================================

        st.subheader("📊 Métricas Generales")

        col1, col2, col3, col4 = st.columns(4)

        avg_ppm = df1['Gas_PPM'].mean()
        max_ppm = df1['Gas_PPM'].max()
        min_ppm = df1['Gas_PPM'].min()
        avg_raw = df1['Gas_Raw'].mean()

        col1.metric("PPM Promedio", f"{avg_ppm:.2f}")
        col2.metric("PPM Máximo", f"{max_ppm:.2f}")
        col3.metric("PPM Mínimo", f"{min_ppm:.2f}")
        col4.metric("RAW Promedio", f"{avg_raw:.2f}")

        # =====================================================
        # ALERTAS
        # =====================================================

        if avg_ppm > 400:
            st.error("🚨 Niveles peligrosos de gas detectados")
        elif avg_ppm > 200:
            st.warning("⚠️ Niveles elevados de gas")
        else:
            st.success("✅ Calidad del aire estable")

        # =====================================================
        # TABS
        # =====================================================

        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Monitoreo",
            "🧪 Análisis",
            "🎛️ Filtros",
            "📍 Estación"
        ])

        # =====================================================
        # TAB 1 - MONITOREO
        # =====================================================

        with tab1:

            st.subheader("📈 Visualización de Datos")

            chart_type = st.selectbox(
                "Seleccione tipo de gráfico",
                ["Línea", "Área", "Barra"]
            )

            if chart_type == "Línea":
                st.line_chart(df1[["Gas_PPM", "Gas_Raw"]])

            elif chart_type == "Área":
                st.area_chart(df1[["Gas_PPM", "Gas_Raw"]])

            else:
                st.bar_chart(df1[["Gas_PPM", "Gas_Raw"]])

            if st.checkbox("Mostrar datos crudos"):
                st.dataframe(df1)

        # =====================================================
        # TAB 2 - ANÁLISIS
        # =====================================================

        with tab2:

            st.subheader("🧪 Análisis Estadístico")

            stats_ppm = df1["Gas_PPM"].describe()
            stats_raw = df1["Gas_Raw"].describe()

            col1, col2 = st.columns(2)

            with col1:
                st.write("### Estadísticas Gas_PPM")
                st.dataframe(stats_ppm)

            with col2:
                st.write("### Estadísticas Gas_Raw")
                st.dataframe(stats_raw)

        # =====================================================
        # TAB 3 - FILTROS
        # =====================================================

        with tab3:

            st.subheader("🎛️ Filtros de Datos")

            min_value = float(df1["Gas_PPM"].min())
            max_value = float(df1["Gas_PPM"].max())

            filtro = st.slider(
                "Seleccione rango de PPM",
                min_value=min_value,
                max_value=max_value,
                value=(min_value, max_value)
            )

            filtrado_df = df1[
                (df1["Gas_PPM"] >= filtro[0]) &
                (df1["Gas_PPM"] <= filtro[1])
            ]

            st.write(f"Registros filtrados: {len(filtrado_df)}")
            st.dataframe(filtrado_df)

            # Descarga
            csv = filtrado_df.to_csv().encode('utf-8')

            st.download_button(
                label="⬇️ Descargar datos filtrados",
                data=csv,
                file_name='datos_filtrados.csv',
                mime='text/csv',
            )

        # =====================================================
        # TAB 4 - INFORMACIÓN
        # =====================================================

        with tab4:

            st.subheader("📍 Información de la Estación")

            col1, col2 = st.columns(2)

            with col1:

                st.write("### 📌 Ubicación")

                st.write("""
                **Universidad EAFIT**
                
                - Ciudad: Medellín
                - Latitud: 6.2006
                - Longitud: -75.5783
                - Altitud: ~1495 msnm
                """)

            with col2:

                st.write("### 🔧 Sensor")

                st.write("""
                - Microcontrolador: ESP32
                - Variables medidas:
                    - Gas_PPM
                    - Gas_Raw
                - Tipo de sistema: IoT
                - Frecuencia: Tiempo real
                """)

    except Exception as e:

        st.error(f"❌ Error al procesar el archivo: {str(e)}")

        st.info("""
        Verifique que el archivo CSV tenga:

        - Columna Time
        - Columna Gas_PPM
        - Columna Gas_Raw
        """)

# =========================================================
# MENSAJE SI NO HAY ARCHIVO
# =========================================================

else:

    st.warning("📂 Por favor cargue un archivo CSV para comenzar el análisis.")

# =========================================================
# FOOTER
# =========================================================

st.markdown("""
---
🌫️ Sistema de Monitoreo Ambiental IoT  
📍 Universidad EAFIT — Medellín, Colombia  
🛰️ Proyecto académico de análisis de calidad del aire
""")
