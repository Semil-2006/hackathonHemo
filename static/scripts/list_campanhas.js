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

    await carregarMinhasParticipacoes();
    renderizarTabela(campanhasAtuais);
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

async function participarCampanha(botao, campanhaObj) {
  try {
    const res = await fetch('/api/me', {
      method: 'GET',
      headers: { 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json' },
      credentials: 'same-origin'
    });
    if (res.status === 401) {
      window.location.href = '/login';
      return;
    }
  } catch (err) {
    console.warn('Falha ao verificar autenticação:', err);
  }

  campanhaSelecionada = campanhaObj;
  botaoSelecionado = botao;

  const nome = campanhaObj && (campanhaObj.nome || campanhaObj) || 'Campanha';
  const tipo = campanhaObj && (campanhaObj.tipo_sanguineo || campanhaObj.tipoSanguineo || '') || '';

  document.getElementById('modalMessage').innerHTML = 
    `Você está prestes a participar da campanha:<br><strong>${nome}</strong><br><br>Tipo sanguíneo necessário: <strong>${tipo || 'Todos'}</strong>`;

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
        window.location.href = '/login';
        return;
      }
      if (res.status === 409) {
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

      if (botaoSelecionado) {
        botaoSelecionado.textContent = 'Participando ✓';
        botaoSelecionado.disabled = true;
        botaoSelecionado.classList.add('text-green-600', 'font-bold');
        const linha = botaoSelecionado.closest('tr');
        if (linha) linha.classList.add('bg-green-50');
      }
      minhasParticipacoesIds.add(String(campaignId));
      mostrarMensagemSucesso(`Você agora está participando da campanha: ${campanhaSelecionada.nome}`, '/perfil');
      await carregarCampanhas();
    } else {
      if (botaoSelecionado) {
        botaoSelecionado.textContent = 'Participando ✓';
        botaoSelecionado.disabled = true;
        botaoSelecionado.classList.add('text-green-600', 'font-bold');
        const linha = botaoSelecionado.closest('tr');
        if (linha) linha.classList.add('bg-green-50');
      }
      mostrarMensagemSucesso(`Você agora está participando da campanha: ${campanhaSelecionada && (campanhaSelecionada.nome || campanhaSelecionada)}`, '/perfil');
      await carregarCampanhas();
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
    const ids = (data.participations || []).map(p => String(p.id || p.campanha_id || p.campaign_id || p.campanhaId || p.campaignId));
    minhasParticipacoesIds = new Set(ids);
  } catch (err) {
    console.warn('Não foi possível carregar participações do usuário:', err);
  }
}

function fecharModal() {
  const modalEl = document.getElementById('confirmModal');
  if (modalEl) modalEl.style.display = 'none';
  campanhaSelecionada = null;
  botaoSelecionado = null;
}

function mostrarMensagemSucesso(mensagem) {
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

const _confirmModalEl = document.getElementById('confirmModal');
if (_confirmModalEl) {
  _confirmModalEl.addEventListener('click', function (e) {
    if (e.target === this) fecharModal();
  });
}

document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') fecharModal();
});

document.addEventListener('DOMContentLoaded', () => {
  carregarCampanhas();
});

async function carregarEstatisticas() {
  try {
    // Buscar informações do usuário
    const resUsuario = await fetch('/api/me', { credentials: 'same-origin' });
    let usuario = {};
    if (resUsuario.ok) {
      usuario = await resUsuario.json();
    }

    // Buscar participações
    const resParticipacoes = await fetch('/api/my_participations', { credentials: 'same-origin' });
    let participacoesCount = 0;
    if (resParticipacoes.ok) {
      const dataPart = await resParticipacoes.json();
      participacoesCount = (dataPart.participations || []).length;
    }

    // Calcular selos (conquistas) no JS
    const selos = [];
    if (usuario.ja_doou === 'sim' || usuario.primeira_vez) {
      selos.push({ nome: 'Primeira Doação', caminhoImagem: 'assets/selo-primeira-doacao.png' });
    }
    if (participacoesCount >= 1) {
      selos.push({ nome: 'Iniciante', caminhoImagem: 'assets/emblemas/1.png' });
    }
    if (participacoesCount >= 3) {
      selos.push({ nome: 'Comprometido', caminhoImagem: 'assets/emblemas/2.png' });
    }
    if (participacoesCount >= 6) {
      selos.push({ nome: 'Heróico', caminhoImagem: 'assets/emblemas/3.png' });
    }

    // Atualizar estatísticas na tela
    const elConquistas = document.getElementById('totalCampanhas');
    if (elConquistas) elConquistas.textContent = selos.length;

    const elParticipacoes = document.getElementById('totalParticipantes');
    if (elParticipacoes) elParticipacoes.textContent = participacoesCount;

  } catch (err) {
    console.error('Erro ao carregar estatísticas:', err);
  }
}

// Chama junto com carregarCampanhas
document.addEventListener('DOMContentLoaded', () => {
  carregarCampanhas();
  carregarEstatisticas();
});
