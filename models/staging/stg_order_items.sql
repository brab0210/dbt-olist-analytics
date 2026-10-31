WITH source AS (
    SELECT * FROM {{ source('olist', 'olist_order_items_dataset') }}
),
renamed AS (
    SELECT
        order_id,
        order_item_id,
        product_id,
        seller_id,
        TRY_CAST(shipping_limit_date AS TIMESTAMP) AS shipping_limit_at,
        TRY_CAST(price AS DOUBLE) AS item_price,
        TRY_CAST(freight_value AS DOUBLE) AS freight_value
    FROM source
)
SELECT * FROM renamed