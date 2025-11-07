let campanhaSelecionada = null;
let botaoSelecionado = null;
let campanhasAtuais = [];
let minhasParticipacoesIds = new Set();

async function carregarCampanhas() {
  const body = document.getElementById('campanhasTableBody');
  body.innerHTML = '<tr class="table-row"><td colspan="3" class="table-loading">Carregando campanhas...</td></tr>';

  try {
  const res = await fetch('/api/campaigns');
    if (!res.ok) throw new Error('Falha ao buscar campanhas');
    const data = await res.json();
    campanhasAtuais = data.campaigns || [];

    // try to fetch my participations to mark buttons
  await carregarMinhasParticipacoes();

    renderizarTabela(campanhasAtuais);
    atualizarEstatisticas(campanhasAtuais);
  } catch (err) {
    console.error(err);
    body.innerHTML = '<tr class="table-row"><td colspan="3" class="table-loading">Não foi possível carregar campanhas.</td></tr>';
  }
}

function renderizarTabela(campanhas) {
  const body = document.getElementById('campanhasTableBody');
  body.innerHTML = '';
  if (!campanhas || campanhas.length === 0) {
    body.innerHTML = '<tr class="table-row"><td colspan="3" class="table-loading">Nenhuma campanha encontrada.</td></tr>';
    return;
  }

  campanhas.forEach(c => {
    const tr = document.createElement('tr');
    tr.className = 'table-row';

    const tdNome = document.createElement('td');
    tdNome.textContent = c.nome || '—';
    tdNome.className = 'table-cell';

    const tdTipo = document.createElement('td');
    tdTipo.textContent = c.tipo_sanguineo || 'Todos';
    tdTipo.className = 'table-cell';

    const tdAcao = document.createElement('td');
    tdAcao.className = 'table-cell';

    const btn = document.createElement('button');
    btn.className = 'participar-button';
    btn.textContent = c.status && c.status !== 'Ativa' ? 'Encerrada' : 'Participar';
    btn.disabled = c.status && c.status !== 'Ativa';
    btn.dataset.campaignId = c.id;

    if (minhasParticipacoesIds.has(String(c.id))) {
      btn.textContent = 'Participando ✓';
      btn.disabled = true;
      tr.classList.add('bg-green-50');
    } else if (c.status && c.status !== 'Ativa') {
      btn.classList.add('text-gray-400');
    } else {
      btn.onclick = () => participarCampanha(btn, c);
    }

    tdAcao.appendChild(btn);

    tr.appendChild(tdNome);
    tr.appendChild(tdTipo);
    tr.appendChild(tdAcao);
    body.appendChild(tr);
  });
}

function atualizarEstatisticas(campanhas) {
  const totalAtivas = campanhas.filter(c => (c.status || 'Ativa') === 'Ativa').length;
  const totalParticipantes = campanhas.reduce((s, c) => s + (parseInt(c.participantes) || 0), 0);
  const totalVagas = campanhas.reduce((s, c) => s + (parseInt(c.vagas) || 0), 0);

  document.getElementById('totalCampanhas').textContent = totalAtivas;
  document.getElementById('totalParticipantes').textContent = totalParticipantes;
  document.getElementById('vagasDisponiveis').textContent = Math.max(totalVagas - totalParticipantes, 0);
}

async function participarCampanha(botao, campanhaObj) {
  // Verifica se o usuário está autenticado antes de abrir o modal.
  // Assunção: existe um endpoint `/api/me` que retorna 200 com dados do usuário quando autenticado
  // e 401 quando não autenticado. Se esse endpoint for diferente no seu backend, ajuste a URL.
  try {
      const res = await fetch('/api/me', {
        method: 'GET',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json'
        },
        credentials: 'same-origin'
      });
    if (res.status === 401) {
      // Usuário não autenticado -> redireciona para a tela de login
      window.location.href = '/login';
      return;
    }
    // Se retornou outro erro, permitimos o fluxo (o backend também valida na confirmação).
  } catch (err) {
    // Se a verificação falhar por rede, deixamos o fluxo prosseguir e o servidor validará na confirmação.
    console.warn('Falha ao verificar autenticação:', err);
  }

  // Abre o modal de confirmação
  campanhaSelecionada = campanhaObj;
  botaoSelecionado = botao;

  // campanhaObj pode ser um objeto com campos (quando vindo da API) ou uma string (fallback estático).
  const nome = campanhaObj && (campanhaObj.nome || campanhaObj) || 'Campanha';
  const tipo = campanhaObj && (campanhaObj.tipo_sanguineo || campanhaObj.tipoSanguineo || '') || '';

  const modalMessage = `Você está prestes a participar da campanha:<br><strong>${nome}</strong><br><br>Tipo sanguíneo necessário: <strong>${tipo || 'Todos'}</strong>`;
  document.getElementById('modalMessage').innerHTML = modalMessage;
  // O CSS define `.modal-overlay { display: none }` por padrão,
  // então usamos style.display para mostrar o modal (flex para centralizar)
  const modalEl = document.getElementById('confirmModal');
  if (modalEl) modalEl.style.display = 'flex';
}

