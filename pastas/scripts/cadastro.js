// Espera o DOM carregar antes de rodar
document.addEventListener("DOMContentLoaded", () => {
    
    // Verifica se a função 'loadComponent' foi carregada (do global.js)
    if (typeof loadComponent === 'function') {
        
        // Carrega os componentes globais
        loadComponent("header", "components/header.html");
        loadComponent("footer", "components/footer.html");

    } else {
        console.error("A função 'loadComponent' não foi encontrada. Verifique se 'global.js' está sendo carregado corretamente.");
    }

    // --- Início da Lógica do Formulário de Doador ---

    // 1. Lógica da API ViaCEP
    const cepInput = document.getElementById('cep');
    const enderecoInput = document.getElementById('endereco');

    if (cepInput && enderecoInput) {
        cepInput.addEventListener('blur', async () => {
            const cep = cepInput.value.replace(/\D/g, ''); // Limpa o CEP
            if (cep.length === 8) {
                try {
                    // Define o campo como "buscando..."
                    enderecoInput.value = 'Buscando...';
                    
                    const res = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
                    
                    if (!res.ok) {
                        throw new Error('Falha ao buscar CEP');
                    }
                    
                    const data = await res.json();
                    
                    if (data.erro) {
                        enderecoInput.value = 'CEP não encontrado.';
                    } else {
                        // Preenche o endereço de forma mais completa
                        enderecoInput.value = `${data.logradouro}, ${data.bairro} - ${data.localidade}/${data.uf}`;
                    }
                } catch (error) {
                    console.error('Erro na API ViaCEP:', error);
                    enderecoInput.value = 'Erro ao buscar CEP.';
                }
            } else {
                // Limpa o campo se o CEP for inválido
                if (cep.length > 0) {
                    enderecoInput.value = 'CEP inválido.';
                } else {
                    enderecoInput.value = '';
                }
            }
        });
    }

    // 2. Lógica para mostrar/esconder campos condicionais
    const jaDoouSelect = document.getElementById('ja_doou');
    const perguntaSim = document.getElementById('pergunta_sim');
    const perguntaNao = document.getElementById('pergunta_nao');

    if (jaDoouSelect && perguntaSim && perguntaNao) {
        
        // Função interna para atualizar a visibilidade
        const togglePerguntas = () => {
            const val = jaDoouSelect.value;
            perguntaSim.style.display = val === 'sim' ? 'block' : 'none';
            perguntaNao.style.display = val === 'nao' ? 'block' : 'none';
        };

        // Adiciona o listener de 'change'
        jaDoouSelect.addEventListener('change', togglePerguntas);

        // Executa uma vez no carregamento para garantir que estejam escondidos
        togglePerguntas();
    }
});