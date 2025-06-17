# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 18:41:19 2025

@author: jahop
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Configuración inicial de la página
st.set_page_config(
    page_title="Portafolio Analítico - Javier Pérez",
    page_icon="🏥",
    layout="wide"
)

# --- SECCIÓN DE PRESENTACIÓN ---
st.markdown("""
# Javier Horacio Pérez Ricárdez  
### Portafolio Analítico para Vacante: **Analista de Datos / Transformación Data-Driven**  
**Hospital Gea González**  
            
[🔗 Enlace a la vacante en LinkedIn](https://www.linkedin.com/posts/alfredo-mora-pav%C3%B3n-161319103_datadriven-geadn-activity-7340417322370646016-0-kY/?utm_source=share&utm_medium=member_android&rcm=ACoAABBZ75cBBjwb62_VCQMrYD9W6dCuwPkGJP8)  

📌 **Contacto:**  
- 📧 jahoperi@gmail.com  
- 📱 +52 56 1056 4095  
---
""")

# --- SIMULACIÓN DE DATOS HOSPITALARIOS ---
@st.cache_data
def generar_datos_simulados():
    """Genera datos simulados para demostración analítica"""
    np.random.seed(42)
    dates = pd.date_range(start='2025-01-01', periods=100)
    areas = ['Urgencias', 'Cardiología', 'Oncología', 'Pediatría', 'Neurología']
    
    data = {
        'Fecha': np.random.choice(dates, 1000),
        'Área': np.random.choice(areas, 1000, p=[0.3, 0.2, 0.15, 0.2, 0.15]),
        'Pacientes': np.random.poisson(5, 1000),
        'Ocupación %': np.clip(np.random.normal(70, 15, 1000), 40, 100),
        'Tiempo Espera (min)': np.clip(np.random.exponential(30, 1000), 5, 180)
    }
    
    df = pd.DataFrame(data)
    df['Prioridad'] = pd.cut(df['Tiempo Espera (min)'], 
                            bins=[0, 15, 45, 180],
                            labels=['Alta', 'Media', 'Baja'])
    return df

df = generar_datos_simulados()

# --- INTERFAZ PRINCIPAL ---
st.title("🏥 Dashboard Analítico para Gestión Hospitalaria")
st.markdown("""
Este dashboard interactivo demuestra capacidades analíticas aplicables al sector salud, 
mostrando KPIs relevantes, tendencias temporales y distribución de recursos.  
*Datos simulados para fines demostrativos.*
""")

# --- BARRA LATERAL CON FILTROS ---
with st.sidebar:
    st.header("⚙️ Panel de Control")
    
    
    # Filtros de fecha con validación
    fecha_min, fecha_max = df['Fecha'].min(), df['Fecha'].max()
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha inicio", 
                                   value=fecha_min,
                                   min_value=fecha_min,
                                   max_value=fecha_max)
    with col2:
        fecha_fin = st.date_input("Fecha fin", 
                                value=fecha_max,
                                min_value=fecha_min,
                                max_value=fecha_max)
    
    # Validación de rango de fechas
    if fecha_inicio > fecha_fin:
        st.error("Error: Fecha inicio debe ser anterior a fecha fin")
        st.stop()
    
    # Filtros adicionales
    areas_disponibles = sorted(df['Área'].unique())
    area_select = st.multiselect("Áreas médicas", 
                               options=areas_disponibles,
                               default=areas_disponibles)
    
    prioridades = ['Alta', 'Media', 'Baja']
    prioridad_select = st.multiselect("Nivel de prioridad", 
                                    options=prioridades,
                                    default=prioridades)

# --- PROCESAMIENTO DE DATOS ---
df_filtered = df[
    (df['Fecha'] >= pd.to_datetime(fecha_inicio)) &
    (df['Fecha'] <= pd.to_datetime(fecha_fin)) &
    (df['Área'].isin(area_select)) &
    (df['Prioridad'].isin(prioridad_select))
]

# Cálculo de métricas clave
total_pacientes = df_filtered['Pacientes'].sum()
ocupacion_promedio = df_filtered['Ocupación %'].mean()
tiempo_espera_promedio = df_filtered['Tiempo Espera (min)'].mean()

# --- SECCIÓN DE KPI ---
st.subheader("📊 Indicadores Clave de Desempeño")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Pacientes atendidos", 
             f"{total_pacientes:,}", 
             help="Total de pacientes en el período seleccionado")
