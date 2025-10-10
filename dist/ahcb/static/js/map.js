let map;
let timelineControl;
let currentHighlight;
let geojsonLayer;
let highResLayer;
let currentDate;
let dateStabilityTimer;
let loadedHighResData = new Map();
let isHighResMode = false;

let downloadModal;

document.body.addEventListener("keydown", (event) => {
  if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
    if (event.target.classList.contains("time-slider")) {
      event.preventDefault();
      handleRangeInputKeypress(event.key);
    }
  }
});

// Configuration
const HIGH_RES_DELAY = 500;
const CACHE_LIMIT = 10;

function getDateFromURL() {
  const urlParams = new URLSearchParams(window.location.search);
  const dateParam = urlParams.get("date");

  if (dateParam) {
    return parseHistoricalDate(dateParam);
  }
  return null;
}

function parseHistoricalDate(dateString, returnType = "timestamp") {
  // console.log(" parseHistoricalDate dateString", dateString)

  // Parse as UTC to avoid timezone issues, then create a local date at noon
  // This prevents off-by-one errors from timezone shifts
  if (typeof dateString === "number") {
    let date = new Date(dateString);
    if (returnType === "date") {
      return date;
    } else {
      return date.getTime();
    }
  } else if (
    typeof dateString === "undefined" ||
    typeof dateString !== "string" ||
    dateString.indexOf("-") === -1
  ) {
    dateString = "2000-12-31";
  }
  const parts = dateString.split("-") || ["2000", "12", "31"];
  if (parts.length === 3) {
    const year = parseInt(parts[0]);
    const month = parseInt(parts[1]) - 1; // Month is 0-indexed
    const day = parseInt(parts[2]);

    if (!isNaN(year) && !isNaN(month) && !isNaN(day)) {
      // Create date at noon local time to avoid timezone edge cases
      const date = new Date(year, month, day, 12, 0, 0);
      if (returnType === "date") {
        return date;
      } else {
        return date.getTime();
      }
    }
  }
  return new Date().getTime();
}

function createTimelineControl(timelineData) {
  // Get date range
  // Dedupe date list
  const allDates = [];
  timelineData.features.forEach((feature) => {
    allDates.push(feature.properties.START_DATE);
    allDates.push(feature.properties.END_DATE);
  });

  let dates = [...new Set(allDates)].map((d) => new Date(d).getTime());
  const minDate = Math.min(...dates);
  const maxDate = Math.max(...dates);

  const urlDate = getDateFromURL();

  if (urlDate && (urlDate < minDate || urlDate > maxDate)) {
    console.warn(
      `Date parameter ${new Date(urlDate).toISOString().split("T")[0]} is outside data range (${new Date(minDate).toISOString().split("T")[0]} - ${new Date(maxDate).toISOString().split("T")[0]})`,
    );
  }

  geojsonLayer = L.timeline(timelineData, {
    pointToLayer: function (feature, latlng) {
      return L.circleMarker(latlng, {
        radius: 5,
        fillColor: "var(--county-bg-color)",
        color: "var(--county-fg-color)",
        weight: 2,
        opacity: 0.6,
        fillopacity: 0.5,
      });
    },
    style: function (feature) {
      return {
        fillColor: "var(--county-bg-color)",
        color: "var(--county-fg-color)",
        weight: 1,
        opacity: 0.6,
        fillopacity: 0.4,
      };
    },
    onEachFeature: function (feature, layer) {
      layer.on("click", function (e) {
        onCountyClick(feature, layer);
      });

      layer.on("mouseover", function (e) {
        layer.setStyle({
          weight: 2,
          opacity: 0.8,
          fillopacity: 0.6,
          fillColor: "var(--county-accent-color)",
        });
      });

      layer.on("mouseout", function (e) {
        if (currentHighlight !== layer) {
          layer.setStyle({
            weight: 1,
            opacity: 0.6,
            fillopacity: 0.4,
            fillColor: "var(--county-bg-color)",
          });
        }
      });
    },
  }).addTo(map);

  // Create timeline control
  timelineControl = L.timelineSliderControl({
    formatOutput: function (date) {
      return formatDate(parseHistoricalDate(date, "date"));
    },
    duration: 10000,
    showTicks: true,
    waitToUpdateMap: true,
    enablePlayback: true,
    enableKeyboardControls: true,
  });

  timelineControl.addTo(map);
  timelineControl.addTimelines(geojsonLayer);

  // If URL date was provided and is valid, set the timeline to that date
  if (urlDate && urlDate >= minDate && urlDate <= maxDate) {
    timelineControl.setTime(urlDate);
    // console.log(
    //   `Timeline positioned at URL date: ${new Date(urlDate).toISOString().split("T")[0]}`,
    // );
  }

  geojsonLayer.on("change", function (e) {
    const newDate = e.target.time;
    onTimelineChange(newDate);
  });

  currentDate = geojsonLayer.time || minDate; // Use actual timeline time or fallback to minDate

  // Start timer for initial high-res loading
  dateStabilityTimer = setTimeout(() => {
    loadHighResDataForDate(currentDate);
  }, HIGH_RES_DELAY);
}

