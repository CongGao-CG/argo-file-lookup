/* app.js — search works with year only; lat/lon optional */

const cache = {};
const $ = id => document.getElementById(id);

/* ---------- helper to fetch & cache a year file ---------- */
async function loadYear(Y) {
  if (cache[Y]) return cache[Y];
  const r = await fetch(`${Y}.json`);
  if (!r.ok) throw new Error(`Year file ${Y}.json not found on server`);
  const js = await r.json();
  cache[Y] = js;
  console.info(`Loaded ${js.length} rows for ${Y}`);
  return js;
}

/* ---------------- form handler ---------------- */
$("qry").addEventListener("submit", async e => {
  e.preventDefault();

  const Y  = +$("yr").value;
  if (Y < 1997 || Y > 2025) {               // ← new guard
    alert("Year must be between 1997 and 2025");
    return;
  }
  const M  = $("mo").value ? +$("mo").value : null;
  const D  = $("dy").value ? +$("dy").value : null;
  const latVal = $("lat").value;
  const lonVal = $("lon").value;
  const LAT = latVal === "" ? null : Math.round(+latVal);
  const LON = lonVal === "" ? null : Math.round(+lonVal);

  try {
    const rows = await loadYear(Y);

    const hits = rows.filter(r => {
      /* coordinate filters only if provided */
      if (LAT !== null && r.lat_round !== LAT) return false;
      if (LON !== null && r.lon_round !== LON) return false;

      const ymd = r.YYYYMMDD;
      const m = (ymd % 10000) / 100 | 0;
      const d =  ymd % 100;
      if (M !== null && m !== M) return false;
      if (D !== null && d !== D) return false;
      return true;
    });

    $("count").textContent = `${hits.length} file${hits.length!==1?"s":""} found`;
    $("res").querySelector("tbody").innerHTML = hits.map(h=>{
      const url=`https://data-argo.ifremer.fr/dac/${h.file}`;
      return `<tr><td><a href="${url}" target="_blank" rel="noopener">${h.file}</a></td></tr>`;
    }).join("");

  } catch(err) {
    alert(err.message);
  }
});
