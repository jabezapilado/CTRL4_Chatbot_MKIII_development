function getLoginUrl() {
  return "/login?reason=session-required";
}

function requireAuth() {
  const user = sessionStorage.getItem("hau_user");

  return user ? JSON.parse(user) : null;
}

function clearClientAuthState() {
  sessionStorage.clear();
  [
    "hau_escalations",
    "hau_escalation_event",
    "hau_escalation_staff_msg",
    "hau_escalation_user_msg",
  ].forEach((key) => localStorage.removeItem(key));
  sessionStorage.removeItem("current_escalation");
}

async function endAuthenticatedSession({
  finalize = true,
  reason = "logged-out",
} = {}) {
  try {
    if (finalize && window.finalizeConversation) {
      await window.finalizeConversation({ resetUI: false });
    }
  } catch (error) {
    console.error("Conversation finalization before logout failed:", error);
  }

  fetch(`${window.location.origin}/auth/logout`, { method: "POST" })
    .catch(() => {})
    .finally(() => {
      clearClientAuthState();
      window.location.replace(`/login?reason=${encodeURIComponent(reason)}`);
    });
}

async function logout() {
  return endAuthenticatedSession();
}

window.getLoginUrl = getLoginUrl;
window.requireAuth = requireAuth;
window.logout = logout;
window.endAuthenticatedSession = endAuthenticatedSession;

document.getElementById("chat-logout-btn")?.addEventListener("click", logout);
