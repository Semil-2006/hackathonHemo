// Espera o DOM carregar antes de rodar
document.addEventListener("DOMContentLoaded", () => {
    
    // Verifica se a função 'loadComponent' foi carregada (do global.js)
    if (typeof loadComponent === 'function') {
        
        // Carrega os componentes globais
        loadComponent("header-placeholder", "components/header.html");
        loadComponent("footer-placeholder", "components/footer.html");

    } else {
        console.error("A função 'loadComponent' não foi encontrada. Verifique se 'global.js' está sendo carregado corretamente.");
    }

    // Nenhuma lógica extra de formulário é necessária para a página de login por enquanto.
});