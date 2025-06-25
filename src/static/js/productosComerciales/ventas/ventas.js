
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
                console.log("Respuesta de la API:", data);
                // Rellenamos la fila con los datos
                fila.innerHTML = `                   
                    <td>${detalle.nombre_producto}</td>
                    <td>${detalle.cantidad}</td>                   
                    <td>${detalle.precio_unitario}</td>
                     <td style="color: yellow; font-weight: bold;">${detalle.subtotal}</td>
                `;
        
                // Añadimos la fila al cuerpo del modal
                cuerpoModal.appendChild(fila);
            });
        
            // Referencia al contenedor de detalles adicionales (fuera de la tabla)
            const contenedorAdicional = document.getElementById("detallePedidoExtras");
            contenedorAdicional.innerHTML = ""; // Limpiar contenido previo
        
            // Mostrar el total del pedido
            const total = document.createElement("p");

            total.innerHTML = `<strong">Total del pedido:</strong> <span style="color: #90EE90;; font-weight: bold;">$ ${data.total}</span>`;
            contenedorAdicional.appendChild(total);
        
            // Mostrar la consulta del cliente
            const consulta = document.createElement("p");
            consulta.innerHTML = `<strong>Consulta del cliente:</strong> ${data.consulta}`;
            contenedorAdicional.appendChild(consulta);
        
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






















function actualizarEstado(pedidoId, checkbox) { 
    const nuevoEstado = checkbox.checked ? 'entregado' : 'pendiente'; // Cambia según tu lógica de estados
    console.log(`Pedido ID: ${pedidoId}, Nuevo Estado: ${nuevoEstado}`);
    
    fetch(`/productosComerciales_pedidos_ventasProductosComerciales_actualizarEstado_pedido/${pedidoId}`, {
        method: 'POST',  // Cambiar a POST
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ estado: nuevoEstado })  // Asegúrate de enviar el estado en el cuerpo
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Estado actualizado');
            // Encontramos la fila a la que queremos aplicar el estilo
            const fila = checkbox.closest('tr'); // Esto selecciona la fila más cercana al checkbox
            console.log("Fila seleccionada:", fila);  // Muestra toda la fila en consola

            // Asegúrate de que estamos seleccionando la fila correcta
            if (fila) {
                const estadoCelda = fila.querySelector('td:nth-child(4)'); // Suponiendo que el estado es la 4ta columna
                if (estadoCelda) {
                    estadoCelda.textContent = nuevoEstado;

                    if (nuevoEstado === 'entregado') {
                        estadoCelda.style.backgroundColor = '#90EE90'; // Verde claro
                        estadoCelda.style.color = 'black';  // Aseguramos que el texto sea visible
                    } else {
                        estadoCelda.style.backgroundColor = ''; // Restaurar el color original si no está entregado
                        estadoCelda.style.color = '';  // Restaurar el color del texto
                    }
                } else {
                    console.error("No se encontró la celda de estado.");
                }
            } else {
                console.error("No se encontró la fila.");
            }
        } else {
            alert('No se pudo actualizar el estado');
        }
    })
    .catch(error => {
        console.error('Error al actualizar el estado:', error);
        alert('Hubo un error al actualizar el estado');
    });
}



// Función para mostrar los datos del cliente
function datosDelCliente(pedidoId) {
    // Obtener los datos del cliente relacionado con el pedido
    fetch(`/productosComerciales_pedidos_ventasProductosComerciales_DatosDelCliente_pedido/${pedidoId}`)
        .then(response => response.json())
        .then(data => {
            if (data.detalles) {
                const cliente = data.detalles[0];  // Suponiendo que 'detalles' es una lista con un único objeto
                alert(`Datos del cliente:\nNombre: ${cliente.nombreCliente} \nApellido: ${cliente.apellidoCliente}\nTeléfono: ${cliente.telefonoCliente}\nEmail: ${cliente.emailCliente}`);
            } else {
                alert('No se encontraron datos del cliente');
            }
        })
        .catch(error => {
            console.error('Error al obtener los datos del cliente:', error);
            alert('Hubo un error al obtener los datos del cliente');
        });
}



