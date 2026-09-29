/**
 * Twitter Data Mining Suite - Frontend Controller
 * Integrates Chart.js, Vis.js Network, Leaflet Map, and REST API calls.
 */

// Global State
let chartTerms = null;
let chartBigrams = null;
let chartSentiment = null;
let chartTopics = null;
let chartTimeline = null;
let networkGraph = null;
let leafletMap = null;
let mapMarkers = [];

let currentExplorerPage = 1;
const explorerPerPage = 10;

// Initialize on DOM Load
document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initCharts();
  initLeafletMap();
  initEventListeners();
  
  // Initial data load
  loadDashboardData();
  loadNetworkGraph();
  loadGeoTweets();
  loadTweetExplorer();
  runSandboxAnalysis(); // Initial sandbox run
});

// Toast notification helper
function showToast(message, isError = false) {
  const toast = document.getElementById("toast");
  toast.innerText = message;
  toast.style.borderColor = isError ? "var(--rose)" : "var(--primary)";
  toast.style.display = "block";
  setTimeout(() => {
    toast.style.display = "none";
  }, 3500);
}

// --------------------------------------------------------------------------
// Navigation Tabs
// --------------------------------------------------------------------------
function initTabs() {
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");

      tabButtons.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPane = document.getElementById(`tab-${targetTab}`);
      if (targetPane) {
        targetPane.classList.add("active");
      }

      // Handle map resize when switching to map tab
      if (targetTab === "geomap" && leafletMap) {
        setTimeout(() => leafletMap.invalidateSize(), 200);
      }
      // Handle network physics when switching to network tab
      if (targetTab === "network" && networkGraph) {
        setTimeout(() => networkGraph.fit(), 200);
      }
    });
  });
}

// --------------------------------------------------------------------------
// Chart.js Setup
// --------------------------------------------------------------------------
function initCharts() {
  const chartDefaults = {
    color: '#94a3b8',
    font: { family: "'Outfit', sans-serif" }
  };
  Chart.defaults.color = chartDefaults.color;
  Chart.defaults.font.family = chartDefaults.font.family;

  // 1. Top Terms Bar Chart
  const ctxTerms = document.getElementById("chart-terms").getContext("2d");
  chartTerms = new Chart(ctxTerms, {
    type: "bar",
    data: {
      labels: [],
      datasets: [{
        label: "Occurrences",
        data: [],
        backgroundColor: "rgba(99, 102, 241, 0.75)",
        borderColor: "#6366f1",
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: "rgba(255, 255, 255, 0.05)" } },
        y: { grid: { display: false } }
      }
    }
  });

  // 2. Top Bigrams Bar Chart
  const ctxBigrams = document.getElementById("chart-bigrams").getContext("2d");
  chartBigrams = new Chart(ctxBigrams, {
    type: "bar",
    data: {
      labels: [],
      datasets: [{
        label: "Occurrences",
        data: [],
        backgroundColor: "rgba(56, 189, 248, 0.75)",
        borderColor: "#38bdf8",
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: "rgba(255, 255, 255, 0.05)" } },
        y: { grid: { display: false } }
      }
    }
  });

  // 3. Sentiment Doughnut
  const ctxSentiment = document.getElementById("chart-sentiment").getContext("2d");
  chartSentiment = new Chart(ctxSentiment, {
    type: "doughnut",
    data: {
      labels: ["Positive", "Neutral", "Negative"],
      datasets: [{
        data: [0, 0, 0],
        backgroundColor: ["#10b981", "#94a3b8", "#f43f5e"],
        borderWidth: 0,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom" }
      },
      cutout: "68%"
    }
  });

  // 4. Topic Category Chart
  const ctxTopics = document.getElementById("chart-topics").getContext("2d");
  chartTopics = new Chart(ctxTopics, {
    type: "bar",
    data: {
      labels: [],
      datasets: [{
        label: "Tweets",
        data: [],
        backgroundColor: [
          "rgba(168, 85, 247, 0.75)",
          "rgba(99, 102, 241, 0.75)",
          "rgba(245, 158, 11, 0.75)",
          "rgba(16, 185, 129, 0.75)",
          "rgba(56, 189, 248, 0.75)"
        ],
        borderWidth: 0,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { grid: { color: "rgba(255, 255, 255, 0.05)" } },
        x: { grid: { display: false } }
      }
    }
  });

  // 5. Timeline Velocity Chart
  const ctxTimeline = document.getElementById("chart-timeline").getContext("2d");
  chartTimeline = new Chart(ctxTimeline, {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        label: "Tweets per Period",
        data: [],
        borderColor: "#6366f1",
        backgroundColor: "rgba(99, 102, 241, 0.15)",
        fill: true,
        tension: 0.35,
        borderWidth: 2,
        pointRadius: 4,
        pointBackgroundColor: "#818cf8"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { grid: { color: "rgba(255, 255, 255, 0.05)" } },
        x: { grid: { color: "rgba(255, 255, 255, 0.05)" } }
      }
    }
  });
}

