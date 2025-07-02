// Navbar JavaScript completamente nuevo
document.addEventListener("DOMContentLoaded", () => {
  // Elementos del DOM
  const mobileMenu = document.getElementById("mobile-menu")
  const navbarMenu = document.getElementById("navbar-menu")
  const navbar = document.querySelector(".custom-navbar")
  const dropdowns = document.querySelectorAll(".custom-dropdown")

  // Toggle menú móvil
  if (mobileMenu && navbarMenu) {
    mobileMenu.addEventListener("click", () => {
      mobileMenu.classList.toggle("active")
      navbarMenu.classList.toggle("active")

      // Prevenir scroll del body cuando el menú está abierto
      if (navbarMenu.classList.contains("active")) {
        document.body.style.overflow = "hidden"
      } else {
        document.body.style.overflow = ""
      }
    })
  }

  // Manejar dropdowns
  dropdowns.forEach((dropdown) => {
    const toggle = dropdown.querySelector(".custom-dropdown-toggle")
    const menu = dropdown.querySelector(".custom-dropdown-menu")

    // Para desktop - hover
    dropdown.addEventListener("mouseenter", () => {
      if (window.innerWidth > 768) {
        dropdown.classList.add("show")
      }
    })

    dropdown.addEventListener("mouseleave", () => {
      if (window.innerWidth > 768) {
        dropdown.classList.remove("show")
      }
    })

    // Click para todos los tamaños
    if (toggle) {
      toggle.addEventListener("click", (e) => {
        e.preventDefault()
        e.stopPropagation()

        // Toggle el dropdown actual
        dropdown.classList.toggle("show")
        dropdown.classList.toggle("active")

        // Cerrar otros dropdowns
        dropdowns.forEach((otherDropdown) => {
          if (otherDropdown !== dropdown) {
            otherDropdown.classList.remove("show")
            otherDropdown.classList.remove("active")
          }
        })
      })
    }
  })

  // Cerrar dropdowns al hacer clic fuera
  document.addEventListener("click", (e) => {
    dropdowns.forEach((dropdown) => {
      if (!dropdown.contains(e.target)) {
        dropdown.classList.remove("show")
        dropdown.classList.remove("active")
      }
    })
  })

  // Efecto scroll en navbar
  if (navbar) {
    window.addEventListener("scroll", () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop

      if (scrollTop > 50) {
        navbar.classList.add("scrolled")
      } else {
        navbar.classList.remove("scrolled")
      }
    })
  }

  // Cerrar menú móvil al redimensionar ventana
  window.addEventListener("resize", () => {
    if (window.innerWidth > 768) {
      if (mobileMenu) mobileMenu.classList.remove("active")
      if (navbarMenu) navbarMenu.classList.remove("active")
      document.body.style.overflow = ""

      // Cerrar todos los dropdowns
      dropdowns.forEach((dropdown) => {
        dropdown.classList.remove("active")
      })
    }
  })

  // Manejar selección de dominio
  const domainItems = document.querySelectorAll("[data-domain]")
  domainItems.forEach((item) => {
    item.addEventListener("click", function (e) {
      e.preventDefault()
      const domain = this.getAttribute("data-domain")

      // Actualizar el input hidden
      const domainInput = document.getElementById("domain")
      if (domainInput) {
        domainInput.value = domain
      }

      // Actualizar estado activo
      domainItems.forEach((i) => i.classList.remove("active"))
      this.classList.add("active")

      console.log("Dominio seleccionado:", domain)
    })
  })

  // Manejar clics en las categorías del dropdown principal
  const categoryLinks = document.querySelectorAll('.custom-dropdown-item[data-domain]');
    
  categoryLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      
      const domain = this.getAttribute('data-domain');
      const categoryName = this.textContent.trim();
      
      // Guardar el dominio seleccionado
      localStorage.setItem('dominio', domain);
      localStorage.setItem('banderaCategorias', 'True');
      
      // Actualizar el título de la categoría actual
      const ambitoActual = document.getElementById('ambitoActual');
      if (ambitoActual) {
        ambitoActual.innerHTML = `<a style='text-decoration:none; color:orange;'>${categoryName}</a>`;
      }
      
      // Actualizar el campo hidden del domain
      const domainInput = document.getElementById('domain');
      if (domainInput) {
        domainInput.value = domain;
      }
      
      // IMPORTANTE: Forzar la carga inmediata de las nuevas subcategorías
      setTimeout(() => {
        if (typeof cargarAmbitosCategorias === 'function') {
          cargarAmbitosCategorias();
        } else {
          console.warn('Función cargarAmbitosCategorias no disponible');
        }
      }, 100); // Pequeño delay para asegurar que localStorage se actualice
      
      // Cerrar el dropdown
      const dropdown = this.closest('.custom-dropdown');
      if (dropdown) {
        dropdown.classList.remove('show');
      }
      
      // Cargar las publicaciones de la categoría seleccionada
      cargarPublicacionesPorCategoria(domain);
      
      // Scroll hacia la sección de publicaciones
      const seccionPublicaciones = document.getElementById('domains-publicaciones');
      if (seccionPublicaciones) {
        seccionPublicaciones.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
})

