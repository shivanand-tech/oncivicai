/**
 * CivicAI - Core Frontend Utilities, Navigation & Aura Copilot
 */

document.addEventListener("DOMContentLoaded", () => {
  // Mobile Top Navigation Toggle
  const mobileBtn = document.querySelector(".mobile-menu-btn");
  const navLinks = document.querySelector(".nav-links");

  if (mobileBtn && navLinks) {
    mobileBtn.addEventListener("click", () => {
      navLinks.classList.toggle("open");
    });
  }

  // Responsive Admin Sidebar Toggle
  const sidebarToggleBtn = document.getElementById("sidebarToggleBtn");
  const sidebar = document.querySelector(".sidebar");
  if (sidebarToggleBtn && sidebar) {
    sidebarToggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });
  }

  // Initialize Aura AI Assistant
  initAuraAssistant();
});

// Toast Notifications System
function showToast(message, type = "info") {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;

  const iconMap = {
    success: "fa-check-circle text-success",
    danger: "fa-exclamation-triangle text-danger",
    warning: "fa-exclamation-circle text-warning",
    info: "fa-info-circle text-teal"
  };

  const icon = iconMap[type] || iconMap.info;
  toast.innerHTML = `
    <i class="fas ${icon}" style="font-size: 1.15rem;"></i>
    <div style="flex: 1;">${message}</div>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Format Date/Time
function formatDateTime(isoString) {
  if (!isoString) return "N/A";
  try {
    const d = new Date(isoString);
    return d.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  } catch (e) {
    return isoString;
  }
}

// Format Relative Time (e.g., 2h ago)
function timeAgo(isoString) {
  if (!isoString) return "";
  const d = new Date(isoString);
  const now = new Date();
  const diffSec = Math.floor((now - d) / 1000);

  if (diffSec < 60) return "Just now";
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
  return `${Math.floor(diffSec / 86400)}d ago`;
}

// Render Priority Badge
function renderPriorityBadge(priority, score = null) {
  const p = (priority || "MEDIUM").toUpperCase();
  const scoreTxt = score !== null ? ` • ${score}` : "";
  return `<span class="badge priority-${p}"><i class="fas fa-shield-alt"></i> ${p}${scoreTxt}</span>`;
}

// Render Status Badge
function renderStatusBadge(status) {
  const s = status || "Submitted";
  const safeClass = s.replace(/\s+/g, "-");
  let icon = "fa-circle-notch";

  if (s === "Submitted") icon = "fa-file-alt";
  else if (s === "Under Review") icon = "fa-search";
  else if (s === "Assigned") icon = "fa-user-check";
  else if (s === "In Progress") icon = "fa-tools";
  else if (s === "Resolved") icon = "fa-check-double";

  return `<span class="badge status-${safeClass}" data-status="${s}"><i class="fas ${icon}"></i> ${s}</span>`;
}

// Floating Aura Assistant Logic
function initAuraAssistant() {
  const toggleBtn = document.getElementById("auraToggleBtn");
  const chatBox = document.getElementById("auraChatBox");
  const closeBtn = document.getElementById("auraCloseBtn");
  const sendBtn = document.getElementById("auraSendBtn");
  const input = document.getElementById("auraInput");
  const messagesContainer = document.getElementById("auraMessages");

  if (!toggleBtn || !chatBox) return;

  toggleBtn.addEventListener("click", () => {
    chatBox.classList.toggle("open");
    if (chatBox.classList.contains("open") && input) {
      input.focus();
    }
  });

  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      chatBox.classList.remove("open");
    });
  }

  function appendMsg(text, sender = "bot") {
    if (!messagesContainer) return;
    const msg = document.createElement("div");
    msg.className = `aura-msg ${sender}`;

    let formatted = text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="text-teal" style="text-decoration: underline;">$1</a>');

    msg.innerHTML = formatted;
    messagesContainer.appendChild(msg);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  async function handleSend() {
    if (!input) return;
    const txt = input.value.trim();
    if (!txt) return;

    appendMsg(txt, "user");
    input.value = "";

    const typingId = "typing-" + Date.now();
    const typingMsg = document.createElement("div");
    typingMsg.id = typingId;
    typingMsg.className = "aura-msg bot";
    typingMsg.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Aura is thinking...';
    messagesContainer.appendChild(typingMsg);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
      const res = await fetch("/api/assistant/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: txt })
      });
      const data = await res.json();
      const typingEl = document.getElementById(typingId);
      if (typingEl) typingEl.remove();

      appendMsg(data.reply || "I'm having trouble analyzing that. Please try again.", "bot");
    } catch (err) {
      const typingEl = document.getElementById(typingId);
      if (typingEl) typingEl.remove();
      appendMsg("Network connection error. Please verify your connection.", "bot");
    }
  }

  if (sendBtn) {
    sendBtn.addEventListener("click", handleSend);
  }

  if (input) {
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        handleSend();
      }
    });
  }
}
