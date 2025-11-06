// Espera o DOM carregar antes de rodar
document.addEventListener("DOMContentLoaded", () => {
    
    /* MUDANÇA AQUI:
      A função 'loadComponent' foi REMOVIDA daqui.
      O Jinja2 ({% include ... %}) no arquivo .html 
      agora faz esse trabalho no servidor.
    */
    console.log("Script 'cadastro.js' carregado. Lógica do formulário (ViaCEP, etc.) ativa.");

    // --- Início da Lógica do Formulário de Doador ---
    // (Esta parte permanece igual, pois é JavaScript puro do lado do cliente)

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