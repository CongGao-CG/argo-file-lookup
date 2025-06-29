/*  app.js  –  loads only the year requested, then filters in-memory   */

/* ----------------------- helpers & cache --------------------------- */
const cache = {};                       // { 2024: [{…}, …], … }
const $     = id => document.getElementById(id);

async function loadYear(year) {
  if (cache[year]) return cache[year];               // already fetched

  const res = await fetch(`${year}.json`);
  if (!res.ok) throw new Error(`Year file ${year}.json not found`);

  const json = await res.json();
  cache[year] = json;
  console.info(`Loaded ${json.length} rows for ${year}`);
  return json;
}

/* -------------------- DOM references ------------------------------- */
const yr=$("yr"), mo=$("mo"), dy=$("dy"), la=$("lat"), lo=$("lon");
const tbody = $("res").querySelector("tbody");
const countLbl = $("count");

/* -------------------- form handler -------------------------------- */
$("qry").addEventListener("submit", async evt => {
  evt.preventDefault();

  const year  = +yr.value;
  const month = mo.value ? +mo.value : null;
  const day   = dy.value ? +dy.value : null;
  const latR  = Math.round(+la.value);
  const lonR  = Math.round(+lo.value);

  try {
    const rows = await loadYear(year);

    const hits = rows.filter(r => {
      if (r.lat_round !== latR || r.lon_round !== lonR) return false;
      const ymd = r.YYYYMMDD;
      const m = (ymd % 10000) / 100 | 0;
      const d =  ymd % 100;

      if (month !== null && m !== month) return false;
      if (day   !== null && d !== day)   return false;
      return true;
    });

    countLbl.textContent = `${hits.length} file${hits.length!==1?"s":""} found`;

    tbody.innerHTML = hits.map(h=>{
      const url=`https://data-argo.ifremer.fr/dac/${h.file}`;
      return `<tr><td><a href="${url}" target="_blank" rel="noopener">${h.file}</a></td></tr>`;
    }).join("");

  } catch(err) {
    alert(err.message);
  }
});