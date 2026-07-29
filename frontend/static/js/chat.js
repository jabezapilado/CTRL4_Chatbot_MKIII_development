/* ─────────────────────────────────────────
   chat.js — SOC Guidance Office Chatbot
   Frontend logic: messaging, rule-based
   responses, emotion badges, escalation.

   NOTE: Replace the local response simulation with a POST
   call to your Flask `/chat` route. That route should load and
   run your local model, returning JSON with response text,
   emotion classification, and escalation status.
───────────────────────────────────────── */

let currentTopic = "";
let currentLanguage = "";
let currentEmotion = "";
let currentFlagged = false;

let inactivityTimer = null;
const INACTIVITY_TIMEOUT = 5 * 60 * 1000;

// ── DOM References ──
const chatArea = document.getElementById("chat-area");

const input = document.getElementById("msg-input");
const qrBar = document.getElementById("quick-replies");
const API_BASE = window.location.origin;

// Escalation / takeover state
let currentEscalationId = sessionStorage.getItem("current_escalation") || null;
let isEscalated = !!currentEscalationId;

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

function pushEscalationEvent(evt) {
  try {
    localStorage.setItem("hau_escalation_event", JSON.stringify(evt));
  } catch (e) {
    console.warn("Escalation event failed", e);
  }
}

function pushStaffMessage(obj) {
  try {
    localStorage.setItem("hau_escalation_staff_msg", JSON.stringify(obj));
  } catch (e) {
    console.warn("Staff msg failed", e);
  }
}

