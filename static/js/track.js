/**
 * CivicAI - Complaint Tracking & Real-Time Status Verification
 */

document.addEventListener("DOMContentLoaded", () => {
  const trackForm = document.getElementById("trackForm");
  const trackInput = document.getElementById("trackInput");
  const trackLoading = document.getElementById("trackLoading");
  const trackError = document.getElementById("trackError");
  const trackErrorMsg = document.getElementById("trackErrorMsg");
  const detailContainer = document.getElementById("complaintDetailContainer");

  if (!trackForm) return;

  // Sample ID chips
  document.querySelectorAll(".sample-id-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      trackInput.value = chip.dataset.id;
      loadComplaint(chip.dataset.id);
    });
  });

  // Track Form Submit
  trackForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const id = trackInput.value.trim();
    if (id) loadComplaint(id);
  });

  // Auto-load if prefilled
  if (trackInput.value.trim()) {
    loadComplaint(trackInput.value.trim());
  }

  async function loadComplaint(identifier) {
    if (trackLoading) trackLoading.style.display = "block";
    if (trackError) trackError.style.display = "none";
    if (detailContainer) detailContainer.style.display = "none";

    try {
      const res = await fetch(`/api/complaints/${encodeURIComponent(identifier)}`);
      const data = await res.json();
      if (trackLoading) trackLoading.style.display = "none";

      if (!res.ok || !data.success) {
        if (trackErrorMsg) trackErrorMsg.textContent = data.error || `No municipal record found for '${identifier}'.`;
        if (trackError) trackError.style.display = "block";
        return;
      }

      renderComplaintDetails(data.complaint);
      if (detailContainer) {
        detailContainer.style.display = "block";
        detailContainer.scrollIntoView({ behavior: "smooth" });
      }
    } catch (err) {
      if (trackLoading) trackLoading.style.display = "none";
      if (trackErrorMsg) trackErrorMsg.textContent = "Error connecting to CivicAI registry service.";
      if (trackError) trackError.style.display = "block";
    }
  }

  function renderComplaintDetails(c) {
    // Header
    const detailId = document.getElementById("detailId");
    const detailStatusBadge = document.getElementById("detailStatusBadge");
    const detailPriorityBadge = document.getElementById("detailPriorityBadge");
    const detailCreatedAt = document.getElementById("detailCreatedAt");
    const detailSlaDeadline = document.getElementById("detailSlaDeadline");
    const detailSlaStatus = document.getElementById("detailSlaStatus");

    if (detailId) detailId.textContent = c.complaint_id;
    if (detailStatusBadge) detailStatusBadge.innerHTML = renderStatusBadge(c.status);
    if (detailPriorityBadge) detailPriorityBadge.innerHTML = renderPriorityBadge(c.priority, c.priority_score);
    if (detailCreatedAt) detailCreatedAt.textContent = formatDateTime(c.created_at);
    if (detailSlaDeadline) detailSlaDeadline.textContent = formatDateTime(c.sla_deadline);

    // Calculate SLA delta
    const now = new Date();
    const deadline = new Date(c.sla_deadline);
    const diffHours = Math.round((deadline - now) / (1000 * 60 * 60));

    if (detailSlaStatus) {
      if (c.status === "Resolved") {
        detailSlaStatus.innerHTML = `<i class="fas fa-check-circle text-success"></i> Resolved within SLA window`;
      } else if (diffHours > 0) {
        detailSlaStatus.innerHTML = `<i class="fas fa-clock text-warning"></i> ${diffHours}h remaining to SLA target`;
      } else {
        detailSlaStatus.innerHTML = `<i class="fas fa-exclamation-triangle text-danger"></i> SLA target exceeded by ${Math.abs(diffHours)}h`;
      }
    }

    // 5-Stage Timeline
    renderTimeline(c.status, c.created_at, c.updated_at, c.resolved_at, c.timeline);

    // Particulars
    const detailTitle = document.getElementById("detailTitle");
    const detailCategory = document.getElementById("detailCategory");
    const detailCitizen = document.getElementById("detailCitizen");
    const detailDescription = document.getElementById("detailDescription");
    const detailDept = document.getElementById("detailDept");
    const detailOfficer = document.getElementById("detailOfficer");
    const detailLocation = document.getElementById("detailLocation");
    const detailCoords = document.getElementById("detailCoords");

    if (detailTitle) detailTitle.textContent = c.title;
    if (detailCategory) detailCategory.textContent = c.category;
    if (detailCitizen) detailCitizen.textContent = `${c.citizen_name} (${c.citizen_contact || 'Registered Citizen'})`;
    if (detailDescription) detailDescription.textContent = c.description;
    if (detailDept) detailDept.textContent = c.assigned_department || "Municipal Administration";
    if (detailOfficer) detailOfficer.textContent = c.assigned_officer || "Pending Field Officer Assignment";
    if (detailLocation) detailLocation.textContent = c.location_name;
    if (detailCoords) detailCoords.textContent = `GPS: ${c.latitude.toFixed(5)}, ${c.longitude.toFixed(5)}`;

    // Official Remediation / Inspection Notes
    const notesWrap = document.getElementById("detailResolutionNotesWrap");
    const notesEl = document.getElementById("detailResolutionNotes");
    if (notesWrap && notesEl) {
      if (c.resolution_notes && c.resolution_notes.trim()) {
        notesEl.textContent = c.resolution_notes;
        notesWrap.style.display = "block";
      } else {
        notesWrap.style.display = "none";
      }
    }

    // Photographic Evidence
    const evidenceBox = document.getElementById("evidenceImages");
    if (evidenceBox) {
      let evHtml = `
        <div>
          <div style="font-size: 0.75rem; color: var(--text-dim); margin-bottom: 0.25rem;">Citizen Upload Evidence:</div>
          <img src="${c.image_url || '/static/images/samples/pothole_crater_1.svg'}" alt="Report photo" style="width: 100%; height: 190px; object-fit: cover; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
        </div>
      `;

      if (c.resolution_image_url) {
        evHtml += `
          <div>
            <div style="font-size: 0.75rem; color: #34d399; margin-bottom: 0.25rem;"><i class="fas fa-check"></i> Field Resolution Proof:</div>
            <img src="${c.resolution_image_url}" alt="Resolution proof" style="width: 100%; height: 190px; object-fit: cover; border-radius: var(--radius-sm); border: 1px solid rgba(16, 185, 129, 0.4);">
          </div>
        `;
      }
      evidenceBox.innerHTML = evHtml;
    }

    // Official Audit Trail
    const auditBox = document.getElementById("auditLogList");
    if (auditBox) {
      if (c.timeline && c.timeline.length > 0) {
        auditBox.innerHTML = c.timeline.map(log => `
          <div style="display: flex; gap: 0.75rem; align-items: flex-start; padding-bottom: 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <div style="width: 28px; height: 28px; border-radius: 50%; background: rgba(6, 182, 212, 0.15); border: 1px solid rgba(6, 182, 212, 0.4); display: flex; align-items: center; justify-content: center; font-size: 0.75rem; color: var(--cyan-400); flex-shrink: 0; margin-top: 2px;">
              <i class="fas fa-check"></i>
            </div>
            <div style="flex: 1;">
              <div style="display: flex; justify-content: space-between; font-size: 0.82rem;">
                <span style="font-weight: 700; color: #ffffff;">${log.event_type}</span>
                <span style="font-size: 0.75rem; color: var(--text-dim);">${formatDateTime(log.timestamp)}</span>
              </div>
              <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 2px;">${log.description}</div>
              <div style="font-size: 0.75rem; color: var(--teal-400); margin-top: 2px;"><i class="fas fa-user-circle"></i> Actor: ${log.actor}</div>
            </div>
          </div>
        `).join("");
      } else {
        auditBox.innerHTML = `<div class="text-muted" style="font-size: 0.85rem;">No audit events recorded yet.</div>`;
      }
    }

    // AI Priority Breakdown
    const aiScoreTag = document.getElementById("aiScoreTag");
    const aiExplanation = document.getElementById("aiExplanation");
    const factorsBox = document.getElementById("aiFactorsList");

    if (aiScoreTag) aiScoreTag.textContent = `${c.priority_score} / 100 PTS`;
    if (aiExplanation) aiExplanation.textContent = c.priority_explanation || "Computed using multi-factor hazard severity heuristics.";

    if (factorsBox) {
      if (c.priority_factors && c.priority_factors.length > 0) {
        factorsBox.innerHTML = c.priority_factors.map(f => `
          <div style="background: rgba(15, 23, 42, 0.7); padding: 0.65rem 0.85rem; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 0.25rem;">
              <span style="font-weight: 600; color: #ffffff;">${f.factor}</span>
              <span style="color: var(--cyan-400); font-weight: 700;">+${f.points} / ${f.max}</span>
            </div>
            <div style="font-size: 0.78rem; color: var(--text-muted);">${f.detail}</div>
          </div>
        `).join("");
      } else {
        factorsBox.innerHTML = `<div class="text-muted" style="font-size: 0.82rem;">Factors details unavailable.</div>`;
      }
    }

    // Action Brief
    const ab = c.action_brief || {};
    const briefBox = document.getElementById("actionBriefContent");
    if (briefBox) {
      briefBox.innerHTML = `
        <div style="margin-bottom: 0.65rem;">
          <span class="text-dim">Executive Action:</span>
          <div style="font-weight: 600; color: #ffffff;">${ab.action_title || 'Deploy Rapid Response Unit'}</div>
        </div>
        <div style="margin-bottom: 0.65rem;">
          <span class="text-dim">Recommended Crew & Gear:</span>
          <div style="color: var(--cyan-300);">${ab.recommended_crew_and_gear || '2-person repair squad + inspection tools'}</div>
        </div>
        <div style="margin-bottom: 0.65rem;">
          <span class="text-dim">Dispatch Urgency:</span>
          <div style="color: #fbbf24;">${ab.dispatch_urgency || 'Standard Work Order'}</div>
        </div>
        <div>
          <span class="text-dim">Verification Protocol:</span>
          <div>${ab.verification_protocol || 'Geo-tagged photographic audit required.'}</div>
        </div>
      `;
    }

    // Duplicate Radar Candidates
    const dupBox = document.getElementById("duplicateRadarList");
    const dupBadge = document.getElementById("duplicateCountBadge");
    const dupCandidates = c.duplicate_candidates || [];

    if (dupBadge) dupBadge.textContent = `${dupCandidates.length} Detected`;
    if (dupBox) {
      if (dupCandidates.length > 0) {
        dupBox.innerHTML = dupCandidates.map(d => `
          <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: var(--radius-sm); padding: 0.75rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 0.25rem;">
              <a href="/track?id=${d.complaint_id}" class="text-teal" style="font-family: monospace; font-weight: 700;">
                <i class="fas fa-tag"></i> ${d.complaint_id}
              </a>
              <span class="badge" style="background: rgba(99, 102, 241, 0.25); color: #c4b5fd;">
                ${d.similarity_score}% Match
              </span>
            </div>
            <div style="font-size: 0.82rem; color: #ffffff; margin-bottom: 0.35rem; line-height: 1.3;">${d.title}</div>
            <div style="font-size: 0.75rem; color: var(--text-dim);">
              <i class="fas fa-map-marker-alt text-teal"></i> ${d.distance_meters}m away • ${d.reasons.join(", ")}
            </div>
          </div>
        `).join("");
      } else {
        dupBox.innerHTML = `<div class="text-muted" style="font-size: 0.82rem;">No duplicate reports detected within 600m radius. Unique incident.</div>`;
      }
    }

    // Citizen Rating Box for Resolved Complaints
    const ratingBox = document.getElementById("citizenRatingBox");
    if (ratingBox) {
      if (c.status === "Resolved") {
        ratingBox.style.display = "block";
        setupCitizenRating(c.id);
      } else {
        ratingBox.style.display = "none";
      }
    }
  }

  function renderTimeline(currentStatus, created, updated, resolved, timelineLogs = []) {
    const stageTimes = {
      "Submitted": created,
      "Under Review": null,
      "Assigned": null,
      "In Progress": updated,
      "Resolved": resolved
    };

    if (Array.isArray(timelineLogs)) {
      timelineLogs.forEach(log => {
        const desc = (log.description || "").toLowerCase();
        if (desc.includes("to 'under review'") || desc.includes("under review")) {
          stageTimes["Under Review"] = log.timestamp;
        } else if (desc.includes("to 'assigned'") || desc.includes("assigned")) {
          stageTimes["Assigned"] = log.timestamp;
        } else if (desc.includes("to 'in progress'") || desc.includes("in progress")) {
          stageTimes["In Progress"] = log.timestamp;
        } else if (desc.includes("to 'resolved'") || desc.includes("resolved")) {
          stageTimes["Resolved"] = log.timestamp;
        }
      });
    }

    const stages = [
      { key: "Submitted", label: "Submitted", icon: "1", time: stageTimes["Submitted"] },
      { key: "Under Review", label: "Under Review", icon: "2", time: stageTimes["Under Review"] },
      { key: "Assigned", label: "Assigned", icon: "3", time: stageTimes["Assigned"] },
      { key: "In Progress", label: "In Progress", icon: "4", time: stageTimes["In Progress"] },
      { key: "Resolved", label: "Resolved", icon: "5", time: stageTimes["Resolved"] }
    ];

    const stageOrder = ["Submitted", "Under Review", "Assigned", "In Progress", "Resolved"];
    const currentIdx = stageOrder.indexOf(currentStatus);

    const tl = document.getElementById("statusTimeline");
    if (!tl) return;
    const progressPct = currentIdx >= 0 ? (currentIdx / (stages.length - 1)) * 100 : 0;

    tl.innerHTML = `
      <div class="timeline-progress" style="width: ${progressPct}%;"></div>
      ${stages.map((st, i) => {
      let stateClass = "";
      if (i < currentIdx) stateClass = "completed";
      else if (i === currentIdx) stateClass = "active";

      let timeDisplay = "";
      if (st.time) {
        timeDisplay = timeAgo(st.time);
      } else if (i === currentIdx) {
        timeDisplay = '<span style="color: var(--cyan-400);">Current</span>';
      } else if (i < currentIdx) {
        timeDisplay = '<span style="color: #34d399;">Done</span>';
      } else {
        timeDisplay = '<span style="color: var(--text-dim);">Pending</span>';
      }

      return `
          <div class="timeline-step ${stateClass}">
            <div class="step-circle">
              ${i < currentIdx ? '<i class="fas fa-check"></i>' : st.icon}
            </div>
            <div class="step-label">${st.label}</div>
            <div class="step-time">${timeDisplay}</div>
          </div>
        `;
    }).join("")}
    `;
  }

  function setupCitizenRating(complaintDbId) {
    const starBtns = document.querySelectorAll(".star-btn");
    const inputRating = document.getElementById("inputRating");
    const ratingForm = document.getElementById("ratingForm");

    starBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        const val = parseInt(btn.dataset.value);
        if (inputRating) inputRating.value = val;
        starBtns.forEach(b => {
          if (parseInt(b.dataset.value) <= val) {
            b.classList.remove("far");
            b.classList.add("fas");
          } else {
            b.classList.remove("fas");
            b.classList.add("far");
          }
        });
      });
    });

    if (ratingForm) {
      ratingForm.onsubmit = async (e) => {
        e.preventDefault();
        try {
          const res = await fetch(`/api/complaints/${complaintDbId}/rate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              rating: inputRating ? inputRating.value : 5,
              feedback: document.getElementById("inputFeedback") ? document.getElementById("inputFeedback").value : ""
            })
          });
          const data = await res.json();
          if (data.success) {
            showToast("Thank you! Citizen verification registered.", "success");
            ratingForm.innerHTML = `<div style="color: #34d399; font-weight: 600;"><i class="fas fa-check-circle"></i> Verification submitted! Thank you for validating this resolution.</div>`;
          }
        } catch (err) {
          showToast("Error recording rating", "danger");
        }
      };
    }
  }
});