// Initialize the map
function initializeMap(stateCode, stateName, previewData, manifestData) {
  const bounds = calculateBounds(previewData);

  // Initialize map
  map = L.map("map").fitBounds(bounds, {
    padding: [20, 20],
    paddingBottomRight: [220, 20],
  });

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
      '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  const timelineData = processDataForTimeline(previewData);

  createTimelineControl(timelineData);
  setupInfoPanel();
  addLoadingIndicator();
}

function calculateBounds(geojsonData) {
  const group = L.geoJSON(geojsonData);
  return group.getBounds();
}

function processDataForTimeline(geojsonData) {
  const processedFeatures = geojsonData.features.map((feature) => {
    const startDate =
      feature.properties.START_DATE &&
      typeof feature.properties.START_DATE === "string"
        ? parseHistoricalDate(feature.properties.START_DATE)
        : new Date().getTime();
    const endDate =
      feature.properties.END_DATE &&
      typeof feature.properties.END_DATE === "string"
        ? parseHistoricalDate(feature.properties.END_DATE)
        : new Date().getTime();

    return {
      type: "Feature",
      properties: {
        ...feature.properties,
        start: startDate,
        end: endDate,
      },
      geometry: feature.geometry,
    };
  });
  return {
    type: "FeatureCollection",
    features: processedFeatures,
  };
}

function onTimelineChange(newDate) {
  currentDate = newDate;
  // console.log("currentDate", currentDate);
  // Clear any existing timer
  if (dateStabilityTimer) {
    clearTimeout(dateStabilityTimer);
  }

  if (isHighResMode) {
    switchToPreviewMode();
  }

  dateStabilityTimer = setTimeout(() => {
    loadHighResDataForDate(currentDate);
  }, HIGH_RES_DELAY);
}

// Load high-resolution data for the current date
async function loadHighResDataForDate(date) {
  const dateKey = date.toString();

  // Check if we already have this data cached
  if (loadedHighResData.has(dateKey)) {
    switchToHighResMode(loadedHighResData.get(dateKey));
    return;
  }

  showLoadingIndicator();

  try {
    const visibleFeatures = getVisibleFeaturesAtDate(date);

    if (visibleFeatures.length === 0) {
      hideLoadingIndicator();
      return;
    }

    const highResFeatures = await loadHighResFeatures(visibleFeatures);

    if (highResFeatures.length > 0) {
      const highResData = {
        type: "FeatureCollection",
        features: highResFeatures,
      };

      manageCache(dateKey, highResData);
      switchToHighResMode(highResData);
    }
  } catch (error) {
    console.error("Error loading high-resolution data:", error);
  } finally {
    hideLoadingIndicator();
  }
}

function getVisibleFeaturesAtDate(date) {
  const visibleFeatures = [];

  geojsonLayer.getLayers().forEach((layer) => {
    if (layer.feature) {
      const feature = layer.feature;
      const startTime = feature.properties.start;
      const endTime = feature.properties.end;

      if (date >= startTime && date <= endTime) {
        visibleFeatures.push(feature);
      }
    }
  });

  return visibleFeatures;
}

