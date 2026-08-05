function getLoginUrl() {
  return "/login?reason=session-required";
}

function requireAuth() {
  const user = sessionStorage.getItem("hau_user");

  return user ? JSON.parse(user) : null;
}

async function logout() {
  try {
    if (window.finalizeConversation) {
      await window.finalizeConversation({ resetUI: false });
    }
  } catch (error) {
    console.error("Conversation finalization before logout failed:", error);
  }

  fetch(`${window.location.origin}/auth/logout`, { method: "POST" })
    .catch(() => {})
    .finally(() => {
      sessionStorage.clear();
      [
        "hau_escalations",
        "hau_escalation_event",
        "hau_escalation_staff_msg",
        "hau_escalation_user_msg",
        "hau_takeover_case",
      ].forEach((key) => localStorage.removeItem(key));
      sessionStorage.removeItem("current_escalation");
      window.location.replace("/login?reason=logged-out");
    });
}

window.getLoginUrl = getLoginUrl;
window.requireAuth = requireAuth;
window.logout = logout;

document.getElementById("chat-logout-btn")?.addEventListener("click", logout);
