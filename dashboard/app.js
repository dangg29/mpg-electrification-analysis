'use strict';
const $ = id => document.getElementById(id);
const fmt = (n, d=0) => Number.isFinite(n) ? n.toLocaleString('en-US', {maximumFractionDigits:d, minimumFractionDigits:d}) : '—';
const esc = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const ELECTRIC = new Set(['HEV','PHEV','BEV']);
let data, rows, downloadURL;
const sum = (rs,key) => rs.reduce((a,r)=>a+r[key],0);
const mean = (rs,key,denom) => sum(rs,denom) ? sum(rs,key)/sum(rs,denom) : NaN;
function group(rs,key){const out=new Map();rs.forEach(r=>{if(!out.has(r[key]))out.set(r[key],[]);out.get(r[key]).push(r)});return [...out];}
function table(headers, values){return `<table><thead><tr>${headers.map(h=>`<th scope="col">${esc(h)}</th>`).join('')}</tr></thead><tbody>${values.map(v=>`<tr>${v.map(x=>`<td>${esc(x)}</td>`).join('')}</tr>`).join('')}</tbody></table>`;}
function line(id, points, label, color='#087f74', fixedMax){
 const valid=points.filter(p=>Number.isFinite(p[1])).sort((a,b)=>a[0]-b[0]);
 if(!valid.length){$(id).innerHTML='<div class="empty">No matching records for this chart.</div>';return;}
 const W=520,H=230,L=48,R=20,T=18,B=32;
 const minX=Math.min(...valid.map(p=>p[0])),maxX=Math.max(...valid.map(p=>p[0]));
 const maxY=fixedMax||Math.max(...valid.map(p=>p[1]))*1.12||1;
 const x=v=>L+(v-minX)/(maxX-minX||1)*(W-L-R), y=v=>H-B-v/maxY*(H-T-B);
 let svg=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(label)}"><title>${esc(label)}</title>`;
 for(let i=0;i<=4;i++){const v=maxY*i/4;svg+=`<line x1="${L}" y1="${y(v)}" x2="${W-R}" y2="${y(v)}" stroke="#e6eeea"/><text x="${L-8}" y="${y(v)+4}" text-anchor="end">${fmt(v)}</text>`;}
 [...new Set([minX,Math.round((minX+maxX)/2),maxX])].forEach(v=>{svg+=`<text x="${x(v)}" y="${H-8}" text-anchor="middle">${v}</text>`});
 svg+=`<polyline points="${valid.map(p=>`${x(p[0])},${y(p[1])}`).join(' ')}" fill="none" stroke="${color}" stroke-width="2.6"/>`;
 valid.forEach(p=>{svg+=`<circle cx="${x(p[0])}" cy="${y(p[1])}" r="3" fill="${color}"><title>${p[0]}: ${fmt(p[1],1)}</title></circle>`});
 $(id).innerHTML=svg+'</svg>';
}
function bars(id, values){
 if(!values.length){$(id).innerHTML='<div class="empty">No matching records.</div>';return;}
 values.sort((a,b)=>b[1]-a[1]);const height=Math.max(230,values.length*30),max=Math.max(...values.map(v=>v[1]));
 let svg=`<svg viewBox="0 0 520 ${height}" role="img" aria-label="Powertrain record counts"><title>Powertrain record counts</title>`;
 values.forEach(([name,n],i)=>{let y=12+i*(height-20)/values.length;svg+=`<text x="83" y="${y+14}" text-anchor="end">${esc(name)}</text><rect x="96" y="${y}" width="${n/max*325}" height="20" rx="3" fill="${ELECTRIC.has(name)?'#087f74':'#97ada4'}"/><text x="${106+n/max*325}" y="${y+14}">${fmt(n)}</text>`});
 $(id).innerHTML=svg+'</svg>';
}
function options(id, values){values.forEach(value=>{const o=document.createElement('option');o.value=value;o.textContent=value;$(id).append(o)})}
function reset(){ $('start').value=data.minYear; $('end').value=data.maxYear-1; ['make','segment','powertrain'].forEach(id=>$(id).value=''); render(); }
function render(){
 const start=Number($('start').value),end=Number($('end').value);
 const selected=rows.filter(r=>r.year>=start&&r.year<=end&&['make','segment','powertrain'].every(k=>!$(k).value||r[k]===$(k).value));
 const n=sum(selected,'n'),gas=selected.filter(r=>r.powertrain==='Gasoline'),bev=selected.filter(r=>r.powertrain==='BEV');
 $('status').textContent=start>end?'Choose a start year no later than the end year.':!n?'No records match these filters. Try a wider selection.':`${fmt(n)} records selected · ${start}–${end}${end===data.maxYear?' · Newest model year may be incomplete.':' · Newest observed model year excluded by default.'}`;
 $('records').textContent=fmt(n);$('years').textContent=`Model years ${start}–${end}`;
 $('electric').textContent=n?fmt(sum(selected.filter(r=>ELECTRIC.has(r.powertrain)),'n')/n*100,1)+'%':'—';
 $('mpg').textContent=fmt(mean(gas,'mpg_sum','mpg_n'),1);$('range').textContent=fmt(mean(bev,'range_sum','range_n'),0);
 line('efficiency',group(gas,'year').map(([y,rs])=>[y,mean(rs,'mpg_sum','mpg_n')]),'Gasoline combined MPG by model year');
 line('adoption',group(selected,'year').map(([y,rs])=>[y,sum(rs.filter(r=>ELECTRIC.has(r.powertrain)),'n')/sum(rs,'n')*100]),'Electrified share of selected records by model year','#b9822d',100);
 line('bev',group(bev,'year').map(([y,rs])=>[y,mean(rs,'range_sum','range_n')]),'BEV range in miles by model year');
 bars('mix',group(selected,'powertrain').map(([p,rs])=>[p,sum(rs,'n')]));
 const comparison=group(selected,'powertrain').sort((a,b)=>a[0].localeCompare(b[0])).map(([p,rs])=>[p,fmt(sum(rs,'n')),fmt(mean(rs,'mpg_sum','mpg_n'),1),p==='BEV'?'MPGe':p==='PHEV'?'MPG · gasoline mode':p==='Hydrogen'?'MPGe':p==='CNG'?'Gasoline-equivalent MPG':'MPG']);
 $('comparison').innerHTML=comparison.length?table(['Powertrain','Records','Mean comb08','Metric context'],comparison):'<p>No matching records.</p>';
 const ranking=group(gas,'make').map(([make,rs])=>({make,n:sum(rs,'n'),mpg:mean(rs,'mpg_sum','mpg_n')})).filter(x=>x.n>=20).sort((a,b)=>b.mpg-a.mpg).slice(0,15);
 $('ranking').innerHTML=ranking.length?table(['Manufacturer','Records','Combined MPG'],ranking.map(r=>[r.make,fmt(r.n),fmt(r.mpg,1)])):'<p>No manufacturers meet the 20-record threshold.</p>';
 const csv=[data.columns.join(','),...selected.map(r=>data.columns.map(k=>'"'+String(r[k]).replace(/"/g,'""')+'"').join(','))].join('\n');
 if(downloadURL)URL.revokeObjectURL(downloadURL);downloadURL=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));$('download').href=downloadURL;
}
function models(){
 const m=data.metrics,r=m.mpg_regression,c=m.electrification_classification,f=m.mpg_forecast;
 $('model-scope').textContent=`Trained through ${m.train_through}; evaluated on ${m.test_years.join('–')}. Model year ${m.excluded_latest_year} excluded. Features are documented in the project report.`;
 $('model-metrics').innerHTML=`<div class="model-card"><span>Gasoline MPG regression · MAE</span><strong>${fmt(r.mae,2)} MPG</strong><span>Mean-only baseline: ${fmt(r.baseline_mae,2)} MPG</span></div><div class="model-card"><span>Electrification classifier · ROC AUC</span><strong>${fmt(c.roc_auc,3)}</strong><span>Balanced accuracy: ${fmt(c.balanced_accuracy*100,1)}%</span></div><div class="model-card"><span>MPG trend backtest · MAE</span><strong>${fmt(f.holdout_mae,2)} MPG</strong><span>Last-value baseline: ${fmt(f.last_value_baseline_mae,2)} MPG</span></div>`;
 $('forecasts').innerHTML=table(['Scenario year','Gasoline mean MPG','Electrified record share'],data.forecasts.map(f=>[f.year,fmt(f.gasoline_mpg_scenario,1),fmt(f.electrified_record_share_scenario*100,1)+'%']));
}
async function init(){
 try{const response=await fetch('data.json');if(!response.ok)throw Error(`Data request returned ${response.status}`);data=await response.json();rows=data.rows.map(r=>Object.fromEntries(data.columns.map((k,i)=>[k,r[i]])));
 const years=Array.from({length:data.maxYear-data.minYear+1},(_,i)=>data.minYear+i);options('start',years);options('end',years);
 ['make','segment','powertrain'].forEach(k=>options(k,[...new Set(rows.map(r=>r[k]))].sort()));
 ['start','end','make','segment','powertrain'].forEach(k=>$(k).addEventListener('change',render));$('reset').addEventListener('click',reset);models();reset();
 }catch(error){$('status').textContent=`Unable to load the snapshot. Serve the dashboard over HTTP and check that data.json exists. ${error.message}`;console.error(error);}
}
init();
