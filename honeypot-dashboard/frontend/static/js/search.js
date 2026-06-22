// Search bar over /api/search; while active, the live feed pauses its refresh.
const HoneypotSearch = (function () {
  let active = false;

  async function run(event) {
    if (event) event.preventDefault();
    const params = new URLSearchParams();
    const ip = document.getElementById("q-ip").value.trim();
    const country = document.getElementById("q-country").value.trim();
    const user = document.getElementById("q-user").value.trim();
    if (ip) params.set("ip", ip);
    if (country) params.set("country", country);
    if (user) params.set("username", user);
    if (![...params].length) { reset(); return; }

    const resp = await fetch("/api/search?" + params.toString(), { headers: { Accept: "application/json" } });
    if (!resp.ok) return;
    const rows = await resp.json();
    active = true;
    document.getElementById("feed-title").textContent = "Suchergebnisse (" + rows.length + ")";
    HoneypotFeed.update(rows);
  }

  function reset() {
    active = false;
    document.getElementById("q-ip").value = "";
    document.getElementById("q-country").value = "";
    document.getElementById("q-user").value = "";
    document.getElementById("feed-title").textContent = "Live-Feed — letzte Angriffe";
  }

  function init() {
    document.getElementById("search").addEventListener("submit", run);
    document.getElementById("q-reset").addEventListener("click", reset);
  }

  return { init: init, reset: reset, isActive: function () { return active; } };
})();
