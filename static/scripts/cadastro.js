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

document.addEventListener("DOMContentLoaded", () => {
/**
 * scripts/formatador_numerico.js
 *
 * Função para formatar um campo de input para o padrão numérico brasileiro (telefone).
 *
 * Exemplo de uso no HTML:
 * <input type="text" id="telefone" oninput="formatarTelefone(this)" maxlength="15" placeholder="(99) 99999-9999" />
 */

/**
 * Aplica a máscara de telefone (xx) xxxxx-xxxx em tempo real.
 * @param {HTMLInputElement} input O elemento input a ser formatado.
 */
function formatarTelefone(input) {
    // 1. Remove tudo que não for dígito (garante que só números serão formatados)
    let value = input.value.replace(/\D/g, '');

    // 2. Limita o valor a 11 dígitos (incluindo o 9º dígito)
    if (value.length > 11) {
        value = value.substring(0, 11);
    }

    // 3. Aplica a máscara
    if (value.length > 0) {
        // (xx) xxxxx-xxxx ou (xx) xxxx-xxxx
        value = value.replace(/^(\d{2})(\d)/g, '($1) $2'); // Coloca parênteses e espaço (xx) x
        
        if (value.length > 9) { // Se tem mais de 5 dígitos (contando a máscara), insere o hífen
            if (value.length <= 14) {
                // Formato (xx) xxxx-xxxx (8º dígito)
                value = value.replace(/(\d{4})(\d)/, '$1-$2');
            } else {
                // Formato (xx) xxxxx-xxxx (9º dígito)
                value = value.replace(/(\d{5})(\d)/, '$1-$2');
            }
        }
    }

    // 4. Atualiza o valor do input
    input.value = value;
}

/**
 * Função utilitária para garantir que apenas dígitos são inseridos.
 * (Bloqueia a tecla pressionada se não for um número)
 * * @param {Event} event O evento keypress do input.
 */
function somenteNumeros(event) {
    const charCode = (event.which) ? event.which : event.keyCode;
    // 48 a 57 são os códigos para 0-9
    if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        // Impede a inserção de caracteres não numéricos
        event.preventDefault();
    }
}
}  );