async function loadHighResFeatures(visibleFeatures) {
  const highResFeatures = [];
  // console.log("visibleFeatures", visibleFeatures);

  const featureIds = [];

  for (const feature of visibleFeatures) {
    const countyId = feature.properties.ID;
    const startDate = feature.properties.START_DATE;
    const endDate = feature.properties.END_DATE;

    let manifestFeature = null;

    for (const [key, manifest] of Object.entries(manifestData.features)) {
      if (
        manifest.county_id === countyId &&
        manifest.start_date === startDate &&
        manifest.end_date === endDate
      ) {
        manifestFeature = manifest;
        break;
      }
    }

    if (manifestFeature) {
      const filename = manifestFeature.filename.replace(".json", "");
      featureIds.push({
        filename: filename,
        originalFeature: feature,
      });
    }
  }

  if (featureIds.length === 0) {
    return highResFeatures;
  }

  for (const featureInfo of featureIds) {
    try {
      const response = await fetch(
        `/ahcb/data/${stateCode}/features/${featureInfo.filename}.json`,
      );

      if (response.ok) {
        const data = await response.json();

        if (data.features) {
          // Handle many features (usually the case)
          data.features.forEach((highResFeature) => {
            highResFeature.properties = {
              ...highResFeature.properties,
              ...featureInfo.originalFeature.properties,
            };
          });
          highResFeatures.push(...data.features);
        } else {
          // Handle single Feature
          data.properties = {
            ...data.properties,
            ...featureInfo.originalFeature.properties,
          };
          highResFeatures.push(data);
        }
      }
    } catch (error) {
      console.error(`Error loading feature ${featureInfo.filename}:`, error);
    }
  }

  return highResFeatures;
}

function switchToHighResMode(highResData) {
  if (!highResData || highResData.features.length === 0) return;

  if (highResLayer) {
    map.removeLayer(highResLayer);
  }

  // Create new high-res layer
  highResLayer = L.geoJSON(highResData, {
    style: function (feature) {
      return {
        fillColor: "var(--county-bg-color)",
        color: "var(--county-fg-color)",
        weight: 1,
        opacity: 0.7,
        fillOpacity: 0.7,
      };
    },
    onEachFeature: function (feature, layer) {
      layer.on("click", function (e) {
        onCountyClick(feature, layer, true);
      });

      layer.on("mouseover", function (e) {
        layer.setStyle({
          weight: 2,
          opacity: 0.8,
          fillopacity: 0.7,
        });
      });

      layer.on("mouseout", function (e) {
        layer.setStyle({
          weight: currentHighlight === layer ? 2 : 1,
          opacity: currentHighlight === layer ? 1 : 0.7,
          fillOpacity: currentHighlight === layer ? 0.4 : 0.7,
        });
      });
    },
  }).addTo(map);

  // Hide the preview layer
  if (geojsonLayer) {
    geojsonLayer.setStyle({ opacity: 0, fillOpacity: 0 });
  }

  isHighResMode = true;
  highResLoading("loaded");
}

function switchToPreviewMode() {
  if (highResLayer) {
    map.removeLayer(highResLayer);
    highResLayer = null;
  }

  // Show the preview layer again
  if (geojsonLayer) {
    geojsonLayer.setStyle({
      opacity: 0.7,
      fillOpacity: 0.2,
    });
  }

  isHighResMode = false;
  highResLoading("loading");
}

// Manage cache to prevent memory issues
function manageCache(dateKey, data) {
  // If cache is full, remove oldest entry
  if (loadedHighResData.size >= CACHE_LIMIT) {
    const firstKey = loadedHighResData.keys().next().value;
    loadedHighResData.delete(firstKey);
  }

  loadedHighResData.set(dateKey, data);
}

function addLoadingIndicator() {
  const indicator = document.createElement("div");
  indicator.id = "loading-indicator";
  indicator.className = "loading-indicator hidden";
  indicator.innerHTML = `
<div class="loading-content">
  <div class="loading-spinner"></div>
  <div class="loading-text">Loading...</div>
</div>
`;
  document.body.appendChild(indicator);
}

function showLoadingIndicator(message = "Loading...") {
  const indicator = document.getElementById("loading-indicator");
  if (indicator) {
    indicator.querySelector(".loading-text").textContent = message;
    indicator.classList.remove("hidden");
  }
}

function hideLoadingIndicator() {
  const indicator = document.getElementById("loading-indicator");
  if (indicator) {
    indicator.classList.add("hidden");
  }
}

