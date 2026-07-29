/* =========================================================
   SOC Guidance Office – Appointment Form
   script.js
   ========================================================= */
"use strict";
// The server already protects this route; keep the page usable if sessionStorage
// is empty after a restart.
// ── DOM References ──────────────────────────────────────────────────────────
const form = document.getElementById("appointmentForm");
const submitBtn = document.getElementById("submitBtn");
const clearBtn = document.getElementById("clearBtn");
const backBtn = document.getElementById("backBtn");
const modal = document.getElementById("successModal");
const modalClose = document.getElementById("modalClose");
const refIdEl = document.getElementById("refId");
// ── Field definitions (id + validation rules) ───────────────────────────────
const FIELDS = [
  {
    id: "contact",
    label: "Contact Number",
    required: true,
    validate: (v) => {
      const cleaned = v.replace(/\s/g, "");
      if (!cleaned) return "Contact Number is required.";
      if (!/^(09|\+639)\d{9}$/.test(cleaned))
        return "Enter a valid PH mobile number (e.g. 09XX XXX XXXX).";
      return null;
    },
  },
  {
    id: "prefDate",
    label: "Preferred Date",
    required: true,
    validate: (v) => {
      if (!v) return "Preferred Date is required.";
      const selected = new Date(v);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (selected < today) return "Please select a future date.";

      /*
      Temporary validation.

      Office Days will eventually be loaded dynamically
      from Appointment Settings.
      */
      const day = selected.getDay();
      if (day === 0 || day === 6) return "Please select a weekday (Mon–Fri).";
      return null;
    },
  },
  {
    id: "prefTime",
    label: "Preferred Time Slot",
    required: true,
    validate: (v) => {
      if (!v) {
        return "Please select a preferred time slot.";
      }

      return null;
    },
  },
  {
    id: "appointmentCategory",
    label: "Appointment Category",
    required: true,
    validate: (v) => {
      if (!v) {
        return "Please select an appointment category.";
      }

      return null;
    },
  },
  {
    id: "appointmentMode",
    label: "Appointment Mode",
    required: true,
    validate: (v) => {
      if (!v) {
        return "Please select an appointment mode.";
      }

      return null;
    },
  },
  {
    id: "reason",
    label: "Reason for Appointment",
    required: true,
    validate: (v) => {
      if (!v.trim()) return "Please provide a reason for your appointment.";
      if (v.trim().length < 20)
        return "Please provide a bit more detail (min. 20 characters).";
      if (v.trim().length > 1000)
        return "Reason must not exceed 1000 characters.";
      return null;
    },
  },
];
// ── Helpers ──────────────────────────────────────────────────────────────────
/**
 * Show or clear an error message for a given field.
 * @param {string} id     - Field element ID
 * @param {string|null} msg - Error text or null to clear
 */
function setError(id, msg) {
  const input = document.getElementById(id);
  const errorEl = document.getElementById(`${id}-error`);
  if (msg) {
    input.classList.add("input-error");
    if (errorEl) errorEl.textContent = msg;
  } else {
    input.classList.remove("input-error");
    if (errorEl) errorEl.textContent = "";
  }
}
/**
 * Validate a single field and update UI.
 * @param {{ id: string, validate: function }} field
 * @returns {boolean} true if valid
 */
function validateField(field) {
  const el = document.getElementById(field.id);
  const val = el.value;
  const err = field.validate(val);
  setError(field.id, err);
  return err === null;
}
/**
 * Set the minimum date input to today.
 */
