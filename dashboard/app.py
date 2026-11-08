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

# --- ATENCIÓN ACÁ: Tu catálogo y esquema ---
CATALOG = "workspace"
SCHEMA = "olist_raw" # Modificá esto si tus tablas de dbt están en otro esquema

# --- Consultas SQL a las tablas de dbt ---

# 1. KPIs principales (Agregamos el promedio de días de entrega)
query_kpis = f"""
    SELECT 
        SUM(total_order_value) as ingresos_totales,
        COUNT(order_id) as total_pedidos,
        AVG(total_order_value) as ticket_promedio,
        AVG(delivery_days) as promedio_dias_entrega
    FROM {CATALOG}.{SCHEMA}.fct_orders
    WHERE order_status = 'delivered'
"""

# 2. Evolución mensual
query_ventas_mes = f"""
    SELECT 
        DATE_TRUNC('month', purchased_at) as mes,
        SUM(total_order_value) as ingresos
    FROM {CATALOG}.{SCHEMA}.fct_orders
    WHERE order_status = 'delivered' AND purchased_at IS NOT NULL
    GROUP BY 1
    ORDER BY 1
"""

# 3. Top 10 categorías
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

# 4. Medios de pago (NUEVO)
query_pagos = f"""
    SELECT 
        payment_type as medio_pago,
        COUNT(*) as cantidad,
        SUM(payment_value) as total_recaudado
    FROM {CATALOG}.{SCHEMA}.fct_payments
    GROUP BY 1
    ORDER BY 2 DESC
"""

# 5. Ventas por estado (NUEVO)
query_estados = f"""
    SELECT 
        c.state as estado,
        SUM(o.total_order_value) as ingresos
    FROM {CATALOG}.{SCHEMA}.fct_orders o
    JOIN {CATALOG}.{SCHEMA}.dim_customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1
    ORDER BY 2 DESC
"""

# --- Carga de datos ---
try:
    with st.spinner("Cargando datos desde Databricks..."):
        df_kpis = load_data(query_kpis)
        df_ventas = load_data(query_ventas_mes)
        df_categorias = load_data(query_categorias)
        df_pagos = load_data(query_pagos)
        df_estados = load_data(query_estados)
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
    st.stop()

# --- KPIs Principales ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.info(f"**Ingresos Totales**\n\n### ${df_kpis['ingresos_totales'][0]:,.2f}")
with col2:
    st.info(f"**Pedidos Entregados**\n\n### {df_kpis['total_pedidos'][0]:,}")
with col3:
    st.info(f"**Ticket Promedio**\n\n### ${df_kpis['ticket_promedio'][0]:,.2f}")
with col4:
    # Si el promedio es nulo (porque no hay entregas), mostramos 0
    dias_entrega = df_kpis['promedio_dias_entrega'][0] if pd.notnull(df_kpis['promedio_dias_entrega'][0]) else 0
    st.info(f"**Días Promedio de Entrega**\n\n### {dias_entrega:.1f} días")

st.divider()

# --- Fila 1: Evolución y Categorías ---
col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader(" Evolución de Ingresos")
    fig_ventas = px.line(df_ventas, x="mes", y="ingresos", markers=True,
                         labels={"mes": "Fecha", "ingresos": "Ingresos (BRL)"})
    st.plotly_chart(fig_ventas, use_container_width=True)

with col_der:
    st.subheader(" Top 10 Categorías")
    fig_categorias = px.bar(df_categorias, x="ingresos", y="categoria", orientation='h',
                            labels={"ingresos": "Ingresos (BRL)", "categoria": "Categoría"},
                            color="ingresos", color_continuous_scale="Blues")
    fig_categorias.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_categorias, use_container_width=True)

# --- Fila 2: Pagos y Estados ---
st.divider()
col_pagos, col_estados = st.columns(2)

with col_pagos:
    st.subheader(" Medios de Pago")
    fig_pagos = px.pie(df_pagos, values="cantidad", names="medio_pago", 
                       title="Distribución de métodos de pago",
                       hole=0.4) # Gráfico de dona
    st.plotly_chart(fig_pagos, use_container_width=True)

with col_estados:
    st.subheader(" Ventas por Estado")
    # Mostramos el Top 10 de estados para no amontonar el gráfico
    fig_estados = px.bar(df_estados.head(10), x="estado", y="ingresos",
                         labels={"estado": "Estado", "ingresos": "Ingresos (BRL)"},
                         color="ingresos", color_continuous_scale="Teal")
    st.plotly_chart(fig_estados, use_container_width=True)
