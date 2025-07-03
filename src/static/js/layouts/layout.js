// ===== LAYOUT.JS UNIFICADO =====
// Combina toda la funcionalidad de layout.js y layout_dpi.js

// ===== FUNCIONES DE ADMINISTRACIÓN =====
function handleAdminClick(event) {
    event.preventDefault();
    
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
            return response.text();
        } else {
            throw new Error('Error en la solicitud');
        }
    })
    .then(html => {
        document.body.innerHTML = html;
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ocurrió un error al procesar la solicitud.');
    });
}

// ===== FUNCIÓN PARA COOKIES =====
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// ===== FUNCIÓN PARA CARGAR PUBLICACIONES POR CATEGORÍA =====
async function cargarPublicacionesPorCategoria(domain) {
    try {
        const splashNotificaciones = document.getElementById('splashNotificaciones');
        if (splashNotificaciones) {
            splashNotificaciones.style.display = 'block';
        }
        
        const galeriaURL = '/media-publicaciones-mostrar-dpi/';
        const access_token = 'access_dpi_token_usuario_anonimo';
        const cp = localStorage.getItem('codigoPostal');
        const lenguaje = localStorage.getItem('language') || 'in';
        
        console.log('Cargando publicaciones para dominio:', domain);
        
        $.ajax({
            type: 'POST',
            url: galeriaURL,
            dataType: 'json',
            headers: { 'Authorization': 'Bearer ' + access_token },
            data: { 
                ambitos: domain,
                categoria: '1',
                lenguaje: lenguaje,
                cp: cp || ''
            },
            success: function (response) {
                if (splashNotificaciones) {
                    splashNotificaciones.style.display = 'none';
                }
                
                if (Array.isArray(response) && response.length > 0) {
                    var postDisplayContainer = $('.dpi-muestra-publicaciones-centrales');
                    postDisplayContainer.empty();

                    response.forEach(function(post) {
                        if (post.imagenes.length > 0 || post.videos.length > 0) {
                            var mediaHtml = '';

                            if (Array.isArray(post.imagenes) && post.imagenes.length > 0) {
                                if (post.imagenes[0].imagen != null) {
                                    var firstImageBase64 = post.imagenes[0].imagen;
                                    var firstImageUrl = `data:${post.imagenes[0].mimetype};base64,${firstImageBase64}`;
                                    mediaHtml += `<img src="${firstImageUrl}" alt="Imagen de la publicación" onclick="abrirPublicacionHome(${post.publicacion_id}, '${post.layout}')" style="cursor: pointer;">`;
                                } else {
                                    var firstImageUrl = post.imagenes[0].filepath;
                                    mediaHtml += `<img src="${firstImageUrl}" alt="Imagen de la publicación" onclick="abrirPublicacionHome(${post.publicacion_id}, '${post.layout}')" style="cursor: pointer;">`;
                                }
                            } else if (Array.isArray(post.videos) && post.videos.length > 0) {
                                var firstVideoUrl = post.videos[0].filepath;
                                mediaHtml += `
                                    <video controls style="cursor: pointer;" onclick="abrirPublicacionHome(${post.publicacion_id}, '${post.layout}')">
                                        <source src="${firstVideoUrl}" type="video/mp4">
                                        Tu navegador no soporta la reproducción de videos.
                                    </video>
                                `;
                            }

                            var cardHtml = `
                                <div class="card-publicacion-admin" id="card-${post.publicacion_id}">
                                    <div class="card-body">
                                        <a class="btn-close-publicacion" onclick="cerrarPublicacion(${post.publicacion_id})">
                                            <span class="text-white">&times;</span>
                                        </a>
                                        <h5 class="card-title">${post.titulo}</h5>
                                        <div class="card-media-grid-publicacion-en-ambito">
                                            ${mediaHtml}
                                        </div>
                                        <p class="card-date">${formatDate(post.fecha_creacion)}</p>
                                        <p class="card-text text-truncated" id="postText-${post.publicacion_id}">${post.texto}</p>
                                        <a href="#" class="btn-ver-mas" onclick="toggleTexto(${post.publicacion_id}); return false;">Ver más</a>
                                    </div>
                                </div>
                            `;

                            postDisplayContainer.append(cardHtml);
                        }
                    });
                } else {
                    var postDisplayContainer = $('.dpi-muestra-publicaciones-centrales');
                    postDisplayContainer.empty();
                    postDisplayContainer.append(`
                        <div class="alert alert-info text-center">
                            <h4>Selecciona una subcategoría</h4>
                            <p>Has seleccionado "${domain}". Ahora elige una subcategoría específica para ver las publicaciones.</p>
                        </div>
                    `);
                }
            },
            error: function (xhr, status, error) {
                if (splashNotificaciones) {
                    splashNotificaciones.style.display = 'none';
                }
                console.error('Error al cargar publicaciones:', error);
                
                var postDisplayContainer = $('.dpi-muestra-publicaciones-centrales');
                postDisplayContainer.empty();
                postDisplayContainer.append(`
                    <div class="alert alert-warning text-center">
                        <h4>Selecciona una subcategoría</h4>
                        <p>Para ver publicaciones específicas, elige una subcategoría del menú "Categorías".</p>
                    </div>
                `);
            }
        });
        
    } catch (error) {
        console.error('Error en la petición:', error);
    }
}

