
# ==============================================================================
# APLICACIÓN DE STREAMLIT PARA EL PRONÓSTICO SEMANAL DE VENTAS (VERSIÓN FINAL)
# ==============================================================================

import streamlit as st
import pandas as pd
import joblib
import os
from datetime import datetime
import io
import warnings

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Pronóstico Semanal de Ventas",
    page_icon="📈",
    layout="wide"
)

# --- ESTRUCTURA JERÁRQUICA DEL NEGOCIO (ACTUALIZADA) ---
HIERARCHY = {
    'INDUSTRIA': [],
    'SALES': [],
    'QUIMICOS': []
}
DISPLAY_ORDER = [
    'INDUSTRIA', 'SALES', 'QUIMICOS'
]

# --- FUNCIÓN PARA CARGAR MODELOS ---
@st.cache_resource
def cargar_modelos(directorio='mejores_modelos'):
    """Carga todos los modelos .joblib de un directorio."""
    modelos = {}
    if not os.path.exists(directorio):
        return None # Devuelve None si la carpeta no existe

    for filename in os.listdir(directorio):
        if filename.endswith('.joblib'):
            segmento = filename.replace('forecaster_', '').replace('.joblib', '')
            ruta_completa = os.path.join(directorio, filename)
            try:
                modelos[segmento] = joblib.load(ruta_completa)
            except Exception as e:
                st.warning(f"No se pudo cargar el modelo '{filename}'. Error: {e}")
    return modelos

# --- CARGA DE MODELOS AL INICIAR LA APP ---
modelos_cargados = cargar_modelos()

if not modelos_cargados:
    st.error(
        "Error Crítico: La carpeta 'mejores_modelos' no fue encontrada o está vacía. "
        "Asegúrate de que esta carpeta y los archivos .joblib estén en el repositorio de GitHub junto a este script."
    )
    st.stop()

# --- INTERFAZ DE USUARIO ---
st.title("📈 Pronóstico Semanal de Ventas")
st.write("Selecciona los parámetros para la semana que deseas predecir.")

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
        dias_habiles = st.number_input("Días Hábiles en la Semana:", min_value=0, max_value=7, value=5, step=1)
    with col5:
        presupuesto_semanal = st.number_input("Presupuesto para la Semana (Ton):", min_value=0.0, value=500.0, step=50.0)

    submit_button = st.form_submit_button(label="🚀 Generar Pronóstico")

if submit_button:
    exog_futuro = pd.DataFrame({
        'Hábil': [dias_habiles],
        'Presupuesto (Ton)': [presupuesto_semanal]
    })

    st.header(f"Resultados del Pronóstico para la Semana {selected_week} de {selected_month}/{selected_year}")

    resultados = []

    for item in DISPLAY_ORDER:
        if item in modelos_cargados:
            forecaster = modelos_cargados[item]
            try:
                prediccion = forecaster.predict(steps=1, exog=exog_futuro)
                valor_predicho = prediccion.iloc[0]

                nombre_agrupacion = item
                if item not in ['INDUSTRIA', 'SALES', 'QUIMICOS']:
                    nombre_agrupacion = f"    - {item}"

                resultados.append({'Agrupación': nombre_agrupacion, 'Venta (Ton)': valor_predicho})
            except Exception as e:
                st.error(f"Error al predecir para '{item}': {e}")
        else:
            st.warning(f"No se encontró un modelo para '{item}'. Se omitirá.")

    df_resultado = pd.DataFrame(resultados).set_index('Agrupación')

    def resaltar_totales(row):
        return ['font-weight: bold; background-color: #f2f2f2' if not row.name.strip().startswith('-') else '' for _ in row]

    df_resultado_styled = df_resultado.style.format("{:,.2f}").apply(resaltar_totales, axis=1)

    st.dataframe(df_resultado_styled, use_container_width=True)

    @st.cache_data
    def to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=True, sheet_name='Pronostico_Semanal')
        return output.getvalue()

    excel_data = to_excel(df_resultado)

    st.download_button(
        label="📥 Descargar Resultados en Excel",
        data=excel_data,
        file_name=f'pronostico_Y{selected_year}_M{selected_month}_W{selected_week}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

else:
    st.info("Completa los parámetros y haz clic en 'Generar Pronóstico' para ver los resultados.")

# --- SECCIÓN DE DEPURACIÓN (opcional) ---
with st.expander("Ver versiones de las librerías"):
    st.write("Versiones de las librerías importantes usadas en esta aplicación:")
    try:
        import skforecast, sklearn, lightgbm, xgboost
        st.write(f"- Streamlit: {st.__version__}")
        st.write(f"- Pandas: {pd.__version__}")
        st.write(f"- Joblib: {joblib.__version__}")
        st.write(f"- Skforecast: {skforecast.__version__}")
        st.write(f"- Scikit-learn: {sklearn.__version__}")
        st.write(f"- LightGBM: {lightgbm.__version__}")
        st.write(f"- XGBoost: {xgboost.__version__}")
    except Exception as e:
        st.write(f"No se pudieron cargar todas las versiones. Error: {e}")
