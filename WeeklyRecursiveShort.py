
# ==============================================================================
# APLICACIÓN STREAMLIT SIMPLIFICADA PARA PRONÓSTICO DE INDUSTRIA
# ==============================================================================

import streamlit as st
import pandas as pd
import joblib
import os
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Pronóstico de Industria",
    page_icon="🏭",
    layout="centered"
)

# --- FUNCIÓN PARA CARGAR EL MODELO DE INDUSTRIA ---
@st.cache_resource
def cargar_modelo_industria(directorio='mejores_modelos'):
    """Carga únicamente el modelo para INDUSTRIA."""
    ruta_modelo = os.path.join(directorio, 'forecaster_INDUSTRIA.joblib')
    try:
        if os.path.exists(ruta_modelo):
            modelo = joblib.load(ruta_modelo)
            return modelo
        else:
            return None
    except Exception as e:
        st.error(f"Error al cargar el modelo de INDUSTRIA: {e}")
        return None

# --- CARGA DEL MODELO AL INICIAR LA APP ---
forecaster_industria = cargar_modelo_industria()

if forecaster_industria is None:
    st.error(
        "Error Crítico: No se encontró el archivo 'forecaster_INDUSTRIA.joblib' en la carpeta 'mejores_modelos'. "
        "Asegúrate de que la carpeta y el modelo estén en el repositorio de GitHub."
    )
    st.stop()

# --- INTERFAZ DE USUARIO ---
st.title("🏭 Pronóstico Semanal de Ventas: Total Industria")
st.write("Selecciona los parámetros para la semana que deseas predecir.")

# --- FORMULARIO DE ENTRADA ---
with st.form("prediction_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        current_year = datetime.now().year
        selected_year = st.selectbox("Año:", list(range(current_year, current_year + 5)))
    with col2:
        selected_month = st.selectbox("Mes:", list(range(1, 13)))
    with col3:
        selected_week = st.selectbox("Semana del Mes:", list(range(1, 6)))

    col4, col5 = st.columns(2)
    with col4:
        dias_habiles = st.number_input("Días Hábiles:", min_value=0, max_value=7, value=5, step=1)
    with col5:
        presupuesto_semanal = st.number_input("Presupuesto (Ton):", min_value=0.0, value=500.0, step=50.0)
    
    submit_button = st.form_submit_button(label="🚀 Generar Pronóstico")

# --- LÓGICA DE PREDICCIÓN ---
if submit_button:
    exog_futuro = pd.DataFrame({
        'Hábil': [dias_habiles],
        'Presupuesto (Ton)': [presupuesto_semanal]
    })

    st.header(f"Resultado del Pronóstico")
    
    with st.spinner('Generando predicción...'):
        try:
            prediccion = forecaster_industria.predict(steps=1, exog=exog_futuro)
            valor_predicho = prediccion.iloc[0]
            
            st.metric(
                label=f"Venta Pronosticada para INDUSTRIA (Semana {selected_week} de {selected_month}/{selected_year})",
                value=f"{valor_predicho:,.2f} Toneladas"
            )
            
        except Exception as e:
            st.error(f"Ocurrió un error durante la predicción: {e}")

else:
    st.info("Completa los parámetros y haz clic en 'Generar Pronóstico'.")
