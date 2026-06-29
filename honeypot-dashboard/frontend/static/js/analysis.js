// Analysis panels: top attacker commands, HIBP leak hits, botnet waves.
const HoneypotAnalysis = (function () {
  async function getJSON(url) {
    const resp = await fetch(url, { headers: { Accept: "application/json" } });
    if (!resp.ok) throw new Error(url + " → " + resp.status);
    return resp.json();
  }

  function fillTable(selector, rows, columns) {
    const tbody = document.querySelector(selector + " tbody");
    tbody.replaceChildren();
    rows.forEach(function (row) {
      const tr = document.createElement("tr");
      columns.forEach(function (pick) {
        const td = document.createElement("td");
        const value = pick(row);
        td.textContent = (value == null || value === "") ? "–" : value;
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
  }

  function pwnedLabel(r) {
    if (r.pwned == null) return "?";
    return r.pwned > 0 ? "✓ " + r.pwned.toLocaleString() + "×" : "nein";
  }

  async function update() {
    const [commands, passwords, botnet, downloads, providers, attackers] = await Promise.all([
      getJSON("/api/analysis/commands"),
      getJSON("/api/analysis/passwords"),
      getJSON("/api/analysis/botnet"),
      getJSON("/api/analysis/downloads"),
      getJSON("/api/analysis/providers"),
      getJSON("/api/analysis/attackers"),
    ]);
    fillTable("#attacker-table", attackers, [
      function (r) { return r.src_ip; },
      function (r) { return r.country; },
      function (r) { return r.asn; },
      function (r) { return r.count; },
    ]);
    fillTable("#cmd-table", commands, [function (r) { return r.value; }, function (r) { return r.count; }]);
    fillTable("#hibp-table", passwords, [
      function (r) { return r.value; },
      function (r) { return r.count; },
      pwnedLabel,
    ]);
    fillTable("#botnet-table", botnet, [
      function (r) { return r.window; },
      function (r) { return r.ip_count; },
      function (r) { return r.attempts; },
    ]);
    fillTable("#dl-table", downloads, [function (r) { return r.value; }, function (r) { return r.count; }]);
    fillTable("#provider-table", providers, [
      function (r) { return r.value; },
      function (r) { return r.ips; },
      function (r) { return r.count; },
    ]);
  }

  return { update: update };
})();
