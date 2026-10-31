-- Si esto devuelve filas, significa que hay order_id repetidos en la fuente
SELECT order_id, COUNT(*) as cantidad
FROM {{ ref('stg_orders') }}
GROUP BY order_id
HAVING COUNT(*) > 1

-- Revisamos si hay órdenes que no tienen ítems asociados
SELECT 
    o.order_id, 
    o.order_status,
    SUM(i.item_price) as total_item,
    SUM(i.freight_value) as total_freight
FROM {{ ref('stg_orders') }} o
LEFT JOIN {{ ref('stg_order_items') }} i ON o.order_id = i.order_id
GROUP BY o.order_id, o.order_status
HAVING SUM(i.item_price) IS NULL