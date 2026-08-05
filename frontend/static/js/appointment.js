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
const studentAppointmentsList = document.getElementById(
  "studentAppointmentsList",
);
const studentAppointmentsMessage = document.getElementById(
  "studentAppointmentsMessage",
);
const refreshStudentAppointmentsButton = document.getElementById(
  "refreshStudentAppointments",
);
const rescheduleModal = document.getElementById("rescheduleModal");
const rescheduleForm = document.getElementById("rescheduleForm");
const rescheduleDate = document.getElementById("rescheduleDate");
const rescheduleTime = document.getElementById("rescheduleTime");
const rescheduleClose = document.getElementById("rescheduleClose");
const rescheduleSubmit = document.getElementById("rescheduleSubmit");
const rescheduleMessage = document.getElementById("rescheduleMessage");
const rescheduleAppointmentSummary = document.getElementById(
  "rescheduleAppointmentSummary",
);

const STUDENT_MODIFICATION_MESSAGE =
  "This appointment can no longer be modified because it is scheduled within the next hour.";
const STUDENT_MODIFICATION_DEADLINE_MS = 60 * 60 * 1000;
const STUDENT_APPOINTMENT_STATUS_LABELS = {
  pending: "Pending",
  confirmed: "Confirmed",
  cancelled: "Cancelled",
  rejected: "Rejected",
  completed: "Completed",
};

let reschedulingAppointmentId = null;
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
      throw new Error(result.message || "Unable to submit appointment request.");
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

    refIdEl.textContent = result.data?.id || "Pending";

    openModal();
    void loadStudentAppointments({ preserveMessage: true });
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

function setStudentAppointmentMessage(message, type = "", element) {
  const target = element || studentAppointmentsMessage;
  if (!target) return;

  target.textContent = message || "";
  target.hidden = !message;
  target.classList.remove("error", "success");

  if (type) {
    target.classList.add(type);
  }
}

function formatStudentAppointmentDate(value) {
  const match = String(value || "").match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) return String(value || "No date");

  return new Date(
    Number(match[1]),
    Number(match[2]) - 1,
    Number(match[3]),
  ).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatStudentAppointmentTime(value) {
  const time = String(value || "").trim();
  const twelveHourMatch = time.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);

  if (twelveHourMatch) {
    return `${Number(twelveHourMatch[1])}:${twelveHourMatch[2]} ${twelveHourMatch[3].toUpperCase()}`;
  }

  const twentyFourHourMatch = time.match(/^(\d{1,2}):(\d{2})$/);
  if (twentyFourHourMatch) {
    const date = new Date();
    date.setHours(
      Number(twentyFourHourMatch[1]),
      Number(twentyFourHourMatch[2]),
      0,
      0,
    );
    return date.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
    });
  }

  return time || "No time";
}

function formatStudentAppointmentValue(value, labels) {
  const normalized = String(value || "").trim();
  if (!normalized) return "—";
  return labels[normalized] || normalized.replaceAll("_", " ");
}

function getStudentAppointmentDateTime(appointment) {
  const dateMatch = String(appointment.preferred_date || "").match(
    /^(\d{4})-(\d{2})-(\d{2})$/,
  );
  const time = String(appointment.preferred_time_slot || "").trim();
  const twelveHourMatch = time.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
  const twentyFourHourMatch = time.match(/^(\d{1,2}):(\d{2})$/);

  if (!dateMatch || (!twelveHourMatch && !twentyFourHourMatch)) {
    return null;
  }

  let hour;
  let minute;

  if (twelveHourMatch) {
    const inputHour = Number(twelveHourMatch[1]);
    minute = Number(twelveHourMatch[2]);

    if (inputHour < 1 || inputHour > 12 || minute > 59) {
      return null;
    }

    hour =
      (inputHour % 12) +
      (twelveHourMatch[3].toUpperCase() === "PM" ? 12 : 0);
  } else {
    hour = Number(twentyFourHourMatch[1]);
    minute = Number(twentyFourHourMatch[2]);

    if (hour > 23 || minute > 59) {
      return null;
    }
  }

  const appointmentDate = new Date(
    Number(dateMatch[1]),
    Number(dateMatch[2]) - 1,
    Number(dateMatch[3]),
    hour,
    minute,
    0,
    0,
  );

  return Number.isNaN(appointmentDate.getTime()) ? null : appointmentDate;
}

function canStudentModifyAppointment(appointment) {
  const appointmentDate = getStudentAppointmentDateTime(appointment);
  return Boolean(
    appointmentDate &&
      appointmentDate.getTime() - Date.now() >= STUDENT_MODIFICATION_DEADLINE_MS,
  );
}

