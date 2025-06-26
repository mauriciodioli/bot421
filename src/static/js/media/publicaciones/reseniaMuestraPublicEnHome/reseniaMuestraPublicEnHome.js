<<<<<<< HEAD

  const reseñasFijas = [
    {
      nombre: "Juan Pérez",
      comentario: "Excelente producto, superó mis expectativas."
    },
    {
      nombre: "María López",
      comentario: "Entrega rápida y atención al cliente impecable."
    }
  ];


  document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('form-reseña');
  const userId = localStorage.getItem('usuario_id');
  const correo = localStorage.getItem('correo_electronico');

  if (!userId || !correo) {
    form.style.display = 'none';
  }

  cargarReseñas();
});


function cargarReseñas() {
  const contenedor = document.getElementById('contenedor-reseñas');
  const mensaje = document.getElementById('mensaje-sin-reseñas');
  const data = JSON.parse(localStorage.getItem(storageKey)) || [];

  contenedor.innerHTML = '';

  if (data.length === 0) {
    mensaje.style.display = 'block';
    return;
  }

  mensaje.style.display = 'none';

  const ordenadas = ordenarPorFechaDescendente(data);
  const primerasTres = ordenadas.slice(0, 3);
  const restantes = ordenadas.slice(3);

  // Mostrar las 3 más recientes
  primerasTres.forEach((r, i) => {
    contenedor.innerHTML += generarHTMLReseña(r, i);
  });

  // Si hay más, generar el desplegable
  if (restantes.length > 0) {
    contenedor.innerHTML += generarDesplegableReseñas('reseñas-extra', restantes, 3);
  }
}




function eliminarReseña(index) {
  const reseñas = JSON.parse(localStorage.getItem(storageKey)) || [];
  reseñas.splice(index, 1);
  localStorage.setItem(storageKey, JSON.stringify(reseñas));
  cargarReseñas();
}

function editarReseña(index) {
  const reseñas = JSON.parse(localStorage.getItem(storageKey)) || [];
  const nuevaNombre = prompt("Editar nombre:", reseñas[index].nombre);
  const nuevoComentario = prompt("Editar comentario:", reseñas[index].comentario);

  if (nuevaNombre && nuevoComentario) {
    reseñas[index].nombre = nuevaNombre;
    reseñas[index].comentario = nuevoComentario;
    localStorage.setItem(storageKey, JSON.stringify(reseñas));
    cargarReseñas();
  }
}


 document.getElementById('form-reseña').addEventListener('submit', e => {
  e.preventDefault();
  const nombre = document.getElementById('nombre-reseña').value.trim();
  const comentario = document.getElementById('comentario-reseña').value.trim();
  if (!nombre || !comentario) return;

  const nuevas = JSON.parse(localStorage.getItem(storageKey)) || [];
  const userId = localStorage.getItem('usuario_id');
  const correo = localStorage.getItem('correo_electronico');

    nuevas.push({ 
    nombre, 
    comentario, 
    fecha: new Date().toISOString(),
    user_id: userId,
    correo_electronico: correo
    });

  localStorage.setItem(storageKey, JSON.stringify(nuevas));

  document.getElementById('form-reseña').reset();
  cargarReseñas();
});




function ordenarPorFechaDescendente(reseñas) {
  return reseñas.sort((a, b) => {
    const fechaA = new Date(a.fecha || 0);
    const fechaB = new Date(b.fecha || 0);
    return fechaB - fechaA;
  });
}


function generarHTMLReseña(r, index) {
  const fechaFormateada = r.fecha
    ? new Date(r.fecha).toLocaleString('es-AR')
    : 'Fecha desconocida';

  const userId = localStorage.getItem('usuario_id');
  const correo = localStorage.getItem('correo_electronico');

  const esAutor = r.user_id === userId && r.correo_electronico === correo;

  const botones = esAutor
    ? `
      <div class="acciones-reseña">
        <button class="icono-btn" onclick="editarReseña(${index})" title="Editar reseña">✏️</button>
        <button class="icono-btn" onclick="eliminarReseña(${index})" title="Eliminar reseña">🗑️</button>
      </div>
      `
    : '';

  return `
    <div class="testimonial">
      <small>${fechaFormateada}</small>
      <p>"${r.comentario}"</p>
      <h4>- ${r.nombre}</h4>
      ${botones}
    </div>
  `;
}




function generarDesplegableReseñas(id, reseñasOcultas, offset = 0) {
  const contenido = reseñasOcultas.map((r, i) => generarHTMLReseña(r, i + offset)).join('');

  return `
    <button onclick="toggleReseñas('${id}', this)">Mostrar más reseñas</button>
    <div id="${id}" style="display: none;">
      ${contenido}
    </div>
  `;
}