// Función para cargar publicaciones por categoría
async function cargarPublicacionesPorCategoria(domain) {
  try {
    // Mostrar loading
    const splashNotificaciones = document.getElementById('splashNotificaciones');
    if (splashNotificaciones) {
      splashNotificaciones.style.display = 'block';
    }
    
    // Hacer la petición para cargar las publicaciones
    const response = await fetch(`/publicaciones-por-categoria?domain=${domain}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.text();
      
      // Actualizar el contenido de publicaciones
      const contenedorPublicaciones = document.querySelector('.dpi-muestra-publicaciones-centrales');
      if (contenedorPublicaciones) {
        contenedorPublicaciones.innerHTML = data;
      }
    } else {
      console.error('Error al cargar publicaciones:', response.statusText);
    }
    
  } catch (error) {
    console.error('Error en la petición:', error);
  } finally {
    // Ocultar loading
    const splashNotificaciones = document.getElementById('splashNotificaciones');
    if (splashNotificaciones) {
      splashNotificaciones.style.display = 'none';
    }
  }
}

// Modificar la función cargarSubcategorias para usar la lógica existente
function cargarSubcategorias(domain, subcategoriasPorDominio) {
    // Guardar el dominio seleccionado en localStorage
    localStorage.setItem('dominio', domain);
    localStorage.setItem('banderaCategorias', 'True');
    
    // Llamar a la función existente que carga desde el backend
    if (typeof cargarAmbitosCategorias === 'function') {
        cargarAmbitosCategorias();
    } else {
        console.warn('Función cargarAmbitosCategorias no está disponible');
        // Fallback al sistema estático si la función no está disponible
        cargarSubcategoriasEstaticas(domain, subcategoriasPorDominio);
    }
}

// Función de respaldo con subcategorías estáticas
function cargarSubcategoriasEstaticas(domain, subcategoriasPorDominio) {
    const dropdownMenu = document.querySelector('.categoria-dropdown-menu');
    
    if (!dropdownMenu) {
        console.warn('No se encontró el dropdown de categorías');
        return;
    }
    
    // Limpiar el contenido actual
    dropdownMenu.innerHTML = '';
    
    // Obtener las subcategorías para el dominio seleccionado
    const subcategorias = subcategoriasPorDominio[domain] || [];
    
    if (subcategorias.length === 0) {
        const li = document.createElement('li');
        li.innerHTML = '<span class="dropdown-item text-muted">Sin subcategorías</span>';
        dropdownMenu.appendChild(li);
        return;
    }
    
    // Agregar cada subcategoría al dropdown
    subcategorias.forEach(subcategoria => {
        const li = document.createElement('li');
        li.style.padding = '10px';
        li.innerHTML = `
            <a href="#" class="categoria-dropdown-item" 
               id="${subcategoria.id}" 
               data-value="${subcategoria.name}"
               data-color="${subcategoria.color}"
               style="color: ${subcategoria.color}; padding: 10px;">
                ${subcategoria.name}
            </a>
        `;
        dropdownMenu.appendChild(li);
        
        // Agregar separador excepto para el último elemento
        if (subcategoria !== subcategorias[subcategorias.length - 1]) {
            const divider = document.createElement('li');
            divider.innerHTML = '<hr class="dropdown-divider">';
            dropdownMenu.appendChild(divider);
        }
    });
}