async function requestStudentAppointment(path, options = {}) {
  const response = await fetch(`${window.location.origin}${path}`, options);
  const payload = await response.json();

  if (!response.ok) {
    throw new Error(payload.message || "Unable to update appointment.");
  }

  return payload;
}

function createStudentAppointmentStatus(status) {
  const normalizedStatus = String(status || "").toLowerCase();
  const badge = document.createElement("span");

  badge.className = `student-appointment-status ${
    STUDENT_APPOINTMENT_STATUS_LABELS[normalizedStatus]
      ? normalizedStatus
      : "pending"
  }`;
  badge.textContent =
    STUDENT_APPOINTMENT_STATUS_LABELS[normalizedStatus] || "Pending";

  return badge;
}

function appendStudentAppointmentMeta(container, label, value) {
  const item = document.createElement("div");
  const heading = document.createElement("span");
  const content = document.createElement("strong");

  heading.textContent = label;
  content.textContent = value;
  item.append(heading, content);
  container.appendChild(item);
}

function createStudentAppointmentCard(appointment) {
  const card = document.createElement("article");
  const status = String(appointment.status || "").toLowerCase();
  const header = document.createElement("div");
  const title = document.createElement("h3");
  const metadata = document.createElement("div");

  card.className = "student-appointment-card";
  header.className = "student-appointment-card-header";
  title.textContent = `${formatStudentAppointmentDate(
    appointment.preferred_date,
  )} at ${formatStudentAppointmentTime(appointment.preferred_time_slot)}`;
  header.append(title, createStudentAppointmentStatus(status));

  metadata.className = "student-appointment-meta";
  appendStudentAppointmentMeta(
    metadata,
    "Category",
    formatStudentAppointmentValue(appointment.appointment_category, {
      career_schooling: "Career / Schooling",
      home_family: "Home and Family",
      personality: "Personality Development",
      personality_development: "Personality Development",
      relationships: "Relationships",
      religion: "Religion / Spiritual Development",
      religion_spiritual: "Religion / Spiritual Development",
      health: "Health and Recreation",
      health_recreation: "Health and Recreation",
      employment: "Employment",
      others: "Others",
    }),
  );
  appendStudentAppointmentMeta(
    metadata,
    "Mode",
    formatStudentAppointmentValue(appointment.appointment_mode, {
      onsite: "Onsite",
      online: "Online",
      hybrid: "Hybrid",
    }),
  );
  appendStudentAppointmentMeta(
    metadata,
    "Source",
    formatStudentAppointmentValue(appointment.appointment_source, {
      chatbot: "Chatbot",
      walk_in: "Walk-in",
      hotline: "Hotline",
      messenger: "Messenger",
      email: "Email",
      staff_manual: "Staff Manual Entry",
    }),
  );

  card.append(header, metadata);

  if (status === "pending") {
    if (canStudentModifyAppointment(appointment)) {
      const actions = document.createElement("div");
      const cancelButton = document.createElement("button");
      const rescheduleButton = document.createElement("button");

      actions.className = "student-appointment-actions";
      cancelButton.type = "button";
      cancelButton.className = "btn-secondary";
      cancelButton.textContent = "Cancel Appointment";
      rescheduleButton.type = "button";
      rescheduleButton.className = "btn-primary";
      rescheduleButton.textContent = "Reschedule";

      cancelButton.addEventListener("click", () => {
        void cancelStudentAppointment(
          appointment.id,
          cancelButton,
          rescheduleButton,
        );
      });
      rescheduleButton.addEventListener("click", () => {
        openRescheduleModal(appointment);
      });

      actions.append(cancelButton, rescheduleButton);
      card.appendChild(actions);
    } else {
      const restriction = document.createElement("p");
      restriction.className = "student-appointment-policy";
      restriction.textContent = STUDENT_MODIFICATION_MESSAGE;
      card.appendChild(restriction);
    }
  }

  return card;
}

function renderStudentAppointments(appointments) {
  studentAppointmentsList.replaceChildren();

  if (!appointments.length) {
    const empty = document.createElement("p");
    empty.className = "student-appointment-policy";
    empty.textContent = "No appointments found.";
    studentAppointmentsList.appendChild(empty);
    return;
  }

  appointments.forEach((appointment) => {
    studentAppointmentsList.appendChild(createStudentAppointmentCard(appointment));
  });
}