// --------------------------------------------------------------------------
// Leaflet Map Initialization
// --------------------------------------------------------------------------
function initLeafletMap() {
  const container = document.getElementById("map-container");
  if (!container) return;

  leafletMap = L.map(container, {
    center: [25.0, 10.0],
    zoom: 2,
    zoomControl: true,
    minZoom: 2,
    maxZoom: 12
  });

  // Dark CartoDB tile layer
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://carto.com/">CARTO</a>, &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    subdomains: 'abcd',
    maxZoom: 19
  }).addTo(leafletMap);
}

// --------------------------------------------------------------------------
// API Fetchers & UI Updaters
// --------------------------------------------------------------------------

// Main Dashboard Data
async function loadDashboardData() {
  try {
    const res = await fetch("/api/stats");
    const data = await res.json();

    // Stats Cards
    document.getElementById("stat-total").innerText = data.total_tweets.toLocaleString();
    const polarityVal = data.average_polarity;
    const polElem = document.getElementById("stat-polarity");
    polElem.innerText = (polarityVal > 0 ? "+" : "") + polarityVal.toFixed(3);
    
    const polLabel = document.getElementById("stat-polarity-label");
    if (polarityVal >= 0.05) {
      polLabel.innerText = "Trending Positive";
      polLabel.style.color = "var(--emerald)";
    } else if (polarityVal <= -0.05) {
      polLabel.innerText = "Trending Negative";
      polLabel.style.color = "var(--rose)";
    } else {
      polLabel.innerText = "Balanced / Neutral";
      polLabel.style.color = "var(--text-muted)";
    }

    if (data.top_hashtags && data.top_hashtags.length > 0) {
      document.getElementById("stat-hashtag").innerText = data.top_hashtags[0][0];
      document.getElementById("stat-hashtag-count").innerText = `${data.top_hashtags[0][1]} occurrences`;
    } else {
      document.getElementById("stat-hashtag").innerText = "--";
    }

    document.getElementById("stat-vocab").innerText = Object.keys(data.top_terms || {}).length > 0 
      ? `${data.top_terms.length}+ Terms` : "--";

    // Update Top Terms Chart
    const terms15 = (data.top_terms || []).slice(0, 15);
    chartTerms.data.labels = terms15.map(t => t[0]);
    chartTerms.data.datasets[0].data = terms15.map(t => t[1]);
    chartTerms.update();

    // Update Top Bigrams Chart
    const bigrams12 = (data.top_bigrams || []).slice(0, 12);
    chartBigrams.data.labels = bigrams12.map(b => b[0]);
    chartBigrams.data.datasets[0].data = bigrams12.map(b => b[1]);
    chartBigrams.update();

    // Tag Clouds
    renderTagCloud("list-hashtags", data.top_hashtags, "#");
    renderTagCloud("list-mentions", data.top_mentions, "@");
    renderTagCloud("list-emoticons", data.top_emoticons, "");

    // Update Sentiment Chart
    const sc = data.sentiment_counts || { positive: 0, neutral: 0, negative: 0 };
    chartSentiment.data.datasets[0].data = [sc.positive, sc.neutral, sc.negative];
    chartSentiment.update();

    // Update Topics Chart
    const topics = data.topic_counts || {};
    chartTopics.data.labels = Object.keys(topics);
    chartTopics.data.datasets[0].data = Object.values(topics);
    chartTopics.update();

    // Update Timeline Chart
    const timeline = data.time_series || {};
    chartTimeline.data.labels = Object.keys(timeline);
    chartTimeline.data.datasets[0].data = Object.values(timeline);
    chartTimeline.update();

  } catch (err) {
    console.error("Failed to load dashboard data:", err);
    showToast("Error loading stats", true);
  }
}

