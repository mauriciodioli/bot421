function agrandarImagenVideoPublicacion(tipo = 'imagen', url = '') {
  const modal = document.getElementById("media-modal");
  const img = document.getElementById("media-modal-img");
  const video = document.getElementById("media-modal-video");
  const iframe = document.getElementById("media-modal-iframe");

  // Ocultar todo primero
  img.style.display = "none";
  video.style.display = "none";
  iframe.style.display = "none";

  if (tipo === 'imagen') {
    img.src = url;
    img.style.display = "block";
  } else if (tipo === 'video') {
    video.src = url;
    video.style.display = "block";
    video.play();
  } else if (tipo === 'iframe') {
    iframe.src = url;
    iframe.style.display = "block";
  }

  modal.style.display = "block";
}

function cerrarModal() {
  document.getElementById("media-modal").style.display = "none";

  // Pausar y resetear
  const video = document.getElementById("media-modal-video");
  const iframe = document.getElementById("media-modal-iframe");

  video.pause();
  video.currentTime = 0;
  video.src = "";

  iframe.src = "";
}
