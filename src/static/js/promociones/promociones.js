document.addEventListener('DOMContentLoaded', function() {
    fetch('/productosComerciales_promociones_muestra_promociones/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.planes) {
            console.log(data);
            promocionesGlobal = data.promociones; // Guardar datos en planesGlobal
            updatePromocionTable(promocionesGlobal);
        } else {
            console.error('Error en la respuesta del servidor:', data);
            alert('Error al cargar los planes');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al cargar los planes');
    });
});

function updatePromocionTable(promociones) {
    promocionesGlobal = promociones; // Hacer accesible planes globalmente
    
    // Verificar si existe el elemento con ID plansTable
    const table = document.getElementById('promocionesTable');
    if (!table) {
         console.error('No se encontró el elemento con ID plansTable correcto control en Home');
        return;
    }

    const tableBody = table.getElementsByTagName('tbody')[0];
    tableBody.innerHTML = '';

    promociones.forEach(promocion => {
        const row = tableBody.insertRow();
        
        row.insertCell(0).textContent = promocion.id;
        row.insertCell(1).textContent = promocion.idPlan;
        row.insertCell(2).textContent = promocion.reason;
        row.insertCell(3).textContent = promocion.description;
        row.insertCell(4).textContent = promocion.price;
        row.insertCell(5).textContent = promocion.discount;
        row.insertCell(5).textContent = promocion.image_url;
  

       
    });
}