(async () => {
const cases=[{"filters": {"start": 1984, "end": 2026, "make": "", "segment": "", "powertrain": ""}, "n": 49868, "gas_mpg": 20.26430240359035, "bev_range": 270.00139178844813, "electric_share": 7.35742359829951}, {"filters": {"start": 2018, "end": 2026, "make": "Toyota", "segment": "SUV", "powertrain": ""}, "n": 240, "gas_mpg": 23.522058823529413, "bev_range": 254.52173913043478, "electric_share": 42.916666666666664}, {"filters": {"start": 2012, "end": 2026, "make": "Tesla", "segment": "", "powertrain": "BEV"}, "n": 185, "gas_mpg": null, "bev_range": 300.8918918918919, "electric_share": 100.0}, {"filters": {"start": 1984, "end": 1985, "make": "Tesla", "segment": "", "powertrain": ""}, "n": 0, "gas_mpg": null, "bev_range": null, "electric_share": null}, {"filters": {"start": 2027, "end": 1984, "make": "", "segment": "", "powertrain": ""}, "n": 0, "gas_mpg": null, "bev_range": null, "electric_share": null}];

const results=[];
for(const test of cases){
 for(const [key,value] of Object.entries(test.filters)){
  const control=document.getElementById(key);control.value=String(value);control.dispatchEvent(new Event('change',{bubbles:true}));
 }
 const text=id=>document.getElementById(id).textContent;
 const numeric=id=>Number(text(id).replace(/[,%%]/g,''));
 if(numeric('records')!==test.n)throw Error('Record count mismatch');
 for(const [id,key,tolerance] of [['mpg','gas_mpg',.051],['range','bev_range',.51],['electric','electric_share',.051]]){
  if(test[key]===null){if(text(id)!=='\u2014')throw Error('Empty metric not marked unavailable: '+id)}
  else if(Math.abs(numeric(id)-test[key])>tolerance)throw Error('Metric mismatch '+id);
 }
 const csv=await (await fetch(document.getElementById('download').href)).text();
 const lines=csv.trim().split('\n');
 const count=lines.slice(1).reduce((s,l)=>s+Number(l.match(/(?:"(?:[^"]|"")*"|[^,]+)/g)[4].replace(/"/g,'')),0);
 if(count!==test.n)throw Error('CSV download count mismatch');
 results.push({filters:test.filters,records:test.n,charts:document.querySelectorAll('.chart svg').length,csvRecords:count,status:text('status')});
}
document.getElementById('reset').click();
return JSON.stringify({passed:results.length,cases:results,resetRecords:document.getElementById('records').textContent});
})()
