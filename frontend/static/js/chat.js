/* ─────────────────────────────────────────
   chat.js — SOC Guidance Office Chatbot
   Frontend logic: messaging, bounded server-owned continuity,
   emotion badges, and escalation display.
───────────────────────────────────────── */

let currentTopic = "";
let currentLanguage = "";
let currentEmotion = "";
let currentFlagged = false;

let inactivityTimer = null;
const INACTIVITY_TIMEOUT = 5 * 60 * 1000;
const legacyProtectedStorageKeys = [
  "hau_escalations",
  "hau_escalation_event",
  "hau_escalation_staff_msg",
  "hau_escalation_user_msg",
  "hau_takeover_case",
];

legacyProtectedStorageKeys.forEach((key) => localStorage.removeItem(key));
sessionStorage.removeItem("current_escalation");

// ── DOM References ──
const chatArea = document.getElementById("chat-area");

const input = document.getElementById("msg-input");
const API_BASE = window.location.origin;

function serializeChat() {
  const rows = Array.from(chatArea.querySelectorAll(".msg-row"));
  return rows.map((r) => {
    const isUser = r.classList.contains("user");
    const bubble = r.querySelector(".bubble");
    const timeEl = r.querySelector(".bubble-time");
    return {
      from: isUser ? "user" : "bot",
      text: bubble ? bubble.innerText : "",
      time: timeEl ? timeEl.textContent : "",
    };
  });
}

function resetInactivityTimer() {
  clearTimeout(inactivityTimer);

  inactivityTimer = setTimeout(async () => {
    if (document.hidden) {
      return;
    }
    const finalized = await finalizeConversation({ resetUI: false });

    if (finalized) {
      console.log("Conversation finalized due to inactivity.");
    }
  }, INACTIVITY_TIMEOUT);
}

function recordActivity() {
  resetInactivityTimer();
}

function getTime() {
  return new Date().toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  });
}

// ── Auto-grow textarea ──
input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 100) + "px";
});

// ── Send on Enter (Shift+Enter = new line) ──
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// ─────────────────────────────
// UTILITIES
// ─────────────────────────────

function scrollToBottom() {
  chatArea.scrollTop = chatArea.scrollHeight;
}

function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function linkifyUrls(text) {
  if (!text) return "";

  return String(text).replace(/https?:\/\/[^\s<]+/g, (rawUrl) => {
    const trimmed = rawUrl.replace(/[),.;!?]+$/, "");
    const trailing = rawUrl.slice(trimmed.length);
    return `<a href="${trimmed}" target="_blank" rel="noopener noreferrer">${trimmed}</a>${trailing}`;
  });
}

// ─────────────────────────────
// APPEND MESSAGES
// ─────────────────────────────

function appendUserMessage(text) {
  const row = document.createElement("div");
  row.className = "msg-row user";
  row.innerHTML = `
    <div class="bubble-wrap">
      <div class="bubble">${escapeHtml(text)}</div>
      <span class="bubble-time">${getTime()}</span>
    </div>`;
  chatArea.appendChild(row);
  scrollToBottom();
}

function appendBotMessage(htmlContent, emotionLabel) {
  const row = document.createElement("div");
  row.className = "msg-row bot";

  const formattedContent = DOMPurify.sanitize(
    marked.parse(linkifyUrls(htmlContent)),
  );

  let badge = "";
  if (emotionLabel === "negative") {
    badge = `<span class="emotion-badge negative">Negative emotion detected</span>`;
  } else if (emotionLabel === "neutral") {
    badge = `<span class="emotion-badge neutral">Routine inquiry</span>`;
  }

  row.innerHTML = `
    <div class="avatar">🤖</div>
    <div class="bubble-wrap">
      <div class="bubble">${formattedContent}${badge ? "<br>" + badge : ""}</div>
      <span class="bubble-time">${getTime()}</span>
    </div>`;
  chatArea.appendChild(row);
  scrollToBottom();
}

function appendEscalationNotice() {
  const wrap = document.createElement("div");
  wrap.className = "escalation-wrap";
  wrap.innerHTML = `
    <div class="escalation-notice">
      <span class="icon"></span>
      <span>Your message has been flagged and referred to a Guidance Office counselor. A staff member will follow up with you shortly.</span>
    </div>`;
  chatArea.appendChild(wrap);
  scrollToBottom();
}

function showTypingIndicator() {
  const row = document.createElement("div");
  row.className = "typing-row";
  row.id = "typing-indicator";
  row.innerHTML = `
    <div class="avatar">🤖</div>
    <div class="typing-bubble">
      <div class="dot"></div>
      <div class="dot"></div>
      <div class="dot"></div>
    </div>`;
  chatArea.appendChild(row);
  scrollToBottom();
}

function removeTypingIndicator() {
  const el = document.getElementById("typing-indicator");
  if (el) el.remove();
}

// ─────────────────────────────
// SEND MESSAGE
// ─────────────────────────────

