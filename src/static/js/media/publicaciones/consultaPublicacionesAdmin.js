document.addEventListener('DOMContentLoaded', function () {
    const localUserId = localStorage.getItem('usuario_id');

    // Mostrar u ocultar botones "Eliminar" según el user_id
    document.querySelectorAll('.remove-button').forEach(button => {
        const consultaUserId = button.getAttribute('data-user-id');

        if (localUserId === consultaUserId) {
            button.style.display = 'inline-block'; // Mostrar botón
        } else {
            button.style.display = 'none'; // Ocultar si no corresponde
        }

        // Añadir listener al botón
        button.addEventListener('click', function (e) {
            e.preventDefault();

            const publicacionId = this.getAttribute('data-consulta-id');
            const token = localStorage.getItem('access_token');
            const correo = localStorage.getItem('correo_electronico') || '';

            if (!token) {
                alert('Token no disponible. Inicia sesión nuevamente.');
                return;
            }

            if (!confirm('¿Estás seguro de que deseas eliminar esta publicación?')) {
                return;
            }

            const formData = new FormData();
            formData.append('publicacion_id', publicacionId);
            formData.append('correo_electronico', correo);

            fetch('/social_imagenes_eliminar_publicacion/', {
                method: 'POST',
                headers: {
                    'Authorization': 'Bearer ' + token
                },
                body: formData
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    const row = e.target.closest('tr');
                    if (row) row.remove();
                    mostrarMensaje('✅ Publicación eliminada con éxito.');
                } else {
                    mostrarMensaje('❌ Error al eliminar: ' + (result.error || 'desconocido'), 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarMensaje('❌ Error al enviar la solicitud.', 'danger');
            });
        });
    });
});

// Función para mostrar mensajes al usuario
function mostrarMensaje(mensaje, tipo = 'success') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${tipo} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    document.body.prepend(alert);

    setTimeout(() => {
        alert.remove();
    }, 4000);
}





// Obtener el modal
var modal = document.getElementById("detalleModal");

// Obtener el botón de cerrar
var span = document.getElementsByClassName("close")[0];

// Función para abrir el modal con los datos de la publicación
function mostrarDetalle(consultaId) {
    // Llamada AJAX para obtener los datos de la publicación
    fetch(`/obtener_detalle_publicacion/${consultaId}`)
        .then(response => response.json())
        .then(data => {
            // Rellenar el modal con los datos de la publicación
            document.getElementById('productoNombre').textContent = data.nombre_producto;
            document.getElementById('productoDescripcion').textContent = data.descripcion;
            document.getElementById('productoTexto').textContent = data.texto;
            document.getElementById('productoCorreo').textContent = data.correoElectronico;
            document.getElementById('productoFecha').textContent = data.fechaCreacion;
            document.getElementById('productoUserId').textContent = data.user_id;
            
            // Mostrar el modal
            modal.style.display = "block";
        })
        .catch(error => console.log("Error al obtener los datos:", error));
}

// Agregar el evento de clic para cada botón de "Detalle"
document.querySelectorAll('.detalleProducto').forEach(button => {
    button.addEventListener('click', function () {
        var consultaId = this.getAttribute('data-consulta-id');
        mostrarDetalle(consultaId);  // Llamada a la nueva función
    });
});

// Cuando el usuario hace clic en el botón de cerrar, cierra el modal
span.onclick = function () {
    modal.style.display = "none";
}

// Cuando el usuario hace clic fuera del modal, cierra el modal
window.onclick = function (event) {
    if (event.target === modal) {
        modal.style.display = "none";
    }
}
















