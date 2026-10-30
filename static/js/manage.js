/**
 * CivicAI - Complaint Management Console & Workflow Controller
 */

let allComplaints = [];

document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const filterSearch = document.getElementById("filterSearch");
  const filterCategory = document.getElementById("filterCategory");
  const filterStatus = document.getElementById("filterStatus");
  const filterPriority = document.getElementById("filterPriority");
  const chkIncludeDuplicates = document.getElementById("chkIncludeDuplicates");

  if (filterSearch && urlParams.has("search")) {
    filterSearch.value = urlParams.get("search");
  }
  if (filterPriority && urlParams.has("priority")) {
    filterPriority.value = urlParams.get("priority");
  }
  if (filterStatus && urlParams.has("status")) {
    filterStatus.value = urlParams.get("status");
  }

  loadComplaints();

  // Attach filter listeners
  if (filterSearch) filterSearch.addEventListener("input", debounce(filterTable, 250));
  if (filterCategory) filterCategory.addEventListener("change", filterTable);
  if (filterStatus) filterStatus.addEventListener("change", filterTable);
  if (filterPriority) filterPriority.addEventListener("change", filterTable);
  if (chkIncludeDuplicates) chkIncludeDuplicates.addEventListener("change", filterTable);

  const btnReset = document.getElementById("btnResetFilters");
  if (btnReset) {
    btnReset.addEventListener("click", () => {
      if (filterSearch) filterSearch.value = "";
      if (filterCategory) filterCategory.value = "All";
      if (filterStatus) filterStatus.value = "All";
      if (filterPriority) filterPriority.value = "All";
      if (chkIncludeDuplicates) chkIncludeDuplicates.checked = true;
      filterTable();
    });
  }

  // Modal close handlers
  const btnCloseModal = document.getElementById("btnCloseModal");
  const btnCancelModal = document.getElementById("btnCancelModal");
  if (btnCloseModal) btnCloseModal.addEventListener("click", closeModal);
  if (btnCancelModal) btnCancelModal.addEventListener("click", closeModal);

  // Modal Update Form Submit
  const updateForm = document.getElementById("updateStatusForm");
  if (updateForm) {
    updateForm.addEventListener("submit", handleStatusUpdate);
  }
});

function debounce(func, delay) {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => func.apply(this, args), delay);
  };
}

async function loadComplaints() {
  const tbody = document.getElementById("complaintsTableBody");
  try {
    const res = await fetch("/api/complaints?include_duplicates=true");
    const data = await res.json();
    if (data.success) {
      allComplaints = data.complaints;
      filterTable();
    }
  } catch (err) {
    if (tbody) {
      tbody.innerHTML = `
        <tr><td colspan="8" style="text-align: center; color: var(--critical);">Error loading complaints from database.</td></tr>
      `;
    }
  }
}

function filterTable() {
  const filterSearch = document.getElementById("filterSearch");
  const filterCategory = document.getElementById("filterCategory");
  const filterStatus = document.getElementById("filterStatus");
  const filterPriority = document.getElementById("filterPriority");
  const chkIncludeDuplicates = document.getElementById("chkIncludeDuplicates");

  const search = filterSearch ? filterSearch.value.toLowerCase().trim() : "";
  const category = filterCategory ? filterCategory.value : "All";
  const status = filterStatus ? filterStatus.value : "All";
  const priority = filterPriority ? filterPriority.value : "All";
  const includeDups = chkIncludeDuplicates ? chkIncludeDuplicates.checked : true;

  const filtered = allComplaints.filter(c => {
    if (!includeDups && c.is_duplicate) return false;
    if (category !== "All" && c.category !== category) {
      // Also allow legacy category equivalents
      const legacyMap = {
        "Road Damage": "Roads & Potholes",
        "Waterlogging": "Waterlogging & Drainage",
        "Garbage": "Garbage & Sanitation",
        "Streetlight": "Streetlights & Electricity",
        "Drainage": "Open Manhole & Safety"
      };
      if (legacyMap[category] !== c.category && category !== c.category) {
        return false;
      }
    }
    if (status !== "All" && c.status !== status) return false;
    if (priority !== "All" && (c.priority || "").toUpperCase() !== (priority || "").toUpperCase()) return false;

    if (search) {
      const match = 
        (c.complaint_id && c.complaint_id.toLowerCase().includes(search)) ||
        (c.title && c.title.toLowerCase().includes(search)) ||
        (c.citizen_name && c.citizen_name.toLowerCase().includes(search)) ||
        (c.location_name && c.location_name.toLowerCase().includes(search)) ||
        (c.description && c.description.toLowerCase().includes(search));
      if (!match) return false;
    }
    return true;
  });

  const countText = document.getElementById("filteredCountText");
  if (countText) {
    countText.textContent = `Showing ${filtered.length} of ${allComplaints.length} records`;
  }
  renderTable(filtered);
}

