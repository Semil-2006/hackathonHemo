// =======================================================================
// === campanhas_admin.js: Lógica de Gerenciamento de Campanhas (Admin) ===
// =======================================================================

// Variável global para o modal de edição
const modal = document.getElementById('editModal');

// =======================================================================
// 1. Inicialização e Listeners
// =======================================================================

document.addEventListener("DOMContentLoaded", () => {
    // 1. Carrega a tabela de campanhas assim que a página abre
    carregarCampanhasAdmin();

    // 2. Adiciona o listener para o formulário de CRIAÇÃO
    const formCriar = document.getElementById('formCriarCampanha');
    if (formCriar) {
        // Garante que o campo 'vagas' existe antes de tentar submeter
        if (formCriar.elements['vagas']) {
            formCriar.addEventListener('submit', handleCriarCampanha);
        } else {
            console.error("ERRO: Campo 'vagas' faltando no formulário de criação.");
        }
    }

    // 3. Adiciona o listener para a barra de PESQUISA (Filtro)
    const filtro = document.getElementById('filtroCampanha');
    if (filtro) {
        filtro.addEventListener('input', handlePesquisar);
    }

    // 4. Adiciona listener para fechar o modal ao clicar fora dele (opcional)
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                fecharModalEdicao();
            }
        });
    }
});


// =======================================================================
// 2. Operação R (Read/Leitura)
// =======================================================================

/**
 * Busca as campanhas da API e preenche a tabela de gerenciamento.
 */
async function carregarCampanhasAdmin() {
    const tableBody = document.getElementById('tabelaAdminCampanhas');
    if (!tableBody) return;

    // Feedback visual de carregamento
    tableBody.innerHTML = '<tr><td colspan="5" class="table-loading">Carregando...</td></tr>';

    try {
        const response = await fetch('/api/campanhas');
        if (!response.ok) throw new Error(`HTTP Erro: ${response.status} ao buscar campanhas.`);
        
        // A API deve retornar um objeto, por exemplo: { "campanhas": [...] }
        const data = await response.json();
        const campanhas = data.campanhas || []; // Usa '[]' como fallback

        // Limpa a tabela
        tableBody.innerHTML = '';

        if (campanhas.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="table-loading">Nenhuma campanha cadastrada.</td></tr>';
            return;
        }

        // Preenche a tabela com as linhas geradas
        campanhas.forEach(c => {
            const tr = document.createElement('tr');
            tr.className = 'table-row';
            // Adiciona atributos de dados para o filtro local
            tr.setAttribute('data-id', c.id);
            tr.setAttribute('data-nome', c.nome.toLowerCase());
            tr.setAttribute('data-tipo', c.tipo_sanguineo.toLowerCase());
            
            tr.innerHTML = `
                <td class="table-data-strong">${c.nome}</td>
                <td class="table-data">${c.tipo_sanguineo}</td>
                <td class="table-data">${c.vagas}</td>
                <td class="table-data">${c.participantes}</td>
                <td class="table-data table-actions">
                    <a href="#" onclick="abrirModalEdicao(${c.id}, '${c.nome.replace(/'/g, "\\'")}', '${c.tipo_sanguineo}', ${c.vagas}, '${c.status}')" class="action-button-edit">Editar</a>
                    <a href="#" onclick="handleRemoverCampanha(${c.id})" class="action-button-delete">Remover</a>
                </td>
            `;
            tableBody.appendChild(tr);
        });

    } catch (error) {
        console.error("Erro ao carregar campanhas:", error);
        tableBody.innerHTML = '<tr><td colspan="5" class="table-loading">Erro ao carregar campanhas. Verifique o console.</td></tr>';
    }
}


// =======================================================================
// 3. Operação C (Create/Criação)
// =======================================================================

/**
 * Intercepta o formulário de criação, valida os dados e envia para a API (POST).
 */
async function handleCriarCampanha(event) {
    event.preventDefault(); // Impede o recarregamento da página
    
    const form = event.target;
    const nome = form.elements['nome'].value;
    const tipo_sanguineo = form.elements['tipo_sanguineo'].value;
    const vagas = form.elements['vagas'].value;

    if (!nome || !tipo_sanguineo || !vagas || parseInt(vagas) < 1) {
        alert("Preencha todos os campos e garanta que as vagas são um número positivo.");
        return;
    }

    try {
        const response = await fetch('/api/campanhas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nome: nome,
                tipo_sanguineo: tipo_sanguineo,
                vagas: parseInt(vagas) // Envia vagas para a API
            })
        });

        if (!response.ok) throw new Error(`Falha ao criar campanha: ${response.statusText}`);

        const novaCampanha = await response.json();
        alert(`Campanha "${novaCampanha.campanha.nome}" criada com sucesso!`);
        console.log('Campanha criada:', novaCampanha);

        // Limpa o formulário e recarrega a tabela
        form.reset();
        carregarCampanhasAdmin();

    } catch (error) {
        console.error("Erro ao criar campanha:", error);
        alert('Erro ao criar campanha. Tente novamente.');
    }
}