function setMinDate() {
  const dateInput = document.getElementById("prefDate");
  const today = new Date().toISOString().split("T")[0];
  dateInput.setAttribute("min", today);
}
// ── Live Validation (on blur) ────────────────────────────────────────────────
FIELDS.forEach((field) => {
  const el = document.getElementById(field.id);
  if (!el) return;
  // Validate on blur
  el.addEventListener("blur", () => validateField(field));
  // Clear error while typing/changing (after first blur)
  el.addEventListener("input", () => {
    if (el.classList.contains("input-error")) {
      validateField(field);
    }
  });
  // For select, also listen on change
  if (el.tagName === "SELECT") {
    el.addEventListener("change", () => validateField(field));
  }
});
// ── Form Submission ──────────────────────────────────────────────────────────
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  let isValid = true;

  FIELDS.forEach((field) => {
    if (!validateField(field)) isValid = false;
  });

  if (!isValid) {
    const firstError = form.querySelector(".input-error");

    if (firstError) {
      firstError.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });

      firstError.focus();
    }

    return;
  }

  submitBtn.classList.add("loading");
  submitBtn.disabled = true;

  const payload = collectFormData();

  try {
    /*
    Future Sprint:

    Appointment Conflict Detection will be
    performed before appointment creation.

    The following values will eventually be
    validated against Appointment Settings:

    - Office Days
    - Available Time Slots
    - Appointment Categories
    - Appointment Modes
    */
    const response = await fetch(`${window.location.origin}/api/appointments`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        contact_number: payload.contact,
        appointment_category: payload.appointmentCategory,
        appointment_mode: payload.appointmentMode,
        preferred_date: payload.preferredDate,
        preferred_time_slot: payload.preferredTime,
        reason: payload.reason,
      }),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "Unable to submit appointment request.");
    }

    if (window.finalizeConversation) {
      try {
        await window.finalizeConversation({ resetUI: false });
      } catch (error) {
        console.error(
          "Conversation finalization after appointment submission failed:",
          error,
        );
      }
    }

    refIdEl.textContent = result.id || "Pending";

    openModal();
  } catch (err) {
    alert(
      err.message || "Unable to submit appointment request. Please try again.",
    );
  } finally {
    submitBtn.classList.remove("loading");
    submitBtn.disabled = false;
  }
});
// ── Collect Form Data ────────────────────────────────────────────────────────
function collectFormData() {
  return {
    contact: document.getElementById("contact").value.trim(),

    preferredDate: document.getElementById("prefDate").value,

    preferredTime: document.getElementById("prefTime").value,

    appointmentCategory: document.getElementById("appointmentCategory").value,

    appointmentMode: document.getElementById("appointmentMode").value,

    reason: document.getElementById("reason").value.trim(),
  };
}
// ── Clear Form ───────────────────────────────────────────────────────────────
clearBtn.addEventListener("click", () => {
  if (!confirm("Are you sure you want to clear all fields?")) return;
  resetForm();
});

backBtn?.addEventListener("click", () => {
  window.location.href = "/chatbot";
});

function resetForm() {
  form.reset();
  // Remove all error states
  FIELDS.forEach((field) => setError(field.id, null));
  // Scroll to top of form
  form.scrollIntoView({ behavior: "smooth", block: "start" });
}
// ── Modal Controls ───────────────────────────────────────────────────────────
function openModal() {
  modal.classList.add("active");
  document.body.style.overflow = "hidden";
  modalClose.focus();
}
function closeModal() {
  modal.classList.remove("active");
  document.body.style.overflow = "";
  resetForm();
  submitBtn.focus();
}
modalClose.addEventListener("click", closeModal);
// Close on overlay click
modal.addEventListener("click", (e) => {
  if (e.target === modal) closeModal();
});
// Close on Escape key
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && modal.classList.contains("active")) {
    closeModal();
  }
});
// ── Character Counter for Reason ─────────────────────────────────────────────
(function setupCharCounter() {
  const reasonEl = document.getElementById("reason");
  const errorEl = document.getElementById("reason-error");
  const MAX_CHARS = 1000;
  // Create counter element
  const counter = document.createElement("span");
  counter.className = "char-counter";
  counter.style.cssText = `
    display: block;
    font-size: 0.72rem;
    color: var(--text-muted);
    text-align: right;
    margin-top: 4px;
  `;
  // Insert after the textarea's parent form-group
  reasonEl.parentNode.appendChild(counter);
  updateCounter();
  reasonEl.addEventListener("input", updateCounter);
  function updateCounter() {
    const len = reasonEl.value.length;
    counter.textContent = `${len} / ${MAX_CHARS}`;
    counter.style.color = len > MAX_CHARS ? "#cc2222" : "var(--text-muted)";
  }
})();
// ── Contact Number Auto-Formatting ───────────────────────────────────────────
(function setupContactFormat() {
  const contactEl = document.getElementById("contact");
  contactEl.addEventListener("input", () => {
    let val = contactEl.value.replace(/\D/g, "");
    if (val.startsWith("63")) val = "0" + val.slice(2);
    if (val.length > 11) val = val.slice(0, 11);
    // Format: XXXX XXX XXXX
    const parts = [val.slice(0, 4), val.slice(4, 7), val.slice(7, 11)].filter(
      Boolean,
    );
    contactEl.value = parts.join(" ");
  });
})();
// ── Init ─────────────────────────────────────────────────────────────────────
setMinDate();
