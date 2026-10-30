/**
 * CivicAI - Executive Admin Dashboard & Real-Time Analytics
 */

let catChartInstance = null;
let prioChartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
  loadAdminStats();
  loadAdminHotspots();
  loadCriticalIncidents();

  const btnRefresh = document.getElementById("btnRefreshStats");
  if (btnRefresh) {
    btnRefresh.addEventListener("click", () => {
      loadAdminStats();
      loadAdminHotspots();
      loadCriticalIncidents();
      showToast("Dashboard metrics refreshed!", "info");
    });
  }
});

async function loadAdminStats() {
  try {
    const res = await fetch("/api/stats");
    const stats = await res.json();
    if (!stats.success) return;

    // 4 Primary Statistics Cards
    const kpiTotal = document.getElementById("kpiTotal");
    const kpiPending = document.getElementById("kpiPending");
    const kpiResolved = document.getElementById("kpiResolved");
    const kpiUrgent = document.getElementById("kpiUrgent");
    const kpiDuplicates = document.getElementById("kpiDuplicates");
    const kpiAvgHours = document.getElementById("kpiAvgHours");

    if (kpiTotal) kpiTotal.textContent = stats.total_complaints;
    if (kpiPending) kpiPending.textContent = stats.pending_complaints;
    if (kpiResolved) kpiResolved.textContent = stats.resolved_complaints;
    if (kpiUrgent) kpiUrgent.textContent = stats.urgent_complaints !== undefined ? stats.urgent_complaints : stats.critical_unresolved;
    if (kpiDuplicates) kpiDuplicates.textContent = stats.duplicates_detected;
    if (kpiAvgHours) kpiAvgHours.textContent = `${stats.avg_resolution_hours}h`;

    // Charts
    renderCategoryChart(stats.by_category);
    renderPriorityChart(stats.by_priority);

    // Department Performance
    renderDepartmentTable(stats.department_performance);

  } catch (err) {
    console.error("Error loading admin stats:", err);
  }
}

function renderCategoryChart(categories) {
  const canvas = document.getElementById("categoryChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (catChartInstance) catChartInstance.destroy();

  const labels = categories.map(c => c.category);
  const data = categories.map(c => c.count);
  const colors = [
    "#06b6d4", "#14b8a6", "#3b82f6", "#8b5cf6", "#f59e0b", "#ec4899"
  ];

  catChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: colors,
        borderColor: "#0f172a",
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "right",
          labels: { color: "#e2e8f0", font: { family: "Plus Jakarta Sans", size: 12 } }
        }
      }
    }
  });
}

function renderPriorityChart(priorities) {
  const canvas = document.getElementById("priorityChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (prioChartInstance) prioChartInstance.destroy();

  const labels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];
  const colorMap = {
    "CRITICAL": "#ef4444",
    "HIGH": "#f59e0b",
    "MEDIUM": "#06b6d4",
    "LOW": "#10b981"
  };

  const counts = labels.map(l => {
    let total = 0;
    priorities.forEach(p => {
      if ((p.priority || "").toUpperCase() === l) {
        total += p.count;
      }
    });
    return total;
  });

  prioChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Number of Complaints",
        data: counts,
        backgroundColor: labels.map(l => colorMap[l]),
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          ticks: { color: "#94a3b8", font: { family: "Plus Jakarta Sans", weight: "bold" } },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        },
        y: {
          beginAtZero: true,
          ticks: { color: "#94a3b8" },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        }
      }
    }
  });
}

