$(document).ready(function() {
    $('#savePromotionBtnAgregarPromocion').click(function() {
        const promotionData = {
            precio: $('#promotionPrice').val(),
            descripcion: $('#promotionDescription').val(),
            descuento: $('#promotionDiscount').val(),
            razon: $('#promotionReason').val(),
            estado: $('#promotionStatus').val(),         
            moneda: $('#promotionCurrency').val()
        };

        $.ajax({
            url: '/productosComerciales_promociones_agrega_promocionesSinPlan',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(promotionData),
            success: function(response) {
                alert('Promoción agregada exitosamente');
                $('#modalAgregarPromocionSinPlan').modal('hide');
            },
            error: function(error) {
                alert('Error al agregar promoción');
            }
        });
    });
});