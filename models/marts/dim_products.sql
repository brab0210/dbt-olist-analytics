WITH products AS (
    SELECT * FROM {{ ref('stg_products') }}
)

SELECT
    product_id,
    -- Si la categoría viene vacía (NULL), le ponemos 'unknown' para no tener problemas en los reportes
    COALESCE(category_name, 'unknown') AS category_name,
    weight_g,
    length_cm,
    height_cm,
    width_cm
FROM products