// ===== EVENT LISTENERS PRINCIPALES =====
document.addEventListener('DOMContentLoaded', function () {
    
    // ===== NAVBAR FUNCTIONALITY =====
    const mobileMenu = document.getElementById("mobile-menu");
    const navbarMenu = document.getElementById("navbar-menu");
    const navbar = document.querySelector(".custom-navbar");
    const dropdowns = document.querySelectorAll(".custom-dropdown");

    // Toggle menú móvil
    if (mobileMenu && navbarMenu) {
        mobileMenu.addEventListener("click", () => {
            mobileMenu.classList.toggle("active");
            navbarMenu.classList.toggle("active");

            if (navbarMenu.classList.contains("active")) {
                document.body.style.overflow = "hidden";
            } else {
                document.body.style.overflow = "";
            }
        });
    }

    // Manejar dropdowns
    dropdowns.forEach((dropdown) => {
        const toggle = dropdown.querySelector(".custom-dropdown-toggle");

        dropdown.addEventListener("mouseenter", () => {
            if (window.innerWidth > 768) {
                dropdown.classList.add("show");
            }
        });

        dropdown.addEventListener("mouseleave", () => {
            if (window.innerWidth > 768) {
                dropdown.classList.remove("show");
            }
        });

        if (toggle) {
            toggle.addEventListener("click", (e) => {
                e.preventDefault();
                e.stopPropagation();

                dropdown.classList.toggle("show");
                dropdown.classList.toggle("active");

                dropdowns.forEach((otherDropdown) => {
                    if (otherDropdown !== dropdown) {
                        otherDropdown.classList.remove("show");
                        otherDropdown.classList.remove("active");
                    }
                });
            });
        }
    });

    // Cerrar dropdowns al hacer clic fuera
    document.addEventListener("click", (e) => {
        dropdowns.forEach((dropdown) => {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove("show");
                dropdown.classList.remove("active");
            }
        });
    });

    // Efecto scroll en navbar
    if (navbar) {
        window.addEventListener("scroll", () => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            if (scrollTop > 50) {
                navbar.classList.add("scrolled");
            } else {
                navbar.classList.remove("scrolled");
            }
        });
    }

    // Cerrar menú móvil al redimensionar ventana
    window.addEventListener("resize", () => {
        if (window.innerWidth > 768) {
            if (mobileMenu) mobileMenu.classList.remove("active");
            if (navbarMenu) navbarMenu.classList.remove("active");
            document.body.style.overflow = "";

            dropdowns.forEach((dropdown) => {
                dropdown.classList.remove("active");
            });
        }
    });

    // ===== CÓDIGO POSTAL SIMPLE =====
    const codigoPostalInput = document.getElementById('codigoPostalSimple');
    
    if (codigoPostalInput) {
        const savedCP = localStorage.getItem('codigoPostal');
        if (savedCP) {
            codigoPostalInput.value = savedCP;
        }

        codigoPostalInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/[^0-9]/g, '');
            e.target.value = value;
            
            if (value) {
                localStorage.setItem('codigoPostal', value);
                console.log('CP guardado:', value);
            }
        });

        codigoPostalInput.addEventListener('blur', function(e) {
            const value = e.target.value.trim();
            if (value) {
                localStorage.setItem('codigoPostal', value);
                console.log('CP guardado (blur):', value);
            }
        });

        codigoPostalInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const value = e.target.value.trim();
                if (value) {
                    localStorage.setItem('codigoPostal', value);
                    console.log('CP guardado (enter):', value);
                    
                    if (typeof cargarAmbitosCategorias === 'function') {
                        setTimeout(() => {
                            cargarAmbitosCategorias();
                        }, 100);
                    }
                }
            }
        });
    }

    // ===== MANEJAR CLICS EN CATEGORÍAS PRINCIPALES SOLAMENTE =====
    // CAMBIAR este selector para que NO interfiera con las subcategorías
    const categoryLinks = document.querySelectorAll('.custom-dropdown-item[data-domain]');
        
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const domain = this.getAttribute('data-domain');
            const categoryName = this.textContent.trim();
            
            console.log('Categoría principal seleccionada:', domain, categoryName); // Debug
            
            localStorage.setItem('dominio', domain);
            localStorage.setItem('banderaCategorias', 'True');
            
            const ambitoActual = document.getElementById('ambitoActual');
            if (ambitoActual) {
                ambitoActual.innerHTML = `<a style='text-decoration:none; color:orange;'>${categoryName}</a>`;
            }
            
            const domainInput = document.getElementById('domain');
            if (domainInput) {
                domainInput.value = domain;
            }
            
            setTimeout(() => {
                if (typeof cargarAmbitosCategorias === 'function') {
                    cargarAmbitosCategorias();
                } else {
                    console.warn('Función cargarAmbitosCategorias no disponible');
                }
            }, 100);
            
            const dropdown = this.closest('.custom-dropdown');
            if (dropdown) {
                dropdown.classList.remove('show');
            }
            
            cargarPublicacionesPorCategoria(domain);
            
            const seccionPublicaciones = document.getElementById('domains-publicaciones');
            if (seccionPublicaciones) {
                seccionPublicaciones.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // ===== NO TOCAR LAS SUBCATEGORÍAS - las maneja navBarCaracteristicas.js =====

    // ===== ADMIN LINK =====
    const adminLink = document.getElementById('admin-link');
    if (adminLink) {
        adminLink.addEventListener('click', handleAdminClick);
    }

    // ===== VENTAS LINK =====
    const ventasLink = document.getElementById('ventas-link');
    if (ventasLink) {
        ventasLink.addEventListener('click', function (event) {
            event.preventDefault();
            const form = document.getElementById('ventas-form');
            let access_token = localStorage.getItem("access_token");
            var ambito = localStorage.getItem("dominio");
            
            document.getElementById('access_token_form_Ventas').value = access_token;
            document.getElementById('ambito_form_Ventas').value = ambito;
            form.submit();
        });
    }

    // ===== COMPRAS LINK =====
    const comprasLink = document.getElementById('compras-link');
    if (comprasLink) {
        comprasLink.addEventListener('click', function (event) {
            event.preventDefault();
            const form = document.getElementById('compras-form');
            let access_token = localStorage.getItem("access_token");
            var ambito = localStorage.getItem("dominio");
            
            document.getElementById('access_token_btn_compras').value = access_token;
            document.getElementById('ambito_btn_compras').value = ambito;
            form.submit();
        });
    }

    // ===== CONSULTAS LINK =====
    const consultasLink = document.getElementById('consultas-link');
    if (consultasLink) {
        consultasLink.addEventListener('click', function (event) {
            event.preventDefault();
            const form = document.getElementById('consultas-form');
            let access_token = localStorage.getItem("access_token");
            var ambito = localStorage.getItem("dominio");
            
            document.getElementById('access_token_btn_consultas').value = access_token;
            document.getElementById('ambito_btn_consultas').value = ambito;
            form.submit();
        });
    }

    // ===== INICIALIZACIÓN DE IDIOMA =====
    var currentLanguage = 'in';
    var languageLink = document.getElementById("languageLink");

    if (!getCookie("language")) {
        document.cookie = `language=${currentLanguage}; path=/; max-age=31536000`;
        currentLanguage = "in";
        localStorage.setItem("language", currentLanguage);
        if (languageLink) {
            languageLink.textContent = "ENG";
        }
    } else {
        currentLanguage = getCookie("language");
        localStorage.setItem("language", currentLanguage);
        if (languageLink) {
            languageLink.textContent = currentLanguage === "in" ? "ENG" : "ES";
        }
    }

    // ===== SELECTOR DE IDIOMA =====
    const selector = document.getElementById("languageSelector");
    const selected = selector?.querySelector(".selected-language");
    const dropdown = selector?.querySelector(".language-dropdown");

    if (selector && selected && dropdown) {
        const languages = {
            es: { name: "Español", code: "ES", flag: "https://flagcdn.com/24x18/es.png" },
            in: { name: "English", code: "ENG", flag: "https://flagcdn.com/24x18/us.png" },
            fr: { name: "Français", code: "FR", flag: "https://flagcdn.com/24x18/fr.png" },
            de: { name: "Deutsch", code: "DE", flag: "https://flagcdn.com/24x18/de.png" },
            it: { name: "Italiano", code: "IT", flag: "https://flagcdn.com/24x18/it.png" },
            pt: { name: "Português", code: "PT", flag: "https://flagcdn.com/24x18/pt.png" }
        };

        const availableLanguages = Object.keys(languages);

        function setLanguage(lang) {
            const langData = languages[lang];
            if (!langData) return;

            localStorage.setItem("language", lang);
            document.cookie = `language=${lang}; path=/; max-age=31536000`;

            selected.innerHTML = `<img src="${langData.flag}"> ${langData.code}`;

            if (languageLink) {
                languageLink.textContent = langData.code;
            }

            dropdown.style.display = "none";

            if (typeof cargarAmbitos === "function") cargarAmbitos();
            if (typeof cargarAmbitosCarrusel === "function") cargarAmbitosCarrusel();
        }

        function buildDropdown() {
            dropdown.innerHTML = "";
            for (const [code, lang] of Object.entries(languages)) {
                const option = document.createElement("div");
                option.className = "language-option";
                option.innerHTML = `<img src="${lang.flag}"> ${lang.name}`;
                option.addEventListener("click", () => setLanguage(code));
                dropdown.appendChild(option);
            }
        }

        selected.addEventListener("click", () => {
            dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
        });

        document.addEventListener("click", (e) => {
            if (!selector.contains(e.target) && e.target !== languageLink) {
                dropdown.style.display = "none";
            }
        });

        if (languageLink) {
            languageLink.addEventListener("click", function (event) {
                event.preventDefault();

                const currentLang = localStorage.getItem("language") || getCookie("language") || "in";
                const currentIndex = availableLanguages.indexOf(currentLang);
                const nextIndex = (currentIndex + 1) % availableLanguages.length;
                const nextLang = availableLanguages[nextIndex];

                setLanguage(nextLang);
            });
        }

        const currentLang = localStorage.getItem("language") || getCookie("language") || "in";
        setLanguage(currentLang);
        buildDropdown();
    }
});