$(document).ready(function() {
    // Función para realizar la búsqueda
    function realizarBusqueda() {
        var consulta = $('#consulta_publicaciones_data').val();
        var ambito = localStorage.getItem('dominio');
        var accessToken = localStorage.getItem('access_token');
        
        // Verifica si hay texto en el campo
        if (consulta.trim() !== "") {
            $.ajax({
                url: '/media_consultaPublicaciones_lupa_muestra/',  // URL de la ruta
                type: 'POST',
                data: {
                    consulta: consulta,  // Envía el texto de búsqueda al servidor
                    ambito: ambito,
                    accessToken: accessToken
                },
                success: function(response) {
                    // Verifica si hay datos en la respuesta
                    if (response.data && response.data.length > 0) {
                        var tableContent = '';
                        var total = 0;
                        var subtotal = 0;
                        
                        // Recorre los datos y construye el HTML de la tabla
                        response.data.forEach(function(consulta) {
                            subtotal += parseFloat(consulta.precio_venta) || 0;  // Sumar precios al subtotal
                            tableContent += `
                                <tr data-precio="${consulta.precio_venta}" data-id="${consulta.id}">
                                    <td>
                                        ${consulta.imagen_url ? 
                                            `<img src="${consulta.imagen_url}" alt="Imagen del producto" class="product-image">` : 
                                            `<img src="default.jpg" alt="Producto sin imagen" class="product-image">`}
                                    </td>
                                    <td class="text">${consulta.nombre_producto}</td>
                                    <td class="price">
                                        <span class="unit-price">${consulta.precio_venta}</span>
                                    </td>
                                    <td>
                                        <input type="number" id="quantity-${consulta.id}" name="quantity" class="quantity-input" value="1" min="1">
                                    </td>
                                    <td>
                                        <input type="checkbox" class="estado-checkbox" onchange="agregarListado(${consulta.id}, this)" 
                                               ${consulta.precio_venta === 'entregado' ? 'checked' : ''}>
                                    </td>
                                    <td>
                                        <button class="remove-button" data-consulta-id="${consulta.id}" data-user-id="${consulta.user_id}" style="display: none;">
                                            Eliminar
                                        </button>
                                    </td>
                                    <td>
                                        <button class="btn-success detalleProducto" data-consulta-id="${consulta.id}" data-user-id="${consulta.user_id}">
                                            Detalle
                                        </button>
                                    </td>
                                </tr>
                            `;
                        });
                        
                        // Calcular el total (esto depende de tu lógica)
                        total = subtotal;  // O ajusta según sea necesario
    
                        // Inserta el contenido generado en el contenedor de la tabla
                        $('.table-container tbody').html(tableContent);
                        
                        // Mostrar el resumen del carrito
                        var cartSummary = `...`; // El resumen del carrito sigue igual
                        $('.cart-summary-container').html(cartSummary);
                        
                        // Asignar el evento click a los botones "Detalle" después de que el contenido haya sido insertado
                        $('.detalleProducto').click(function() {
                            var consultaId = $(this).data('consulta-id');
                            var userId = $(this).data('user-id');
                            
                            // Llamar a la función para mostrar el modal
                            mostrarDetalle(consultaId, userId); 
                                                });
                        

                    } else {
                        console.log("No se encontraron publicaciones.");
                        $('.table-container tbody').html('<tr><td colspan="7">No se encontraron publicaciones.</td></tr>');
                        $('.cart-summary-container').html('');  // Ocultar el resumen si no hay datos
                    }
                },
                error: function(xhr, status, error) {
                    console.log('Error al realizar la búsqueda:', error);
                }
            });
        } else {
            console.log("Por favor ingrese una consulta.");
        }
    }
    
    // Llamar a la función cuando se hace clic en el ícono de lupa
    $('#search_button').click(function() {
        realizarBusqueda();
    });

    // También permitir la búsqueda presionando Enter
    $('#consulta_publicaciones_data').keypress(function(e) {
        if (e.which == 13) { // 13 es el código de la tecla Enter
            realizarBusqueda();
        }
    });
});
















