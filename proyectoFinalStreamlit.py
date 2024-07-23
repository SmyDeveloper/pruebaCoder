import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Fitness Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv('C:/Users/admin/OneDrive/Documentos/aprende_programando/dataAnalitycsConPython/dashboardfitness/dailyActivity_merged.csv')
    df['ActivityDate'] = pd.to_datetime(df['ActivityDate'])
    return df

df = load_data()

st.title('Dashboard Completo de Fitness')

# Sidebar para filtros
st.sidebar.header('Filtros')
date_range = st.sidebar.date_input('Rango de fechas', [df['ActivityDate'].min(), df['ActivityDate'].max()])
metric = st.sidebar.selectbox('Métrica principal', ['TotalSteps', 'TotalDistance', 'Calories'])

# Filtrar datos
mask = (df['ActivityDate'] >= pd.to_datetime(date_range[0])) & (df['ActivityDate'] <= pd.to_datetime(date_range[1]))
filtered_df = df.loc[mask]

# Layout principal
col1, col2 = st.columns([2, 1])


with col1:
    st.subheader(f'Tendencia de {metric}')
    
    # Agregar los datos por día
    daily_avg = filtered_df.groupby('ActivityDate')[metric].mean().reset_index()

    # Crear el gráfico
    fig = px.bar(daily_avg, x='ActivityDate', y=metric,
                 title=f'Promedio diario de {metric}',
                 labels={'ActivityDate': 'Fecha', metric: 'Valor promedio'})

    # Añadir una línea de tendencia
    fig.add_trace(go.Scatter(x=daily_avg['ActivityDate'], 
                             y=daily_avg[metric].rolling(window=7).mean(), 
                             mode='lines', 
                             name='Tendencia (promedio móvil de 7 días)',
                             line=dict(color='red', width=2)))

    # Ajustar el diseño
    fig.update_layout(xaxis_range=[daily_avg['ActivityDate'].min(), daily_avg['ActivityDate'].max()])

    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader('Distribución de Actividad')
    activity_data = filtered_df[['VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes', 'SedentaryMinutes']].sum()
    fig_pie = px.pie(values=activity_data.values, names=activity_data.index)
    st.plotly_chart(fig_pie, use_container_width=True)

# Métricas resumidas
st.subheader('Métricas Clave')
col1, col2, col3, col4 = st.columns(4)
col1.metric("Promedio de Pasos", f"{filtered_df['TotalSteps'].mean():.0f}")
col2.metric("Promedio de Distancia", f"{filtered_df['TotalDistance'].mean():.2f} km")
col3.metric("Promedio de Calorías", f"{filtered_df['Calories'].mean():.0f}")
col4.metric("Días Activos", f"{len(filtered_df)}")

# Heatmap de actividad semanal
st.subheader('Patrón de Actividad Semanal')
df_heatmap = filtered_df.groupby([filtered_df['ActivityDate'].dt.dayofweek, filtered_df['ActivityDate'].dt.hour])[metric].mean().unstack()
fig_heatmap = px.imshow(df_heatmap, labels=dict(x="Hora del día", y="Día de la semana", color=metric),
                        x=df_heatmap.columns, y=['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'])
st.plotly_chart(fig_heatmap, use_container_width=True)

# Tabla de datos
st.subheader('Datos Detallados')
st.dataframe(filtered_df)