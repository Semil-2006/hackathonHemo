// Espera o DOM carregar antes de rodar
document.addEventListener("DOMContentLoaded", () => {
    
    // 1. Carrega os componentes (header/footer)
    if (typeof loadComponent === 'function') {
        
        // Carrega os componentes globais
        loadComponent("header", "components/header.html");
        loadComponent("footer", "components/footer.html");

    } else {
        console.error("A função 'loadComponent' não foi encontrada. Verifique se 'global.js' está sendo carregado corretamente.");
    }
    
    // 2. Chama a nova função para carregar os dados do perfil
    carregarDadosDoPerfil();
});

// --- Esta é a nova função ---
async function carregarDadosDoPerfil() {
    try {
        // ETAPA 2: Busca os dados da sua API (EXEMPLO)
        // Você precisará substituir pelo endpoint real da sua API.
        
        // --- INÍCIO DOS DADOS DE EXEMPLO ---
        // ATUALIZE OS CAMINHOS DAS IMAGENS para apontar para sua pasta 'assets/'
        const dadosSimulados = {
            nome: "Ana Clara Silva",
            email: "ana.silva@email.com",
            telefone: "(61) 98877-6655",
            dataNascimento: "15/05/1992",
            genero: "Feminino",
            cep: "70000-000",
            enderecoCompleto: "SQN 210, Bloco A, Apto 301 - Brasília/DF",
            tipoSanguineo: "A+",
            jaDoou: true,
            primeiraVez: "10/01/2023",
            nivel: "Doador Iniciante",
            progressoPercentual: 33,
            selos: [
                { nome: "Primeira Doação", caminhoImagem: "assets/emblemas/1.png" },
                { nome: "Compromisso (3 Doações)", caminhoImagem: "assets/emblemas/2.png" }
            ]
        };
        // --- FIM DOS DADOS DE EXEMPLO ---
        
        // const response = await fetch('/api/usuario/123'); // API REAL IRIA AQUI
        // const data = await response.json(); // API REAL IRIA AQUI
        const data = dadosSimulados; // Usando os dados simulados

        // ETAPA 3: Preenche os placeholders do HTML
        
        // Informações Pessoais
        document.getElementById('user-name').textContent = data.nome;
        document.getElementById('user-email').textContent = data.email;
        document.getElementById('user-phone').textContent = data.telefone;
        document.getElementById('user-dob').textContent = data.dataNascimento;
        document.getElementById('user-gender').textContent = data.genero;

        // Endereço
        document.getElementById('user-cep').textContent = data.cep;
        document.getElementById('user-address').textContent = data.enderecoCompleto;

        // Informações de Doador
        document.getElementById('user-blood-type').textContent = data.tipoSanguineo;
        document.getElementById('user-has-donated').textContent = data.jaDoou ? 'Sim' : 'Não';
        
        // Esconde ou mostra o campo "primeira vez"
        const firstDonationEl = document.getElementById('first-donation-item');
        if (data.jaDoou && data.primeiraVez) {
            document.getElementById('user-first-donation').textContent = data.primeiraVez;
            firstDonationEl.style.display = 'grid'; // Mostra o campo (usando 'grid' para manter o layout)
        } else {
            firstDonationEl.style.display = 'none'; // Esconde o campo
        }

        // Gamificação
        const userLevelElement = document.getElementById('user-level');
        if (userLevelElement) {
             // Limpa o "Carregando..."
            userLevelElement.innerHTML = `
                <svg class="level-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg> 
                ${data.nivel}`;
        }
       
        document.getElementById('user-progress').style.width = data.progressoPercentual + '%';
        
        // Limpa os selos de exemplo e adiciona os reais
        const badgesContainer = document.getElementById('user-badges');
        badgesContainer.innerHTML = ''; // Limpa os placeholders
        
        if (data.selos && data.selos.length > 0) {
            data.selos.forEach(selo => {
                // Cria o container do selo
                const badgeEl = document.createElement('div');
                badgeEl.className = 'badge';
                badgeEl.title = selo.nome;
                
                // Cria a imagem
                const imgEl = document.createElement('img');
                imgEl.src = selo.caminhoImagem;
                imgEl.alt = selo.nome;
                imgEl.className = 'badge-image';
                // Adiciona um fallback caso a imagem não carregue
                imgEl.onerror = () => { imgEl.src = 'https://placehold.co/64x64/e0e0e0/b0b0b0?text=Selo'; };
                
                // Adiciona a imagem ao container do selo
                badgeEl.appendChild(imgEl);
                // Adiciona o selo ao container principal
                badgesContainer.appendChild(badgeEl);
            });
        } else {
            badgesContainer.innerHTML = '<p class="info-data">Nenhuma conquista ainda.</p>';
        }

    } catch (error) {
        console.error('Erro ao carregar dados do perfil:', error);
        // Coloca uma mensagem de erro na tela
        const profileContainer = document.getElementById('profile-container');
        if(profileContainer) {
            profileContainer.innerHTML = '<h1 class="profile-title">Erro ao carregar o perfil.</h1><p class="profile-subtitle">Por favor, tente novamente mais tarde.</p>';
        }
    }
}