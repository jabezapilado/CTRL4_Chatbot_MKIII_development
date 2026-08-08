/* Student terms acknowledgement required before chat access. */

(() => {
  "use strict";

  const dialog = document.getElementById("terms-dialog");
  if (!dialog) return;

  const agreement = document.getElementById("terms-agreement");
  const accept = document.getElementById("terms-accept");
  const decline = document.getElementById("terms-decline");
  const error = document.getElementById("terms-error");

  function setError(message) {
    error.textContent = message || "";
    error.hidden = !message;
  }

  agreement.addEventListener("change", () => {
    accept.disabled = !agreement.checked;
    setError("");
  });

  decline.addEventListener("click", () => {
    window.logout();
  });

  accept.addEventListener("click", async () => {
    if (!agreement.checked) {
      setError("You must agree to continue.");
      return;
    }

    accept.disabled = true;
    try {
      const response = await fetch("/auth/terms/accept", { method: "POST" });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.message || "Unable to record your agreement.");
      }
      dialog.close();
    } catch (requestError) {
      accept.disabled = false;
      setError(requestError.message || "Unable to record your agreement.");
    }
  });

  dialog.showModal();
})();
