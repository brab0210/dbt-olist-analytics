#  Olist Analytics Pipeline (dbt + Databricks + Streamlit)

Este proyecto implementa un pipeline de datos end-to-end para el dataset público de e-commerce de **Olist (Brasil)**. Los datos se transforman utilizando **dbt (data build tool)** sobre Databricks (Unity Catalog) y se visualizan en un dashboard interactivo construido con **Streamlit**.

 **[Ver Dashboard en Vivo](https://dbt-olist-analytics-k9tt9jdwsgyec7q27astkf.streamlit.app/)**

---

##  Arquitectura y Modelado

El pipeline sigue el estándar de dbt para organizar las transformaciones en capas:

1. **Staging (`stg_`):** Limpieza, casteo de tipos de datos (`TRY_CAST`) y estandarización de nombres de columnas.
2. **Marts (`dim_` y `fct_`):** Modelado dimensional (Esquema Estrella) listo para ser consumido por herramientas de BI.

### Modelo Estrella (Star Schema)
*   **Dimensiones:**
    *   `dim_customers`: Información demográfica y ubicación de los clientes.
    *   `dim_products`: Catálogo de productos y categorías.
*   **Tablas de Hechos:**
    *   `fct_orders`: Resumen financiero por pedido (ingresos por ítems + envío) y cálculo de días de entrega (`delivery_days`).
    *   `fct_payments`: Detalle transaccional de los pagos realizados.

##  Características del Dashboard (Streamlit)

El dashboard conecta en tiempo real a Databricks para consumir los modelos de dbt y presenta:
*   **KPIs Generales:** Ingresos totales, pedidos entregados, ticket promedio y días promedio de entrega (logística).
*   **Evolución de Ingresos:** Gráfico de líneas temporales de las ventas.
*   **Top 10 Categorías:** Ranking de las categorías de productos más vendidas.
*   **Medios de Pago:** Distribución de los métodos de pago utilizados por los clientes.
*   **Ventas por Estado:** Análisis geográfico de los ingresos por provincia de Brasil.

##  Calidad de Datos (Data Quality)

El proyecto incluye **tests automáticos de dbt** para garantizar la integridad del pipeline antes de que los datos lleguen a producción:
*   `unique` y `not_null` en todas las claves primarias (evita duplicados y valores vacíos).
*   Uso de `ROW_NUMBER()` para deduplicar pedidos en la capa de Staging.
*   Uso de `COALESCE` para manejar pedidos sin ítems y evitar nulos en las sumatorias.

##  Tecnologías Utilizadas

*   **Transformación:** dbt Cloud
*   **Data Warehouse:** Databricks (SQL Warehouse, Unity Catalog)
*   **Visualización:** Streamlit (Community Cloud), Plotly, Pandas
*   **Lenguajes:** SQL analítico (Spark SQL), Python
*   **Control de versiones:** Git / GitHub

##  Estructura del Repositorio

```text
dbt-olist-analytics/
│
├── dashboard/                 # Código de la aplicación Streamlit
│   ├── app.py                 # Lógica de visualización y consultas
│   └── requirements.txt       # Dependencias de la app
│
├── models/                    # Modelos de dbt
│   ├── staging/               # Modelos de limpieza inicial (stg_)
│   └── marts/                 # Modelos dimensionales (dim_ y fct_)
│
├── tests/                     # Tests personalizados
├── dbt_project.yml            # Configuración del proyecto dbt
├── .gitignore                 # Excluye archivos sensibles (.streamlit/secrets.toml)
└── README.md                  # Este archivo
