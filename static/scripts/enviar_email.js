/* * Código para a página: enviar_email.html (RF03)
 * Responsável por:
 * 1. Inicializar o editor de texto (Quill.js)
 * 2. Alternar entre formulário de E-mail e WhatsApp
 * 3. Coletar dados do formulário e enviar (simulação) ao backend
 */

// Espera o HTML ser totalmente carregado antes de executar
document.addEventListener('DOMContentLoaded', function() {

    // --- 1. Inicializa o Editor de Texto (Critério 3 do RF03) ---
    const quill = new Quill('#editor-container', {
        theme: 'snow', 
        modules: {
            toolbar: [
                ['bold', 'italic', 'underline', 'link'], 
                [{ 'size': ['small', false, 'large', 'huge'] }],
                [{ 'header': 1 }, { 'header': 2 }],
                [{ 'list': 'ordered'}, { 'list': 'bullet' }]
            ]
        }
    });

    // --- 2. Lógica para alternar formulários (E-mail vs WhatsApp) ---

    // Encontra os elementos no HTML
    const radioEmail = document.getElementById('channel-type-email');
    const radioWhatsApp = document.getElementById('channel-type-whatsapp');
    const formEmail = document.getElementById('form-for-email');
    const formWhatsApp = document.getElementById('form-for-whatsapp');

    // Adiciona os "escutadores" de clique nos botões de rádio
    if(radioEmail) {
        radioEmail.addEventListener('click', function() {
            formEmail.style.display = 'block';      // MOSTRA o form de email
            formWhatsApp.style.display = 'none';    // ESCONDE o form de WhatsApp
        });
    }

    if(radioWhatsApp) {
        radioWhatsApp.addEventListener('click', function() {
            formEmail.style.display = 'none';       // ESCONDE o form de email
            formWhatsApp.style.display = 'block';     // MOSTRA o form de WhatsApp
        });
    }

    // --- 3. Adiciona os "escutadores" de clique aos botões de envio ---
    const btnEnviar = document.getElementById('btn-enviar-agora');
    const btnAgendar = document.getElementById('btn-agendar');

    if (btnEnviar) {
        btnEnviar.addEventListener('click', function() {
            enviarCampanha(false, quill); // Envia agora
        });
    }

    if (btnAgendar) {
        btnAgendar.addEventListener('click', function() {
            enviarCampanha(true, quill); // Agenda
        });
    }

}); // Fim do 'DOMContentLoaded'


/**
 * Função principal para coletar dados e enviar ao backend.
 * @param {boolean} agendado - Define se a campanha é agendada ou não.
 * @param {object} quillInstance - A instância do editor Quill.
 */
function enviarCampanha(agendado, quillInstance) {
    
    // --- 1. Coleta do Canal de Disparo ---
    const canalSelecionado = document.querySelector('input[name="channel-type"]:checked').value;
    
    // --- 2. Coleta do Conteúdo ---
    let conteudo;
    if (canalSelecionado === 'email') {
        // Coleta o conteúdo HTML de dentro do editor Quill
        conteudo = quillInstance.root.innerHTML;
    } else {
        // Coleta o texto simples do <textarea>
        conteudo = document.getElementById('whatsapp-message').value;
    }

    // --- 3. Coleta da Segmentação (Critério 1) ---
    const segmentacao = {
        tipo_sanguineo: getSelectedOptions('seg-tipo-sanguineo'),
        cidade: getSelectedOptions('seg-cidade'),
        classificacao: document.getElementById('seg-classificacao').value,
        interesse: document.getElementById('seg-interesse').value,
        genero: (document.getElementById('seg-genero') ? document.getElementById('seg-genero').value : ''),
        min_age: (document.getElementById('seg-min-age') && document.getElementById('seg-min-age').value) ? Number(document.getElementById('seg-min-age').value) : null,
        max_age: (document.getElementById('seg-max-age') && document.getElementById('seg-max-age').value) ? Number(document.getElementById('seg-max-age').value) : null
    };

    // --- 4. Coleta do Remetente (E-mail) e Agendamento (Critério 3) ---
    const remetente = (canalSelecionado === 'email') ? document.getElementById('msg-remetente').value : null;
    const agendamentoData = agendado ? document.getElementById('camp-agendamento').value : null;

    if (agendado && !agendamentoData) {
        alert('Por favor, selecione uma data para o agendamento.');
        return; 
    }
    
    // Objeto final para enviar ao backend
    const dadosCampanha = {
        canal_disparo: canalSelecionado,
        remetente: remetente,
        conteudo: conteudo,
        segmentacao: segmentacao,
        agendamento: agendamentoData
    };

    // Linha de DEBUG: Mostra no console do navegador o JSON que será enviado.
    console.log("Enviando para o backend:", JSON.stringify(dadosCampanha, null, 2));

    // Envia para o backend o job de envio de campanha.
    fetch('/api/admin/send_campaign', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin',
        body: JSON.stringify(dadosCampanha)
    })
    .then(async (response) => {
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            console.error('Erro ao enviar campanha:', data);
            alert('Erro ao enviar campanha: ' + (data.error || response.statusText));
            return;
        }
        alert(`Campanha enviada. E-mails enviados: ${data.sent || 0}. Falhas: ${data.failed ? data.failed.length : 0}`);
    })
    .catch((error) => {
        console.error('Erro:', error);
        alert('Erro ao enviar campanha. Veja o console para detalhes.');
    });
}


/**
 * Função auxiliar para pegar valores de um <select multiple>.
 * @param {string} selectId - O ID do elemento <select>.
 * @returns {Array} Um array com os valores selecionados.
 */
function getSelectedOptions(selectId) {
    const select = document.getElementById(selectId);
    if (!select) return [];
    
    return Array.from(select.selectedOptions).map(option => option.value);
}