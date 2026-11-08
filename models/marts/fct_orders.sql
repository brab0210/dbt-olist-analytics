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
        o.delivered_to_customer_at,
        COALESCE(SUM(i.item_price), 0) AS total_item_price,
        COALESCE(SUM(i.freight_value), 0) AS total_freight_value,
        COALESCE(SUM(i.item_price), 0) + COALESCE(SUM(i.freight_value), 0) AS total_order_value,
        
        -- NUEVO: Calculamos los días que tardó la entrega (si es que ya fue entregado)
        DATEDIFF(day, o.purchased_at, o.delivered_to_customer_at) AS delivery_days
        
    FROM orders o
    LEFT JOIN order_items i 
        ON o.order_id = i.order_id
    GROUP BY 
        o.order_id,
        o.customer_id,
        o.order_status,
        o.purchased_at,
        o.delivered_to_customer_at -- Tenemos que agregarlo al GROUP BY
)

SELECT * FROM final