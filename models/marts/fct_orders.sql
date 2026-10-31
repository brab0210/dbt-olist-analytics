WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

order_items AS (
    SELECT * FROM {{ ref('stg_order_items') }}
),

final AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_status,
        o.purchased_at,
        -- Usamos COALESCE para que si la suma da NULL, ponga un 0
        COALESCE(SUM(i.item_price), 0) AS total_item_price,
        COALESCE(SUM(i.freight_value), 0) AS total_freight_value,
        COALESCE(SUM(i.item_price), 0) + COALESCE(SUM(i.freight_value), 0) AS total_order_value
    FROM orders o
    LEFT JOIN order_items i 
        ON o.order_id = i.order_id
    GROUP BY 
        o.order_id,
        o.customer_id,
        o.order_status,
        o.purchased_at
)

SELECT * FROM final