function renderTable(complaints) {
  const tbody = document.getElementById("complaintsTableBody");
  if (!tbody) return;

  if (complaints.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; padding: 3rem; color: var(--text-muted);">
          No complaints match the selected filter criteria.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = complaints.map(c => `
    <tr>
      <td>
        <span style="font-family: monospace; font-weight: 700; color: var(--cyan-400);">
          ${c.complaint_id}
        </span>
        ${c.is_duplicate ? '<span class="badge" style="background: rgba(99, 102, 241, 0.2); color: #c4b5fd; font-size: 0.65rem; margin-left: 4px;">DUP</span>' : ''}
      </td>
      <td>
        <div style="font-weight: 600; color: #ffffff;">${c.citizen_name}</div>
        <div style="font-size: 0.75rem; color: var(--text-dim);">${timeAgo(c.created_at)}</div>
      </td>
      <td>
        <div style="font-weight: 600; color: #ffffff; max-width: 280px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
          ${c.title}
        </div>
        <div style="font-size: 0.75rem; color: var(--text-dim);">${c.category}</div>
      </td>
      <td>
        <div style="font-size: 0.82rem; max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
          ${c.location_name}
        </div>
      </td>
      <td>
        ${renderPriorityBadge(c.priority, c.priority_score)}
      </td>
      <td>
        ${renderStatusBadge(c.status)}
      </td>
      <td>
        <div style="font-size: 0.82rem; color: #e2e8f0; max-width: 170px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
          ${c.assigned_department || 'Unassigned'}
        </div>
        <div style="font-size: 0.72rem; color: var(--text-dim);">${c.assigned_officer || 'No officer'}</div>
      </td>
      <td style="text-align: right;">
        <button class="btn btn-outline-teal btn-sm" onclick="openManageModal(${c.id})">
          <i class="fas fa-sliders-h"></i> Manage
        </button>
      </td>
    </tr>
  `).join("");
}

async function openManageModal(complaintId) {
  try {
    const res = await fetch(`/api/complaints/${complaintId}`);
    const data = await res.json();
    if (!data.success) return;

    const c = data.complaint;
    document.getElementById("modalComplaintDbId").value = c.id;
    document.getElementById("modalId").textContent = c.complaint_id;
    document.getElementById("modalStatusBadge").innerHTML = renderStatusBadge(c.status);
    document.getElementById("modalPriorityBadge").innerHTML = renderPriorityBadge(c.priority, c.priority_score);
    document.getElementById("modalDate").textContent = formatDateTime(c.created_at);
    document.getElementById("modalCitizen").textContent = `${c.citizen_name} (${c.citizen_contact || 'No contact'})`;

    document.getElementById("modalTitle").textContent = c.title;
    document.getElementById("modalDesc").textContent = c.description;
    document.getElementById("modalLocation").textContent = `${c.location_name} (GPS: ${c.latitude.toFixed(4)}, ${c.longitude.toFixed(4)})`;
    document.getElementById("modalImg").src = c.image_url || '/static/images/samples/pothole_crater_1.svg';

    document.getElementById("modalScoreText").textContent = `Score: ${c.priority_score}/100`;
    
    // AI Summary
    const summaryEl = document.getElementById("modalAiSummary");
    if (summaryEl) {
      summaryEl.textContent = c.summary || c.description;
    }

    // AI Priority Justification Bullet Points
    const reasonsList = document.getElementById("modalPriorityReasons");
    if (reasonsList) {
      const reasons = c.priority_reasons || (c.priority_factors ? c.priority_factors.map(f => f.detail || f.factor) : []);
      if (reasons.length > 0) {
        reasonsList.innerHTML = reasons.map(r => `<li>${r}</li>`).join("");
      } else {
        reasonsList.innerHTML = `<li>Standard municipal maintenance priority assigned based on safety score.</li>`;
      }
    }

    const explanationEl = document.getElementById("modalExplanation");
    if (explanationEl) {
      explanationEl.textContent = c.priority_explanation || "AI priority evaluated on public hazard metrics.";
    }

    const factorsBox = document.getElementById("modalFactors");
    if (c.priority_factors && c.priority_factors.length > 0) {
      factorsBox.innerHTML = c.priority_factors.map(f => `
        <span class="badge" style="background: rgba(6, 182, 212, 0.15); color: var(--cyan-300);">
          ${f.factor}: +${f.points}
        </span>
      `).join("");
    } else {
      factorsBox.innerHTML = "";
    }

    // Pre-fill Form
    document.getElementById("modalSelectStatus").value = c.status;
    if (c.assigned_department) document.getElementById("modalSelectDept").value = c.assigned_department;
    document.getElementById("modalInputOfficer").value = c.assigned_officer || "";
    document.getElementById("modalResolutionNotes").value = c.resolution_notes || "";

    // Track link
    document.getElementById("modalTrackLink").href = `/track?id=${c.complaint_id}`;

    // Duplicate Radar
    const dupContainer = document.getElementById("modalDupContainer");
    const dupBadge = document.getElementById("modalDupBadge");
    const candidates = c.duplicate_candidates || [];

    if (dupBadge) dupBadge.textContent = `${candidates.length} Detected`;
    if (dupContainer) {
      if (candidates.length > 0) {
        dupContainer.innerHTML = candidates.map(d => `
          <div style="background: rgba(15, 23, 42, 0.9); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: var(--radius-sm); padding: 0.75rem; display: flex; justify-content: space-between; align-items: center;">
            <div>
              <div style="font-weight: 700; color: #ffffff; font-size: 0.85rem;">
                <span style="font-family: monospace; color: var(--cyan-400);">${d.complaint_id}</span> • ${d.title}
              </div>
              <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 2px;">
                <i class="fas fa-map-marker-alt text-teal"></i> ${d.distance_meters}m away • ${d.similarity_score}% match (${d.reasons.join(", ")})
              </div>
            </div>
            <button type="button" class="btn btn-outline-teal btn-sm" onclick="mergeDuplicate(${d.candidate_id}, ${c.id})">
              <i class="fas fa-compress-arrows-alt"></i> Merge Into This
            </button>
          </div>
        `).join("");
      } else {
        dupContainer.innerHTML = `<div class="text-muted" style="font-size: 0.82rem;">No nearby duplicate reports found.</div>`;
      }
    }

    document.getElementById("manageModal").classList.add("active");
  } catch (err) {
    showToast("Error opening complaint details", "danger");
  }
}

function closeModal() {
  const modal = document.getElementById("manageModal");
  if (modal) modal.classList.remove("active");
}

async function handleStatusUpdate(e) {
  e.preventDefault();
  const dbId = document.getElementById("modalComplaintDbId").value;
  const status = document.getElementById("modalSelectStatus").value;
  const dept = document.getElementById("modalSelectDept").value;
  const officer = document.getElementById("modalInputOfficer").value;
  const notes = document.getElementById("modalResolutionNotes").value;
  const actor = document.getElementById("modalInputActor").value || "Municipal Admin";

  const btnSave = document.getElementById("btnSaveStatus");
  btnSave.disabled = true;
  btnSave.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Saving changes...';

  try {
    const res = await fetch(`/api/complaints/${dbId}/status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        status: status,
        assigned_department: dept,
        assigned_officer: officer,
        resolution_notes: notes,
        actor: actor
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, "success");
      closeModal();
      loadComplaints();
    } else {
      showToast(data.error || "Update failed", "danger");
    }
  } catch (err) {
    showToast("Network error updating status", "danger");
  } finally {
    btnSave.disabled = false;
    btnSave.innerHTML = '<i class="fas fa-save"></i> Save Status & Dispatch Changes';
  }
}

async function mergeDuplicate(duplicateId, masterId) {
  if (!confirm("Are you sure you want to merge this duplicate complaint into the master incident?")) return;

  try {
    const res = await fetch(`/api/complaints/${duplicateId}/merge`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ master_id: masterId })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, "success");
      openManageModal(masterId);
      loadComplaints();
    } else {
      showToast(data.error || "Merge failed", "danger");
    }
  } catch (err) {
    showToast("Error merging duplicate", "danger");
  }
}

