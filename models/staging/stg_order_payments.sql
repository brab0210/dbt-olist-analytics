WITH source AS (
    SELECT * FROM {{ source('olist', 'olist_order_payments_dataset') }}
),

renamed AS (
    SELECT
        order_id,
        TRY_CAST(payment_sequential AS INT) AS payment_sequential,
        payment_type,
        TRY_CAST(payment_installments AS INT) AS payment_installments,
        TRY_CAST(payment_value AS DOUBLE) AS payment_value
    FROM source
)

SELECT * FROM renamed