function cancelarPedido(pedidoId) {
    debugger;

    fetch(`/productosComerciales_pedidos_ventasProductosComerciales_cancela_pedido/${pedidoId}`, {
        method: 'POST', // Método de la solicitud
        headers: {
            'Content-Type': 'application/json', // Tipo de contenido
        },
        body: JSON.stringify({ pedidoId: pedidoId }) // Datos que se envían en el cuerpo (si los necesitas)
    })
    .then(response => response.json())  // Convertir la respuesta a JSON
    .then(data => {
        if (data.success) {
            alert("Pedido cancelado exitosamente");
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error al cancelar el pedido:', error);
        alert("Hubo un error al intentar cancelar el pedido");
    });
}







// Función para abrir el modal con el id del pedido
// Función para abrir el modal con el id del pedido
function comentarDescripcionalCliente(cluster_id) {
    // Guardar el id del pedido en una variable global
    window.cluster_id = cluster_id;
    // Abrir el modal
    var myModal = new bootstrap.Modal(document.getElementById('modalComentario'));
    myModal.show();
  }
  
  // Función para enviar el comentario por AJAX
  function enviarComentario() {
    // Obtener el texto del comentario
    var respuesta = document.getElementById('comentarioText').value;  // Cambié 'comentario' por 'respuesta'
    // Obtener el access_token desde el localStorage
    var accessToken = localStorage.getItem('access_token');
    
    // Verificar que el comentario y el token estén presentes
    if (!respuesta || !accessToken) {
      alert('Por favor, ingresa una respuesta y asegúrate de estar autenticado.');
      return;
    }
  
    // Enviar la solicitud AJAX para modificar la respuesta del pedido
    $.ajax({
      url: '/productosComerciales_pedidos_ventasProductosComerciales_actualizarRespuesta_pedido/',  // Reemplaza con la URL correcta
      type: 'POST',
      data: {
        cluster_id: window.cluster_id,
        respuesta: respuesta,  // Cambié 'comentario' por 'respuesta'
        access_token_form_Ventas: accessToken  // Asegúrate de que el nombre del campo coincida
      },
      success: function(response) {
        // Aquí puedes manejar la respuesta del servidor
        alert('Respuesta enviada correctamente');
        // Cerrar el modal
        var myModal = bootstrap.Modal.getInstance(document.getElementById('modalComentario'));
        myModal.hide();
      },
      error: function(xhr, status, error) {
        // Manejar cualquier error de la solicitud
        alert('Hubo un error al enviar la respuesta');
      }
    });
  }
  
  





















// Función para recargar la tabla
function recargarTabla() {
    const data = new FormData();
    let access_token = localStorage.getItem("access_token");
    var ambito = localStorage.getItem("dominio");
    data.append('access_token_form_Ventas', access_token);
    data.append('ambito_form_Ventas', ambito);

    fetch('/productosComerciales_pedidos_recargaAutomatica_muestra/', {
        method: 'POST',
        body: data
    })
    .then(response => response.json())
    .then(pedidos => {
        const tabla = document.getElementById("tablaPedidosEntrega");  // Actualizado a 'tablaPedidosEntrega'
        tabla.innerHTML = '';  // Limpiar la tabla

        pedidos.forEach(pedido => {
            const fila = document.createElement("tr");
            fila.innerHTML = `
                <td>${pedido.fecha_entrega}</td>
                <td>${pedido.nombreCliente}</td>
                <td>${pedido.lugar_entrega}</td>
                <td>${pedido.estado}</td>
                <td style="color: rgb(232, 232, 95); font-weight: bold;">$ ${pedido.precio_venta}</td>
                <td>
                    <input type="checkbox" class="estado-checkbox" onchange="actualizarEstado(${pedido.id}, this)" 
                           ${pedido.estado === 'entregado' ? 'checked' : ''}>
                </td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="mostrarDetalles(${pedido.id})">
                        Detalle
                    </button>
                    <button class="btn btn-primary btn-sm" onclick="datosDelCliente(${pedido.id})">
                        Cliente
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="cancelarPedido(${pedido.id})">
                        Cancelar
                    </button>
                </td>
            `;
            tabla.appendChild(fila);
        });
    })
    .catch(error => {
        console.error('Error al recargar la tabla:', error);
    });
}

// Recargar la tabla cada 2 minutos (120,000 ms)
setInterval(recargarTabla, 120000);




