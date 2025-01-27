
document.addEventListener('DOMContentLoaded', () => {
  window.cargarAmbitosCarrusel(); // Llamar a la función cuando el DOM esté listo
});

window.cargarAmbitosCarrusel = function () {
  fetch('/social-media-publicaciones-obtener-ambitos', {
      method: 'GET',
      headers: {
          'Content-Type': 'application/json',
      }
  })
  .then(response => {
      if (!response.ok) {
          throw new Error('Error al obtener los ámbitos.');
      }
      return response.json();
  })
  .then(data => {
   
      // Obtener el contenedor donde se agregará el carrusel
      const carruselContainer = document.querySelector('.carrusel-container');
      
      // Limpiar el contenedor en caso de que ya haya elementos
      carruselContainer.innerHTML = '';
      
      // Iterar sobre los datos y crear los items del carrusel con los valores 'nombre' y 'valor'
      data.forEach(item => {
          const divItem = document.createElement('div');
          divItem.classList.add('carrusel-item');
          divItem.textContent = item.nombre;  // Usar 'nombre' para mostrar en el carrusel
          divItem.setAttribute('data-valor', item.valor);  // Almacenar 'valor' en un atributo para su uso posterior
          carruselContainer.appendChild(divItem);
      });

      // Obtener todos los elementos del carrusel para añadirles el evento de clic
      const items = document.querySelectorAll('.carrusel-item');

      // Añadir el event listener para cada item
      items.forEach(item => {
          item.addEventListener('click', () => {
              // Elimina la clase 'active' de todos los items
              items.forEach(i => i.classList.remove('active'));
              
              // Añadir la clase 'active' al item en el que se ha hecho clic
              item.classList.add('active');
             
              // Obtener el valor almacenado en el atributo 'data-valor'
              const valor = item.getAttribute('data-valor');
             
             
              // Modificar el localStorage con el nuevo valor seleccionado
              localStorage.setItem('dominio', valor);
              // Llamar a cargarPublicaciones si está definida
                if (typeof cargarPublicaciones === 'function') {
                    cargarPublicaciones(valor, 'layout');
                } else {
                    console.warn('La función cargarPublicaciones no está definida.');
                }
                
                // Llamar a enviarDominioAJAX si está definida
                if (typeof enviarDominioAJAX === 'function') {
                    enviarDominioAJAX(valor);
                } else {
                    console.warn('La función enviarDominioAJAX no está definida.');
                }
          });
      });
  })
  .catch(error => {
      console.error('Error:', error);
  });
};




const prevButton = document.querySelector('.prev');
const nextButton = document.querySelector('.next');
const dominioActivo = localStorage.getItem('dominio');
const carouselContainer = document.querySelector('.carrusel-container');
let currentIndex = 0;

const items = document.querySelectorAll('.carrusel-item');
const totalItems = items.length;

// Añadir un event listener para cada item
items.forEach(item => {
    item.addEventListener('click', () => {
        // Elimina la clase 'active' de todos los items
        items.forEach(i => i.classList.remove('active'));
        
        // Añadir la clase 'active' al item en el que se ha hecho clic
        item.classList.add('active');
    });
});



// Función para mover el carrusel al siguiente item
document.querySelector('.next').addEventListener('click', () => {
    const container = document.querySelector('.carrusel-container');
    container.scrollBy({ left: 300, behavior: 'smooth' }); // Ajusta la cantidad de desplazamiento si es necesario
  });
  
  // Función para mover el carrusel al item anterior
  document.querySelector('.prev').addEventListener('click', () => {
    const container = document.querySelector('.carrusel-container');
    container.scrollBy({ left: -300, behavior: 'smooth' }); // Ajusta la cantidad de desplazamiento si es necesario
  });
  

  
// Recorremos los items y agregamos la clase "active" al que coincida con el valor de "dominio"
items.forEach(item => {
    if (item.textContent === dominioActivo) {
      item.classList.add('active'); // Agregar la clase active al item correspondiente
    } else {
      item.classList.remove('active'); // Eliminar la clase active en los demás items
    }
  });
  
  // Si deseas que el valor de "dominio" cambie al hacer clic en un item y actualizar el localStorage
  items.forEach(item => {
    item.addEventListener('click', () => {
      // Cambiar el valor de "dominio" en localStorage
      localStorage.setItem('dominio', item.textContent);
  
      // Volver a aplicar la clase active
      items.forEach(i => i.classList.remove('active')); // Eliminar la clase active de todos
      item.classList.add('active'); // Añadir la clase active al item clickeado
    });
  });


   // Verifica si existe el token de acceso en localStorage
 document.addEventListener('DOMContentLoaded', () => {
  
  const accessToken = localStorage.getItem('access_token');
  const container_carrucel = document.getElementById('container-carrusel');
  
  if (container_carrucel) {  // Asegúrate de que el contenedor exista
    if (accessToken) {
      container_carrucel.style.marginTop = '0px';
    } else {
      container_carrucel.style.marginTop = '110px';
    }
  } else {
    console.error('El contenedor no se encontró.');
  }
});