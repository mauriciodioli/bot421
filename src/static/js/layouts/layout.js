// Definir la función que manejará el clic en "Administración"
function handleAdminClick(event) {
    event.preventDefault(); // Evita el comportamiento predeterminado del enlace
    debugger;
    const token = localStorage.getItem('access_token');
    if (!token) {
        alert('No se encontró un token de acceso.');
        return;
    }

    fetch('/herramientaAdmin-administracion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            layout: 'layout_administracion',
            tipoUso: 'admin'
        })
    })
    .then(response => {
        if (response.ok) {
            return response.text(); // Recibe el HTML de la respuesta
        } else {
            throw new Error('Error en la solicitud');
        }
    })
    .then(html => {
        document.body.innerHTML = html; // Reemplaza el contenido actual por el nuevo HTML
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ocurrió un error al procesar la solicitud.');
    });
}

// Asociar la función al enlace después de que el DOM esté cargado
document.addEventListener('DOMContentLoaded', function () {
    const adminLink = document.getElementById('admin-link');
    if (adminLink) {
        adminLink.addEventListener('click', handleAdminClick);
    } else {
        console.error("No se encontró el elemento con ID 'admin-link'.");
    }
});




document.getElementById('ventas-link').addEventListener('click', function (event) {
    event.preventDefault(); // Prevenir la acción predeterminada del enlace
    
    try {
        const token = localStorage.getItem('access_token');
        const dominio = localStorage.getItem('ambito');

        if (!token || !dominio) {
            throw new Error("Datos faltantes en localStorage.");
        }

        // Asignar valores al formulario
        document.getElementById('pedidos_ventas_accessToken').value = token;
        document.getElementById('pedidos_ventas_dominio').value = dominio;

        // Enviar el formulario
        document.getElementById('ventas-form').submit();
    } catch (error) {
        console.error("Error al procesar el formulario:", error.message);
        alert("No se pudo procesar la solicitud. Intente nuevamente.");
    }
});
