/**
 * CivicAI - Complaint Submission & Real-time AI Triage Assistant
 */

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("complaintForm");
  if (!form) return;

  const inputTitle = document.getElementById("inputTitle");
  const inputDesc = document.getElementById("inputDescription");
  const inputCategory = document.getElementById("inputCategory");
  const inputLocation = document.getElementById("inputLocation");
  const inputLat = document.getElementById("inputLat");
  const inputLng = document.getElementById("inputLng");

  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const previewBox = document.getElementById("previewBox");
  const previewImg = document.getElementById("previewImg");
  const btnRemoveImg = document.getElementById("btnRemoveImg");
  const selectedSampleUrl = document.getElementById("selectedSampleUrl");

  const visionResults = document.getElementById("visionResults");
  const visionStatus = document.getElementById("visionStatus");
  const estPriorityBadge = document.getElementById("estPriorityBadge");
  const scoreText = document.getElementById("scoreText");
  const scoreBar = document.getElementById("scoreBar");
  const priorityJustification = document.getElementById("priorityJustification");
  const estSlaHours = document.getElementById("estSlaHours");

  // Location preset chips
  document.querySelectorAll(".loc-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      inputLocation.value = chip.dataset.name;
      inputLat.value = chip.dataset.lat;
      inputLng.value = chip.dataset.lng;
      showToast(`Selected location: ${chip.dataset.name}`, "info");
      updatePriorityEstimate();
    });
  });

  // GPS Geolocation Button
  const btnGPS = document.getElementById("btnDetectLocation");
  if (btnGPS) {
    btnGPS.addEventListener("click", () => {
      if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
          pos => {
            inputLat.value = pos.coords.latitude.toFixed(5);
            inputLng.value = pos.coords.longitude.toFixed(5);
            inputLocation.value = `GPS: ${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`;
            showToast("GPS coordinates acquired!", "success");
            updatePriorityEstimate();
          },
          err => {
            showToast("Geolocation unavailable: Using default coordinates", "warning");
          }
        );
      }
    });
  }

  // Dropzone file selection & drag/drop
  if (dropzone && fileInput) {
    dropzone.addEventListener("click", () => fileInput.click());

    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    });

    dropzone.addEventListener("dragleave", () => {
      dropzone.classList.remove("dragover");
    });

    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragover");
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        fileInput.files = e.dataTransfer.files;
        handleSelectedFile(e.dataTransfer.files[0]);
      }
    });

    fileInput.addEventListener("change", () => {
      if (fileInput.files && fileInput.files[0]) {
        handleSelectedFile(fileInput.files[0]);
      }
    });
  }

  function handleSelectedFile(file) {
    const reader = new FileReader();
    reader.onload = e => {
      previewImg.src = e.target.result;
      previewBox.style.display = "block";
      selectedSampleUrl.value = "";
      triggerVisionScanFile(file);
    };
    reader.readAsDataURL(file);
  }

  // Sample Issue Photo Picker
  document.querySelectorAll(".sample-pick-item").forEach(item => {
    item.addEventListener("click", () => {
      const url = item.dataset.url;
      previewImg.src = url;
      previewBox.style.display = "block";
      selectedSampleUrl.value = url;
      if (fileInput) fileInput.value = "";

      if (!inputTitle.value) inputTitle.value = item.dataset.title;
      if (!inputDesc.value) inputDesc.value = `Severe hazard detected at ${inputLocation.value}. Immediate municipal remediation requested.`;
      if (inputCategory.value === "Auto-Detect") inputCategory.value = item.dataset.cat;

      triggerVisionScanUrl(url);
      updatePriorityEstimate();
    });
  });

  if (btnRemoveImg) {
    btnRemoveImg.addEventListener("click", () => {
      if (fileInput) fileInput.value = "";
      previewImg.src = "";
      previewBox.style.display = "none";
      selectedSampleUrl.value = "";
      visionResults.innerHTML = `<p class="text-muted" style="font-size: 0.88rem;">Upload an image or pick a sample photo to run real-time visual feature detection.</p>`;
      visionStatus.textContent = "Standby";
    });
  }

  // Real-time Priority Estimator on typing
  inputTitle.addEventListener("input", updatePriorityEstimate);
  inputDesc.addEventListener("input", updatePriorityEstimate);
  inputCategory.addEventListener("change", updatePriorityEstimate);

  function updatePriorityEstimate() {
    const title = inputTitle.value.toLowerCase();
    const desc = inputDesc.value.toLowerCase();
    const cat = inputCategory.value;
    const text = `${title} ${desc}`;

    let score = 25;
    let baseSla = 96;

    if (cat === "Open Manhole & Safety") { score += 35; }
    else if (cat === "Waterlogging & Drainage") { score += 30; }
    else if (cat === "Streetlights & Electricity") { score += 28; }
    else if (cat === "Roads & Potholes") { score += 24; }
    else if (cat === "Fallen Trees & Obstructions") { score += 26; }
    else { score += 18; }

    const urgentKeywords = ["live wire", "spark", "open manhole", "deep", "accident", "school", "hospital", "flood", "submerged", "fire", "emergency"];
    let detected = [];
    urgentKeywords.forEach(kw => {
      if (text.includes(kw)) {
        score += 12;
        detected.push(kw);
      }
    });

    score = Math.min(100, Math.max(15, score));

    let priority = "LOW";
    let slaHours = 168;

    if (score >= 80) {
      priority = "CRITICAL";
      slaHours = 24;
    } else if (score >= 60) {
      priority = "HIGH";
      slaHours = 48;
    } else if (score >= 35) {
      priority = "MEDIUM";
      slaHours = 96;
    }

    if (estPriorityBadge) {
      estPriorityBadge.className = `badge priority-${priority}`;
      estPriorityBadge.innerHTML = `<i class="fas fa-shield-alt"></i> ${priority} • ${score}`;
    }
    if (scoreText) scoreText.textContent = `${score} / 100`;
    if (scoreBar) {
      scoreBar.style.width = `${score}%`;
      if (score >= 80) scoreBar.style.background = "var(--critical)";
      else if (score >= 60) scoreBar.style.background = "var(--high)";
      else scoreBar.style.background = "linear-gradient(90deg, #06b6d4, #14b8a6)";
    }
    if (estSlaHours) {
      estSlaHours.textContent = `${slaHours} Hours (${Math.round(slaHours/24)} Days)`;
    }

    if (priorityJustification) {
      let reason = `Evaluated as <strong>${priority}</strong> (${score}/100 pts). `;
      if (detected.length > 0) {
        reason += `Priority elevated due to safety risk markers: <em>${detected.join(", ")}</em>. `;
      } else {
        reason += `Standard category baseline triage. `;
      }
      reason += `Enforced SLA: <strong>${slaHours} hours</strong>.`;
      priorityJustification.innerHTML = reason;
    }
  }

  // Vision Scan using URL
  async function triggerVisionScanUrl(url) {
    if (visionStatus) visionStatus.textContent = "Scanning...";
    try {
      const fd = new FormData();
      fd.append("image_url", url);
      fd.append("description", `${inputTitle.value} ${inputDesc.value}`);

      const res = await fetch("/api/ai/vision-scan", { method: "POST", body: fd });
      const data = await res.json();
      renderVisionAnalysis(data.analysis);
    } catch (err) {
      if (visionStatus) visionStatus.textContent = "Error";
    }
  }

  // Vision Scan using File
  async function triggerVisionScanFile(file) {
    if (visionStatus) visionStatus.textContent = "Scanning...";
    try {
      const fd = new FormData();
      fd.append("image", file);
      fd.append("description", `${inputTitle.value} ${inputDesc.value}`);

      const res = await fetch("/api/ai/vision-scan", { method: "POST", body: fd });
      const data = await res.json();
      renderVisionAnalysis(data.analysis);
    } catch (err) {
      if (visionStatus) visionStatus.textContent = "Error";
    }
  }

  function renderVisionAnalysis(analysis) {
    if (visionStatus) visionStatus.textContent = "Scan Verified";
    if (visionResults) {
      visionResults.innerHTML = `
        <div style="background: rgba(6, 182, 212, 0.08); padding: 0.85rem; border-radius: var(--radius-sm); border: 1px solid rgba(6, 182, 212, 0.25); margin-bottom: 0.75rem;">
          <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.35rem;">
            <span style="color: var(--text-muted);">Predicted Category:</span>
            <span style="font-weight: 700; color: #ffffff;">${analysis.predicted_category}</span>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
            <span style="color: var(--text-muted);">Confidence Score:</span>
            <span style="font-weight: 700; color: var(--teal-400);">${analysis.confidence_score}%</span>
          </div>
        </div>

        <div style="font-size: 0.82rem; margin-bottom: 0.5rem; color: #ffffff; font-weight: 600;">Detected Structural Features:</div>
        <ul style="font-size: 0.8rem; color: var(--text-muted); padding-left: 1.25rem; line-height: 1.5; margin-bottom: 0.75rem;">
          ${analysis.detected_features.map(f => `<li>${f}</li>`).join("")}
        </ul>

        <div style="font-size: 0.8rem; color: var(--cyan-300); background: #0c1a2e; padding: 0.65rem; border-radius: 4px; border-left: 2px solid var(--teal-400);">
          <i class="fas fa-hard-hat"></i> <strong>AI Action Recommendation:</strong> ${analysis.suggested_action}
        </div>
      `;
    }

    if (inputCategory.value === "Auto-Detect") {
      inputCategory.value = analysis.predicted_category;
      updatePriorityEstimate();
    }
  }

  // Handle Form Submission
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btnSubmit = document.getElementById("btnSubmit");
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Submitting & Triaging...';

    const formData = new FormData(form);

    try {
      const res = await fetch("/api/complaints", {
        method: "POST",
        body: formData
      });
      const data = await res.json();

      if (data.success) {
        document.getElementById("receiptComplaintId").textContent = data.complaint_id;
        document.getElementById("receiptPriority").innerHTML = renderPriorityBadge(data.priority, data.priority_score);
        document.getElementById("receiptDept").textContent = data.assigned_department;
        document.getElementById("receiptSla").textContent = `${data.sla_hours} Hours Target`;
        document.getElementById("receiptDuplicates").textContent = data.potential_duplicates > 0 ? `${data.potential_duplicates} Related Nearby Reports Detected` : "Unique Incident (No duplicates)";
        document.getElementById("receiptExplanation").innerHTML = `<strong>Triage Justification:</strong> ${data.explanation}`;
        document.getElementById("btnGoTrack").href = `/track?id=${data.complaint_id}`;

        document.getElementById("receiptModal").classList.add("active");
        showToast("Complaint filed successfully!", "success");
      } else {
        showToast(data.error || "Submission failed", "danger");
      }
    } catch (err) {
      showToast("Network error submitting complaint", "danger");
    } finally {
      btnSubmit.disabled = false;
      btnSubmit.innerHTML = '<i class="fas fa-paper-plane"></i> File Incident Report';
    }
  });

  // Modal interactions
  const btnCloseReceipt = document.getElementById("btnCloseReceipt");
  if (btnCloseReceipt) {
    btnCloseReceipt.addEventListener("click", () => {
      document.getElementById("receiptModal").classList.remove("active");
    });
  }

  const btnCopyId = document.getElementById("btnCopyId");
  if (btnCopyId) {
    btnCopyId.addEventListener("click", () => {
      const id = document.getElementById("receiptComplaintId").textContent;
      navigator.clipboard.writeText(id).then(() => {
        showToast("Tracking ID copied to clipboard!", "success");
      });
    });
  }
});

