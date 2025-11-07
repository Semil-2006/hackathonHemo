// --- Dados de exemplo (mock) ---


function updateAll(){ computeScores(); buildCharts(); renderMetrics(); renderTable(); renderRanking(); }


// initial render
/*
	Lightweight dashboard script that makes the existing `templates/dashboard_admin.html`
	interactive without requiring heavy libraries. It provides:
		- mock/sample data (replace with real API calls later)
		- computing a simple score and populating the table
		- handlers for available controls (export CSV, refresh, simulate)
	The script is defensive: it checks for DOM elements before attaching handlers.
*/

document.addEventListener('DOMContentLoaded', () => {
	// --- sample data will be fetched from server API; fallback local sample ---
	let sampleData = [];

	const state = {
		data: [],
		weights: { p: 6, e: 3, l: 1 },
		filter: { period: 30, channel: 'todos' }
	};

	// Try to fetch aggregated dashboard data from the backend. If it fails, fall back
	// to a small local sample so the UI still works.
	fetch('/api/dashboard_data')
		.then(r => r.json())
		.then(json => {
			if (json && Array.isArray(json.data) && json.data.length) {
				sampleData = json.data.map(d => ({ city: d.city, potential: d.potential, engage: d.engage, distance: d.distance }));
			} else {
				sampleData = [
					{ city: 'Região Central', potential: 1250, engage: 0.12, distance: 10 },
					{ city: 'Região Norte', potential: 840, engage: 0.11, distance: 25 },
					{ city: 'Região Sul', potential: 910, engage: 0.08, distance: 40 },
					{ city: 'Região Oeste', potential: 1100, engage: 0.09, distance: 18 }
				];
			}
		})
		.catch(err => {
			console.warn('Falha ao carregar dados do servidor, usando amostra local:', err);
			sampleData = [
				{ city: 'Região Central', potential: 1250, engage: 0.12, distance: 10 },
				{ city: 'Região Norte', potential: 840, engage: 0.11, distance: 25 },
				{ city: 'Região Sul', potential: 910, engage: 0.08, distance: 40 },
				{ city: 'Região Oeste', potential: 1100, engage: 0.09, distance: 18 }
			];
		})
		.finally(() => {
			state.data = sampleData.slice();
			updateAll();
		});

	// --- utility: compute a combined score for ranking ---
	function computeScores() {
		const maxP = Math.max(...state.data.map(d => d.potential || 0), 1);
		const maxE = Math.max(...state.data.map(d => d.engage || 0), 1);
		const maxL = Math.max(...state.data.map(d => 1 / (1 + d.distance) || 0), 1);
		state.data.forEach(d => {
			const p = (d.potential || 0) / maxP;
			const e = (d.engage || 0) / maxE;
			const l = (1 / (1 + (d.distance || 0))) / maxL;
			d.score = Math.round((p * state.weights.p + e * state.weights.e + l * state.weights.l) * 100) / 100;
		});
	}

	// --- render functions ---
	function renderTable() {
		const table = document.querySelector('.data-table tbody');
		if (!table) return;
		table.innerHTML = '';
		const rows = state.data.slice().sort((a, b) => b.score - a.score);
		rows.forEach(r => {
			const tr = document.createElement('tr');
			tr.innerHTML = `
				<td>${r.city}</td>
				<td>${r.potential}</td>
				<td>${Math.round((r.engage || 0) * 100)}</td>
				<td>${r.distance}</td>
				<td class="text-success">${r.score}</td>
			`;
			table.appendChild(tr);
		});
	}

	function buildCharts() {
		// Small behaviour: update the .blood-type-days elements if present
		const daysEls = document.querySelectorAll('.blood-type-days');
		const days = [8.2, 4.5, 9.0, 1.8, 7.1, 2.5, 5.0, 10.0];
		daysEls.forEach((el, i) => { if (days[i] !== undefined) el.textContent = days[i]; });
	}

	function renderRanking() {
		// Update ranking list if present
		const rankingList = document.querySelector('.ranking-list');
		if (!rankingList) return;
		const items = state.data.slice().sort((a, b) => b.score - a.score).slice(0, 5);
		rankingList.innerHTML = items.map((it, idx) => `
			<li class="ranking-item">
				<span class="font-medium">${idx + 1}. ${it.city}</span>
				<span class="ranking-potential-value">Potencial: ${it.score}</span>
			</li>
		`).join('');
	}

	function renderMetrics() {
		// placeholder for top-level KPIs (could populate DOM if you add elements)
	}

	function updateAll() {
		computeScores();
		buildCharts();
		renderMetrics();
		renderTable();
		renderRanking();
	}

	// initial render
	updateAll();

	// --- safe DOM helpers to attach handlers only when element exists ---
	function on(idOrEl, event, handler) {
		const el = (typeof idOrEl === 'string') ? document.getElementById(idOrEl) : idOrEl;
		if (!el) return null;
		el.addEventListener(event, handler);
		return el;
	}

	// Refresh button (if exists) - find element with class 'refresh' or id 'refresh'
	const refreshBtn = document.querySelector('.refresh') || document.getElementById('refresh');
	if (refreshBtn) refreshBtn.addEventListener('click', () => { state.data = sampleData.slice(); updateAll(); });

	// Export CSV - button has class 'btn-csv' in template
	const exportCsvBtn = document.querySelector('.btn-csv');
	if (exportCsvBtn) {
		exportCsvBtn.addEventListener('click', () => {
			const rows = [['Cidade','Estimativa','Engajamento(%)','Distância (km)','Score']];
			state.data.slice().sort((a,b)=>b.score-a.score).forEach(d=>rows.push([d.city,d.potential,Math.round((d.engage||0)*100),d.distance,d.score]));
			const csv = rows.map(r=>r.join(',')).join('\n');
			const blob = new Blob([csv],{type:'text/csv'});
			const url = URL.createObjectURL(blob);
			const a = document.createElement('a'); a.href = url; a.download = 'previsoes_coleta.csv'; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
		});
	}

	// Export PDF placeholder (no PDF lib included) - simply alert or call print
	const exportPdfBtn = document.querySelector('.btn-pdf');
	if (exportPdfBtn) exportPdfBtn.addEventListener('click', () => { window.print(); });

	// Simulation controls: if present, perform a small adjustment
	const runSimBtn = document.getElementById('runSim');
	const clearSimBtn = document.getElementById('clearSim');
	if (runSimBtn) {
		runSimBtn.addEventListener('click', () => {
			const dateEl = document.getElementById('simDate');
			const hoursEl = document.getElementById('simHours');
			const date = dateEl ? dateEl.value : null;
			const hours = hoursEl ? Number(hoursEl.value) : 6;
			if (!date) { alert('Escolha uma data para simulação'); return; }
			const dt = new Date(date); const wd = dt.getDay(); const factor = (wd===0||wd===6)?0.9:1.05; const hourFactor = 1 + (hours-6)/12;
			state.data.forEach(d => { d.potential = Math.max(5, Math.round((d.potential || 0) * factor * hourFactor)); });
			updateAll();
			alert('Simulação aplicada — valores atualizados temporariamente');
		});
	}
	if (clearSimBtn) clearSimBtn.addEventListener('click', () => { state.data = sampleData.slice(); updateAll(); });

	// Weights controls: find inputs by IDs if present and wire apply/reset
	const applyWeights = document.getElementById('applyWeights');
	const resetWeights = document.getElementById('resetWeights');
	if (applyWeights) {
		applyWeights.addEventListener('click', () => {
			const wP = document.getElementById('wPotential');
			const wE = document.getElementById('wEngage');
			const wL = document.getElementById('wLog');
			state.weights.p = wP ? Number(wP.value) : state.weights.p;
			state.weights.e = wE ? Number(wE.value) : state.weights.e;
			state.weights.l = wL ? Number(wL.value) : state.weights.l;
			updateAll();
		});
	}
	if (resetWeights) {
		resetWeights.addEventListener('click', () => {
			const wP = document.getElementById('wPotential');
			const wE = document.getElementById('wEngage');
			const wL = document.getElementById('wLog');
			if (wP) wP.value = 6; if (wE) wE.value = 3; if (wL) wL.value = 1;
			state.weights = { p:6, e:3, l:1 };
			updateAll();
		});
	}

	// Channel/region/date filters: try to wire existing selects in the template
	const regionSel = document.getElementById('region');
	const bloodTypeSel = document.getElementById('blood_type');
	if (regionSel) {
		regionSel.addEventListener('change', e => {
			// simple filter: if 'todas' then restore, else filter by matching substring
			const v = e.target.value;
			if (v === 'todas') state.data = sampleData.slice();
			else state.data = sampleData.filter(d => d.city.toLowerCase().includes(v.replace('regiao_','').replace('_',' ')));
			updateAll();
		});
	}
	if (bloodTypeSel) {
		bloodTypeSel.addEventListener('change', e => { /* placeholder for blood-type filtering */ updateAll(); });
	}

	// Small helper buttons: contactGroup / copyPlan / showHelp
	const contactGroup = document.getElementById('contactGroup');
	if (contactGroup) contactGroup.addEventListener('click', () => { alert('Gerando grupo recomendável para comunicação (mock)'); });
	const copyPlan = document.getElementById('copyPlan');
	if (copyPlan) copyPlan.addEventListener('click', () => { navigator.clipboard.writeText('Plano de ação: ' + state.data.slice().sort((a,b)=>b.score-a.score).map(x=>x.city).slice(0,3).join(', ')); alert('Plano copiado para área de transferência.'); });
	const showHelp = document.getElementById('showHelp');
	if (showHelp) showHelp.addEventListener('click', () => { alert('Resumo do modelo: scores calculados por potencial, engajamento e logística.'); });

	// If a detail box exists, wire single-click on table rows to show details
	const detailBox = document.getElementById('detailBox');
	const tableBody = document.querySelector('.data-table tbody');
	if (tableBody && detailBox) {
		tableBody.addEventListener('click', (e) => {
			const tr = e.target.closest('tr'); if (!tr) return;
			const city = tr.children[0].textContent.trim();
			const item = state.data.find(d => d.city === city);
			if (!item) return;
			detailBox.innerHTML = `<h4 style="margin:6px 0">${item.city}</h4>
				<div>Estimativa: <strong>${item.potential}</strong></div>
				<div>Engajamento previsto: <strong>${Math.round((item.engage||0)*100)}%</strong></div>
				<div>Distância: <strong>${item.distance} km</strong></div>
				<div style="margin-top:8px;color:var(--muted)">Recomendação: <strong>${item.engage>0.25 ? 'E-mail + SMS' : 'Campanha local'}</strong></div>`;
		});
	}

});