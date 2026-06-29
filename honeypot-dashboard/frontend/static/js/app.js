// Orchestrator: fetch the API, fill the page, refresh every 30s.
(function () {
  const statusEl = document.getElementById("status");

  async function getJSON(url) {
    const resp = await fetch(url, { headers: { Accept: "application/json" } });
    if (!resp.ok) throw new Error(url + " → " + resp.status);
    return resp.json();
  }

  async function refresh() {
    try {
      const [stats, attacks, recent, timeline] = await Promise.all([
        getJSON("/api/stats"),
        getJSON("/api/attacks"),
        getJSON("/api/recent"),
        getJSON("/api/analysis/timeline"),
      ]);
      document.getElementById("stat-total").textContent = stats.total;
      document.getElementById("stat-ips").textContent = stats.unique_ips;
      document.getElementById("stat-countries").textContent = stats.countries;
      HoneypotCharts.update(stats);
      HoneypotCharts.updateDaily(timeline);
      HoneypotMap.update(attacks);
      if (!HoneypotSearch.isActive()) HoneypotFeed.update(recent);
      HoneypotAnalysis.update().catch(function () {});
      statusEl.textContent = "aktualisiert " + new Date().toLocaleTimeString();
      statusEl.classList.remove("err");
    } catch (e) {
      statusEl.textContent = "Fehler: " + e.message;
      statusEl.classList.add("err");
    }
  }

  HoneypotMap.init();
  HoneypotCharts.init();
  HoneypotSearch.init();
  refresh();
  setInterval(refresh, 30000);
})();