function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  // Clear input
  input.value = "";
  input.style.height = "auto";

  // Show user message
  appendUserMessage(text);

  recordActivity();

  // Show typing indicator
  showTypingIndicator();

  fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: text,
      conversation: serializeChat(),
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      removeTypingIndicator();

      const result = data.data || {};

      appendBotMessage(
        result.response || "Sorry, I could not generate a response.",
        result.emotion || "",
      );

      currentTopic = result.topic || currentTopic;
      currentLanguage = result.language || currentLanguage;
      currentEmotion = result.emotion || currentEmotion;
      currentFlagged = Boolean(result.escalated);

      recordActivity();

      if (result.escalated) {
        setTimeout(appendEscalationNotice, 400);
      }
    })
    .catch(() => {
      removeTypingIndicator();
      appendBotMessage(
        "Sorry, I am having trouble connecting right now. Please try again.",
        "",
      );
    });
}

function showAppointmentPrompt() {
  const existing = document.getElementById("appointment-confirmation");
  if (existing) existing.remove();

  const overlay = document.createElement("div");
  overlay.id = "appointment-confirmation";
  overlay.className = "confirmation-popup";
  overlay.innerHTML = `
    <div class="confirmation-card">
      <h3>Book an appointment?</h3>
      <p>You’ll be taken to the appointment request form where you can submit your details for guidance support.</p>
      <div class="confirmation-actions">
        <button type="button" class="cancel-btn">Cancel</button>
        <button type="button" class="confirm-btn">Open form</button>
      </div>
    </div>`;

  document.body.appendChild(overlay);

  overlay
    .querySelector(".cancel-btn")
    .addEventListener("click", () => overlay.remove());
  overlay.querySelector(".confirm-btn").addEventListener("click", () => {
    overlay.remove();
    window.location.href = "/appointment";
  });
}

function sendQuick(text) {
  if (/book an appointment/i.test(text)) {
    showAppointmentPrompt();
    return;
  }
  input.value = text;
  sendMessage();
}

async function finalizeConversation({ resetUI = true } = {}) {
  const conversation = serializeChat();

  if (conversation.length === 0) {
    return true;
  }

  try {
    const response = await fetch(`${API_BASE}/chat/finalize`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        conversation,
        topic: currentTopic,
        language: currentLanguage,
        emotion: currentEmotion,
        flagged: currentFlagged,
      }),
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(data.error || "Unable to finalize conversation.");
    }

    clearTimeout(inactivityTimer);

    currentTopic = "";
    currentLanguage = "";
    currentEmotion = "";
    currentFlagged = false;

    if (resetUI) {
      chatArea.innerHTML = `
        <div class="date-divider">
          <span>Today</span>
        </div>`;
      input.value = "";
      input.style.height = "auto";
      input.placeholder = "Type your message here...";

      initializeChat();
      resetInactivityTimer();
    }

    return true;
  } catch (error) {
    console.error("Conversation finalization failed:", error);
    return false;
  }
}

window.finalizeConversation = finalizeConversation;

const exportBtn = document.getElementById("export-chat-btn");
if (exportBtn) {
  exportBtn.remove();
}

const endConversationBtn = document.getElementById("end-conversation-btn");
if (endConversationBtn) {
  endConversationBtn.remove();
}

// -----------------------------------------
// Initial Welcome Message
// -----------------------------------------

const user = JSON.parse(sessionStorage.getItem("hau_user") || "{}");

const firstName = (user.name || "there").trim().split(" ")[0];

const WELCOME_MESSAGE = `Hello, ${firstName}! Welcome to CTRL4.
I'm your AI Guidance Assistant, here to support you with personal concerns, academic challenges, and questions about Guidance Office services.
Take your time—what would you like to talk about today?`;

function loadActiveChat() {
  try {
    const state = document.getElementById("active-chat-state");
    const items = state ? JSON.parse(state.textContent || "[]") : [];
    return Array.isArray(items) ? items : [];
  } catch (_) {
    // The server remains authoritative. Malformed page state starts a new
    // visible exchange without writing protected content to browser storage.
    return [];
  }
}

function restoreVisibleChat(items) {
  items.forEach((item) => {
    if (!item || typeof item.text !== "string") return;
    if (item.from === "user") {
      appendUserMessage(item.text);
    } else if (item.from === "bot") {
      appendBotMessage(item.text);
    }
  });
}

async function initializeChat() {
  input.disabled = true;

  const activeChat = loadActiveChat();
  if (activeChat.length > 0) {
    restoreVisibleChat(activeChat);
    input.disabled = false;
    input.focus();
    resetInactivityTimer();
    return;
  }

  // Show typing indicator
  showTypingIndicator();
  const typingDelay = 800 + Math.random() * 500;
  setTimeout(() => {
    // Remove typing indicator
    removeTypingIndicator();

    // Send greeting
    appendBotMessage(WELCOME_MESSAGE);
    input.disabled = false;
    input.focus();
    resetInactivityTimer();
  }, typingDelay);
}

document.querySelectorAll("[data-quick-message]").forEach((button) => {
  button.addEventListener("click", () => sendQuick(button.dataset.quickMessage || ""));
});
document.getElementById("send-message")?.addEventListener("click", sendMessage);

window.sendMessage = sendMessage;
window.sendQuick = sendQuick;
document.addEventListener("DOMContentLoaded", initializeChat, { once: true });
window.addEventListener("beforeunload", () => {
  clearTimeout(inactivityTimer);
});