async function loadStudentAppointments({ preserveMessage = false } = {}) {
  if (!studentAppointmentsList) return false;

  if (!preserveMessage) {
    setStudentAppointmentMessage("");
  }

  studentAppointmentsList.replaceChildren();
  const loading = document.createElement("p");
  loading.className = "student-appointment-policy";
  loading.textContent = "Loading appointments…";
  studentAppointmentsList.appendChild(loading);

  try {
    const response = await requestStudentAppointment("/api/appointments/my");
    const appointments = Array.isArray(response.data?.items)
      ? response.data.items
      : [];

    renderStudentAppointments(appointments);
    return true;
  } catch (error) {
    studentAppointmentsList.replaceChildren();
    const unavailable = document.createElement("p");
    unavailable.className = "student-appointment-policy";
    unavailable.textContent = "Unable to load appointments.";
    studentAppointmentsList.appendChild(unavailable);

    if (!preserveMessage) {
      setStudentAppointmentMessage(
        error.message || "Unable to load appointments.",
        "error",
      );
    }
    return false;
  }
}

async function cancelStudentAppointment(
  appointmentId,
  cancelButton,
  rescheduleButton,
) {
  if (!window.confirm("Cancel this appointment request?")) {
    return;
  }

  cancelButton.disabled = true;
  rescheduleButton.disabled = true;

  try {
    const response = await requestStudentAppointment(
      `/api/appointments/my/${encodeURIComponent(appointmentId)}/cancel`,
      { method: "PATCH" },
    );
    setStudentAppointmentMessage(
      response.message || "Appointment cancelled successfully.",
      "success",
    );
    await loadStudentAppointments({ preserveMessage: true });
  } catch (error) {
    setStudentAppointmentMessage(
      error.message || "Unable to cancel appointment.",
      "error",
    );
    cancelButton.disabled = false;
    rescheduleButton.disabled = false;
  }
}

function populateRescheduleTimeOptions() {
  const preferredTime = document.getElementById("prefTime");
  if (!preferredTime || !rescheduleTime) return;

  rescheduleTime.replaceChildren(
    ...Array.from(preferredTime.options, (option) => option.cloneNode(true)),
  );
  rescheduleTime.selectedIndex = 0;
}

function openRescheduleModal(appointment) {
  reschedulingAppointmentId = appointment.id;
  populateRescheduleTimeOptions();
  rescheduleDate.value = "";
  rescheduleDate.min = document.getElementById("prefDate")?.min || "";
  rescheduleAppointmentSummary.textContent = `Current request: ${formatStudentAppointmentDate(
    appointment.preferred_date,
  )} at ${formatStudentAppointmentTime(appointment.preferred_time_slot)}.`;
  setStudentAppointmentMessage("", "", rescheduleMessage);
  rescheduleModal.classList.add("active");
  document.body.style.overflow = "hidden";
  rescheduleDate.focus();
}

function closeRescheduleModal() {
  rescheduleModal.classList.remove("active");
  document.body.style.overflow = "";
  rescheduleForm.reset();
  reschedulingAppointmentId = null;
}

refreshStudentAppointmentsButton?.addEventListener("click", () => {
  void loadStudentAppointments();
});

rescheduleClose?.addEventListener("click", closeRescheduleModal);

rescheduleModal?.addEventListener("click", (event) => {
  if (event.target === rescheduleModal) {
    closeRescheduleModal();
  }
});

rescheduleForm?.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!reschedulingAppointmentId) {
    return;
  }

  if (!rescheduleDate.value || !rescheduleTime.value) {
    setStudentAppointmentMessage(
      "Select a new preferred date and time.",
      "error",
      rescheduleMessage,
    );
    return;
  }

  rescheduleSubmit.classList.add("loading");
  rescheduleSubmit.disabled = true;

  try {
    const response = await requestStudentAppointment(
      `/api/appointments/my/${encodeURIComponent(
        reschedulingAppointmentId,
      )}/reschedule`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          preferred_date: rescheduleDate.value,
          preferred_time_slot: rescheduleTime.value,
        }),
      },
    );
    closeRescheduleModal();
    setStudentAppointmentMessage(
      response.message || "Appointment rescheduled successfully.",
      "success",
    );
    await loadStudentAppointments({ preserveMessage: true });
  } catch (error) {
    setStudentAppointmentMessage(
      error.message || "Unable to reschedule appointment.",
      "error",
      rescheduleMessage,
    );
  } finally {
    rescheduleSubmit.classList.remove("loading");
    rescheduleSubmit.disabled = false;
  }
});

modalClose.addEventListener("click", closeModal);
// Close on overlay click
modal.addEventListener("click", (e) => {
  if (e.target === modal) closeModal();
});
// Close on Escape key
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    if (modal.classList.contains("active")) {
      closeModal();
    }
    if (rescheduleModal?.classList.contains("active")) {
      closeRescheduleModal();
    }
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
populateRescheduleTimeOptions();
void loadStudentAppointments();
