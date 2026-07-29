/* chat_admin.js — Admin takeover chat page */

if (!sessionStorage.getItem("hau_user")) {
}

const adminChatArea = document.getElementById("admin-chat-area");
const adminInput = document.getElementById("admin-msg-input");
const adminSendBtn = document.getElementById("admin-send-btn");

const takeoverDataKey = "hau_takeover_case";

function getTime() {
  return new Date().toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  });
}

function loadTakeoverCase() {
  try {
    const raw = localStorage.getItem(takeoverDataKey);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch (error) {
    console.error("Unable to load takeover case", error);
    return null;
  }
}

function saveTakeoverCase(caseData) {
  try {
    localStorage.setItem(takeoverDataKey, JSON.stringify(caseData));
    return true;
  } catch (error) {
    console.error("Unable to save takeover case", error);
    return false;
  }
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
  const caseInfo = loadTakeoverCase();
  if (!caseInfo) {
    setCaseDetails({ message: "No active takeover", status: "none" });
    appendMessage("Waiting for a takeover case to open.", "bot");
    return;
  }

  setCaseDetails(caseInfo);
  if (caseInfo.conversation) {
    caseInfo.conversation.forEach((item) => {
      appendMessage(item.text, item.from === "user" ? "bot" : "staff");
    });
  }
}

adminSendBtn.addEventListener("click", () => {
  const text = adminInput.value.trim();
  if (!text) return;
  appendMessage(text, "staff");
  adminInput.value = "";
  adminInput.style.height = "auto";
  // store admin message locally for the session
  const caseInfo = loadTakeoverCase() || {};
  caseInfo.messages = caseInfo.messages || [];
  caseInfo.messages.push({
    from: "staff",
    text,
    time: new Date().toISOString(),
  });
  saveTakeoverCase(caseInfo);
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
