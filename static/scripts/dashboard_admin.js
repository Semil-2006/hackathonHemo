// --- Dados de exemplo (mock) ---


function updateAll(){ computeScores(); buildCharts(); renderMetrics(); renderTable(); renderRanking(); }


// initial render
updateAll();


// interactions
function onBarClick(evt,items){ if(items.length>0){ const idx=items[0].index; const city=state.data[idx]; showDetails(city);} }


function showDetails(city){
const el=document.getElementById('detailBox');
el.innerHTML=`<h4 style="margin:6px 0">${city.city}</h4>
<div>Estimativa: <strong>${city.potential}</strong></div>
<div>Engajamento previsto: <strong>${(city.engage*100).toFixed(0)}%</strong></div>
<div>Distância: <strong>${city.distance} km</strong></div>
<div style="margin-top:8px;color:var(--muted)">Recomendação de comunicação: <strong>${recommendChannel(city)}</strong></div>
`;
}


function recommendChannel(city){ // simple rule-of-thumb
if(city.engage>0.3) return 'E-mail + SMS (alta prioridade)';
if(city.engage>0.22) return 'E-mail segmentado';
return 'Campanha local (rádio/avisos) + SMS';
}


// weights control
document.getElementById('wPotential').addEventListener('input',e=>{document.getElementById('wPotentialVal').textContent=e.target.value;});
document.getElementById('wEngage').addEventListener('input',e=>{document.getElementById('wEngageVal').textContent=e.target.value;});
document.getElementById('wLog').addEventListener('input',e=>{document.getElementById('wLogVal').textContent=e.target.value;});
document.getElementById('applyWeights').addEventListener('click',()=>{
state.weights.p = +document.getElementById('wPotential').value;
state.weights.e = +document.getElementById('wEngage').value;
state.weights.l = +document.getElementById('wLog').value;
updateAll();
});
document.getElementById('resetWeights').addEventListener('click',()=>{document.getElementById('wPotential').value=6;document.getElementById('wEngage').value=3;document.getElementById('wLog').value=1;document.getElementById('wPotentialVal').textContent=6;document.getElementById('wEngageVal').textContent=3;document.getElementById('wLogVal').textContent=1;state.weights={p:6,e:3,l:1};updateAll();});


// filters
citySelect.addEventListener('change',e=>{const v=e.target.value; if(v==='all'){state.data=sampleData.slice()} else {state.data=sampleData.filter(d=>d.city===v)}; updateAll();});
document.getElementById('periodSelect').addEventListener('change',e=>{state.filter.period=+e.target.value; /* placeholder for model recalculation */ updateAll();});
document.getElementById('channelSelect').addEventListener('change',e=>{state.filter.channel=e.target.value; updateAll();});


// simulation
document.getElementById('runSim').addEventListener('click',()=>{
const date=document.getElementById('simDate').value; const hours=+document.getElementById('simHours').value;
if(!date){alert('Escolha uma data para simulação');return}
// naive sim: adjust potential by weekday and hours
const dt=new Date(date); const wd=dt.getDay(); const factor = (wd===0||wd===6)?0.9:1.05; const hourFactor = 1 + (hours-6)/12;
state.data.forEach(d=>{d.potential = Math.max(5, Math.round(d.potential * factor * hourFactor));}); updateAll();
alert('Simulação aplicada — valores atualizados temporariamente');
});
document.getElementById('clearSim').addEventListener('click',()=>{state.data=sampleData.slice(); updateAll();});


document.getElementById('refresh').addEventListener('click',()=>{state.data=sampleData.slice(); updateAll();});


// export CSV
document.getElementById('exportCsv').addEventListener('click',()=>{
const rows = [['Cidade','Estimativa','Engajamento','Distância (km)','Score']];
state.data.slice().sort((a,b)=>b.score-a.score).forEach(d=>rows.push([d.city,d.potential,(d.engage*100).toFixed(0)+'%',d.distance,d.score]));
const csv = rows.map(r=>r.join(',')).join('\n');
const blob = new Blob([csv],{type:'text/csv'}); const url=URL.createObjectURL(blob);
const a=document.createElement('a');a.href=url;a.download='previsoes_coleta.csv';document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);
});


// export recommendations
document.getElementById('contactGroup').addEventListener('click',()=>{alert('Geração do grupo recomendável para comunicação (apenas agregados). Use a segmentação de RF03 para enviar mensagens respeitando consentimentos).');});
document.getElementById('copyPlan').addEventListener('click',()=>{navigator.clipboard.writeText('Plano de ação: Priorizar cidades: '+state.data.slice().sort((a,b)=>b.score-a.score).map(x=>x.city).slice(0,3).join(', ')); alert('Plano copiado para área de transferência.');});


// click on help to show model summary
document.getElementById('showHelp').addEventListener('click',()=>{
alert('Resumo do modelo: scores calculados por normalização de potenciais, engajamento e logística (distância). Valores são explicativos; recomenda-se validação por especialistas.');
});