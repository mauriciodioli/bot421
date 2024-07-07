document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('savePromotionBtnModificaPromocion').addEventListener('click', () => {
        const id = document.querySelector('.modificar-promocion[data-id]').getAttribute('data-id');
        const price = document.getElementById('promotionPrice').value;
        const description = document.getElementById('promotionDescription').value;
        const discount = document.getElementById('promotionDiscount').value;
        const reason = document.getElementById('promotionReason').value;
        const state = document.getElementById('promotionStatus').value;
        const currency_id = document.getElementById('promotionCurrency').value;
        const cluster = document.getElementById('promotionCluster').value;

        const data = {
            id: id,
            precio: price,
            descripcion: description,
            descuento: discount,
            razon: reason,
            estado: state,
            moneda: currency_id,
            cluster: cluster
        };

        fetch('/productosComerciales_promociones_modifica_promocionesSinPlan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
            } else {
                // Actualizar la tabla con las promociones recibidas
                updateTablePromociones(data.promociones);
                // Cerrar el modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalModificaPromocion'));
                modal.hide();
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});