function highResLoading(state) {
  const highResLoadText = document.getElementById("highres-loading");
  if (highResLoadText) {
    if (state === "loading") {
      highResLoadText.innerText = "Full details loading...";
    } else if (state === "loaded") {
      highResLoadText.innerText = "Full details loaded.";
    }
  }
}

function onCountyClick(feature, layer, isHighRes = false) {
  // Remove previous highlight
  if (currentHighlight) {
    if (isHighResMode && !isHighRes) {
      // Don't reset style for preview layer when in high-res mode
    } else {
      currentHighlight.setStyle({
        weight: 1,
        opacity: 0.7,
        fillOpacity: 0.7,
        color: "var(--county-fg-color)",
        fillColor: "var(--county-bg-color)",
      });
    }
  }

  layer.setStyle({
    weight: 3,
    opacity: 0.6,
    fillOpacity: 0.4,
  });

  currentHighlight = layer;

  updateInfoPanel(feature.properties, isHighRes);
}

function updateInfoPanel(properties, isHighRes = false) {
  const infoPanel = document.getElementById("infotext");
  const infoHTML = `
<div class="county-info">
  <h3>${properties.FULL_NAME || properties.NAME}</h3>
  <div class="info-item">
  <label>Effective Dates:</label>
  <p>${formatDate(parseHistoricalDate(properties.START_DATE, "date"))} - ${properties.END_DATE ? formatDate(parseHistoricalDate(properties.END_DATE, "date")) : "Present"}</p>
</div>
${
  properties.CHANGE
    ? `
<div class="info-item">
  <label>Change:</label>
  <p>${properties.CHANGE}</p>
</div>
`
    : ""
}
${
  properties.CITATION
    ? `
<div class="info-item">
  <cite>${properties.CITATION}</cite>
</div>
`
    : ""
}
  <p class="highres-info" id="highres-loading">Full details load${isHighRes ? "ed" : "ing.."}.</p>
</div>
`;

  infoPanel.innerHTML = infoHTML;
}

// Setup info panel
// for resetting after date change
function setupInfoPanel() {
  const infoPanel = document.getElementById("infotext");
  infoPanel.innerHTML = `
<div class="county-info">
  <p>Use the time slider to see how the county boundaries have changed over time.</p>
  <p>Use the arrow keys, play button, or next/previous buttons to navigate.</p>
  <p>Click on a county to explore the data!</p>
  <p class="highres-info" id="highres-loading">Full details loading...</p>
</div>
`;
}

// Modify date display to prevent user apoplexy
function formatDate(date) {
  const m = date.getMonth() + 1;
  const d = date.getDate();
  const y = date.getFullYear();

  return `<span class="m">${m}</span>/<span class="d">${d}</span>/<span class="y">${y}</span>`;
}

function handleRangeInputKeypress(key) {
  if (key === "ArrowLeft") {
    const prevButton = document.querySelector(
      ".leaflet-timeline-control .prev",
    );
    if (prevButton) prevButton.click();
  } else {
    const nextButton = document.querySelector(
      ".leaflet-timeline-control .next",
    );
    if (nextButton) nextButton.click();
  }
}

const uiBtn = document.getElementById("change-ui-size");
uiBtn.addEventListener("click", changeUISize);

function changeUISize(e) {
  const btn = e.target;
  const leafletControls = document.querySelector(
    ".leaflet-bottom:has(.leaflet-timeline-control)",
  );
  const linkSelect = document.getElementById("link-select");
  const resizableElements = [btn, leafletControls, linkSelect];
  if (leafletControls.classList.contains("double-size")) {
    resizableElements.forEach((el) =>
      toggleSize(["double-size", "one-point-five-size"], "", el),
    );
  } else if (leafletControls.classList.contains("one-point-five-size")) {
    resizableElements.forEach((el) =>
      toggleSize(["one-point-five-size"], "double-size", el),
    );
  } else {
    resizableElements.forEach((el) =>
      toggleSize(["double-size"], "one-point-five-size", el),
    );
  }
}
function toggleSize(outClass, inClass, el) {
  outClass.forEach((c) => el.classList.remove(c));
  if (inClass) el.classList.add(inClass);
}

window.mapUtils = {
  formatDate,
  updateInfoPanel,
  changeUISize,
  switchToHighResMode,
  switchToPreviewMode,
  loadHighResDataForDate,
};