async function confirmarParticipacao() {
  if (!campanhaSelecionada) return fecharModal();
  const campaignId = campanhaSelecionada && campanhaSelecionada.id;
  try {
    if (campaignId) {
        const res = await fetch(`/api/campaigns/${campaignId}/participate`, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          credentials: 'same-origin'
      });
      if (res.status === 401) {
        // not logged in (session expired) -> redirect to login
        window.location.href = '/login';
        return;
      }
      if (res.status === 409) {
        // Already subscribed (server-side) - update UI accordingly
        if (botaoSelecionado) {
          botaoSelecionado.textContent = 'Participando ✓';
          botaoSelecionado.disabled = true;
          const linha = botaoSelecionado.closest('tr');
          if (linha) linha.classList.add('bg-green-50');
        }
        minhasParticipacoesIds.add(String(campaignId));
        mostrarMensagemSucesso('Você já está inscrito nesta campanha.');
        await carregarCampanhas();
        return;
      }
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Erro ao participar');

      // Update UI for API-backed campaign
      if (botaoSelecionado) {
        botaoSelecionado.textContent = 'Participando ✓';
        botaoSelecionado.disabled = true;
        botaoSelecionado.classList.add('text-green-600', 'font-bold');
        const linha = botaoSelecionado.closest('tr');
        if (linha) linha.classList.add('bg-green-50');
      }
    minhasParticipacoesIds.add(String(campaignId));
  mostrarMensagemSucesso(`Você agora está participando da campanha: ${campanhaSelecionada.nome}`, '/perfil');
      // refresh stats
      await carregarCampanhas();
    } else {
      // Fallback para campanhas estáticas (sem id): simulamos participação localmente
      if (botaoSelecionado) {
        botaoSelecionado.textContent = 'Participando ✓';
        botaoSelecionado.disabled = true;
        botaoSelecionado.classList.add('text-green-600', 'font-bold');
        const linha = botaoSelecionado.closest('tr');
        if (linha) linha.classList.add('bg-green-50');
      }
    mostrarMensagemSucesso(`Você agora está participando da campanha: ${campanhaSelecionada && (campanhaSelecionada.nome || campanhaSelecionada)}`, '/perfil');
      // Recalcula estatísticas localmente recarregando a lista (se aplicável)
      try { await carregarCampanhas(); } catch (e) { /* non-blocking */ }
    }
  } catch (err) {
    console.error(err);
    mostrarMensagemErro('Não foi possível confirmar participação.');
  } finally {
    fecharModal();
  }
}

async function carregarMinhasParticipacoes() {
  try {
  const res = await fetch('/api/my_participations', { credentials: 'same-origin', headers: { 'X-Requested-With': 'XMLHttpRequest' } });
    if (!res.ok) return;
    const data = await res.json();
    // Normalize ids to strings to avoid type mismatches between DB and JS
    const ids = (data.participations || []).map(p => String(p.id || p.campanha_id || p.campaign_id || p.campanhaId || p.campaignId));
    minhasParticipacoesIds = new Set(ids);
  } catch (err) {
    console.warn('Não foi possível carregar participações do usuário:', err);
  }
}

// Função para fechar modal
function fecharModal() {
  const modalEl = document.getElementById('confirmModal');
  if (modalEl) modalEl.style.display = 'none';
  campanhaSelecionada = null;
  botaoSelecionado = null;
}

// Mensagens
function mostrarMensagemSucesso(mensagem) {
  // optional second argument may be a URL to view details (like '/perfil')
  const url = arguments[1] || null;
  const mensagemDiv = document.createElement('div');
  mensagemDiv.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 transform transition-transform duration-300';
  mensagemDiv.innerHTML = `<div class="flex items-center">${mensagem}${url ? ' <a href="'+url+'" class="ml-4 underline font-semibold">Ver meu perfil</a>' : ''}</div>`;
  document.body.appendChild(mensagemDiv);
  setTimeout(() => mensagemDiv.remove(), 4000);
}

function mostrarMensagemErro(mensagem) {
  const mensagemDiv = document.createElement('div');
  mensagemDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 transform transition-transform duration-300';
  mensagemDiv.innerHTML = `<div class="flex items-center">${mensagem}</div>`;
  document.body.appendChild(mensagemDiv);
  setTimeout(() => mensagemDiv.remove(), 3000);
}

// Fechar modal ao clicar fora (guarda null-safe)
const _confirmModalEl = document.getElementById('confirmModal');
if (_confirmModalEl) {
  _confirmModalEl.addEventListener('click', function (e) {
    if (e.target === this) {
      fecharModal();
    }
  });
}

// Fechar modal com ESC
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') {
    fecharModal();
  }
});

document.addEventListener('DOMContentLoaded', () => {
  carregarCampanhas();
});