function toggleReseñas(id, boton) {
  const div = document.getElementById(id);
  const visible = div.style.display === 'block';
  div.style.display = visible ? 'none' : 'block';
  boton.textContent = visible ? 'Mostrar más reseñas' : 'Ocultar reseñas';
}
=======

  const reseñasFijas = [
    {
      nombre: "Juan Pérez",
      comentario: "Excelente producto, superó mis expectativas."
    },
    {
      nombre: "María López",
      comentario: "Entrega rápida y atención al cliente impecable."
    }
  ];


  document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('form-reseña');
  const userId = localStorage.getItem('usuario_id');
  const correo = localStorage.getItem('correo_electronico');

  if (!userId || !correo) {
    form.style.display = 'none';
  }

  cargarReseñas();
});


function cargarReseñas() {
  const contenedor = document.getElementById('contenedor-reseñas');
  const mensaje = document.getElementById('mensaje-sin-reseñas');
  const data = JSON.parse(localStorage.getItem(storageKey)) || [];

  contenedor.innerHTML = '';

  if (data.length === 0) {
    mensaje.style.display = 'block';
    return;
  }

  mensaje.style.display = 'none';

  const ordenadas = ordenarPorFechaDescendente(data);
  const primerasTres = ordenadas.slice(0, 3);
  const restantes = ordenadas.slice(3);

  // Mostrar las 3 más recientes
  primerasTres.forEach((r, i) => {
    contenedor.innerHTML += generarHTMLReseña(r, i);
  });

  // Si hay más, generar el desplegable
  if (restantes.length > 0) {
    contenedor.innerHTML += generarDesplegableReseñas('reseñas-extra', restantes, 3);
  }
}




function eliminarReseña(index) {
  const reseñas = JSON.parse(localStorage.getItem(storageKey)) || [];
  reseñas.splice(index, 1);
  localStorage.setItem(storageKey, JSON.stringify(reseñas));
  cargarReseñas();
}

function editarReseña(index) {
  const reseñas = JSON.parse(localStorage.getItem(storageKey)) || [];
  const nuevaNombre = prompt("Editar nombre:", reseñas[index].nombre);
  const nuevoComentario = prompt("Editar comentario:", reseñas[index].comentario);

  if (nuevaNombre && nuevoComentario) {
    reseñas[index].nombre = nuevaNombre;
    reseñas[index].comentario = nuevoComentario;
    localStorage.setItem(storageKey, JSON.stringify(reseñas));
    cargarReseñas();
  }
}


 document.getElementById('form-reseña').addEventListener('submit', e => {
  e.preventDefault();
  const nombre = document.getElementById('nombre-reseña').value.trim();
  const comentario = document.getElementById('comentario-reseña').value.trim();
  if (!nombre || !comentario) return;

  const nuevas = JSON.parse(localStorage.getItem(storageKey)) || [];
  const userId = localStorage.getItem('usuario_id');
  const correo = localStorage.getItem('correo_electronico');

    nuevas.push({ 
    nombre, 
    comentario, 
    fecha: new Date().toISOString(),
    user_id: userId,
    correo_electronico: correo
    });

  localStorage.setItem(storageKey, JSON.stringify(nuevas));

  document.getElementById('form-reseña').reset();
  cargarReseñas();
});




function ordenarPorFechaDescendente(reseñas) {
  return reseñas.sort((a, b) => {
    const fechaA = new Date(a.fecha || 0);
    const fechaB = new Date(b.fecha || 0);
    return fechaB - fechaA;
  });
}


function generarHTMLReseña(r, index) {
  const fechaFormateada = r.fecha
    ? new Date(r.fecha).toLocaleString('es-AR')
    : 'Fecha desconocida';

  const userId = localStorage.getItem('usuario_id');
  const correo = localStorage.getItem('correo_electronico');

  const esAutor = r.user_id === userId && r.correo_electronico === correo;

  const botones = esAutor
    ? `
      <div class="acciones-reseña">
        <button class="icono-btn" onclick="editarReseña(${index})" title="Editar reseña">✏️</button>
        <button class="icono-btn" onclick="eliminarReseña(${index})" title="Eliminar reseña">🗑️</button>
      </div>
      `
    : '';

  return `
    <div class="testimonial">
      <small>${fechaFormateada}</small>
      <p>"${r.comentario}"</p>
      <h4>- ${r.nombre}</h4>
      ${botones}
    </div>
  `;
}




function generarDesplegableReseñas(id, reseñasOcultas, offset = 0) {
  const contenido = reseñasOcultas.map((r, i) => generarHTMLReseña(r, i + offset)).join('');

  return `
    <button onclick="toggleReseñas('${id}', this)">Mostrar más reseñas</button>
    <div id="${id}" style="display: none;">
      ${contenido}
    </div>
  `;
}


function toggleReseñas(id, boton) {
  const div = document.getElementById(id);
  const visible = div.style.display === 'block';
  div.style.display = visible ? 'none' : 'block';
  boton.textContent = visible ? 'Mostrar más reseñas' : 'Ocultar reseñas';
}
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
