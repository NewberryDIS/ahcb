// Global variables
let map;
let timelineControl;
let currentHighlight;
let geojsonLayer;
let highResLayer;
let currentDate;
let dateStabilityTimer;
let loadedHighResData = new Map();
let isHighResMode = false;

// Configuration
const HIGH_RES_DELAY = 500;
const CACHE_LIMIT = 10;

// Initialize the map
function initializeMap(stateCode, stateName, previewData, manifestData) {
  // Calculate bounds from preview data
  const bounds = calculateBounds(previewData);

  // Initialize map
  map = L.map("map").fitBounds(bounds, {
    padding: [20, 20],
    paddingBottomRight: [220, 20],
  });

  // Add base tile layer
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
      '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  // Process data for timeline
  const timelineData = processDataForTimeline(previewData);

  // Create timeline control
  createTimelineControl(timelineData);

  // Set up info panel
  setupInfoPanel();

  // Add loading indicator
  addLoadingIndicator();
}

// Calculate bounds from GeoJSON data
function calculateBounds(geojsonData) {
  const group = L.geoJSON(geojsonData);
  return group.getBounds();
}

// Process GeoJSON data for timeline use
function processDataForTimeline(geojsonData) {
  const processedFeatures = geojsonData.features.map((feature) => {
    const startDate = new Date(feature.properties.START_DATE);
    const endDate = feature.properties.END_DATE
      ? new Date(feature.properties.END_DATE)
      : new Date();

    return {
      type: "Feature",
      properties: {
        ...feature.properties,
        start: startDate.getTime(),
        end: endDate.getTime(),
      },
      geometry: feature.geometry,
    };
  });

  return {
    type: "FeatureCollection",
    features: processedFeatures,
  };
}

// Create timeline control
function createTimelineControl(timelineData) {
  // Get date range
  const dates = [];
  timelineData.features.forEach((feature) => {
    dates.push(feature.properties.start);
    if (feature.properties.end !== feature.properties.start) {
      dates.push(feature.properties.end);
    }
  });

  const minDate = Math.min(...dates);
  const maxDate = Math.max(...dates);

  // Create timeline layer
  geojsonLayer = L.timeline(timelineData, {
    pointToLayer: function (feature, latlng) {
      return L.circleMarker(latlng, {
        radius: 5,
        fillColor: "var(--county-bg-color)",
        color: "var(--county-fg-color)",
        weight: 2,
        opacity: 1,
        fillOpacity: 0.6,
      });
    },
    style: function (feature) {
      return {
        fillColor: "var(--county-bg-color)",
        color: "var(--county-fg-color)",
        weight: 1,
        opacity: 0.8,
        fillOpacity: 0.6,
      };
    },
    onEachFeature: function (feature, layer) {
      // Add click event
      layer.on("click", function (e) {
        onCountyClick(feature, layer);
      });

      // Add hover effect
      layer.on("mouseover", function (e) {
        layer.setStyle({
          weight: 2,
          opacity: 1,
          fillOpacity: 0.8,
          fillColor: "var(--county-accent-color)",
        });
      });

      layer.on("mouseout", function (e) {
        if (currentHighlight !== layer) {
          layer.setStyle({
            weight: 1,
            opacity: 0.8,
            fillOpacity: 0.6,
            fillColor: "var(--county-bg-color)",
          });
        }
      });
    },
  }).addTo(map);

  // Create timeline control
  timelineControl = L.timelineSliderControl({
    formatOutput: function (date) {
      return formatDate(new Date(date));
    },
    duration: 1000,
    showTicks: true,
    waitToUpdateMap: true,
    enablePlayback: true,
    enableKeyboardControls: true,
  });

  timelineControl.addTo(map);
  timelineControl.addTimelines(geojsonLayer);

  // Listen for timeline changes
  geojsonLayer.on("change", function (e) {
    const newDate = e.target.time;
    onTimelineChange(newDate);
  });

  // Set initial date and trigger potential high-res loading
  const initialDate = geojsonLayer.time || timelineControl.getDisplayed();
  currentDate = initialDate;

  // Start timer for initial high-res loading
  dateStabilityTimer = setTimeout(() => {
    loadHighResDataForDate(currentDate);
  }, HIGH_RES_DELAY);
}

// Handle timeline changes
function onTimelineChange(newDate) {
  currentDate = newDate;

  // Clear any existing timer
  if (dateStabilityTimer) {
    clearTimeout(dateStabilityTimer);
  }

  // If we're in high-res mode and the date changed, switch back to preview
  if (isHighResMode) {
    switchToPreviewMode();
  }

  // Set a new timer to load high-res data after delay
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

  // Show loading indicator
  showLoadingIndicator("Loading detailed boundaries...");

  try {
    // Get features that should be visible at this date
    const visibleFeatures = getVisibleFeaturesAtDate(date);

    if (visibleFeatures.length === 0) {
      hideLoadingIndicator();
      return;
    }

    // Load high-res data for visible features
    const highResFeatures = await loadHighResFeatures(visibleFeatures);

    if (highResFeatures.length > 0) {
      const highResData = {
        type: "FeatureCollection",
        features: highResFeatures,
      };

      // Cache the data (with cache management)
      manageCache(dateKey, highResData);

      // Switch to high-res mode
      switchToHighResMode(highResData);
    }
  } catch (error) {
    console.error("Error loading high-resolution data:", error);
  } finally {
    hideLoadingIndicator();
  }
}

