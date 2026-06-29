// Chart.js charts: top passwords (bar), attacks per hour and per day (line).
const HoneypotCharts = (function () {
  let passwords, hourly, daily;

  function baseConfig(type) {
    return {
      type: type,
      data: {
        labels: [],
        datasets: [{
          data: [],
          backgroundColor: "#00ff41",
          borderColor: "#00ff41",
          tension: 0.3,
        }],
      },
      options: {
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: "#5fffa0" }, grid: { color: "#163a22" } },
          y: { ticks: { color: "#5fffa0" }, grid: { color: "#163a22" }, beginAtZero: true },
        },
      },
    };
  }

  function init() {
    passwords = new Chart(document.getElementById("chart-passwords"), baseConfig("bar"));
    hourly = new Chart(document.getElementById("chart-hourly"), baseConfig("line"));
    daily = new Chart(document.getElementById("chart-daily"), baseConfig("bar"));
  }

  function update(stats) {
    passwords.data.labels = stats.top_passwords.map(function (r) { return r.value; });
    passwords.data.datasets[0].data = stats.top_passwords.map(function (r) { return r.count; });
    passwords.update();

    hourly.data.labels = stats.per_hour.map(function (r) { return r.hour; });
    hourly.data.datasets[0].data = stats.per_hour.map(function (r) { return r.count; });
    hourly.update();
  }

  function updateDaily(rows) {
    daily.data.labels = rows.map(function (r) { return r.day; });
    daily.data.datasets[0].data = rows.map(function (r) { return r.count; });
    daily.update();
  }

  return { init: init, update: update, updateDaily: updateDaily };
})();
