document.addEventListener("DOMContentLoaded", () => {
    // 1. Carrega a tabela de campanhas assim que a página abre
    carregarCampanhasAdmin();

    // 2. Adiciona o listener para o formulário de CRIAÇÃO
    const formCriar = document.getElementById('formCriarCampanha');
    if (formCriar) {
        formCriar.addEventListener('submit', handleCriarCampanha);
    }

    // 3. Adiciona o listener para a barra de PESQUISA
    const filtro = document.getElementById('filtroCampanha');
    if (filtro) {
        filtro.addEventListener('input', handlePesquisar);
    }
});

/**
 * Busca as campanhas da API e preenche a tabela de gerenciamento.
 */
async function carregarCampanhasAdmin() {
    const tableBody = document.getElementById('tabelaAdminCampanhas');
    if (!tableBody) return;

    tableBody.innerHTML = '<tr><td colspan="5" class="table-loading">Carregando...</td></tr>';

    try {
        const response = await fetch('/api/campanhas');
        if (!response.ok) throw new Error('Erro ao buscar campanhas.');
        
        const data = await response.json();
        const campanhas = data.campanhas;

        // Limpa a tabela
        tableBody.innerHTML = '';

        if (campanhas.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="table-loading">Nenhuma campanha cadastrada.</td></tr>';
            return;
        }

        // Preenche a tabela
        campanhas.forEach(c => {
            const tr = document.createElement('tr');
            tr.className = 'table-row';
            tr.setAttribute('data-nome', c.nome.toLowerCase());
            tr.setAttribute('data-tipo', c.tipo_sanguineo.toLowerCase());
            
            tr.innerHTML = `
                <td class="table-data-strong">${c.nome}</td>
                <td class="table-data">${c.tipo_sanguineo}</td>
                <td class="table-data">${c.vagas}</td>
                <td class="table-data">${c.participantes}</td>
                <td class="table-data">
                    <a href="#" onclick="abrirModalEdicao(${c.id}, '${c.nome}', '${c.tipo_sanguineo}', ${c.vagas}, '${c.status}')" class="action-button-edit">Editar</a>
                    <a href="#" onclick="handleRemoverCampanha(${c.id})" class="action-button-delete">Remover</a>
                </td>
            `;
            tableBody.appendChild(tr);
        });

    } catch (error) {
        console.error(error);
        tableBody.innerHTML = '<tr><td colspan="5" class="table-loading">Erro ao carregar campanhas.</td></tr>';
    }
}

/**
 * Intercepta o formulário de criação e envia para a API.
 */
async function handleCriarCampanha(event) {
    event.preventDefault(); // Impede o recarregamento da página
    
    const form = event.target;
    const nome = form.elements['nome'].value;
    const tipo_sanguineo = form.elements['tipo_sanguineo'].value;
    const vagas = form.elements['vagas'].value;

    try {
        const response = await fetch('/api/campanhas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                nome: nome,
                tipo_sanguineo: tipo_sanguineo,
                vagas: parseInt(vagas)
            })
        });

        if (!response.ok) throw new Error('Falha ao criar campanha.');

        const novaCampanha = await response.json();
        console.log('Campanha criada:', novaCampanha);

        // Limpa o formulário e recarrega a tabela
        form.reset();
        carregarCampanhasAdmin();

    } catch (error) {
        console.error(error);
        alert('Erro ao criar campanha. Tente novamente.');
    }
}

/**
 * Envia uma requisição DELETE para a API.
 */
async function handleRemoverCampanha(id) {
    if (!confirm('Tem certeza que deseja remover esta campanha? Esta ação não pode ser desfeita.')) {
        return;
    }

    try {
        const response = await fetch(`/api/campanhas/${id}`, {
            method: 'DELETE',
        });

        if (!response.ok) throw new Error('Falha ao remover campanha.');

        const result = await response.json();
        console.log('Campanha removida:', result);

        // Recarrega a tabela
        carregarCampanhasAdmin();

    } catch (error) {
        console.error(error);
        alert('Erro ao remover campanha.');
    }
}

/**
 * Filtra a tabela localmente (client-side)
 */
function handlePesquisar(event) {
    const filtro = event.target.value.toLowerCase();
    const linhas = document.querySelectorAll('#tabelaAdminCampanhas tr');

    linhas.forEach(linha => {
        const nome = linha.getAttribute('data-nome') || '';
        const tipo = linha.getAttribute('data-tipo') || '';
        
        if (nome.includes(filtro) || tipo.includes(filtro)) {
            linha.style.display = ''; // Mostra a linha
        } else {
            linha.style.display = 'none'; // Esconde a linha
        }
    });
}


// --- Lógica do Modal de Edição ---

const modal = document.getElementById('editModal');

function abrirModalEdicao(id, nome, tipo, vagas, status) {
    if (!modal) return;

    // Preenche o formulário do modal com os dados atuais
    document.getElementById('editCampanhaId').value = id;
    document.getElementById('editNome').value = nome;
    document.getElementById('editTipoSanguineo').value = tipo;
    document.getElementById('editVagas').value = vagas;
    document.getElementById('editStatus').value = status;
    
    // Mostra o modal
    modal.style.display = 'flex';
}

function fecharModalEdicao() {
    if (!modal) return;
    modal.style.display = 'none';
}

async function salvarEdicao() {
    const id = document.getElementById('editCampanhaId').value;
    const nome = document.getElementById('editNome').value;
    const tipo_sanguineo = document.getElementById('editTipoSanguineo').value;
    const vagas = document.getElementById('editVagas').value;
    const status = document.getElementById('editStatus').value;
    
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

        if (!response.ok) throw new Error('Falha ao salvar alterações.');
        
        const campanhaAtualizada = await response.json();
        console.log('Campanha atualizada:', campanhaAtualizada);

        // Fecha o modal e recarrega a tabela
        fecharModalEdicao();
        carregarCampanhasAdmin();

    } catch (error) {
        console.error(error);
        alert('Erro ao salvar alterações.');
    }
}