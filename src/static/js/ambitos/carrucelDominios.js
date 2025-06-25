
document.addEventListener('DOMContentLoaded', () => {
  window.cargarAmbitosCarrusel(); // Llamar a la función cuando el DOM esté listo
});

window.cargarAmbitosCarrusel = function () {
  
  fetch('/social-media-publicaciones-obtener-ambitos/', {
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
              localStorage.setItem('banderaCategorias', 'True');
              // Llamar a cargarPublicaciones si está definida
                if (typeof cargarPublicaciones === 'function') {
                    cargarPublicaciones(valor, 'layout');
                } else {
                    console.warn('La función cargarPublicaciones no está definida.');
                }
                
                // Llamar a enviarDominioAJAX si está definida
                if (typeof enviarDominioAJAX === 'function') {
                    debugger;
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
      localStorage.setItem('banderaCategorias', 'True');
      // Volver a aplicar la clase active
      items.forEach(i => i.classList.remove('active')); // Eliminar la clase active de todos
      item.classList.add('active'); // Añadir la clase active al item clickeado
    });
  });




document.addEventListener("DOMContentLoaded", () => { 
    const banner = document.querySelector(".banner-movil");
    
    const grilla = document.getElementById("contenedor-publicacion");
    const carrusel = document.getElementById("container-carrusel");
    const publicaciones = document.querySelector('.home-muestra-publicaciones-en-ambitos-personales-centrales');

    let altura = 0;
    let espacio = 0;
    let espacio2 = 0;
    if (banner && getComputedStyle(banner).display !== "none") {
        altura = banner.offsetHeight;
     
     espacio = 60;
     espacio2 = 80;
    

    if (grilla) {
        grilla.style.marginTop = `${altura + espacio}px`;
    }

    
        if (carrusel) {
            carrusel.style.marginTop = `${altura + espacio2}px`;
        }  
      

    if (publicaciones) {
        publicaciones.style.marginTop = `${altura + espacio}px`;
        publicaciones.style.transition = 'margin-top 0.3s ease';
    } 
  }else {
    espacio = 0;
    espacio2 = 0;
    if (grilla) {
        grilla.style.marginTop = `${espacio}px`;
    }
    if (carrusel) {
        carrusel.style.marginTop = `${espacio2}px`;
    }  
    if (publicaciones) {
        publicaciones.style.marginTop = `${espacio}px`;
        publicaciones.style.transition = 'margin-top 0.3s ease';
    } 
  }
});
