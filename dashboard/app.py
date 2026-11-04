import streamlit as st
import pandas as pd
import plotly.express as px
from databricks import sql

st.set_page_config(page_title="Olist Analytics", page_icon="🛍️", layout="wide")

st.title("🛍️ Olist E-Commerce Dashboard")
st.markdown("Análisis de ventas y logística basado en el modelo dimensional de dbt.")

# --- Configuración de la conexión ---
def get_databricks_connection():
    return sql.connect(
        server_hostname=st.secrets["DATABRICKS_HOST"],
        http_path=st.secrets["DATABRICKS_HTTP_PATH"],
        access_token=st.secrets["DATABRICKS_TOKEN"]
    )

@st.cache_resource(ttl=300)
def get_cached_connection():
    return get_databricks_connection()

@st.cache_data(ttl=600)
def load_data(query):
    try:
        conn = get_cached_connection()
        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(result, columns=columns)
    except Exception:
        st.cache_resource.clear()
        conn = get_cached_connection()
        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(result, columns=columns)

# --- ATENCIÓN ACÁ: Definí tu catálogo y esquema ---
# Cambiá "workspace" por tu catálogo real, y "dbt_olist" por el esquema donde dbt guardó las tablas (fijate en Databricks)
CATALOG = "workspace"
SCHEMA = "olist_raw" # <-- Modificá esto si tus tablas de dbt están en otro esquema (ej. olist_raw)

# --- Consultas SQL a las tablas de dbt ---
query_kpis = f"""
    SELECT 
        SUM(total_order_value) as ingresos_totales,
        COUNT(order_id) as total_pedidos,
        AVG(total_order_value) as ticket_promedio
    FROM {CATALOG}.{SCHEMA}.fct_orders
    WHERE order_status = 'delivered'
"""

query_ventas_mes = f"""
    SELECT 
        DATE_TRUNC('month', purchased_at) as mes,
        SUM(total_order_value) as ingresos
    FROM {CATALOG}.{SCHEMA}.fct_orders
    WHERE order_status = 'delivered' AND purchased_at IS NOT NULL
    GROUP BY 1
    ORDER BY 1
"""

# Para las categorías, unimos la tabla de hechos de items (usamos staging) con la dimensión de productos
query_categorias = f"""
    SELECT 
        p.category_name as categoria,
        SUM(i.item_price) as ingresos
    FROM {CATALOG}.{SCHEMA}.stg_order_items i
    JOIN {CATALOG}.{SCHEMA}.dim_products p ON i.product_id = p.product_id
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 10
"""

# --- Carga de datos ---
try:
    df_kpis = load_data(query_kpis)
    df_ventas = load_data(query_ventas_mes)
    df_categorias = load_data(query_categorias)
except Exception as e:
    st.error(f"Error al conectar con las tablas de dbt: {e}")
    st.stop()

# --- KPIs Principales ---
 
""" col1.metric("Ingresos Totales", f"${df_kpis['ingresos_totales'][0]:,.2f}")
col2.metric("Pedidos Entregados", f"{df_kpis['total_pedidos'][0]:,}")
col3.metric("Ticket Promedio", f"${df_kpis['ticket_promedio'][0]:,.2f}") """
col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"**Ingresos Totales**\n\n### ${df_kpis['ingresos_totales'][0]:,.2f}")
with col2:
    st.info(f"**Pedidos Entregados**\n\n### {df_kpis['total_pedidos'][0]:,}")
with col3:
    st.info(f"**Ticket Promedio**\n\n### ${df_kpis['ticket_promedio'][0]:,.2f}")

st.divider()

# --- Gráficos ---
col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("📈 Evolución de Ingresos")
    fig_ventas = px.line(df_ventas, x="mes", y="ingresos", markers=True,
                         labels={"mes": "Fecha", "ingresos": "Ingresos (BRL)"})
    st.plotly_chart(fig_ventas, use_container_width=True)

with col_der:
    st.subheader("🏆 Top 10 Categorías")
    fig_categorias = px.bar(df_categorias, x="ingresos", y="categoria", orientation='h',
                            labels={"ingresos": "Ingresos (BRL)", "categoria": "Categoría"},
                            color="ingresos", color_continuous_scale="Blues")
    # Damos vuelta el eje Y para que la categoría más vendida quede arriba
    fig_categorias.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_categorias, use_container_width=True)