function renderDepartmentTable(depts) {
  const tbody = document.getElementById("deptTableBody");
  if (!tbody) return;
  if (!depts || depts.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align: center;">No department records found.</td></tr>`;
    return;
  }

  tbody.innerHTML = depts.map(d => {
    const rate = d.resolution_rate;
    let badgeClass = "priority-medium";
    if (rate >= 60) badgeClass = "priority-low";
    else if (rate < 30) badgeClass = "priority-critical";

    return `
      <tr>
        <td style="font-weight: 600; color: #ffffff;">${d.department}</td>
        <td>${d.total}</td>
        <td style="color: #34d399; font-weight: 600;">${d.resolved}</td>
        <td>
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div style="flex: 1; height: 6px; background: rgba(255,255,255,0.1); border-radius: 9999px; overflow: hidden; min-width: 60px;">
              <div style="width: ${rate}%; height: 100%; background: #06b6d4;"></div>
            </div>
            <span style="font-size: 0.8rem; font-weight: 700;">${rate}%</span>
          </div>
        </td>
        <td>
          <span class="badge ${badgeClass}">${rate >= 60 ? 'Optimal' : rate >= 30 ? 'Moderate' : 'Backlog'}</span>
        </td>
      </tr>
    `;
  }).join("");
}

async function loadCriticalIncidents() {
  const container = document.getElementById("criticalQueue");
  if (!container) return;

  try {
    const res = await fetch("/api/complaints?include_duplicates=false");
    const data = await res.json();
    const allComplaints = data.complaints || [];

    // Filter for active High or Critical priority incidents
    const criticals = allComplaints.filter(c => {
      const prio = (c.priority || "").toUpperCase();
      return (prio === "CRITICAL" || prio === "HIGH") && c.status !== "Resolved";
    });

    if (criticals.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 2rem; color: #34d399; grid-column: 1/-1;">
          <i class="fas fa-shield-alt" style="font-size: 1.5rem;"></i>
          <div style="margin-top: 0.5rem; font-weight: 600;">All critical municipal hazards resolved or in triage!</div>
        </div>
      `;
      return;
    }

    container.innerHTML = criticals.slice(0, 4).map(c => `
      <div class="card card-lift" style="border-color: rgba(239, 68, 68, 0.4); display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.65rem;">
            <a href="/track?id=${c.complaint_id}" style="font-family: monospace; font-weight: 700; color: #f87171;">
              <i class="fas fa-exclamation-triangle"></i> ${c.complaint_id}
            </a>
            ${renderPriorityBadge(c.priority, c.priority_score)}
          </div>

          <h4 style="font-size: 1rem; margin-bottom: 0.4rem; line-height: 1.3;">${c.title}</h4>
          
          <div style="font-size: 0.78rem; color: var(--text-dim); margin-bottom: 0.5rem;">
            <i class="fas fa-map-marker-alt text-teal"></i> ${c.location_name}
          </div>

          <!-- AI Summary -->
          <div style="font-size: 0.8rem; color: #e2e8f0; background: rgba(6, 182, 212, 0.08); padding: 0.6rem; border-radius: var(--radius-sm); border-left: 3px solid var(--cyan-400); margin-bottom: 0.65rem; line-height: 1.4;">
            <strong style="color: var(--cyan-300);"><i class="fas fa-robot"></i> AI Summary:</strong> ${c.summary || c.description}
          </div>

          <!-- Priority Reasons -->
          <div style="margin-bottom: 0.75rem;">
            <div style="font-size: 0.75rem; color: #fca5a5; font-weight: 700; margin-bottom: 2px;">
              <i class="fas fa-exclamation-circle"></i> Priority Justification:
            </div>
            <ul style="padding-left: 1.15rem; font-size: 0.75rem; color: var(--text-muted); line-height: 1.45;">
              ${(c.priority_reasons || ['High emergency hazard requiring rapid mitigation']).map(r => `<li>${r}</li>`).join('')}
            </ul>
          </div>

          <div style="font-size: 0.78rem; color: var(--text-muted); background: rgba(0,0,0,0.3); padding: 0.4rem 0.6rem; border-radius: 4px; margin-bottom: 0.75rem;">
            Dept: <strong style="color: #ffffff;">${c.assigned_department}</strong>
          </div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 0.65rem; border-top: 1px solid var(--border-subtle);">
          ${renderStatusBadge(c.status)}
          <a href="/manage?search=${c.complaint_id}" class="btn btn-primary btn-sm">
            Manage <i class="fas fa-arrow-right"></i>
          </a>
        </div>
      </div>
    `).join("");

  } catch (err) {
    container.innerHTML = `<div class="text-danger" style="text-align: center; grid-column: 1/-1;">Error loading critical incidents.</div>`;
  }
}

async function loadAdminHotspots() {
  const grid = document.getElementById("adminHotspotsGrid");
  const badge = document.getElementById("adminHotspotCountBadge");
  if (!grid) return;

  try {
    const res = await fetch("/api/ai/hotspots");
    const data = await res.json();
    if (!data.success) return;

    const hotspots = data.hotspots || [];
    if (badge) {
      badge.textContent = `${hotspots.length} Clusters Detected`;
    }

    if (hotspots.length === 0) {
      grid.innerHTML = `
        <div style="text-align: center; padding: 2rem; color: #34d399; grid-column: 1/-1;">
          <i class="fas fa-check-circle" style="font-size: 1.5rem;"></i>
          <div style="margin-top: 0.5rem; font-weight: 600;">No geographic complaint clusters currently detected.</div>
        </div>
      `;
      return;
    }

    grid.innerHTML = hotspots.map(h => {
      const urgencyClass = (h.urgency || "High").toUpperCase() === "CRITICAL" ? "priority-critical" :
                           (h.urgency || "High").toUpperCase() === "HIGH" ? "priority-high" : "priority-medium";
      return `
        <div class="card card-lift" style="border-color: rgba(245, 158, 11, 0.3); background: rgba(15, 23, 42, 0.7); display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.65rem;">
              <span style="font-family: monospace; font-weight: 800; color: #fbbf24; font-size: 0.9rem;">
                <i class="fas fa-fire"></i> ${h.hotspot_id}
              </span>
              <span class="badge ${urgencyClass}">${h.urgency} Urgency</span>
            </div>

            <h4 style="font-size: 1rem; margin-bottom: 0.35rem; color: #ffffff;">
              ${h.area_name}
            </h4>

            <div style="font-size: 0.8rem; color: var(--cyan-300); font-weight: 600; margin-bottom: 0.5rem;">
              <i class="fas fa-tag"></i> Primary Issue: ${h.primary_category}
            </div>

            <p style="font-size: 0.78rem; color: var(--text-muted); line-height: 1.45; margin-bottom: 0.75rem;">
              ${h.description}
            </p>

            <div style="display: flex; gap: 0.5rem; font-size: 0.75rem; color: var(--text-dim); margin-bottom: 0.85rem;">
              <span style="background: rgba(255,255,255,0.05); padding: 0.2rem 0.5rem; border-radius: 4px;">
                <i class="fas fa-layer-group text-teal"></i> ${h.complaint_count} Complaints
              </span>
              <span style="background: rgba(255,255,255,0.05); padding: 0.2rem 0.5rem; border-radius: 4px;">
                <i class="fas fa-bullseye text-warning"></i> ${h.radius_meters}m Perimeter
              </span>
            </div>
          </div>

          <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 0.75rem; border-top: 1px solid var(--border-subtle);">
            <span style="font-size: 0.75rem; color: var(--text-dim); font-family: monospace;">
              GPS: ${h.center[0]}, ${h.center[1]}
            </span>
            <a href="/map?lat=${h.center[0]}&lng=${h.center[1]}&zoom=16" class="btn btn-outline-teal btn-sm" style="font-size: 0.75rem; padding: 0.3rem 0.65rem;">
              <i class="fas fa-crosshairs"></i> View on Map
            </a>
          </div>
        </div>
      `;
    }).join("");

  } catch (err) {
    grid.innerHTML = `<div class="text-danger" style="text-align: center; grid-column: 1/-1;">Error loading hotspot analytics.</div>`;
  }
}

