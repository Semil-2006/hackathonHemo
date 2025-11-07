// scripts/campanhas.js - Script específico para a página de campanhas

// Carrega componentes e inicializa a página
document.addEventListener("DOMContentLoaded", () => {
    // header/footer are included server-side via Jinja includes in the templates.
    // Avoid client-side fetch attempts to load template components (they returned 404).
    // If you prefer client-side loading, move the snippets into `static/` and call loadComponent with the static path.
    // Inicializa as funcionalidades da página
    inicializarPaginaCampanhas();
});

function inicializarPaginaCampanhas() {
    // Carrega as campanhas do storage
    carregarCampanhasDoStorage();
    
    // Atualiza estatísticas
    atualizarEstatisticas();
}

function carregarCampanhasDoStorage() {
    const campanhas = JSON.parse(localStorage.getItem('campanhas')) || [];
    // the template uses a <tbody id="campanhasTableBody"> — target that element
    const tabela = document.getElementById('campanhasTableBody');
    
    const campanhasAtivas = campanhas.filter(campanha => campanha.ativa);
    
    if (campanhasAtivas.length === 0) {
        // Campanhas padrão caso não haja nenhuma criada
        tabela.innerHTML = `
            <tr class="table-row">
                <th scope="row" class="px-6 py-4 font-medium whitespace-nowrap">Sangue pela Vida</th>
                <td class="px-6 py-4">O+</td>
                <td class="px-6 py-4">
                    <button onclick="participarCampanha(this, 'Sangue pela Vida', 'O+')" class="font-medium text-red-600 hover:text-red-800 hover:underline">Participar</button>
                </td>
            </tr>
            <tr class="table-row">
                <th scope="row" class="px-6 py-4 font-medium whitespace-nowrap">Doe Esperança</th>
                <td class="px-6 py-4">A-</td>
                <td class="px-6 py-4">
                    <button onclick="participarCampanha(this, 'Doe Esperança', 'A-')" class="font-medium text-red-600 hover:text-red-800 hover:underline">Participar</button>
                </td>
            </tr>
            <tr class="table-row">
                <th scope="row" class="px-6 py-4 font-medium whitespace-nowrap">Gotas de Solidariedade</th>
                <td class="px-6 py-4">B+</td>
                <td class="px-6 py-4">
                    <button onclick="participarCampanha(this, 'Gotas de Solidariedade', 'B+')" class="font-medium text-red-600 hover:text-red-800 hover:underline">Participar</button>
                </td>
            </tr>
            <tr class="table-row">
                <th scope="row" class="px-6 py-4 font-medium whitespace-nowrap">Hemocentro Unificado</th>
                <td class="px-6 py-4">AB-</td>
                <td class="px-6 py-4">
                    <button onclick="participarCampanha(this, 'Hemocentro Unificado', 'AB-')" class="font-medium text-red-600 hover:text-red-800 hover:underline">Participar</button>
                </td>
            </tr>
            <tr class="table-row">
                <th scope="row" class="px-6 py-4 font-medium whitespace-nowrap">Campanha Emergencial</th>
                <td class="px-6 py-4">O- (Doador Universal)</td>
                <td class="px-6 py-4">
                    <button onclick="participarCampanha(this, 'Campanha Emergencial', 'O-')" class="font-medium text-red-600 hover:text-red-800 hover:underline">Participar</button>
                </td>
            </tr>
        `;
    } else {
        tabela.innerHTML = campanhasAtivas.map(campanha => `
            <tr class="table-row">
                <th scope="row" class="px-6 py-4 font-medium whitespace-nowrap">${campanha.nome}</th>
                <td class="px-6 py-4">${campanha.tipoSanguineo}</td>
                <td class="px-6 py-4">
                    <button onclick="participarCampanha(this, '${campanha.nome}', '${campanha.tipoSanguineo}')" 
                            class="font-medium text-red-600 hover:text-red-800 hover:underline">
                        Participar
                    </button>
                </td>
            </tr>
        `).join('');
    }
}

function atualizarEstatisticas() {
    const campanhas = JSON.parse(localStorage.getItem('campanhas')) || [];
    const campanhasAtivas = campanhas.filter(c => c.ativa);
    
    document.getElementById('totalCampanhas').textContent = campanhasAtivas.length;
    document.getElementById('totalParticipantes').textContent = calcularTotalParticipantes();
    document.getElementById('vagasDisponiveis').textContent = calcularVagasDisponiveis();
}

function calcularTotalParticipantes() {
    // Simulação - na implementação real, puxaria do banco de dados
    const participantesPorCampanha = JSON.parse(localStorage.getItem('participantesCampanhas')) || {};
    return Object.values(participantesPorCampanha).reduce((total, participantes) => total + participantes.length, 0);
}

function calcularVagasDisponiveis() {
    // Simulação - 50 vagas por campanha
    const campanhas = JSON.parse(localStorage.getItem('campanhas')) || [];
    const campanhasAtivas = campanhas.filter(c => c.ativa);
    return campanhasAtivas.length * 50;
}

// Função para quando o usuário participar de uma campanha (chamada pelo list_campanhas.js)
function usuarioParticipou(nomeCampanha) {
    // Atualiza estatísticas quando um usuário participa
    setTimeout(atualizarEstatisticas, 100);
    
    // Mostra feedback adicional
    mostrarFeedbackParticipacao(nomeCampanha);
}

function mostrarFeedbackParticipacao(nomeCampanha) {
    const feedbackDiv = document.createElement('div');
    feedbackDiv.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    feedbackDiv.innerHTML = `
        <div class="flex items-center">
            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            Inscrição confirmada na campanha: <strong>${nomeCampanha}</strong>
        </div>
    `;
    
    document.body.appendChild(feedbackDiv);
    
    setTimeout(() => {
        feedbackDiv.remove();
    }, 4000);
}