// Get features that should be visible at a given date
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

// Load high-resolution features from static files
async function loadHighResFeatures(visibleFeatures) {
  const highResFeatures = [];

  // Collect feature IDs that need to be loaded
  const featureIds = [];

  for (const feature of visibleFeatures) {
    const countyId = feature.properties.ID;
    const startDate = feature.properties.START_DATE;
    const endDate = feature.properties.END_DATE;

    // Find the manifest entry that matches this county and date range
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

  // Load each feature individually from static files
  for (const featureInfo of featureIds) {
    try {
      const response = await fetch(
        `/athf/data/${stateCode}/features/${featureInfo.filename}.json`,
      );

      if (response.ok) {
        const data = await response.json();

        if (data.features) {
          // Handle FeatureCollection
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

// Switch to high-resolution mode
function switchToHighResMode(highResData) {
  if (!highResData || highResData.features.length === 0) return;

  // Remove existing high-res layer if it exists
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
        opacity: 0.9,
        fillOpacity: 0.7,
      };
    },
    onEachFeature: function (feature, layer) {
      // Add click event
      layer.on("click", function (e) {
        onCountyClick(feature, layer, true);
      });

      // Add hover effect
      layer.on("mouseover", function (e) {
        layer.setStyle({
          weight: 2,
          opacity: 1,
          fillOpacity: 0.9,
          fillColor: "var(--county-accent-color)",
        });
      });

      layer.on("mouseout", function (e) {
        if (currentHighlight !== layer) {
          layer.setStyle({
            weight: 1,
            opacity: 0.9,
            fillOpacity: 0.7,
            fillColor: "var(--county-bg-color)",
          });
        }
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

// Switch back to preview mode
function switchToPreviewMode() {
  if (highResLayer) {
    map.removeLayer(highResLayer);
    highResLayer = null;
  }

  // Show the preview layer again
  if (geojsonLayer) {
    geojsonLayer.setStyle({
      opacity: 0.8,
      fillOpacity: 0.6,
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

// Add loading indicator to the page
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

// Show loading indicator
function showLoadingIndicator(message = "Loading...") {
  const indicator = document.getElementById("loading-indicator");
  if (indicator) {
    indicator.querySelector(".loading-text").textContent = message;
    indicator.classList.remove("hidden");
  }
}

// Hide loading indicator
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

document.getElementById("map").onkeydown = function (e) {
  e.stopPropagation();
};

// Handle county click
function onCountyClick(feature, layer, isHighRes = false) {
  // Remove previous highlight
  if (currentHighlight) {
    if (isHighResMode && !isHighRes) {
      // Don't reset style for preview layer when in high-res mode
    } else {
      currentHighlight.setStyle({
        weight: 1,
        opacity: isHighRes ? 0.9 : 0.8,
        fillOpacity: isHighRes ? 0.7 : 0.6,
      });
    }
  }

  layer.setStyle({
    weight: 3,
    opacity: 1,
    fillOpacity: isHighRes ? 0.9 : 0.8,
    color: "var(--county-fg-color)",
  });

  currentHighlight = layer;

  // Update info panel
  updateInfoPanel(feature.properties, isHighRes);
}

// Update info panel with county information
function updateInfoPanel(properties, isHighRes = false) {
  const infoPanel = document.getElementById("infotext");

  const infoHTML = `
        <div class="county-info">
            <h3>${properties.FULL_NAME || properties.NAME}</h3>
            ${isHighRes ? '<div class="resolution-badge">High Resolution</div>' : ""}
            <div class="info-item">
                <label>Effective Dates:</label>
                <p>${formatDate(new Date(properties.START_DATE))} - ${properties.END_DATE ? formatDate(new Date(properties.END_DATE)) : "Present"}</p>
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
        <p class="highres-info" id="highres-loading">Full details loaded.</p>
        </div>
    `;

  infoPanel.innerHTML = infoHTML;
}

// Setup info panel
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

// Format date for display
function formatDate(date) {
  const m = date.getMonth() + 1;
  const d = date.getDate();
  const y = date.getFullYear();

  return `<span class="m">${m}</span>/<span class="d">${d}</span>/<span class="y">${y}</span>`;
}

// Export functions for use in other scripts if needed
window.mapUtils = {
  formatDate,
  updateInfoPanel,
  switchToHighResMode,
  switchToPreviewMode,
  loadHighResDataForDate,
};
