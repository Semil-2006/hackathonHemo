// static/scripts/global.js
function loadComponent(componentId, url) {
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erro ao carregar ${url}: ${response.statusText}`);
            }
            return response.text();
        })
        .then(data => {
            document.getElementById(componentId).innerHTML = data;
        })
        .catch(error => {
            console.error(`Erro ao carregar componente ${componentId}:`, error);
        });
}