function agregarListado(pedidoId, checkbox) { 
   
    if (!checkbox.checked) {
        console.log(`El pedido con ID ${pedidoId} no se enviará porque el checkbox no está marcado.`);
        return; // Salir de la función si el checkbox no está marcado
    }
    const nuevoEstado = checkbox.checked ? 'activo' : 'inactivo';  // Determinar el nuevo estado
    const access_token_btn_carrito1 = localStorage.getItem('access_token');
    const correo_electronico_cbox = localStorage.getItem('correo_electronico');
    const ambito_btn_carrito = localStorage.getItem('dominio');
    
    // Obtén el campo de cantidad usando el pedidoId
    const quantityInput = document.querySelector(`#quantity-${pedidoId}`);
    const cantidadSeleccionada = quantityInput ? quantityInput.value : null;

    console.log(`Pedido ID: ${pedidoId}, Nuevo Estado: ${nuevoEstado}, Cantidad: ${cantidadSeleccionada}`);
    
    
    fetch(`/productosComerciales_pedidos_alta_carrito_checkBox/${pedidoId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ estado: nuevoEstado,
            access_token_btn_carrito1: access_token_btn_carrito1,
            correo_electronico_cbox: correo_electronico_cbox,
            ambito_btn_carrito: ambito_btn_carrito,
            publicacion_id: pedidoId,
            cantidadCompra: cantidadSeleccionada, // Incluye la cantidad
            checkbox: checkbox.checked            
         })  // Enviar el estado en el cuerpo
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Agregado al carrito correctamente'); // Muestra el mensaje de éxito
        } else {
            alert(data.message || 'No se pudo actualizar el carrito'); // Muestra mensaje del servidor
        }
    })
    .catch(error => {
        console.error('Error al actualizar el carrito:', error);
        alert('Hubo un error al actualizar el carrito');
    });
}















// Pega este JS (una sola vez). Funciona aunque el botón se renderice después.
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.btn-cp');
  if (!btn) return;

  const pubId  = parseInt(btn.dataset.consultaId, 10);
  const nombre = btn.dataset.nombreProducto || '';

  if (!Number.isFinite(pubId)) {
    console.error('Falta data-consulta-id en el botón');
    return;
  }

  console.log('CLICK CP → pubId:', pubId, 'nombre:', nombre);

  
     cargarCodigosActuales(pubId);
 
});




// guarda el pubId en el modal cuando cargás
async function cargarCodigosActuales(pubId){
  const url = `/publicaciones/${pubId}/codigos-postales`;

  // fetch
  let data;
  try {
    const r = await fetch(url, { headers: { 'Accept': 'application/json' } });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    data = await r.json();
  } catch (e) {
    console.error('cargarCodigosActuales:', e);
    data = { _err: true, codigos: null };
  }

  // pintar chips
  const ul = document.getElementById('cp-lista-actual');
  if (ul) {
    while (ul.firstChild) ul.removeChild(ul.firstChild);
    if (data._err) {
      const li = document.createElement('li');
      li.className = 'cp-chip';
      li.textContent = 'Error listando códigos.';
      ul.appendChild(li);
    } else {
      const codigos = Array.isArray(data.codigos) ? data.codigos : [];
      if (codigos.length === 0) {
        const li = document.createElement('li');
        li.className = 'cp-chip';
        li.textContent = 'Sin códigos postales.';
        ul.appendChild(li);
      } else {
        for (const c of codigos) {
          const li = document.createElement('li');
          li.className = 'cp-chip';
          li.textContent = `#${c.id} · ${c.codigo}${c.ciudad ? ' · ' + c.ciudad : ''}`;
          ul.appendChild(li);
        }
      }
    }
  }

  // título y pubId para el modal
  const titulo = document.getElementById('cp-modal-titulo');
  if (titulo) titulo.textContent = `ID ${pubId}`;
  const modalEl = document.getElementById('codigosPostalesModal');
  if (modalEl) modalEl.dataset.pubId = String(pubId);

  // abrir
  if (modalEl) {
    if (window.bootstrap?.Modal) {
      bootstrap.Modal.getOrCreateInstance(modalEl).show();
    } else {
      modalEl.classList.add('show');
      modalEl.style.display = 'block';
      modalEl.removeAttribute('aria-hidden');
    }
  }
}

// handler del botón "Agregar"
document.addEventListener('click', async (e) => {
  const addBtn = e.target.closest('#cp-btn-agregar');
  if (!addBtn) return;

  const modalEl = document.getElementById('codigosPostalesModal');
  const pubId = Number(modalEl?.dataset.pubId || NaN);
  const input = document.getElementById('cp-input');
  const codigo = (input?.value || '').trim();

  if (!Number.isFinite(pubId)) {
    console.error('Falta pubId en modal.dataset.pubId');
    return;
  }
  if (!codigo) {
    input?.focus();
    return;
  }

  addBtn.disabled = true;
  try {
    const res = await fetch(`/publicaciones/${pubId}/codigos-postales`, {
      method: 'POST',
      headers: { 'Content-Type':'application/json', 'Accept':'application/json' },
      body: JSON.stringify({ codigo_postal: codigo })
    });
    const data = await res.json().catch(()=> ({}));
    if (!res.ok) {
      console.error('POST CP fallo:', res.status, data);
      alert(data?.error || 'No se pudo agregar el código postal.');
      return;
    }
    // ok → refrescar lista
    input.value = '';
    await cargarCodigosActuales(pubId);
  } catch (err) {
    console.error(err);
    alert('Error de red agregando el código postal.');
  } finally {
    addBtn.disabled = false;
  }
});



