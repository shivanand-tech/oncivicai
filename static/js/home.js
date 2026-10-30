/**
 * CivicAI - Home Page Interactive Logic
 * Handles live KPI statistics & public complaints showcase feed
 */

document.addEventListener("DOMContentLoaded", () => {
  loadHomeStatistics();
  loadRecentComplaints();
});

async function loadHomeStatistics() {
  try {
    const res = await fetch("/api/stats");
    const data = await res.json();
    if (!data.success) return;

    // 4 Primary Statistics Cards
    const elTotal = document.getElementById("statTotal");
    const elPending = document.getElementById("statPending");
    const elResolved = document.getElementById("statResolved");
    const elUrgent = document.getElementById("statUrgent");

    if (elTotal) elTotal.textContent = data.total_complaints;
    if (elPending) elPending.textContent = data.pending_complaints;
    if (elResolved) elResolved.textContent = data.resolved_complaints;
    if (elUrgent) elUrgent.textContent = data.urgent_complaints !== undefined ? data.urgent_complaints : data.critical_unresolved;

  } catch (err) {
    console.error("Error loading home statistics:", err);
  }
}

async function loadRecentComplaints() {
  const container = document.getElementById("recentComplaintsGrid");
  if (!container) return;

  try {
    const res = await fetch("/api/complaints?include_duplicates=false");
    const data = await res.json();

    if (data.success && data.complaints && data.complaints.length > 0) {
      const recent = data.complaints.slice(0, 6);
      container.innerHTML = recent.map(c => `
        <div class="card card-lift" style="display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.85rem;">
              <span style="font-family: monospace; font-size: 0.85rem; color: var(--cyan-400); font-weight: 700;">
                <i class="fas fa-tag"></i> ${c.complaint_id}
              </span>
              ${renderPriorityBadge(c.priority, c.priority_score)}
            </div>

            <div style="margin-bottom: 0.85rem; overflow: hidden; border-radius: var(--radius-sm);">
              <img src="${c.image_url || '/static/images/samples/pothole_crater_1.svg'}" alt="${c.title}" style="width: 100%; height: 160px; object-fit: cover; border: 1px solid var(--border-subtle); transition: transform 0.3s ease;" onmouseover="this.style.transform='scale(1.04)'" onmouseout="this.style.transform='scale(1)'">
            </div>

            <h4 style="margin-bottom: 0.4rem; font-size: 1.05rem; line-height: 1.35;">${c.title}</h4>
            <p class="text-muted" style="font-size: 0.85rem; line-height: 1.5; margin-bottom: 0.85rem;">
              ${c.description.length > 95 ? c.description.substring(0, 95) + '...' : c.description}
            </p>
          </div>

          <div>
            <div style="display: flex; align-items: center; gap: 0.4rem; font-size: 0.8rem; color: var(--text-dim); margin-bottom: 0.85rem;">
              <i class="fas fa-map-marker-alt text-teal"></i>
              <span>${c.location_name}</span>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 0.75rem; border-top: 1px solid var(--border-subtle);">
              ${renderStatusBadge(c.status)}
              <a href="/track?id=${c.complaint_id}" class="btn btn-outline-teal btn-sm">
                Track <i class="fas fa-chevron-right"></i>
              </a>
            </div>
          </div>
        </div>
      `).join("");
    } else {
      container.innerHTML = `<div class="card" style="grid-column: 1/-1; text-align: center; padding: 2rem;">No complaints registered yet.</div>`;
    }
  } catch (err) {
    container.innerHTML = `<div class="text-danger" style="grid-column: 1/-1; text-align: center;">Error loading complaints feed.</div>`;
  }
}

