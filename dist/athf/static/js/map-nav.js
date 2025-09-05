const mapdiv = document.getElementById("usa-map");
mapdiv.style.opacity = 0.2;
const zooom = 4.5;
// Initialize map with interactions disabled
const map = L.map("usa-map", {
  // zoomControl: false, // Remove zoom buttons
  scrollWheelZoom: false, // Disable scroll zoom
  doubleClickZoom: false, // Disable double-click zoom
  boxZoom: false, // Disable box zoom
  keyboard: false, // Disable keyboard navigation
  // dragging: false, // Disable panning/dragging
  tap: false, // Disable tap (mobile)
  touchZoom: false, // Disable pinch zoom
  attributionControl: false, // Remove attribution
  minZoom: zooom,
  maxZoom: zooom,
}).setView([39.8283, -98.5795], zooom);

// base layer (the map)
// L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
//     attribution: ''
// }).addTo(map);

// loading = true;
fetch("/athf/static/us-states-albers.json")
  .then((response) => response.json())
  .then((statesData) => {
    L.geoJSON(statesData, {
      style: {
        fillColor: "var(--fg-color)",
        color: "var(--bg-color)",
        weight: 1,
        fillOpacity: 0.8,
      },
      onEachFeature: function (feature, layer) {
        const stateCode = Object.entries(stateLookup).find(
          (f) => f[1] === feature.properties.NAME,
        )[0];
        layer.on({
          mouseover: function (e) {
            e.target.setStyle({
              fillColor: "#fff",
              fillOpacity: 0.9,
              weight: 2,
            });
            const externalTT = document.getElementById("ex-tt");
            const externalTTLink = document.getElementById("ex-tt-link");
            // const externalTTTitle = document.getElementById("ex-tt-title");
            const externalTTImg1 = document.getElementById("ex-tt-img-1");
            const externalTTImg2 = document.getElementById("ex-tt-img-2");
            // externalTTTitle.innerText = feature.properties.NAME;
            // mapdiv.style.backgroundImage = `url("/athf/static/images/pcards/${stateCode}_postcard_bg.webp")`;
            const leftStates = [
              "AK",
              "AZ",
              "CA",
              "CO",
              "HI",
              "IA",
              "ID",
              "KS",
              "MN",
              "MT",
              "NE",
              "ND",
              "NV",
              "NM",
              "OK",
              "OR",
              "SD",
              "TX",
              "UT",
              "WA",
              "WY",
            ];

            if (leftStates.includes(stateCode.toUpperCase())) {
              externalTT.classList.add("left");
              externalTT.classList.remove("right");
            } else {
              externalTT.classList.add("right");
              externalTT.classList.remove("left");
            }
            if (externalTTImg1)
              externalTTImg1.src = `/athf/static/images/pcards/${stateCode}_postcard_bg.webp`;

            if (externalTTImg2)
              externalTTImg2.src = `/athf/static/images/pcards/${stateCode}_postcard_fg.webp`;
            if (externalTTLink) externalTTLink.href = `/athf/${stateCode}`;
          },
          mouseout: function (e) {
            e.target.setStyle({
              fillColor: "var(--fg-color)",
              fillOpacity: 0.8,
              weight: 1,
            });
          },
          click: function (e) {
            window.location = `/athf/${stateCode}`;
            // htmx.ajax("GET", `/athf/${stateCode}`, { target: "body" });
          },
        });

        // Add tooltip with state name
        layer.bindTooltip(feature.properties.NAME, {
          permanent: false,
          offset: [0, 33],
          direction: "center",
          className: "state-tooltip",
        });
      },
    }).addTo(map);

    // Optional: fit map to show all states perfectly
    map.fitBounds(L.geoJSON(statesData).getBounds(), { padding: [10, 10] });
    // loading = false;
    mapdiv.style.opacity = 1;
  });
