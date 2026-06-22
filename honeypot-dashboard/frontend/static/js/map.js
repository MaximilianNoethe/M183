// Leaflet world map with one circle per attacker IP, sized by hit count.
const HoneypotMap = (function () {
  let map, layer;

  function init() {
    map = L.map("map", { worldCopyJump: true }).setView([20, 0], 2);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      attribution: "© OpenStreetMap © CARTO",
      subdomains: "abcd",
      maxZoom: 19,
    }).addTo(map);
    layer = L.layerGroup().addTo(map);
  }

  function update(points) {
    layer.clearLayers();
    points.forEach(function (p) {
      if (p.latitude == null || p.longitude == null) return;
      const radius = Math.min(20, 4 + Math.log(p.count + 1) * 3);
      const marker = L.circleMarker([p.latitude, p.longitude], {
        radius: radius,
        color: "#00ff41",
        weight: 1,
        fillColor: "#00ff41",
        fillOpacity: 0.4,
      });
      marker.bindPopup(popup(p));
      layer.addLayer(marker);
    });
  }

  // build the popup as DOM nodes (textContent only, no innerHTML)
  function popup(p) {
    const box = document.createElement("div");
    box.className = "popup";
    const ip = document.createElement("strong");
    ip.textContent = p.src_ip;
    const place = document.createElement("div");
    place.textContent = [p.city, p.country].filter(Boolean).join(", ");
    const count = document.createElement("div");
    count.textContent = p.count + " Angriffe";
    box.append(ip, place, count);
    return box;
  }

  return { init: init, update: update };
})();