function pushUserMessage(obj) {
  try {
    localStorage.setItem("hau_escalation_user_msg", JSON.stringify(obj));
  } catch (e) {
    console.warn("User msg failed", e);
  }
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

const rules = [
  {
    pattern: /office hour|open|schedule|when|time/i,
    response:
      "The SOC Guidance Office is open <strong>Monday to Friday, 8:00 AM – 5:00 PM</strong>. We are closed on weekends and public holidays.",
    emotion: "neutral",
  },
  {
    pattern: /appoint|book|schedule a meet|consult|visit/i,
    response:
      "To book an appointment, you may visit the SOC Guidance Office personally or send an email to <strong>soc.guidance@hau.edu.ph</strong>. Walk-in consultations are also welcome during office hours.",
    emotion: "neutral",
  },
  {
    pattern:
      /counsel|therapy|mental health|stress|anxious|anxiety|depress|sad|overwhelm|hopeless/i,
    response:
      "We're here for you. Our counselors provide a safe and confidential space to talk about what you're going through.",
    emotion: "negative",
    escalate: true,
  },
  {
    pattern: /bully|harass|abuse|threat|hurt|unsafe|scared|afraid|danger/i,
    response:
      "Thank you for reaching out. Your safety and wellbeing matter to us. Please know you are not alone.",
    emotion: "negative",
    escalate: true,
  },
  {
    pattern: /document|clearance|certification|record|form/i,
    response:
      "For document requests, please visit the SOC Guidance Office and fill out the appropriate request form. Processing typically takes <strong>3–5 working days</strong>.",
    emotion: "neutral",
  },
  {
    pattern:
      /frustrat|disappoint|angry|upset|unfair|no one help|nobody|ignored/i,
    response:
      "I'm sorry to hear you're feeling this way. Let me connect you with one of our counselors who can give you the proper attention you deserve.",
    emotion: "negative",
    escalate: true,
  },
  {
    pattern: /contact|email|phone|reach|how to/i,
    response:
      "You may reach the SOC Guidance Office at <strong>soc.guidance@hau.edu.ph</strong> or visit us at the School of Computing building during office hours.",
    emotion: "neutral",
  },
  {
    pattern: /classmate|friend|concern|report|problem with/i,
    response:
      "Thank you for bringing this to our attention. Please provide more details about your concern so we can assist you better.",
    emotion: "neutral",
  },
];

function getResponse(text) {
  for (const rule of rules) {
    if (rule.pattern.test(text)) return rule;
  }
  return {
    response:
      "Thank you for reaching out to the SOC Guidance Office. Your message has been received. For specific concerns, you may also visit us during office hours or email <strong>soc.guidance@hau.edu.ph</strong>.",
    emotion: "neutral",
  };
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

  // Hide quick replies after first message
  qrBar.style.display = "none";

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
      user_name:
        JSON.parse(sessionStorage.getItem("hau_user") || "{}").name || "",
      user_email:
        JSON.parse(sessionStorage.getItem("hau_user") || "{}").email || "",
      conversation: serializeChat(),
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      removeTypingIndicator();

      if (isEscalated && currentEscalationId) {
        const evt = {
          id: currentEscalationId,
          from: "user",
          text,
          time: new Date().toISOString(),
        };
        pushUserMessage(evt);
        appendBotMessage(
          "Your message has been sent to the Guidance Office counselor.",
          "neutral",
        );
        return;
      }

      appendBotMessage(
        data.response || "Sorry, I could not generate a response.",
        data.emotion || "",
      );

      currentTopic = data.topic || currentTopic;
      currentLanguage = data.language || currentLanguage;
      currentEmotion = data.emotion || currentEmotion;
      currentFlagged = Boolean(data.escalate);

      recordActivity();

      if (data.escalate) {
        const user = JSON.parse(sessionStorage.getItem("hau_user") || "{}");
        const escId = Date.now().toString();
        const esc = {
          id: escId,
          userEmail: user.email || "unknown",
          userName: user.name || user.email || "Unknown",
          time: new Date().toISOString(),
          status: "open",
          conversation: serializeChat(),
        };
        const listRaw = localStorage.getItem("hau_escalations");
        const list = listRaw ? JSON.parse(listRaw) : [];
        list.push(esc);
        localStorage.setItem("hau_escalations", JSON.stringify(list));
        pushEscalationEvent({
          type: "new",
          id: escId,
          userEmail: esc.userEmail,
          userName: esc.userName,
          time: esc.time,
        });
        currentEscalationId = escId;
        sessionStorage.setItem("current_escalation", escId);
        isEscalated = true;
        setTimeout(appendEscalationNotice, 400);
        input.placeholder =
          "A staff member will join shortly — your messages will be sent to staff.";
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

function appendStaffMessage(text) {
  const row = document.createElement("div");
  row.className = "msg-row bot";
  row.innerHTML = `
    <div class="avatar">S</div>
    <div class="bubble-wrap">
      <div class="bubble">${escapeHtml(text)}</div>
      <span class="bubble-time">${getTime()}</span>
    </div>`;
  chatArea.appendChild(row);
  scrollToBottom();
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

    currentEscalationId = null;
    isEscalated = false;
    sessionStorage.removeItem("current_escalation");

    currentTopic = "";
    currentLanguage = "";
    currentEmotion = "";
    currentFlagged = false;

    if (resetUI) {
      chatArea.innerHTML = "";
      input.value = "";
      input.style.height = "auto";
      input.placeholder = "Type your message here...";

      qrBar.style.removeProperty("display");

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

// Listen for storage events so staff messages and escalation events propagate across tabs
window.addEventListener("storage", (e) => {
  try {
    if (!e.key || !e.newValue) return;
    if (e.key === "hau_escalation_staff_msg") {
      const msg = JSON.parse(e.newValue);
      if (msg && msg.id && msg.id === currentEscalationId) {
        appendStaffMessage(msg.text);
      }
    }
    // If a new escalation is created elsewhere that targets this user, set local state
    if (e.key === "hau_escalation_event") {
      const ev = JSON.parse(e.newValue);
      // no-op for now; dashboard handles listing
    }
  } catch (err) {
    console.warn("storage handler error", err);
  }
});

// -----------------------------------------
// Initial Welcome Message
// -----------------------------------------

const user = JSON.parse(sessionStorage.getItem("hau_user") || "{}");

const firstName = (user.name || "there").trim().split(" ")[0];

const WELCOME_MESSAGE = `Hello, ${firstName}! Welcome to CTRL4.
I'm your AI Guidance Assistant, here to support you with personal concerns, academic challenges, and questions about Guidance Office services.
Take your time—what would you like to talk about today?`;

function initializeChat() {
  input.disabled = true;

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

document.addEventListener("DOMContentLoaded", initializeChat);
window.addEventListener("beforeunload", () => {
  clearTimeout(inactivityTimer);
});
