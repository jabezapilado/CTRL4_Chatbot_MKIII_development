/* chat_admin.js — Admin takeover chat page */

if (!sessionStorage.getItem("hau_user")) {
}

const adminChatArea = document.getElementById("admin-chat-area");
const adminInput = document.getElementById("admin-msg-input");
const adminSendBtn = document.getElementById("admin-send-btn");

const legacyTakeoverDataKey = "hau_takeover_case";
localStorage.removeItem(legacyTakeoverDataKey);

function getTime() {
  return new Date().toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  });
}

function setCaseDetails(caseInfo) {
  document.getElementById("admin-student-name").textContent =
    caseInfo.student || "Unknown";
  document.getElementById("admin-student-id").textContent =
    caseInfo.studentId || "Unknown";
  document.getElementById("admin-category").textContent =
    caseInfo.category || "Unknown";
  document.getElementById("admin-time").textContent =
    caseInfo.time || "Unknown";
}

function appendMessage(content, from = "staff") {
  const isStaff = from === "staff";
  const row = document.createElement("div");
  row.className = `msg-row ${isStaff ? "user" : "bot"}`;
  row.innerHTML = `
    <div class="avatar">${isStaff ? "S" : "U"}</div>
    <div class="bubble-wrap">
      <div class="bubble">${escapeHtml(content)}</div>
      <span class="bubble-time">${getTime()}</span>
    </div>`;
  adminChatArea.appendChild(row);
  adminChatArea.scrollTop = adminChatArea.scrollHeight;
}

function escapeHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function openAdminTakeover() {
  setCaseDetails({ message: "No active takeover", status: "none" });
  appendMessage("No locally stored conversation is available.", "bot");
}

adminSendBtn.addEventListener("click", () => {
  const text = adminInput.value.trim();
  if (!text) return;
  appendMessage(text, "staff");
  adminInput.value = "";
  adminInput.style.height = "auto";
});

function appendQuickReply(text) {
  adminInput.value = text;
  adminInput.focus();
}

function returnToDashboard() {
  window.location.href = "dashboard.html";
}

window.returnToDashboard = returnToDashboard;
window.appendQuickReply = appendQuickReply;

adminInput.addEventListener("input", () => {
  adminInput.style.height = "auto";
  adminInput.style.height = Math.min(adminInput.scrollHeight, 120) + "px";
});

adminInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    adminSendBtn.click();
  }
});

openAdminTakeover();
