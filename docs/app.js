/* load gzip (GitHub serves with Content-Encoding: gzip) */
let rows = [];
fetch("search_table.json")
  .then(r => r.json())
  .then(js => { rows = js; console.log("rows", rows.length); })
  .catch(err => alert("Lookup load failed: "+err));

const $ = id => document.getElementById(id);
document.getElementById("qry").addEventListener("submit", e =>{
  e.preventDefault();
  if(!rows.length){ alert("Table loading…"); return;}

  const Y=+$("yr").value,
        M=$("mo").value? +$("mo").value:null,
        D=$("dy").value? +$("dy").value:null,
        LAT=Math.round(+$("lat").value),
        LON=Math.round(+$("lon").value);

  const hits = rows.filter(r=>{
    if(r.lat_round!==LAT||r.lon_round!==LON) return false;
    const ymd=r.YYYYMMDD,
          y = ymd/1e4|0,
          m = (ymd%1e4)/100|0,
          d = ymd%100;
    if(y!==Y) return false;
    if(M!==null && m!==M) return false;
    if(D!==null && d!==D) return false;
    return true;
  });

  $("count").textContent = `${hits.length} file${hits.length!==1?"s":""} found`;
  $("res").querySelector("tbody").innerHTML = hits.map(h=>{
    const url=`https://data-argo.ifremer.fr/dac/${h.file}`;
    return `<tr><td><a href="${url}" target="_blank">${h.file}</a></td></tr>`;
  }).join("");
});