with col2:
    delta_ocupacion = ocupacion_promedio - 70  # Comparación con referencia
    st.metric("Ocupación promedio", 
             f"{ocupacion_promedio:.1f}%", 
             delta=f"{delta_ocupacion:.1f}% vs referencia",
             help="Porcentaje promedio de ocupación hospitalaria")
with col3:
    st.metric("Tiempo espera promedio", 
             f"{tiempo_espera_promedio:.1f} min", 
             help="Tiempo de espera promedio de pacientes")

# Alertas basadas en umbrales
if ocupacion_promedio > 85:
    st.warning("🚨 Alta ocupación: Considerar protocolos de contingencia")
elif ocupacion_promedio < 50:
    st.info("ℹ️ Ocupación baja: Oportunidad para optimizar recursos")

# --- VISUALIZACIONES ---
st.subheader("📈 Tendencias Temporales")
tab1, tab2, tab3 = st.tabs(["Ocupación", "Pacientes", "Tiempos de espera"])

with tab1:
    fig, ax = plt.subplots(figsize=(10, 4))
    ocupacion_diaria = df_filtered.groupby('Fecha')['Ocupación %'].mean()
    ax.plot(ocupacion_diaria.index, ocupacion_diaria.values, 
           color='#1f77b4', linewidth=2, marker='o', markersize=5)
    
    ax.axhline(y=85, color='r', linestyle='--', alpha=0.5, label='Umbral crítico')
    ax.axhline(y=70, color='g', linestyle='--', alpha=0.5, label='Objetivo')
    
    ax.set_title("Ocupación Hospitalaria Diaria", pad=20)
    ax.set_ylabel("Ocupación (%)")
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax.grid(True, alpha=0.3)
    ax.legend()
    st.pyplot(fig)

with tab2:
    fig, ax = plt.subplots(figsize=(10, 4))
    pacientes_diarios = df_filtered.groupby('Fecha')['Pacientes'].sum()
    ax.bar(pacientes_diarios.index, pacientes_diarios.values, 
          color='#2ca02c', alpha=0.7)
    
    ax.set_title("Pacientes Atendidos Diariamente", pad=20)
    ax.set_ylabel("Número de Pacientes")
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

with tab3:
    fig, ax = plt.subplots(figsize=(10, 4))
    espera_diaria = df_filtered.groupby('Fecha')['Tiempo Espera (min)'].mean()
    ax.plot(espera_diaria.index, espera_diaria.values, 
           color='#ff7f0e', linewidth=2)
    
    ax.axhline(y=45, color='r', linestyle='--', alpha=0.5, label='Umbral crítico')
    
    ax.set_title("Tiempo de Espera Promedio", pad=20)
    ax.set_ylabel("Minutos")
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax.grid(True, alpha=0.3)
    ax.legend()
    st.pyplot(fig)

# --- ANÁLISIS POR ÁREA ---
st.subheader("🏨 Distribución por Área Médica")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Pacientes por área**")
    pacientes_area = df_filtered.groupby('Área')['Pacientes'].sum().sort_values()
    
    fig, ax = plt.subplots()
    pacientes_area.plot(kind='barh', ax=ax, color='#17becf')
    ax.set_xlabel("Número de Pacientes")
    ax.set_ylabel("")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

with col2:
    st.markdown("**Ocupación promedio por área**")
    ocupacion_area = df_filtered.groupby('Área')['Ocupación %'].mean().sort_values()
    
    fig, ax = plt.subplots()
    ocupacion_area.plot(kind='barh', ax=ax, color='#9467bd')
    ax.set_xlabel("Ocupación (%)")
    ax.set_ylabel("")
    ax.axvline(x=85, color='r', linestyle='--', alpha=0.5)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

# --- DATOS DETALLADOS ---
with st.expander("🔍 Ver datos detallados"):
    st.dataframe(
        df_filtered.sort_values(by='Fecha').style\
            .background_gradient(subset=['Ocupación %'], cmap='YlOrRd')\
            .bar(subset=['Tiempo Espera (min)'], color='#d65f5f'),
        height=300
    )

# --- CONCLUSIÓN ---
st.markdown("""
---
### 🎯 Sobre esta Demostración

Este dashboard muestra capacidades en:
- **Análisis de datos sanitarios** con KPIs relevantes
- **Visualización efectiva** para toma de decisiones
- **Detección de patrones** y alertas tempranas
- **Herramientas modernas** (Python, Streamlit, Pandas)

Estoy entusiasmado por la oportunidad de contribuir con estas habilidades al **Hospital Gea González** 
en su transformación data-driven.

**Javier Horacio Pérez Ricárdez**  
📧 jahoperi@gmail.com | 📱 +52 56 1056 4095  
""")