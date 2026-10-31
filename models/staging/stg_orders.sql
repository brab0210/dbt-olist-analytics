-- stg_orders.sql
WITH source AS (
    -- Acá usamos la función source() para llamar a la tabla cruda
    SELECT * FROM {{ source('olist', 'olist_orders_dataset') }}
),

renamed AS (
    SELECT
        order_id,
        customer_id,
        order_status,
        -- Casteamos las fechas de texto a Timestamp
        TRY_CAST(order_purchase_timestamp AS TIMESTAMP) AS purchased_at,
        TRY_CAST(order_approved_at AS TIMESTAMP) AS approved_at,
        TRY_CAST(order_delivered_carrier_date AS TIMESTAMP) AS delivered_to_carrier_at,
        TRY_CAST(order_delivered_customer_date AS TIMESTAMP) AS delivered_to_customer_at,
        TRY_CAST(order_estimated_delivery_date AS TIMESTAMP) AS estimated_delivery_at
    FROM source
    WHERE order_id IS NOT NULL
),
deduplicated AS (
    SELECT *,
           ROW_NUMBER() OVER(PARTITION BY order_id ORDER BY purchased_at DESC) as rn
    FROM renamed
)
SELECT * EXCEPT(rn)
FROM deduplicated
WHERE rn = 1