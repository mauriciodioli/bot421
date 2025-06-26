document.addEventListener("DOMContentLoaded", function () {
    const openModalBtn = document.querySelector(".open-pdf-modal"); // Botón que abre el modal
    const fileInput = document.getElementById("pdfInput"); // Input file oculto
    const modal = document.getElementById("pdfModal"); // Modal
    const closeModalBtn = document.querySelector(".close"); // Botón para cerrar modal
    const pdfName = document.getElementById("pdfName"); // Nombre del PDF
    const pdfSize = document.getElementById("pdfSize"); // Tamaño del PDF
    const pdfViewer = document.getElementById("pdfViewer"); // Vista previa
    const uploadButton = document.getElementById("uploadPdf"); // Botón de subir archivo

    // Abre el input file al hacer clic en el botón
    openModalBtn.addEventListener("click", function () {
        fileInput.click();
    });

    // Detectar cuando se selecciona un archivo
    fileInput.addEventListener("change", function (event) {
        const file = event.target.files[0];

        if (file) {
            // Mostrar datos en el modal
            pdfName.textContent = file.name;
            pdfSize.textContent = (file.size / 1024).toFixed(2) + " KB";

            // Crear una URL para la vista previa del PDF
            const fileURL = URL.createObjectURL(file);
            pdfViewer.src = fileURL;

            // Mostrar el modal
            modal.style.display = "block";
        }
    });

    // Cerrar modal
    closeModalBtn.addEventListener("click", function () {
        modal.style.display = "none";
    });

    // Enviar el archivo al servidor al hacer clic en "Subir PDF"
    uploadButton.addEventListener("click", function () {
        const accessToken = localStorage.getItem("access_token");
        if (!accessToken) {
            alert("Debes iniciar sesión para subir un PDF");
            return;
        }

        // Solicitar código de seguridad
        const securityCode = prompt("Introduce el código de seguridad:");

        // Comprobar si el código de seguridad es correcto
        if (securityCode !== "dpiaDoc") {  // Cambia "1234" por el código real
            alert("Código de seguridad incorrecto. No se puede subir el archivo.");
            modal.style.display = "none";
            return;
        }

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        fetch("/media_cargarPdf/", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${accessToken}` // Incluir el token de autorización
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            alert("PDF subido con éxito");
            modal.style.display = "none";
        })
        .catch(error => console.error("Error al subir el PDF:", error));
    });
});



document.addEventListener("DOMContentLoaded", function() {
    const openModalBtns = document.querySelectorAll(".open-pdf-modal");
    const modal = document.getElementById("pdfModal");
    const pdfViewer = document.getElementById("pdfViewer");

    // Función para detectar si el usuario está en un móvil
    function isMobile() {
        return /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);
    }

    openModalBtns.forEach(btn => {
        btn.addEventListener("click", function(event) {
            event.preventDefault();
            const pdfUrl = btn.getAttribute("data-pdf-url");

            if (isMobile()) {
                // Si es un dispositivo móvil, descargar el archivo
                const link = document.createElement("a");
                link.href = pdfUrl;
                link.download = pdfUrl.split("/").pop(); // Intenta sugerir un nombre de archivo
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } else {
                // Si es una PC, mostrar en el modal
                pdfViewer.src = pdfUrl;
                modal.style.display = "flex";
            }
        });
    });

    // Cerrar el modal
    const closeModalBtn = document.querySelector(".btn-close");
    closeModalBtn.addEventListener("click", function() {
        modal.style.display = "none";
        pdfViewer.src = "";  // Limpiar la vista previa cuando se cierre
    });

    // Cerrar el modal si el usuario hace clic fuera del modal
    window.addEventListener("click", function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
            pdfViewer.src = "";  
        }
    });
});
