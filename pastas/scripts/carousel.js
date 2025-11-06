document.addEventListener("DOMContentLoaded", () => {
  const carouselContainer = document.getElementById("partners-carousel");

  // Verifica se o container existe
  if (!carouselContainer) {
    console.error("Erro: elemento #partners-carousel não encontrado no DOM.");
    return;
  }

  const carousel = carouselContainer.querySelector(".carousel");

  // Verifica se o carrossel interno existe
  if (!carousel) {
    console.error("Erro: elemento .carousel não encontrado dentro de #partners-carousel.");
    return;
  }

  const items = carousel.querySelectorAll(".carousel-item");
  const totalItems = items.length;
  let index = 0;
  let interval;

  // Se não houver itens, não inicia o carrossel
  if (totalItems === 0) {
    console.warn("Aviso: nenhum item encontrado no carrossel.");
    return;
  }

  function showNextSlide() {
    index++;
    const visibleItems =
      window.innerWidth >= 768 ? 4 : window.innerWidth >= 480 ? 2 : 1;

    if (index > totalItems - visibleItems) index = 0;

    carousel.style.transform = `translateX(-${index * (100 / visibleItems)}%)`;
  }

  function startCarousel() {
    interval = setInterval(showNextSlide, 2500);
  }

  function stopCarousel() {
    clearInterval(interval);
  }

  carouselContainer.addEventListener("mouseenter", stopCarousel);
  carouselContainer.addEventListener("mouseleave", startCarousel);

  startCarousel();

  console.log("Carrossel iniciado com sucesso!");
});
