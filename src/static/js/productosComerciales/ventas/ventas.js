
// Función para mostrar el modal con los detalles
function mostrarDetalles(pedidoId) {
    fetch(`/productosComerciales_pedidos_ventasProductosComerciales_detalle_pedido/${pedidoId}`)
        .then((response) => response.json())
        .then(data => {
            // Referencia al cuerpo del modal
            const cuerpoModal = document.getElementById("detallePedidoBody");
            cuerpoModal.innerHTML = ""; // Limpiar el contenido previo del modal
    
            // Recorremos cada detalle en la respuesta
            data.detalles.forEach((detalle) => {
                // Creamos una fila para cada detalle
                const fila = document.createElement("tr");
    
                // Rellenamos la fila con los datos
                fila.innerHTML = `                   
                    <td>${detalle.nombre_producto}</td>
                    <td>${detalle.cantidad}</td>
                    <td>${detalle.consulta}</td>
                    <td>${detalle.precio_unitario}</td>
                    <td>${detalle.total}</td>
                   
                `;
                
                // Añadimos la fila al cuerpo del modal
                cuerpoModal.appendChild(fila);
            });
    
            // Mostramos el modal
            const modal = new bootstrap.Modal(document.getElementById("modalDetallePedido"));
            modal.show();
        })
        .catch((err) => console.error("Error:", err));
}






function filtrarTabla() {
    debugger;
    const filtroFecha = document.getElementById("filtroFecha").value.toLowerCase();
    const filtroNombre = document.getElementById("filtroNombre").value.toLowerCase();
    const filtroDireccion = document.getElementById("filtroDireccion").value.toLowerCase();
    const filtroTelefono = document.getElementById("filtroTelefono").value.toLowerCase();
    const filtroCorreo = document.getElementById("filtroCorreo").value.toLowerCase();
    const filtroEstado = document.getElementById("filtroEstado").value.toLowerCase();

    const filas = document.querySelectorAll("#tablaPedidosEntrega tr");

    filas.forEach(function(fila) {
        const fecha = fila.cells[0].innerText.toLowerCase();
        const nombre = fila.cells[1].innerText.toLowerCase();
        const direccion = fila.cells[2].innerText.toLowerCase();
        const telefono = fila.cells[3].innerText.toLowerCase();
        const correo = fila.cells[4].innerText.toLowerCase();
        const estado = fila.cells[5].innerText.toLowerCase();

        // Mostrar o ocultar filas basadas en el filtro
        if (
            (filtroFecha === "" || fecha.includes(filtroFecha)) &&
            (filtroNombre === "" || nombre.includes(filtroNombre)) &&
            (filtroDireccion === "" || direccion.includes(filtroDireccion)) &&
            (filtroTelefono === "" || telefono.includes(filtroTelefono)) &&
            (filtroCorreo === "" || correo.includes(filtroCorreo)) &&
            (filtroEstado === "" || estado.includes(filtroEstado))
        ) {
            fila.style.display = "";
        } else {
            fila.style.display = "none";
        }
    });
}























// Función para actualizar el estado del pedido
function ActualizarEstado(pedidoId) {
    // Aquí puedes hacer una solicitud para actualizar el estado del pedido
    fetch(`/actualizarEstado/${pedidoId}`, {
        method: 'POST',
        body: JSON.stringify({ estado: 'nuevo_estado' }), // Cambia el estado según lo que desees
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': 'token_de_seguridad_aqui' // Si estás usando CSRF Token para seguridad
        }
    })
    .then(response => response.json())
    .then(data => {
        alert('Estado actualizado');
        // Aquí puedes recargar la página o actualizar la interfaz de usuario
        location.reload();
    })
    .catch(error => {
        console.error('Error al actualizar el estado:', error);
        alert('Hubo un error al actualizar el estado');
    });
}

// Función para cancelar un pedido
function cancelarPedido(pedidoId) {
    // Confirmar si el usuario realmente quiere cancelar el pedido
    if (confirm('¿Estás seguro de que deseas cancelar este pedido?')) {
        fetch(`/cancelarPedido/${pedidoId}`, {
            method: 'POST',
            body: JSON.stringify({ estado: 'cancelado' }), // Cambia el estado o agrega lo necesario
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': 'token_de_seguridad_aqui' // Si estás usando CSRF Token
            }
        })
        .then(response => response.json())
        .then(data => {
            alert('Pedido cancelado');
            // Aquí puedes recargar la página o actualizar la interfaz de usuario
            location.reload();
        })
        .catch(error => {
            console.error('Error al cancelar el pedido:', error);
            alert('Hubo un error al cancelar el pedido');
        });
    }
}

// Función para mostrar los datos del cliente
function datosDelCliente(pedidoId) {
    // Obtener los datos del cliente relacionado con el pedido
    fetch(`/datosCliente/${pedidoId}`)
        .then(response => response.json())
        .then(data => {
            // Aquí puedes mostrar los datos del cliente en un modal o en un área específica de tu página
            alert(`Datos del cliente: ${data.nombreCliente}, ${data.telefonoCliente}, ${data.emailCliente}`);
        })
        .catch(error => {
            console.error('Error al obtener los datos del cliente:', error);
            alert('Hubo un error al obtener los datos del cliente');
        });
}