// render con highlight opcional
function renderChips(codigos, highlightId){
  const ul = document.getElementById('cp-lista-actual');
  if (!ul) return;
  while (ul.firstChild) ul.removeChild(ul.firstChild);

  if (!Array.isArray(codigos) || codigos.length === 0){
    const li = document.createElement('li');
    li.className = 'cp-chip';
    li.textContent = 'Sin códigos postales.';
    ul.appendChild(li);
    return;
  }

  for (const c of codigos){
    const li = document.createElement('li');
    li.className = 'cp-chip';
    li.dataset.cpId = c.id; // <-- necesario para borrar
    li.innerHTML = `
      <span>#${c.id} · ${c.codigo}${c.ciudad ? ' · ' + c.ciudad : ''}</span>
      <button type="button" class="cp-del" aria-label="Quitar" title="Quitar">&times;</button>
    `;
    if (highlightId && Number(c.id) === Number(highlightId)) {
      li.classList.add('cp-chip--new');
      setTimeout(()=> li.classList.remove('cp-chip--new'), 1200);
    }
    ul.appendChild(li);
  }
}


// carga lista (con cache off) y opcionalmente resalta uno
async function cargarCodigosActuales(pubId, highlightId){
  let data;
  try {
    const r = await fetch(`/publicaciones/${pubId}/codigos-postales`, {
      headers: { 'Accept': 'application/json' },
      cache: 'no-store'
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    data = await r.json();
  } catch (e) {
    console.error('cargarCodigosActuales:', e);
    data = { _err: true, codigos: [] };
  }

  if (data._err){
    renderChips([], null);
  } else {
    renderChips(data.codigos || [], highlightId);
  }

  const titulo = document.getElementById('cp-modal-titulo');
  if (titulo) titulo.textContent = `ID ${pubId}`;

  const modalEl = document.getElementById('codigosPostalesModal');
  if (modalEl) {
    modalEl.dataset.pubId = String(pubId);
    if (window.bootstrap?.Modal) bootstrap.Modal.getOrCreateInstance(modalEl).show();
    else { modalEl.classList.add('show'); modalEl.style.display='block'; modalEl.removeAttribute('aria-hidden'); }
  }
}

// click en Agregar → POST → recargar y resaltar el nuevo
document.addEventListener('click', async (e) => {
  const addBtn = e.target.closest('#cp-btn-agregar');
  if (!addBtn) return;

  const modalEl = document.getElementById('codigosPostalesModal');
  const pubId = Number(modalEl?.dataset.pubId || NaN);
  const input = document.getElementById('cp-input');
  const codigo = (input?.value || '').trim();
  if (!Number.isFinite(pubId) || !codigo) { input?.focus(); return; }

  addBtn.disabled = true;
  try {
    const res = await fetch(`/publicaciones/${pubId}/codigos-postales`, {
      method: 'POST',
      headers: { 'Content-Type':'application/json', 'Accept':'application/json' },
      body: JSON.stringify({ codigo_postal: codigo })
    });
    const pdata = await res.json().catch(()=> ({}));
    if (!res.ok) { alert(pdata?.error || 'No se pudo agregar.'); return; }

    input.value = '';
    // si el backend devolvió el CP, usamos su id para highlight
    const nuevoId = pdata?.cp?.id;
    await cargarCodigosActuales(pubId, nuevoId);
  } catch (err) {
    console.error(err);
    alert('Error de red agregando el código postal.');
  } finally {
    addBtn.disabled = false;
  }
});





document.getElementById('cp-lista-actual')?.addEventListener('click', async (e) => {
  const btn = e.target.closest('.cp-del');
  if (!btn) return;

  const li = btn.closest('.cp-chip');
  const cpId = Number(li?.dataset.cpId || NaN);

  const modalEl = document.getElementById('codigosPostalesModal');
  const pubId = Number(modalEl?.dataset.pubId || NaN);

  if (!Number.isFinite(pubId) || !Number.isFinite(cpId)) return;

  // opcional: confirm
  // if (!confirm('¿Quitar este código postal?')) return;

  btn.disabled = true;
  try {
    const res = await fetch(`/publicaciones/${pubId}/codigos-postales/${cpId}`, { method: 'DELETE' });
    const data = await res.json().catch(()=> ({}));
    if (!res.ok) {
      console.error('DELETE fallo:', res.status, data);
      alert(data?.error || 'No se pudo eliminar.');
      btn.disabled = false;
      return;
    }
    // sacar del DOM sin recargar todo
    li.remove();
    const ul = document.getElementById('cp-lista-actual');
    if (ul && ul.children.length === 0) {
      const liEmpty = document.createElement('li');
      liEmpty.className = 'cp-chip';
      liEmpty.textContent = 'Sin códigos postales.';
      ul.appendChild(liEmpty);
    }
  } catch (err) {
    console.error(err);
    alert('Error de red eliminando el código postal.');
    btn.disabled = false;
  }
});
