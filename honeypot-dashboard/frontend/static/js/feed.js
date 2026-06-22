// Live-feed table of the most recent attacks (textContent only, no innerHTML).
const HoneypotFeed = (function () {
  function update(rows) {
    const tbody = document.querySelector("#feed tbody");
    tbody.replaceChildren();
    rows.forEach(function (r) {
      const tr = document.createElement("tr");
      const cells = [
        shortTime(r.timestamp), r.src_ip, r.country,
        r.username, r.password, label(r.event_type),
      ];
      cells.forEach(function (value) {
        const td = document.createElement("td");
        td.textContent = (value == null || value === "") ? "–" : value;
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
  }

  function shortTime(ts) {
    return ts ? ts.replace("T", " ").slice(0, 19) : "–";
  }

  function label(ev) {
    return ev ? ev.replace("cowrie.", "") : "–";
  }

  return { update: update };
})();
