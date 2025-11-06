// Encapsula a inicialização do carrossel em uma função
function initCarousel() {
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

  // Se não houver itens, não inicia o carrossel
  if (items.length === 0) {
    console.warn("Aviso: nenhum item encontrado no carrossel.");
    return;
  }

  // Evita inicializar mais de uma vez
  if (carousel.dataset.inited === 'true') return;
  carousel.dataset.inited = 'true';

  // Remover qualquer transition para animarmos manualmente via JS
  carousel.style.transition = 'none';

  // Clona o conteúdo para permitir um loop contínuo e suave
  if (carousel.dataset.cloned !== 'true') {
    const html = carousel.innerHTML;
    carousel.innerHTML += html; // duplica os itens
    carousel.dataset.cloned = 'true';
  }

  // Largura do conjunto original (metade do scrollWidth após clone)
  let originalWidth = carousel.scrollWidth / 2;
  let offset = 0; // deslocamento em pixels
  let lastTime = null;
  let rafId = null;
  let paused = false;

  // velocidade em pixels por segundo (ajuste aqui se quiser mais rápido/lento)
  const speed = 80;

  function step(timestamp) {
    if (paused) {
      lastTime = null;
      rafId = requestAnimationFrame(step);
      return;
    }
    if (!lastTime) lastTime = timestamp;
    const delta = timestamp - lastTime;
    lastTime = timestamp;

    offset += (speed * delta) / 1000;
    if (offset >= originalWidth) {
      // loop: subtrai originalWidth para ficar contínuo
      offset -= originalWidth;
    }

    carousel.style.transform = `translateX(-${offset}px)`;
    rafId = requestAnimationFrame(step);
  }

  function start() {
    if (rafId) return;
    paused = false;
    lastTime = null;
    rafId = requestAnimationFrame(step);
  }

  function pause() {
    paused = true;
    if (rafId) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
  }

  // Pausa quando o mouse entra, retoma quando sai
  carouselContainer.addEventListener('mouseenter', pause);
  carouselContainer.addEventListener('mouseleave', () => { start(); });

  // Recalcula larguras quando a janela muda de tamanho ou imagens carregam
  function recompute() {
    originalWidth = carousel.scrollWidth / 2;
  }
  window.addEventListener('resize', recompute);
  window.addEventListener('load', recompute);
  // também recalcula quando imagens do carrossel terminam de carregar
  carousel.querySelectorAll('img').forEach(img => img.addEventListener('load', recompute));

  // Inicia a animação
  start();
  console.log('Carrossel contínuo iniciado com sucesso!');
}

// Se o componente for carregado dinamicamente por `global.js`, ele dispara um evento
// 'componentLoaded' com { detail: { id } }. Escutamos esse evento para iniciar o carrossel
document.addEventListener('componentLoaded', (e) => {
  if (e && e.detail && e.detail.id === 'carousel') {
    // Pequeno timeout para garantir que o HTML já foi inserido/inicializado
    setTimeout(() => initCarousel(), 0);
  }
});

// Caso o componente já esteja presente (por exemplo se scripts foram executados em outra ordem), inicializa imediatamente
if (document.getElementById('partners-carousel')) {
  // Defer para próxima iteração do loop de eventos
  setTimeout(() => initCarousel(), 0);
}
