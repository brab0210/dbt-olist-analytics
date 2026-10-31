WITH payments AS (
    SELECT * FROM {{ ref('stg_order_payments') }}
)

SELECT
    -- Creamos una llave única para cada pago (porque un pedido puede tener varios pagos)
    CONCAT(order_id, '-', CAST(payment_sequential AS STRING)) AS payment_id,
    order_id,
    payment_type,
    payment_installments,
    payment_value
FROM payments