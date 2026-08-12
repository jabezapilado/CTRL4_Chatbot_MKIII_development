(() => {
  "use strict";

  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
  const unsafeMethods = new Set(["POST", "PUT", "PATCH", "DELETE"]);
  const originalFetch = window.fetch.bind(window);
  const studentSessionStatusIntervalMs = 15_000;
  let sessionReplacementNoticeShown = false;

  function isSameOrigin(input) {
    const target = input instanceof Request ? input.url : input;
    return new URL(target, window.location.href).origin === window.location.origin;
  }

  function returnToLoginAfterSessionReplacement() {
    window.location.replace("/login?reason=session-replaced");
  }

  function showStudentSessionReplacementNotice() {
    if (sessionReplacementNoticeShown || !document.body) return;
    sessionReplacementNoticeShown = true;
    document.activeElement?.blur?.();

    const overlay = document.createElement("div");
    overlay.className = "student-session-ended-overlay";
    overlay.setAttribute("role", "alertdialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-labelledby", "student-session-ended-title");
    overlay.innerHTML = `
      <section class="student-session-ended-card">
        <p class="student-session-ended-kicker">Session ended</p>
        <h1 id="student-session-ended-title">You have been signed out</h1>
        <p>
          This student account was signed in on another device. This chat has
          ended on this device to keep the account secure.
        </p>
        <button type="button" class="btn btn-primary" id="student-session-ended-return">
          Return to sign in
        </button>
      </section>
    `;
    document.body.append(overlay);
    document
      .getElementById("student-session-ended-return")
      ?.addEventListener("click", returnToLoginAfterSessionReplacement);

    window.setTimeout(returnToLoginAfterSessionReplacement, 5_000);
  }

  function redirectIfStudentSessionWasReplaced(input, response) {
    if (
      isSameOrigin(input) &&
      response.headers.get("X-CTRL4-Session-Replaced") === "1"
    ) {
      showStudentSessionReplacementNotice();
    }
    return response;
  }

  window.fetch = (input, init = {}) => {
    const method = (init.method || (input instanceof Request && input.method) || "GET")
      .toUpperCase();

    if (!csrfToken || !unsafeMethods.has(method) || !isSameOrigin(input)) {
      return originalFetch(input, init).then((response) =>
        redirectIfStudentSessionWasReplaced(input, response),
      );
    }

    const headers = new Headers(
      init.headers || (input instanceof Request ? input.headers : undefined),
    );
    headers.set("X-CSRF-Token", csrfToken);
    return originalFetch(input, { ...init, headers }).then((response) =>
      redirectIfStudentSessionWasReplaced(input, response),
    );
  };

  function checkOpenStudentSession() {
    if (document.visibilityState !== "visible") return;
    window
      .fetch("/auth/session-status", {
        cache: "no-store",
        credentials: "same-origin",
      })
      .catch(() => {
        // A transient connectivity failure must not sign a student out locally.
      });
  }

  if (document.body?.dataset.studentSessionMonitor === "true") {
    window.setTimeout(checkOpenStudentSession, studentSessionStatusIntervalMs);
    window.setInterval(checkOpenStudentSession, studentSessionStatusIntervalMs);
    document.addEventListener("visibilitychange", checkOpenStudentSession);
  }
})();
