

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