// =======================================================================
// 4. Operação D (Delete/Remoção)
// =======================================================================

/**
 * Envia uma requisição DELETE para a API para remover uma campanha.
 * @param {number} id - ID da campanha a ser removida.
 */
async function handleRemoverCampanha(id) {
    if (!confirm('Tem certeza que deseja remover esta campanha? Esta ação não pode ser desfeita.')) {
        return;
    }

    try {
        const response = await fetch(`/api/campanhas/${id}`, {
            method: 'DELETE',
        });

        if (!response.ok) throw new Error(`Falha ao remover campanha: ${response.statusText}`);

        const result = await response.json();
        alert(result.mensagem || 'Campanha removida com sucesso!');
        console.log('Campanha removida:', result);

        // Recarrega a tabela para refletir a mudança
        carregarCampanhasAdmin();

    } catch (error) {
        console.error("Erro ao remover campanha:", error);
        alert('Erro ao remover campanha. Verifique o console.');
    }
}


// =======================================================================
// 5. Lógica de Pesquisa (Filtro Client-Side)
// =======================================================================

/**
 * Filtra as linhas da tabela localmente com base no texto de busca.
 */
function handlePesquisar(event) {
    const filtro = event.target.value.toLowerCase().trim();
    // Seleciona todas as linhas de dados (tr.table-row)
    const linhas = document.querySelectorAll('#tabelaAdminCampanhas tr.table-row'); 

    linhas.forEach(linha => {
        // Usa os atributos 'data-' criados na função carregarCampanhasAdmin
        const nome = linha.getAttribute('data-nome') || '';
        const tipo = linha.getAttribute('data-tipo') || '';
        
        // Verifica se o filtro está contido no nome OU no tipo sanguíneo
        if (nome.includes(filtro) || tipo.includes(filtro)) {
            linha.style.display = ''; // Mostra a linha
        } else {
            linha.style.display = 'none'; // Esconde a linha
        }
    });
}


// =======================================================================
// 6. Lógica do Modal de Edição (Operação U - Update/Atualização)
// =======================================================================

/**
 * Preenche os campos do modal com os dados da campanha selecionada e o exibe.
 */
function abrirModalEdicao(id, nome, tipo, vagas, status) {
    if (!modal) {
        console.error("Modal de edição não encontrado (ID: editModal).");
        return;
    }

    // Preenche os campos do modal (usa ID para encontrar os inputs)
    document.getElementById('editCampanhaId').value = id;
    document.getElementById('editNome').value = nome;
    document.getElementById('editTipoSanguineo').value = tipo;
    document.getElementById('editVagas').value = vagas;
    document.getElementById('editStatus').value = status;
    
    // Mostra o modal (Ajusta o CSS para 'flex' ou 'block' dependendo de como você definiu 'active')
    // No seu código original, você usou 'modal.style.display = 'flex';'
    modal.style.display = 'flex'; 
}

/**
 * Esconde o modal de edição.
 */
function fecharModalEdicao() {
    if (!modal) return;
    modal.style.display = 'none';
}

/**
 * Captura os dados do modal e envia uma requisição PUT para a API para atualizar a campanha.
 */
async function salvarEdicao() {
    const id = document.getElementById('editCampanhaId').value;
    const nome = document.getElementById('editNome').value;
    const tipo_sanguineo = document.getElementById('editTipoSanguineo').value;
    const vagas = document.getElementById('editVagas').value;
    const status = document.getElementById('editStatus').value;
    
    if (!nome || !tipo_sanguineo || !id || parseInt(vagas) < 1) {
         alert("Preencha todos os campos do modal corretamente.");
         return;
    }

    try {
        const response = await fetch(`/api/campanhas/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nome: nome,
                tipo_sanguineo: tipo_sanguineo,
                vagas: parseInt(vagas),
                status: status
            })
        });

        if (!response.ok) throw new Error(`Falha ao salvar alterações: ${response.statusText}`);
        
        const campanhaAtualizada = await response.json();
        alert(campanhaAtualizada.mensagem || 'Campanha atualizada com sucesso!');
        console.log('Resposta da atualização:', campanhaAtualizada);

        // Fecha o modal e recarrega a tabela
        fecharModalEdicao();
        carregarCampanhasAdmin();

    } catch (error) {
        console.error("Erro ao salvar alterações:", error);
        alert('Erro ao salvar alterações. Verifique o console.');
    }
}