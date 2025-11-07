// admin_campanhas.js
// Handles create/list/update/delete of campaigns using the backend API

document.addEventListener('DOMContentLoaded', () => {
  const formCriar = document.getElementById('formCriarCampanha');
  const tabelaBody = document.getElementById('tabelaAdminCampanhas');
  const filtro = document.getElementById('filtroCampanha');
  const editModal = document.getElementById('editModal');
  const formEditar = document.getElementById('formEditarCampanha');

  // helpers for modal
  window.abrirModalEdicao = function(campaign){
    document.getElementById('editCampanhaId').value = campaign.id;
    document.getElementById('editNome').value = campaign.nome || '';
    document.getElementById('editTipoSanguineo').value = campaign.tipo_sanguineo || '';
    document.getElementById('editVagas').value = campaign.vagas || 0;
    document.getElementById('editStatus').value = campaign.status || 'Ativa';
    editModal.style.display = 'flex';
  }

  window.fecharModalEdicao = function(){
    editModal.style.display = 'none';
  }

  window.salvarEdicao = function(){
    const id = document.getElementById('editCampanhaId').value;
    const payload = {
      nome: document.getElementById('editNome').value,
      tipo_sanguineo: document.getElementById('editTipoSanguineo').value,
      vagas: Number(document.getElementById('editVagas').value),
      status: document.getElementById('editStatus').value
    };
    fetch('/api/campaigns/' + id, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).then(r => r.json()).then(() => { fecharModalEdicao(); loadCampaigns(); }).catch(err => { alert('Erro ao salvar: '+err); });
  }

  function createRow(c){
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${escapeHtml(c.nome)}</td>
      <td>${escapeHtml(c.tipo_sanguineo || '')}</td>
      <td>${c.vagas}</td>
      <td>${c.participantes || 0}</td>
      <td>
        <a href="#" class="action-button-edit" data-id="${c.id}">Editar</a>
        <a href="#" class="action-button-delete" data-id="${c.id}">Excluir</a>
      </td>
    `;
    return tr;
  }

  function escapeHtml(str){
    if (!str) return '';
    return String(str).replace(/[&<>"']/g, function(m){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"}[m]; });
  }

  function loadCampaigns(){
    fetch('/api/campaigns').then(r => r.json()).then(json => {
      const list = json.campaigns || [];
      renderTable(list);
    }).catch(err => { console.error('Erro ao buscar campanhas', err); tabelaBody.innerHTML = '<tr><td colspan="5">Erro ao carregar</td></tr>'; });
  }

  function renderTable(list){
    tabelaBody.innerHTML = '';
    const q = filtro ? (filtro.value || '').toLowerCase() : '';
    const filtered = list.filter(c => {
      if (!q) return true;
      return (c.nome || '').toLowerCase().includes(q) || (c.tipo_sanguineo || '').toLowerCase().includes(q);
    });
    if (filtered.length === 0){
      tabelaBody.innerHTML = '<tr><td colspan="5">Nenhuma campanha encontrada.</td></tr>';
      return;
    }
    filtered.forEach(c => {
      const tr = createRow(c);
      tabelaBody.appendChild(tr);
    });
  }

  // handle create
  if (formCriar){
    formCriar.addEventListener('submit', (e) => {
      e.preventDefault();
      const nome = document.getElementById('novoNome').value;
      const tipo = document.getElementById('novoTipoSanguineo').value;
      const vagas = Number(document.getElementById('novoVagas').value) || 0;
      fetch('/api/campaigns', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ nome, tipo_sanguineo: tipo, vagas }) })
        .then(r => r.json())
        .then(() => { formCriar.reset(); loadCampaigns(); })
        .catch(err => { alert('Erro ao criar campanha: '+err); });
    });
  }

  // delegate edit/delete clicks
  tabelaBody.addEventListener('click', (e) => {
    const edit = e.target.closest('.action-button-edit');
    const del = e.target.closest('.action-button-delete');
    if (edit){
      e.preventDefault();
      const id = edit.dataset.id;
      // fetch single campaign (or reuse loaded list) - we'll fetch all and find
      fetch('/api/campaigns').then(r=>r.json()).then(json=>{
        const c = (json.campaigns || []).find(x=>String(x.id)===String(id));
        if (c) abrirModalEdicao(c); else alert('Campanha não encontrada');
      });
    }
    if (del){
      e.preventDefault();
      if (!confirm('Excluir campanha?')) return;
      const id = del.dataset.id;
      fetch('/api/campaigns/'+id, { method: 'DELETE' }).then(r=>r.json()).then(()=> loadCampaigns()).catch(err=> alert('Erro: '+err));
    }
  });

  if (filtro){
    filtro.addEventListener('input', () => loadCampaigns());
  }

  // initial load
  loadCampaigns();
});