function renderTagCloud(containerId, items, prefix) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = "";

  if (!items || items.length === 0) {
    container.innerHTML = "<span class='text-muted' style='font-size:0.85rem;'>No items found</span>";
    return;
  }

  items.forEach(([tag, count]) => {
    const badge = document.createElement("div");
    badge.className = "tag-badge";
    badge.innerHTML = `<span>${tag}</span><span class="count">${count}</span>`;
    badge.addEventListener("click", () => {
      // Trigger PMI or Explorer search
      const cleanWord = tag.replace(/^[#@]/, '');
      document.getElementById("input-pmi-term").value = cleanWord;
      calculatePMI(cleanWord);
      // Switch tab to network
      document.getElementById("tab-btn-network").click();
    });
    container.appendChild(badge);
  });
}

// --------------------------------------------------------------------------
// Co-occurrence Network Graph (Vis.js)
// --------------------------------------------------------------------------
async function loadNetworkGraph() {
  const container = document.getElementById("network-container");
  if (!container) return;

  const limit = document.getElementById("select-graph-limit").value || 25;

  try {
    const res = await fetch(`/api/network?limit=${limit}`);
    const data = await res.json();

    const nodes = new vis.DataSet(data.nodes.map(n => ({
      id: n.id,
      label: n.label,
      shape: "dot",
      size: 18,
      font: { color: "#f8fafc", face: "Outfit", size: 13 },
      color: {
        background: "#6366f1",
        border: "#818cf8",
        highlight: { background: "#38bdf8", border: "#ffffff" }
      }
    })));

    const edges = new vis.DataSet(data.edges.map(e => ({
      from: e.from,
      to: e.to,
      value: e.value,
      title: e.title,
      color: { color: "rgba(56, 189, 248, 0.4)", highlight: "#38bdf8" },
      smooth: { type: "continuous" }
    })));

    const options = {
      physics: {
        barnesHut: {
          gravitationalConstant: -3500,
          springLength: 95,
          springConstant: 0.04
        },
        stabilization: { iterations: 120 }
      },
      interaction: {
        hover: true,
        tooltipDelay: 100
      }
    };

    networkGraph = new vis.Network(container, { nodes, edges }, options);

    // Node click triggers PMI calculation
    networkGraph.on("click", (params) => {
      if (params.nodes.length > 0) {
        const selectedNode = params.nodes[0];
        document.getElementById("input-pmi-term").value = selectedNode;
        calculatePMI(selectedNode);
      }
    });

  } catch (err) {
    console.error("Failed to load network graph:", err);
  }
}

// --------------------------------------------------------------------------
// Pointwise Mutual Information (PMI)
// --------------------------------------------------------------------------
async function calculatePMI(term) {
  const resultsContainer = document.getElementById("pmi-results");
  if (!term) {
    resultsContainer.innerHTML = "<div class='empty-state'><p>Please enter a valid term.</p></div>";
    return;
  }

  resultsContainer.innerHTML = "<div class='empty-state'><i class='fa-solid fa-spinner fa-spin'></i><p>Computing associations...</p></div>";

  try {
    const res = await fetch(`/api/pmi?term=${encodeURIComponent(term)}`);
    const data = await res.json();

    if (data.error || !data.pmi_associations || data.pmi_associations.length === 0) {
      resultsContainer.innerHTML = `
        <div class="empty-state">
          <i class="fa-solid fa-circle-question"></i>
          <p>No high-confidence co-occurrences found for '<strong>${term}</strong>'.</p>
        </div>
      `;
      return;
    }

    let html = `
      <div style="margin-bottom: 0.75rem; font-size: 0.825rem; color: var(--text-secondary);">
        Target: <strong style="color:#fff;">${data.term}</strong> (${data.term_count} occurrences)
      </div>
    `;

    data.pmi_associations.forEach(([other, score]) => {
      html += `
        <div class="pmi-row">
          <span><i class="fa-solid fa-link text-cyan"></i> ${other}</span>
          <span class="pmi-score">PMI: ${score.toFixed(3)}</span>
        </div>
      `;
    });

    resultsContainer.innerHTML = html;

  } catch (err) {
    console.error("PMI calculation error:", err);
    resultsContainer.innerHTML = "<div class='empty-state'><p>Failed to compute PMI</p></div>";
  }
}

// --------------------------------------------------------------------------
// Geolocation Map (Leaflet)
// --------------------------------------------------------------------------
async function loadGeoTweets() {
  if (!leafletMap) return;

  try {
    const res = await fetch("/api/geo");
    const data = await res.json();

    // Clear existing markers
    mapMarkers.forEach(m => leafletMap.removeLayer(m));
    mapMarkers = [];

    const tweets = data.geo_tweets || [];
    tweets.forEach(t => {
      const color = t.sentiment.label === "positive" ? "#10b981" :
                    t.sentiment.label === "negative" ? "#f43f5e" : "#94a3b8";

      const circleMarker = L.circleMarker([t.lat, t.lng], {
        radius: 7,
        fillColor: color,
        color: "#ffffff",
        weight: 1.5,
        opacity: 0.9,
        fillOpacity: 0.8
      });

      const popupHtml = `
        <div style="font-family:'Outfit',sans-serif; min-width:180px;">
          <strong style="color:#1e293b;">@${t.user.username || 'user'}</strong>
          <p style="font-size:0.75rem; color:#64748b; margin:2px 0 6px 0;"><i class="fa-solid fa-location-dot"></i> ${t.place_name}</p>
          <p style="font-size:0.85rem; color:#0f172a; margin-bottom:6px;">${t.text}</p>
          <span style="display:inline-block; font-size:0.75rem; padding:2px 6px; border-radius:4px; font-weight:600; background:${color}; color:#fff;">
            ${t.sentiment.label.toUpperCase()} (${t.sentiment.score})
          </span>
        </div>
      `;

      circleMarker.bindPopup(popupHtml);
      circleMarker.addTo(leafletMap);
      mapMarkers.push(circleMarker);
    });

  } catch (err) {
    console.error("Failed to load geo tweets:", err);
  }
}

// --------------------------------------------------------------------------
// Tweet Stream Explorer
// --------------------------------------------------------------------------
async function loadTweetExplorer() {
  const container = document.getElementById("tweet-feed-list");
  const search = document.getElementById("filter-search").value;
  const sentiment = document.getElementById("filter-sentiment").value;
  const topic = document.getElementById("filter-topic").value;

  container.innerHTML = "<div class='feed-loader'><i class='fa-solid fa-spinner fa-spin'></i> Loading tweets...</div>";

  try {
    const params = new URLSearchParams({
      page: currentExplorerPage,
      limit: explorerPerPage,
      search: search,
      sentiment: sentiment,
      topic: topic
    });

    const res = await fetch(`/api/tweets?${params}`);
    const data = await res.json();

    container.innerHTML = "";

    if (!data.tweets || data.tweets.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <i class="fa-solid fa-inbox"></i>
          <p>No tweets matching the filter criteria.</p>
        </div>
      `;
      document.getElementById("pagination-info").innerText = "No results";
      document.getElementById("btn-prev-page").disabled = true;
      document.getElementById("btn-next-page").disabled = true;
      return;
    }

    data.tweets.forEach(t => {
      const user = t.user || {};
      const sent = t.sentiment || { label: "neutral", score: 0.0 };
      const badgeClass = sent.label === "positive" ? "badge-pos" :
                         sent.label === "negative" ? "badge-neg" : "badge-neu";
      
      const metrics = t.public_metrics || { retweet_count: 0, like_count: 0, reply_count: 0 };

      const card = document.createElement("div");
      card.className = "tweet-card";
      card.innerHTML = `
        <div class="tweet-card-top">
          <div class="user-meta">
            <span class="user-name">${user.name || 'User'}</span>
            <span class="user-handle">@${user.username || 'unknown'}</span>
            ${user.verified ? '<i class="fa-solid fa-circle-check text-cyan" style="font-size:0.8rem;"></i>' : ''}
          </div>
          <div style="display:flex; gap:0.5rem;">
            <span class="badge ${badgeClass}"><i class="fa-solid fa-circle"></i> ${sent.label} (${sent.score})</span>
            <span class="badge badge-neu">${t.topic || 'General'}</span>
          </div>
        </div>
        <div class="tweet-text">${t.text}</div>
        <div class="tweet-footer">
          <span><i class="fa-regular fa-clock"></i> ${t.created_at ? t.created_at.replace("T", " ").replace("Z", "") : 'Recent'}</span>
          <div class="tweet-metrics">
            <span><i class="fa-solid fa-retweet"></i> ${metrics.retweet_count}</span>
            <span><i class="fa-regular fa-heart"></i> ${metrics.like_count}</span>
            <span><i class="fa-regular fa-comment"></i> ${metrics.reply_count}</span>
          </div>
        </div>
      `;
      container.appendChild(card);
    });

    // Update pagination
    document.getElementById("pagination-info").innerText = 
      `Showing page ${data.page} of ${data.total_pages} (${data.total} tweets)`;
    document.getElementById("btn-prev-page").disabled = (data.page <= 1);
    document.getElementById("btn-next-page").disabled = (data.page >= data.total_pages);

  } catch (err) {
    console.error("Failed to load tweets:", err);
    container.innerHTML = "<div class='empty-state'><p>Failed to load tweets.</p></div>";
  }
}

// --------------------------------------------------------------------------
// NLP Tokenizer Sandbox
// --------------------------------------------------------------------------
async function runSandboxAnalysis() {
  const textInput = document.getElementById("sandbox-input");
  const text = textInput.value;

  try {
    const res = await fetch("/api/tokenize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    const data = await res.json();

    // 1. Entities
    const entContainer = document.getElementById("out-entities");
    entContainer.innerHTML = "";
    const ent = data.entities || {};

    const appendEntities = (list, type, colorClass) => {
      (list || []).forEach(item => {
        const b = document.createElement("span");
        b.className = "tag-badge";
        b.innerHTML = `<strong class="${colorClass}">${type}:</strong> ${item}`;
        entContainer.appendChild(b);
      });
    };

    appendEntities(ent.hashtags, "#Tag", "text-purple");
    appendEntities(ent.mentions, "@User", "text-blue");
    appendEntities(ent.urls, "URL", "text-cyan");
    appendEntities(ent.emoticons, "Emoticon", "text-amber");

    if (entContainer.children.length === 0) {
      entContainer.innerHTML = "<span class='text-muted' style='font-size:0.85rem;'>No special entities found</span>";
    }

    // 2. Sentiment & Topic
    const sentContainer = document.getElementById("out-sentiment-info");
    const sent = data.sentiment || { label: "neutral", score: 0 };
    const badgeClass = sent.label === "positive" ? "badge-pos" :
                       sent.label === "negative" ? "badge-neg" : "badge-neu";

    sentContainer.innerHTML = `
      <span class="badge ${badgeClass}"><i class="fa-solid fa-circle"></i> ${sent.label.toUpperCase()} (Polarity: ${sent.score})</span>
      <span class="badge badge-neu"><i class="fa-solid fa-layer-group"></i> ${data.topic}</span>
    `;

    // 3. Raw Tokens
    const rawTokensContainer = document.getElementById("out-raw-tokens");
    rawTokensContainer.innerHTML = "";
    (data.raw_tokens || []).forEach(tok => {
      const chip = document.createElement("span");
      chip.className = "token-chip";
      chip.innerText = tok;
      rawTokensContainer.appendChild(chip);
    });

    // 4. Cleaned Tokens
    const cleanContainer = document.getElementById("out-clean-tokens");
    cleanContainer.innerHTML = "";
    (data.cleaned_tokens || []).forEach(tok => {
      const chip = document.createElement("span");
      chip.className = "token-chip";
      chip.innerText = tok;
      cleanContainer.appendChild(chip);
    });

  } catch (err) {
    console.error("Sandbox error:", err);
  }
}

// --------------------------------------------------------------------------
// Event Listeners & Modals
// --------------------------------------------------------------------------
function initEventListeners() {
  // Global Refresh
  document.getElementById("btn-refresh").addEventListener("click", () => {
    loadDashboardData();
    loadNetworkGraph();
    loadGeoTweets();
    loadTweetExplorer();
    showToast("Dashboard analytics refreshed!");
  });

  // PMI Search
  document.getElementById("btn-compute-pmi").addEventListener("click", () => {
    const term = document.getElementById("input-pmi-term").value.trim();
    calculatePMI(term);
  });
  document.getElementById("input-pmi-term").addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      calculatePMI(e.target.value.trim());
    }
  });

  // Graph limit select
  document.getElementById("select-graph-limit").addEventListener("change", () => {
    loadNetworkGraph();
  });

  // Explorer Filters
  document.getElementById("filter-search").addEventListener("input", debounce(() => {
    currentExplorerPage = 1;
    loadTweetExplorer();
  }, 350));
  document.getElementById("filter-sentiment").addEventListener("change", () => {
    currentExplorerPage = 1;
    loadTweetExplorer();
  });
  document.getElementById("filter-topic").addEventListener("change", () => {
    currentExplorerPage = 1;
    loadTweetExplorer();
  });

  // Explorer Pagination
  document.getElementById("btn-prev-page").addEventListener("click", () => {
    if (currentExplorerPage > 1) {
      currentExplorerPage--;
      loadTweetExplorer();
    }
  });
  document.getElementById("btn-next-page").addEventListener("click", () => {
    currentExplorerPage++;
    loadTweetExplorer();
  });

  // NLP Sandbox
  document.getElementById("btn-run-sandbox").addEventListener("click", runSandboxAnalysis);
  document.querySelectorAll(".btn-preset").forEach(btn => {
    btn.addEventListener("click", () => {
      document.getElementById("sandbox-input").value = btn.getAttribute("data-text");
      runSandboxAnalysis();
    });
  });

  // Ingestion Modal
  const modal = document.getElementById("modal-ingest");
  document.getElementById("btn-open-ingest").addEventListener("click", () => {
    modal.classList.add("open");
  });
  document.getElementById("btn-close-modal").addEventListener("click", () => {
    modal.classList.remove("open");
  });
  document.getElementById("btn-cancel-modal").addEventListener("click", () => {
    modal.classList.remove("open");
  });

  // Ingest Execution
  document.getElementById("btn-execute-ingest").addEventListener("click", async () => {
    const count = parseInt(document.getElementById("input-ingest-count").value) || 50;
    const query = document.getElementById("input-ingest-query").value;
    const mode = document.querySelector("input[name='ingest-mode']:checked").value;
    const btn = document.getElementById("btn-execute-ingest");

    btn.disabled = true;
    btn.innerHTML = "<i class='fa-solid fa-spinner fa-spin'></i> Ingesting...";

    try {
      const res = await fetch("/api/collect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ count, query, mode })
      });
      const result = await res.json();
      
      modal.classList.remove("open");
      showToast(result.message || "Tweets ingested successfully!");

      // Refresh all views
      loadDashboardData();
      loadNetworkGraph();
      loadGeoTweets();
      loadTweetExplorer();
    } catch (err) {
      console.error("Ingestion failed:", err);
      showToast("Ingestion failed", true);
    } finally {
      btn.disabled = false;
      btn.innerHTML = "<i class='fa-solid fa-cloud-arrow-down'></i> Start Ingestion";
    }
  });
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}
