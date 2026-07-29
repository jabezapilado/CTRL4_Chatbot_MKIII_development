/* dashboard.js — SOC Staff Dashboard logic */

if (window.requireAuth) {
  window.requireAuth();
}

const API_BASE = window.location.origin;

let sampleInquiries = [];
let conversationSummaries = [];

const views = document.querySelectorAll(".view");

const settingsStorageKey = "hau_dashboard_settings";
const defaultSettings = {
  officeHours: "Monday to Friday, 8:00 AM - 5:00 PM",
  officeEmail: "guidance@hau.edu.ph",
  contactNumber: "(045) 123-4567",
  officeLocation: "SOC Guidance Office, Holy Angel University",
  autoFlag: true,
  showSupport: false,
  escalationMessage:
    "Your concern may need further attention from Guidance Office personnel. Please wait for proper assistance or contact the office directly if urgent.",
  faqs: [
    {
      title: "Office Hours",
      question: "What are your office hours?",
      answer:
        "The SOC Guidance Office is open from Monday to Friday, 8:00 AM to 5:00 PM.",
    },
    {
      title: "Book Appointment",
      question: "How can I book an appointment?",
      answer:
        "You may book an appointment by selecting the Book Appointment option and submitting your preferred date and reason for appointment.",
    },
    {
      title: "Counseling Services",
      question: "Can I speak with a counselor?",
      answer:
        "Yes, you may request counseling assistance through the chatbot or visit the SOC Guidance Office during office hours.",
    },
  ],
};

function loadSettings() {
  try {
    const raw = localStorage.getItem(settingsStorageKey);
    if (!raw) return { ...defaultSettings };
    return { ...defaultSettings, ...JSON.parse(raw) };
  } catch (error) {
    console.error(error);
    return { ...defaultSettings };
  }
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data;
}

function mapInquiry(row) {
  const createdAt = row.created_at ? new Date(row.created_at) : new Date();
  return {
    student: row.user_name || row.student_name || "Unknown",
    studentId: row.student_id || (row.id ? `#${row.id}` : "—"),
    email: row.user_email || row.student_email || "",
    message: row.message || "",
    category: row.category || "General Inquiry",
    status: row.escalate ? "negative" : row.status || row.emotion || "neutral",
    time: createdAt.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
    }),
    staffNotes: row.staff_notes || "",
  };
}

function mapConversationSummary(row) {
  const createdAt = row.created_at ? new Date(row.created_at) : new Date();
  const now = new Date();
  const displayTime =
    createdAt.toDateString() === now.toDateString()
      ? createdAt.toLocaleTimeString("en-US", {
          hour: "numeric",
          minute: "2-digit",
        })
      : createdAt.toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
        });
  return {
    id: row.id,
    student: row.student_name || row.full_name || "Unknown",
    studentId: row.student_id || "—",
    email: row.student_email || "",
    category: row.topic || "General Inquiry",
    message: "AI Summary Available",
    emotion: row.emotion || "Unknown",
    language: row.language || "English",
    flagged: Boolean(row.flagged),
    status: row.status || (row.flagged ? "negative" : "pending"),
    summary: row.summary || "",
    recommendation: row.recommendation || "",
    counselorNotes: row.counselor_notes || "",
    conversation: row.conversation_json || [],
    createdAt,
    time: displayTime,
  };
}

function mapAppointment(row) {
  return {
    id: row.id,
    student: row.student_name || row.full_name || "Unknown",
    studentNumber: row.student_number || "—",
    email: row.student_email || "",

    date: row.preferred_date
      ? new Date(row.preferred_date).toISOString().split("T")[0]
      : "",
    time: row.preferred_time_slot,

    category: row.appointment_category,
    mode: row.appointment_mode,
    source: row.appointment_source,

    contactNumber: row.contact_number,
    reason: row.reason,
    counselorNotes: row.counselor_notes,

    program: row.program || "—",
    assignedTo: row.assigned_to || "—",

    status: row.status || "pending",

    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
}

function formatAppointmentDate(dateValue) {
  if (!dateValue) return "No date";
  const parsed = new Date(`${dateValue}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) return dateValue;
  return parsed.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatAppointmentTime(timeValue) {
  if (!timeValue) return "No time";

  // Already in 12-hour format (e.g. "10:00 AM")
  if (/^\d{1,2}:\d{2}\s?(AM|PM)$/i.test(timeValue.trim())) {
    return timeValue;
  }

  // 24-hour format (e.g. "14:30")
  if (/^\d{1,2}:\d{2}$/.test(timeValue.trim())) {
    const [hourStr, minuteStr] = timeValue.split(":");
    const date = new Date();
    date.setHours(Number(hourStr), Number(minuteStr), 0, 0);
    return date.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
    });
  }

  return timeValue;
}

function formatAppointmentSource(source) {
  const map = {
    chatbot: "Chatbot",
    walk_in: "Walk-in",
    hotline: "Hotline",
    messenger: "Messenger",
    email: "Email",
    staff_manual: "Staff Manual Entry",
  };
  return map[source] || source;
}

function formatAppointmentMode(mode) {
  const map = {
    onsite: "Onsite",
    online: "Online",
    hybrid: "Hybrid",
  };
  return map[mode] || mode || "—";
}

function formatAppointmentCategory(category) {
  if (!category) return "General";
  const map = {
    career_schooling: "Career / Schooling",
    home_family: "Home and Family",
    personality_development: "Personality Development",
    relationships: "Relationships",
    religion_spiritual: "Religion / Spiritual Development",
    health_recreation: "Health and Recreation",
    employment: "Employment",
    others: "Others",
  };
  return (
    map[category] ||
    category.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
  );
}

function renderAppointmentDashboard() {
  renderAppointmentStatistics();
  renderAppointmentRequests();
  renderTodaysAppointments();
  renderAppointmentHistory();
  renderFlaggedAppointmentCases();
  renderManualAppointmentEntry();
}

function renderAppointmentStatistics() {
  const appointments = window.backendAppointments || [];

  const today = new Date(Date.now() - new Date().getTimezoneOffset() * 60000)
    .toISOString()
    .split("T")[0];

  const normalizeDate = (value) => {
    if (!value) return "";
    if (typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
      return value;
    }
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return "";
    return parsed.toISOString().split("T")[0];
  };

  const totalToday = appointments.filter(
    (appointment) => normalizeDate(appointment.date) === today,
  ).length;

  const pendingCount = appointments.filter(
    (appointment) =>
      appointment.status === "pending" && appointment.source !== "staff_manual",
  ).length;

  const completedToday = appointments.filter(
    (appointment) =>
      appointment.status === "done" &&
      normalizeDate(appointment.date) === today,
  ).length;

  document.getElementById("appointments-today-count").textContent = totalToday;

  document.getElementById("pending-appointments-count").textContent =
    pendingCount;

  document.getElementById("completed-appointments-count").textContent =
    completedToday;
}

function renderAppointmentRequests() {
  const appointments = window.backendAppointments || [];

  const pendingAppointments = appointments.filter(
    (appointment) =>
      appointment.status === "pending" && appointment.source !== "staff_manual",
  );

  const container = document.getElementById("appointment-requests-container");

  if (!container) return;

  container.innerHTML = "";

  if (!pendingAppointments.length) {
    container.innerHTML = `
      <p class="sub">
        No pending appointment requests.
      </p>
    `;
    return;
  }

  pendingAppointments.forEach((appointment) => {
    const card = createPendingAppointmentCard(appointment);

    container.appendChild(card);
  });
}

function renderTodaysAppointments() {
  const appointments = window.backendAppointments || [];

  // (debug block moved below)

  const today = new Date(Date.now() - new Date().getTimezoneOffset() * 60000)
    .toISOString()
    .split("T")[0];

  const normalizeDate = (value) => {
    if (!value) return "";
    if (typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
      return value;
    }
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return String(value);
    return parsed.toISOString().split("T")[0];
  };

  // Manual appointments are created with an "approved" status,
  // so no special-case filtering is required here.
  const approvedAppointments = appointments.filter(
    (appointment) => appointment.status === "approved",
  );

  const container = document.getElementById("todays-appointments-container");

  if (!container) return;

  container.innerHTML = "";

  if (!approvedAppointments.length) {
    container.innerHTML = `
      <p class="sub">
        No approved appointments.
      </p>
    `;

    return;
  }

  approvedAppointments.forEach((appointment) => {
    const card = createTodaysAppointmentCard(appointment);
    container.appendChild(card);
  });
}

function renderAppointmentHistory() {
  const appointments = window.backendAppointments || [];

  const historyAppointments = appointments.filter((appointment) =>
    ["done", "did_not_attend", "cancelled"].includes(appointment.status),
  );

  const container = document.getElementById("appointment-history-container");

  if (!container) return;

  container.innerHTML = "";

  if (!historyAppointments.length) {
    container.innerHTML = `
      <p class="sub">
        No appointment history found.
      </p>
    `;

    return;
  }

  historyAppointments.forEach((appointment) => {
    const card = createAppointmentHistoryCard(appointment);

    container.appendChild(card);
  });
}

function renderFlaggedAppointmentCases() {
  const flaggedCases = conversationSummaries.filter(
    (summary) => summary.flagged,
  );

  const container = document.getElementById(
    "flagged-appointment-cases-container",
  );

  if (!container) return;

  container.innerHTML = "";

  if (!flaggedCases.length) {
    container.innerHTML = `
      <p class="sub">
        No flagged cases requiring appointments.
      </p>
    `;

    return;
  }

  flaggedCases.forEach((summary) => {
    const card = createFlaggedAppointmentCaseCard(summary);

    container.appendChild(card);
  });
}

function renderManualAppointmentEntry() {
  const container = document.getElementById(
    "manual-appointment-entry-container",
  );

  if (!container) {
    return;
  }

  container.innerHTML = `
    <div class="manual-appointment-card">
      <div class="field-grid-2">
        <div class="field-group">
          <label>Student</label>
          <input
            id="manual-student-search"
            type="text"
            placeholder="Search by student number or name"
          />
          <div
            id="manual-student-search-results"
            class="search-results"
            hidden
          ></div>
        </div>

        <div class="field-group">
          <label>Appointment Source</label>
          <select id="manual-appointment-source">
            <option>Walk-in</option>
            <option>Hotline</option>
            <option>Messenger</option>
            <option>Email</option>
          </select>
        </div>
      </div>

      <div class="field-grid-2">
        <div class="field-group">
          <label>Student Number</label>
          <input id="manual-student-number" type="text" disabled />
        </div>

        <div class="field-group">
          <label>Program</label>
          <input id="manual-student-program" type="text" disabled />
        </div>

        <div class="field-group">
          <label>Email Address</label>
          <input id="manual-student-email" type="email" disabled />
        </div>
      </div>

      <div class="manual-entry-actions">
        <button
          id="create-manual-appointment-btn"
          class="btn btn-primary"
        >
          Continue
        </button>
      </div>

      <div id="manual-appointment-details" style="display:none; margin-top:24px;">
        <hr style="margin:20px 0; border:none; border-top:1px solid var(--gray-200);">

        <h3 style="margin-bottom:16px;">Appointment Details</h3>

        <!-- Date/Time Row replaced with new layout -->
        <div class="field-group">
          <label>Preferred Date</label>
          <input id="manual-appointment-date" type="date" />
        </div>

        <div class="field-group" style="margin-top:16px;">
          <label>Preferred Time</label>
          <select id="manual-appointment-time">
            <option value="">Select a preferred time slot</option>
            <option value="8:00 AM">8:00 AM</option>
            <option value="9:00 AM">9:00 AM</option>
            <option value="10:00 AM">10:00 AM</option>
            <option value="1:00 PM">1:00 PM</option>
            <option value="2:00 PM">2:00 PM</option>
            <option value="3:00 PM">3:00 PM</option>
          </select>
        </div>

        <div class="field-grid-2" style="margin-top:12px;">
          <div class="field-group">
            <label>Mode</label>
            <select id="manual-appointment-mode">
              <option value="onsite">Onsite</option>
              <option value="online">Online</option>
            </select>
          </div>

          <div class="field-group">
            <label>Category</label>
            <select id="manual-appointment-category">
              <option value="career_schooling">Career / Schooling</option>
              <option value="home_family">Home and Family</option>
              <option value="personality_development">Personality Development</option>
              <option value="relationships">Relationships</option>
              <option value="religion_spiritual">Religion / Spiritual Development</option>
              <option value="health_recreation">Health and Recreation</option>
              <option value="employment">Employment</option>
              <option value="others">Others</option>
            </select>
          </div>
        </div>

        <div class="field-group" style="margin-top:12px;">
          <label>Reason</label>
          <textarea id="manual-appointment-reason" rows="4"></textarea>
        </div>

        <div class="manual-entry-actions" style="margin-top:16px;">
          <button id="save-manual-appointment-btn" class="btn btn-primary">
            Create Appointment
          </button>
        </div>
      </div>
    </div>
  `;

  const studentSearchInput = container.querySelector("#manual-student-search");

  const studentNumberInput = container.querySelector("#manual-student-number");

  const studentProgramInput = container.querySelector(
    "#manual-student-program",
  );

  const studentEmailInput = container.querySelector("#manual-student-email");

  studentSearchInput.value = "";
  studentNumberInput.value = "";
  studentProgramInput.value = "";
  studentEmailInput.value = "";

  const studentSearchResults = container.querySelector(
    "#manual-student-search-results",
  );

  studentSearchResults.innerHTML = "";
  studentSearchResults.hidden = true;
  let selectedStudent = null;

  studentSearchInput.addEventListener("input", async () => {
    const query = studentSearchInput.value.trim();
    selectedStudent = null;

    studentSearchResults.innerHTML = "";
    studentSearchResults.hidden = true;

    studentNumberInput.value = "";
    studentProgramInput.value = "";
    studentEmailInput.value = "";

    if (!query) {
      return;
    }

    try {
      const response = await fetchJson(
        `${API_BASE}/api/accounts/search?q=${encodeURIComponent(query)}`,
      );

      const students = response.items || [];

      studentSearchResults.innerHTML = "";

      if (!students.length) {
        studentSearchResults.hidden = true;
        return;
      }

      studentSearchResults.hidden = false;

      students.forEach((student) => {
        const option = document.createElement("button");
        option.type = "button";
        option.className = "manual-student-search-result";

        option.innerHTML = `
          <strong>${student.full_name}</strong><br>
          <small>${student.student_number} • ${student.program}</small>
        `;

        option.addEventListener("click", () => {
          selectedStudent = student;
          studentSearchInput.value = student.full_name;
          studentNumberInput.value = student.student_number || "";
          studentProgramInput.value = student.program || "";
          studentEmailInput.value = student.email || "";

          studentSearchResults.innerHTML = "";
          studentSearchResults.hidden = true;
        });

        studentSearchResults.appendChild(option);
      });
    } catch (error) {
      console.error(error);
      createToast("Unable to search student accounts.", "info");
    }
  });

  const appointmentSourceSelect = container.querySelector(
    "#manual-appointment-source",
  );

  appointmentSourceSelect.value = "Walk-in";

  const appointmentDateInput = container.querySelector(
    "#manual-appointment-date",
  );
  const appointmentTimeInput = container.querySelector(
    "#manual-appointment-time",
  );
  const appointmentModeSelect = container.querySelector(
    "#manual-appointment-mode",
  );
  const appointmentCategorySelect = container.querySelector(
    "#manual-appointment-category",
  );
  const appointmentReasonInput = container.querySelector(
    "#manual-appointment-reason",
  );

  container
    .querySelector("#create-manual-appointment-btn")
    ?.addEventListener("click", () => {
      if (!selectedStudent) {
        createToast(
          "Select an existing student account before continuing.",
          "info",
        );
        studentSearchInput.focus();
        return;
      }

      const detailsSection = container.querySelector(
        "#manual-appointment-details",
      );
      if (detailsSection) {
        detailsSection.style.display = "block";
        studentSearchInput.disabled = true;
        appointmentSourceSelect.disabled = true;
        detailsSection.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });

  container
    .querySelector("#save-manual-appointment-btn")
    ?.addEventListener("click", async () => {
      if (!appointmentDateInput.value) {
        createToast("Please select an appointment date.", "info");
        appointmentDateInput.focus();
        return;
      }

      if (!appointmentTimeInput.value) {
        createToast("Please select an appointment time.", "info");
        appointmentTimeInput.focus();
        return;
      }

      if (!appointmentReasonInput.value.trim()) {
        createToast("Please enter the appointment reason.", "info");
        appointmentReasonInput.focus();
        return;
      }

      const payload = {
        account_id: selectedStudent.id,
        appointment_source: appointmentSourceSelect.value
          .toLowerCase()
          .replace("-", "_")
          .replace(/\s+/g, "_"),
        preferred_date: appointmentDateInput.value,
        preferred_time_slot: appointmentTimeInput.value,
        appointment_mode: appointmentModeSelect.value,
        appointment_category: appointmentCategorySelect.value,
        reason: appointmentReasonInput.value.trim(),
      };

      try {
        await fetchJson(`${API_BASE}/api/appointments/manual`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        createToast("Manual appointment created successfully.", "success");

        await loadBackendData();
      } catch (error) {
        console.error(error);
        createToast(
          error.message || "Unable to create manual appointment.",
          "info",
        );
      }
    });
}

function createPendingAppointmentCard(appointment) {
  const card = document.createElement("div");
  card.className = "appointment-card";
  card.innerHTML = `
    <div class="appointment-card-header">
      <div>
        <h4>${appointment.student}</h4>
        <p class="sub">${appointment.studentNumber}</p>
      </div>
      ${badgeHTML(appointment.status)}
    </div>
    <div class="appointment-card-body">
      <div class="appointment-meta-grid">
        <div><span>Date</span><strong>${formatAppointmentDate(appointment.date)}</strong></div>
        <div><span>Time</span><strong>${formatAppointmentTime(appointment.time)}</strong></div>
        <div><span>Mode</span><strong>${formatAppointmentMode(appointment.mode)}</strong></div>
        <div><span>Source</span><strong>${formatAppointmentSource(appointment.source)}</strong></div>
      </div>
      <p><strong>${formatAppointmentCategory(appointment.category)}</strong></p>
    </div>
    <div class="appointment-card-footer">
      <button class="btn btn-outline appointment-view-btn">
        View Details
      </button>
      <button
          class="btn btn-primary appointment-approve-btn"
      >
          Approve
      </button>
      <button
          class="btn btn-outline appointment-cancel-btn"
      >
          Cancel
      </button>
    </div>
  `;
  const approveButton = card.querySelector(".appointment-approve-btn");
  const cancelButton = card.querySelector(".appointment-cancel-btn");
  const viewButton = card.querySelector(".appointment-view-btn");
  viewButton?.addEventListener("click", () => {
    openAppointmentDetails(appointment);
  });
  approveButton?.addEventListener("click", () => {
    openAppointmentDetails(appointment);
  });
  cancelButton?.addEventListener("click", () => {
    openAppointmentDetails(appointment);
  });
  return card;
}

function createTodaysAppointmentCard(appointment) {
  const card = document.createElement("div");
  card.className = "appointment-card";
  card.innerHTML = `
    <div class="appointment-card-header">
      <div>
        <h4>${appointment.student}</h4>
        <p class="sub">${appointment.studentNumber}</p>
      </div>
      ${badgeHTML(appointment.status)}
    </div>
    <div class="appointment-card-body">
      <div class="appointment-meta-grid">
        <div><span>Date</span><strong>${formatAppointmentDate(appointment.date)}</strong></div>
        <div><span>Time</span><strong>${formatAppointmentTime(appointment.time)}</strong></div>
        <div><span>Mode</span><strong>${formatAppointmentMode(appointment.mode)}</strong></div>
        <div><span>Source</span><strong>${formatAppointmentSource(appointment.source)}</strong></div>
      </div>
      <p><strong>${formatAppointmentCategory(appointment.category)}</strong></p>
    </div>
    <div class="appointment-card-footer">
      <button class="btn btn-outline appointment-view-btn">
        View Details
      </button>
      <button
        class="btn btn-primary appointment-done-btn"
      >
        Done
      </button>
      <button
        class="btn btn-outline appointment-dna-btn"
      >
        Did Not Attend
      </button>
      <button
        class="btn btn-outline appointment-cancel-btn"
      >
        Cancel
      </button>
    </div>
  `;
  const doneButton = card.querySelector(".appointment-done-btn");
  const didNotAttendButton = card.querySelector(".appointment-dna-btn");
  const cancelButton = card.querySelector(".appointment-cancel-btn");
  const viewButton = card.querySelector(".appointment-view-btn");
  viewButton?.addEventListener("click", () => {
    openAppointmentDetails(appointment);
  });
  doneButton?.addEventListener("click", () => {
    openAppointmentDetails(appointment);
  });
  didNotAttendButton?.addEventListener("click", () => {
    openAppointmentDetails(appointment);
  });
  cancelButton?.addEventListener("click", () => {
    openAppointmentDetails(appointment);
  });
  return card;
}

function createAppointmentHistoryCard(appointment) {
  const card = document.createElement("div");
  card.className = "appointment-card";
  card.innerHTML = `
    <div class="appointment-card-header">
      <div>
        <h4>${appointment.student}</h4>
        <p class="sub">${appointment.studentNumber}</p>
      </div>
      ${badgeHTML(appointment.status)}
    </div>
    <div class="appointment-card-body">
      <div class="appointment-meta-grid">
        <div><span>Date</span><strong>${formatAppointmentDate(appointment.date)}</strong></div>
        <div><span>Time</span><strong>${formatAppointmentTime(appointment.time)}</strong></div>
        <div><span>Mode</span><strong>${formatAppointmentMode(appointment.mode)}</strong></div>
        <div><span>Source</span><strong>${formatAppointmentSource(appointment.source)}</strong></div>
      </div>
      <p><strong>${formatAppointmentCategory(appointment.category)}</strong></p>
    </div>
    <div class="appointment-card-footer">
      <button class="btn btn-outline appointment-view-btn">
        View Details
      </button>
    </div>
  `;
  const viewButton = card.querySelector(".appointment-view-btn");
  viewButton?.addEventListener("click", () => {
    openAppointmentDetails(appointment);
  });
  return card;
}

async function updateAppointment(appointment, updates) {
  await fetchJson(`${API_BASE}/api/appointments/${appointment.id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(updates),
  });

  Object.assign(appointment, updates);

  await loadBackendData();
}

function createFlaggedAppointmentCaseCard(summary) {
  const card = document.createElement("div");

  card.className = "appointment-card";

  card.innerHTML = `
    <div class="appointment-card-header">
      <h4>${summary.student}</h4>
      <p class="sub">${summary.studentId}</p>
    </div>

    <div class="appointment-card-body">
      <p><strong>${summary.category}</strong></p>

      <p>
        Emotion:
        ${capitalize(summary.emotion)}
      </p>

      <p>
        Recommendation:
        ${summary.recommendation || "No recommendation available."}
      </p>

      <p>
        Status:
        ${badgeHTML(summary.status)}
      </p>
    </div>

    <div class="appointment-card-footer">
      <button
        class="btn btn-primary view-case-btn"
      >
        View Case
      </button>
    </div>
  `;

  const viewButton = card.querySelector(".view-case-btn");

  viewButton?.addEventListener("click", () => {
    openCaseDetails(summary);
  });

  return card;
}

function createFaqBlock(title, question, answer) {
  const container = document.createElement("div");
  container.className = "faq-block";
  container.innerHTML = `
    <div class="faq-block-header">
      <div class="faq-title">${title}</div>
      <div class="faq-q">${question}</div>
    </div>
    <div class="faq-block-body">
      <textarea>${answer || ""}</textarea>
    </div>
  `;
  return container;
}

function getFaqPanel() {
  const panel = Array.from(
    document.querySelectorAll("#view-settings .settings-panel"),
  ).find((panelEl) => {
    const heading = panelEl.querySelector("h3");
    return heading && heading.textContent.includes("FAQ Responses");
  });
  return panel || document.querySelector("#view-settings");
}

function getFaqListContainer(panel = getFaqPanel()) {
  if (!panel) return null;
  return panel.querySelector(".faq-list") || panel;
}

function appendFaqBlock(block, panel = getFaqPanel()) {
  const list = getFaqListContainer(panel);
  if (!block || !list) return false;
  list.appendChild(block);
  return true;
}

function getSettingsSnapshot() {
  const root = document.getElementById("view-settings");
  if (!root) return { ...defaultSettings };

  const inputs = root.querySelectorAll(".field-grid-2 .field-group input");
  const toggles = root.querySelectorAll(".toggle-row input[type=checkbox]");
  const escalationPanel = Array.from(
    root.querySelectorAll(".settings-panel"),
  ).find((panel) => {
    const heading = panel.querySelector("h3");
    return heading && heading.textContent.includes("Escalation");
  });

  return {
    officeHours: inputs[0]?.value || "",
    officeEmail: inputs[1]?.value || "",
    contactNumber: inputs[2]?.value || "",
    officeLocation: inputs[3]?.value || "",
    autoFlag: toggles[0]?.checked || false,
    showSupport: toggles[1]?.checked || false,
    escalationMessage:
      escalationPanel?.querySelector("textarea")?.value ||
      defaultSettings.escalationMessage,
    faqs: Array.from(root.querySelectorAll(".faq-block")).map((block) => ({
      title: block.querySelector(".faq-title")?.textContent?.trim() || "",
      question: block.querySelector(".faq-q")?.textContent?.trim() || "",
      answer: block.querySelector(".faq-block-body textarea")?.value || "",
    })),
  };
}

function saveSettingsToStorage(settings = getSettingsSnapshot(), toast = true) {
  try {
    localStorage.setItem(settingsStorageKey, JSON.stringify(settings));
    fetch(`${API_BASE}/api/settings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings),
    }).catch((error) => console.error(error));
    if (toast) createToast("Settings saved", "success");
    return true;
  } catch (error) {
    console.error(error);
    if (toast) createToast("Unable to save settings locally", "info");
    return false;
  }
}

function renderSettingsFromStorage() {
  const root = document.getElementById("view-settings");
  if (!root) return;

  const settings = loadSettings();
  const inputs = root.querySelectorAll(".field-grid-2 .field-group input");
  const toggles = root.querySelectorAll(".toggle-row input[type=checkbox]");
  const escalationPanel = Array.from(
    root.querySelectorAll(".settings-panel"),
  ).find((panel) => {
    const heading = panel.querySelector("h3");
    return heading && heading.textContent.includes("Escalation");
  });

  if (inputs[0]) inputs[0].value = settings.officeHours;
  if (inputs[1]) inputs[1].value = settings.officeEmail;
  if (inputs[2]) inputs[2].value = settings.contactNumber;
  if (inputs[3]) inputs[3].value = settings.officeLocation;

  if (toggles[0]) toggles[0].checked = Boolean(settings.autoFlag);
  if (toggles[1]) toggles[1].checked = Boolean(settings.showSupport);

  if (escalationPanel) {
    const textarea = escalationPanel.querySelector("textarea");
    if (textarea) textarea.value = settings.escalationMessage;
  }

  const faqPanel = getFaqPanel();
  if (faqPanel) {
    const faqList = getFaqListContainer(faqPanel);
    if (faqList) {
      faqList.querySelectorAll(".faq-block").forEach((block) => block.remove());
    }
    settings.faqs.forEach((faq) => {
      appendFaqBlock(
        createFaqBlock(faq.title, faq.question, faq.answer),
        faqPanel,
      );
    });
  }
}

function bindSettingsInteractions() {
  const root = document.getElementById("view-settings");
  if (!root) return;

  root.addEventListener("click", (event) => {
    const remove = event.target.closest(".chip-remove");
    if (remove) {
      const chip = remove.closest(".chip");
      chip?.remove();
      saveSettingsToStorage(undefined, false);
    }
  });

  root.addEventListener("input", (event) => {
    if (event.target.matches("input, textarea, select")) {
      saveSettingsToStorage(undefined, false);
    }
  });
}

// lightweight toast for feedback
function createToast(message, type = "info", timeout = 3400) {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }
  const t = document.createElement("div");
  t.className = "toast " + (type || "");
  t.textContent = message;
  container.appendChild(t);
  // auto remove
  setTimeout(() => {
    t.style.animation = "toast-out 300ms forwards";
    setTimeout(() => t.remove(), 350);
  }, timeout);
  return t;
}

// small prompt modal (returns Promise<string|null>)
function showPrompt(title, placeholder = "", multiline = false) {
  return new Promise((resolve) => {
    const overlay = document.createElement("div");
    overlay.className = "prompt-overlay";
    const prompt = document.createElement("div");
    prompt.className = "prompt";
    const h = document.createElement("h4");
    h.textContent = title;
    prompt.appendChild(h);
    const input = document.createElement(multiline ? "textarea" : "input");
    input.placeholder = placeholder || "";
    prompt.appendChild(input);
    const actions = document.createElement("div");
    actions.className = "prompt-actions";
    const cancel = document.createElement("button");
    cancel.className = "btn btn-outline btn-sm";
    cancel.textContent = "Cancel";
    const ok = document.createElement("button");
    ok.className = "btn btn-primary btn-sm";
    ok.textContent = "OK";
    actions.appendChild(cancel);
    actions.appendChild(ok);
    prompt.appendChild(actions);
    overlay.appendChild(prompt);
    document.body.appendChild(overlay);
    input.focus();

    ok.onclick = () => {
      resolve(input.value.trim() || null);
      overlay.remove();
    };
    cancel.onclick = () => {
      resolve(null);
      overlay.remove();
    };
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) {
        resolve(null);
        overlay.remove();
      }
    });
  });
}

const navItems = document.querySelectorAll(".nav-item[data-view]");
const headerTitle = document.getElementById("header-title");
const headerSub = document.getElementById("header-sub");
const headerActions = document.getElementById("header-actions");
const sidebar = document.getElementById("sidebar");
const sidebarToggle = document.getElementById("sidebar-toggle");
const sidebarOverlay = document.getElementById("sidebar-overlay");
const filterTabs = document.querySelectorAll(".filter-tab");
const currentLocation = window.location.pathname || "";

const viewMeta = {
  inbox: {
    title: "Case Inbox",
    sub: "Completed AI conversations awaiting counselor review.",
    actions:
      '<button class="btn btn-primary" id="new-entry-btn">New Manual Entry</button>',
  },

  flagged: {
    title: "Flagged Cases",
    sub: "Students with detected negative emotion requiring review",
    actions: "",
  },

  appointments: {
    title: "Appointments",
    sub: "Monitor appointment requests, appointment history, and counselor interventions.",
    actions: "",
  },

  resolved: {
    title: "Resolved Inquiries",
    sub: "Cases that have been closed or marked resolved",
    actions: "",
  },

  "conversation-summaries": {
    title: "Conversation Summaries",
    sub: "Review AI-generated summaries of completed student conversations.",
    actions: "",
  },

  "conversation-summary-details": {
    title: "Conversation Summary",
    sub: "Review AI-generated conversation summary and recommendation.",
    actions: '<button class="btn btn-outline" onclick="goBack()">Back</button>',
  },

  reports: {
    title: "Reports",
    sub: "Monitor chatbot inquiries, flagged concerns, and response trends.",
    actions: '<div class="report-period-badge">This Month</div>',
  },
  settings: {
    title: "Settings & FAQ Management",
    sub: "Update chatbot responses, office details, categories, and escalation messages.",
    actions:
      '<button class="btn btn-primary" onclick="saveSettings()">Save Changes</button>',
  },
  "manual-entry": {
    title: "New Manual Entry",
    sub: "Create an inquiry record for concerns received outside the chatbot.",
    actions:
      '<button class="btn btn-outline" onclick="goBack()">Back to Dashboard</button>',
  },
  "case-details": {
    title: "Case Details",
    sub: "Review student concern, chatbot classification, and counselor action.",
    actions:
      '<button class="btn btn-outline" onclick="goBack()">Back to Dashboard</button>',
  },
  "appointment-details": {
    title: "Appointment Details",
    sub: "Review appointment information, manage its status, and record counselor notes.",
    actions:
      '<button class="btn btn-outline" onclick="goBack()">Back to Appointments</button>',
  },
};

let currentView = "inbox";
let prevView = "inbox";
let currentInboxFilter = "all";

function initials(name) {
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function capitalize(value) {
  if (!value) return "Unknown";
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function badgeHTML(status) {
  const map = {
    negative: ["negative", "Negative"],
    neutral: ["neutral", "Routine"],
    resolved: ["resolved", "Resolved"],

    pending: ["pending", "Pending"],
    approved: ["approved", "Approved"],
    done: ["resolved", "Done"],
    cancelled: ["negative", "Cancelled"],
    did_not_attend: ["negative", "Did Not Attend"],
  };
  const [cls, label] = map[status] || ["pending", "Pending"];
  return `<span class="badge ${cls}">${label}</span>`;
}

function updateHeader(viewId) {
  const meta = viewMeta[viewId] || {};
  headerTitle.textContent = meta.title || "";
  headerSub.textContent = meta.sub || "";
  headerActions.innerHTML = meta.actions || "";

  const newEntryBtn = document.getElementById("new-entry-btn");
  if (newEntryBtn) {
    newEntryBtn.addEventListener("click", () => switchView("manual-entry"));
  }

  const backToSettingsBtn = document.getElementById("back-to-settings-btn");
  if (backToSettingsBtn) {
    backToSettingsBtn.addEventListener("click", () => {
      switchView("settings");
    });
  }
}

function switchView(viewId) {
  prevView = currentView;
  currentView = viewId;

  views.forEach((view) => view.classList.remove("active"));
  const activeView = document.getElementById(`view-${viewId}`);
  if (activeView) activeView.classList.add("active");

  navItems.forEach((item) => {
    item.classList.toggle("active", item.dataset.view === viewId);
  });

  updateHeader(viewId);
  window.scrollTo(0, 0);
}

function goBack() {
  switchView(prevView === currentView ? "inbox" : prevView);
}

async function saveSettings() {
  return saveSettingsToStorage(getSettingsSnapshot());
}

navItems.forEach((item) => {
  item.addEventListener("click", () => switchView(item.dataset.view));
});

sidebarToggle.addEventListener("click", () => {
  sidebar.classList.toggle("open");
  sidebarOverlay.classList.toggle("open");
});

sidebarOverlay.addEventListener("click", () => {
  sidebar.classList.remove("open");
  sidebarOverlay.classList.remove("open");
});

function makeRow(inquiry, includeActions = true) {
  const tr = document.createElement("tr");
  const actionsCell = includeActions
    ? `<td>
        <div class="action-cell">
          <button class="action-link view-btn">View</button>
          ${inquiry.status !== "resolved" ? '<button class="action-link resolve-btn">Resolve</button>' : ""}
        </div>
      </td>`
    : "<td></td>";

  const preview = inquiry.summary
    ? inquiry.summary.length > 80
      ? inquiry.summary.slice(0, 80) + "..."
      : inquiry.summary
    : inquiry.message || "No preview available";

  tr.innerHTML = `
    <td>
      <div class="student-cell">
        <div class="student-avatar">${initials(inquiry.student)}</div>
        <div>
          <div class="student-name">${inquiry.student}</div>
          <div class="student-id">${inquiry.studentId}</div>
        </div>
      </div>
    </td>
    <td>
      <div class="msg-preview">
        ${preview}
      </div>
    </td>
    <td>${inquiry.category}</td>
    <td>${badgeHTML(inquiry.status)}</td>
    <td class="time-cell">${inquiry.time}</td>
    ${actionsCell}
  `;

  tr.querySelector(".view-btn")?.addEventListener("click", () =>
    openCaseDetails(inquiry),
  );
  tr.querySelector(".resolve-btn")?.addEventListener("click", () => {
    inquiry.status = "resolved";
    renderAllTables();
    updateFlaggedCount();
  });

  return tr;
}

function renderTable(tbodyId, filter) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  tbody.innerHTML = "";

  const list =
    filter === "all"
      ? sampleInquiries
      : sampleInquiries.filter((inquiry) => inquiry.status === filter);

  if (!list.length) {
    tbody.innerHTML =
      '<tr><td colspan="6" style="text-align:center;color:var(--gray-400);padding:30px">No inquiries found.</td></tr>';
    return;
  }

  list.forEach((inquiry) => tbody.appendChild(makeRow(inquiry)));
}

function renderConversationTable(tbodyId, filter) {
  const tbody = document.getElementById(tbodyId);

  if (!tbody) return;

  tbody.innerHTML = "";

  let list = conversationSummaries;

  if (filter === "negative") {
    list = list.filter((item) => item.flagged);
  } else if (filter === "resolved") {
    list = list.filter((item) => item.status === "resolved");
  } else if (filter === "pending") {
    list = list.filter((item) => item.status === "pending");
  }

  if (!list.length) {
    tbody.innerHTML =
      '<tr><td colspan="6" style="text-align:center;color:var(--gray-400);padding:30px">No conversations found.</td></tr>';
    return;
  }

  list.forEach((summary) => {
    tbody.appendChild(makeRow(summary));
  });
}

function renderAllTables() {
  renderConversationTable("inquiry-tbody", currentInboxFilter);
  renderConversationTable("flagged-tbody", "negative");
  renderConversationTable("resolved-tbody", "resolved");
}

function renderConversationSummaries() {
  const tbody = document.getElementById("conversation-summary-tbody");

  if (!tbody) return;

  tbody.innerHTML = "";

  if (!conversationSummaries.length) {
    tbody.innerHTML =
      '<tr><td colspan="6" style="text-align:center;color:var(--gray-400);padding:30px">No conversation summaries found.</td></tr>';
    return;
  }

  conversationSummaries.forEach((summary) => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${summary.student}</td>
      <td>${summary.category}</td>
      <td>${capitalize(summary.emotion)}</td>
      <td>${
        summary.createdAt
          ? summary.createdAt.toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
              year: "numeric",
            })
          : "—"
      }</td>
      <td>
        <button
          class="action-link view-summary-btn"
          data-id="${summary.id}"
        >
          View
        </button>
      </td>
    `;

    tbody.appendChild(tr);
  });

  tbody.querySelectorAll(".view-summary-btn").forEach((button) => {
    button.addEventListener("click", () => {
      const summary = conversationSummaries.find(
        (item) => String(item.id) === button.dataset.id,
      );

      if (summary) {
        openConversationSummary(summary);
      }
    });
  });
}

function renderReports() {
  const totalInquiries = conversationSummaries.length;

  const flaggedCases = conversationSummaries.filter(
    (summary) => summary.flagged,
  ).length;

  const resolvedCases = conversationSummaries.filter(
    (summary) => summary.status === "resolved",
  ).length;

  document.getElementById("report-total-inquiries").textContent =
    totalInquiries;

  document.getElementById("report-flagged-cases").textContent = flaggedCases;

  document.getElementById("report-resolved-cases").textContent = resolvedCases;
}

function updateFlaggedCount() {
  const count = conversationSummaries.filter(
    (summary) => summary.flagged,
  ).length;
  const flaggedCount = document.getElementById("flagged-count");
  const statFlagged = document.getElementById("stat-flagged");
  const statFlagged2 = document.getElementById("stat-flagged-2");
  if (flaggedCount) flaggedCount.textContent = count;
  if (statFlagged) statFlagged.textContent = count;
  if (statFlagged2) statFlagged2.textContent = count;
}

filterTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    filterTabs.forEach((item) => item.classList.remove("active"));
    tab.classList.add("active");
    currentInboxFilter = tab.dataset.filter;
    renderConversationTable("inquiry-tbody", currentInboxFilter);
  });
});

function openConversationSummary(summary) {
  if (!summary) {
    createToast("Unable to open conversation summary.", "info");
    return;
  }

  document.getElementById("summary-student").textContent =
    summary.student_name || "Unknown";

  document.getElementById("summary-topic").textContent =
    summary.topic || "General";

  document.getElementById("summary-emotion").textContent = capitalize(
    summary.emotion,
  );

  document.getElementById("summary-language").textContent = capitalize(
    summary.language,
  );

  document.getElementById("summary-flagged").innerHTML = summary.flagged
    ? '<span class="badge negative">Flagged</span>'
    : '<span class="badge neutral">Normal</span>';

  document.getElementById("summary-created-at").textContent = summary.created_at
    ? new Date(summary.created_at).toLocaleString()
    : "—";

  document.getElementById("summary-text").textContent =
    summary.summary?.trim() || "No summary available.";

  document.getElementById("summary-recommendation").textContent =
    summary.recommendation?.trim() || "No recommendation available.";

  let transcript = [];

  try {
    if (Array.isArray(summary.conversation_json)) {
      transcript = summary.conversation_json;
    } else if (typeof summary.conversation_json === "string") {
      transcript = JSON.parse(summary.conversation_json);
    }
  } catch (error) {
    transcript = [];
    console.error("Unable to parse transcript:", error);
  }

  const totalMessages = transcript.length;

  const studentMessages = transcript.filter(
    (message) => message.from === "user",
  ).length;

  const aiMessages = transcript.filter(
    (message) => message.from === "bot",
  ).length;

  document.getElementById("summary-total-messages").textContent = totalMessages;

  document.getElementById("summary-student-messages").textContent =
    studentMessages;

  document.getElementById("summary-ai-messages").textContent = aiMessages;

  document.getElementById("summary-escalation-status").textContent =
    summary.flagged ? "Flagged for Review" : "No Escalation";

  switchView("conversation-summary-details");
}

function openCaseDetails(summary) {
  document.getElementById("case-avatar").textContent = initials(
    summary.student,
  );

  document.getElementById("case-name").textContent = summary.student;

  document.getElementById("case-meta").textContent =
    `Student ID: ${summary.studentId} · Email: ${summary.email || "N/A"}`;
  document.getElementById("case-message").textContent =
    summary.summary || "No AI summary available.";
  document.getElementById("case-recommendation").textContent =
    summary.recommendation || "No recommendation available.";
  const notesInput = document.getElementById("case-notes-input");
  const saveNotesBtn = document.getElementById("save-notes-btn");

  notesInput.value = summary.counselorNotes || "";

  let originalNotes = notesInput.value.trim();

  saveNotesBtn.disabled = true;
  saveNotesBtn.classList.add("disabled");

  notesInput.oninput = function () {
    const current = notesInput.value.trim();
    const unchanged = current === originalNotes;

    saveNotesBtn.disabled = unchanged;
    saveNotesBtn.classList.toggle("disabled", unchanged);
  };
  document.getElementById("case-category").textContent = summary.category;
  document.getElementById("case-time").textContent = summary.time;
  document.getElementById("case-emotion").textContent = capitalize(
    summary.emotion,
  );
  document.getElementById("case-status-label").textContent =
    summary.status === "resolved"
      ? "Resolved"
      : summary.flagged
        ? "Pending Review"
        : "Routine";

  const badge = document.getElementById("case-badge");

  if (summary.status === "resolved") {
    badge.className = "badge resolved";
    badge.textContent = "Resolved";
  } else if (summary.flagged) {
    badge.className = "badge negative";
    badge.textContent = "Pending Review";
  } else {
    badge.className = "badge neutral";
    badge.textContent = "Routine";
  }

  let transcript = [];

  try {
    if (Array.isArray(summary.conversation)) {
      transcript = summary.conversation;
    } else if (typeof summary.conversation === "string") {
      transcript = JSON.parse(summary.conversation);
    }
  } catch (error) {
    console.error(error);
    transcript = [];
  }

  const totalMessages = transcript.length;

  const studentMessages = transcript.filter(
    (message) => message.from === "user",
  ).length;

  const aiMessages = transcript.filter(
    (message) => message.from === "bot",
  ).length;

  document.getElementById("case-total-messages").textContent = totalMessages;

  document.getElementById("case-student-messages").textContent =
    studentMessages;

  document.getElementById("case-ai-messages").textContent = aiMessages;

  document.getElementById("case-escalation-status").textContent =
    summary.flagged ? "Flagged for Review" : "No Escalation";

  const resolveBtn = document.getElementById("case-resolve-btn");
  const pendingBtn = document.getElementById("case-pending-btn");

  function updateActionButtons() {
    resolveBtn.disabled = false;
    pendingBtn.disabled = false;

    resolveBtn.classList.remove("disabled");
    pendingBtn.classList.remove("disabled");

    if (summary.status === "resolved") {
      resolveBtn.disabled = true;
      resolveBtn.classList.add("disabled");
    }

    if (summary.status === "pending") {
      pendingBtn.disabled = true;
      pendingBtn.classList.add("disabled");
    }
  }

  updateActionButtons();

  resolveBtn.onclick = async () => {
    try {
      await fetchJson(`${API_BASE}/api/conversation-summaries/${summary.id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          status: "resolved",
        }),
      });

      summary.status = "resolved";

      updateActionButtons();

      document.getElementById("case-status-label").textContent = "Resolved";
      badge.className = "badge resolved";
      badge.textContent = "Resolved";

      renderAllTables();

      createToast("Case marked as resolved.", "success");
    } catch (error) {
      console.error(error);
      createToast("Unable to update case status.", "info");
    }
  };

  pendingBtn.onclick = async () => {
    try {
      await fetchJson(`${API_BASE}/api/conversation-summaries/${summary.id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          status: "pending",
        }),
      });

      summary.status = "pending";

      updateActionButtons();

      document.getElementById("case-status-label").textContent =
        "Pending Review";

      badge.className = "badge negative";
      badge.textContent = "Pending Review";

      renderAllTables();

      createToast("Case marked as pending.", "info");
    } catch (error) {
      console.error(error);
      createToast("Unable to update case status.", "info");
    }
  };

  document.getElementById("save-notes-btn").onclick = async () => {
    const notes = document.getElementById("case-notes-input").value.trim();

    if (!notes) {
      createToast("Please enter a note first.", "info");
      return;
    }

    try {
      await fetchJson(`${API_BASE}/api/conversation-summaries/${summary.id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          status: summary.status,
          counselor_notes: notes,
        }),
      });

      summary.counselorNotes = notes;

      originalNotes = notes.trim();

      saveNotesBtn.disabled = true;
      saveNotesBtn.classList.add("disabled");

      createToast("Counselor notes saved.", "success");
    } catch (error) {
      console.error(error);
      createToast("Unable to save counselor notes.", "info");
    }
  };

  switchView("case-details");
}

function openAppointmentDetails(appointment) {
  document.getElementById("appointment-avatar").textContent = initials(
    appointment.student,
  );

  document.getElementById("appointment-student-name").textContent =
    appointment.student;

  document.getElementById("appointment-student-number").textContent =
    appointment.studentNumber || "—";

  document.getElementById("appointment-email").textContent =
    appointment.email || "—";

  document.getElementById("appointment-contact-number").textContent =
    appointment.contactNumber || "—";

  document.getElementById("appointment-reason").textContent =
    appointment.reason || "No reason provided.";

  document.getElementById("appointment-category").textContent =
    formatAppointmentCategory(appointment.category);

  document.getElementById("appointment-mode").textContent =
    formatAppointmentMode(appointment.mode);

  document.getElementById("appointment-preferred-date").textContent =
    formatAppointmentDate(appointment.date);

  document.getElementById("appointment-preferred-time").textContent =
    formatAppointmentTime(appointment.time);

  document.getElementById("appointment-status").textContent = capitalize(
    appointment.status.replaceAll("_", " "),
  );

  document.getElementById("appointment-source").textContent =
    formatAppointmentSource(appointment.source);

  document.getElementById("appointment-program").textContent =
    appointment.program || "—";

  document.getElementById("appointment-assigned-to").textContent =
    appointment.assignedTo || "—";

  document.getElementById("appointment-created-at").textContent =
    appointment.createdAt
      ? new Date(appointment.createdAt).toLocaleString()
      : "—";
  const badge = document.getElementById("appointment-status-badge");

  badge.className = "badge";

  switch (appointment.status) {
    case "pending":
      badge.classList.add("pending");
      badge.textContent = "Pending";
      break;

    case "approved":
      badge.classList.add("approved");
      badge.textContent = "Approved";
      break;

    case "done":
      badge.classList.add("resolved");
      badge.textContent = "Completed";
      break;

    case "cancelled":
      badge.classList.add("negative");
      badge.textContent = "Cancelled";
      break;

    case "did_not_attend":
      badge.classList.add("negative");
      badge.textContent = "Did Not Attend";
      break;

    default:
      badge.classList.add("pending");
      badge.textContent = appointment.status;
  }

  const notesInput = document.getElementById("appointment-notes-input");
  const saveBtn = document.getElementById("save-appointment-notes-btn");

  const approveBtn = document.getElementById("appointment-approve-btn");
  const doneBtn = document.getElementById("appointment-done-btn");
  const didNotAttendBtn = document.getElementById("appointment-dna-btn");
  const cancelBtn = document.getElementById("appointment-cancel-btn");

  // Action button visibility logic
  approveBtn.hidden = appointment.status !== "pending";

  const canComplete = appointment.status === "approved";

  doneBtn.hidden = !canComplete;
  didNotAttendBtn.hidden = !canComplete;

  cancelBtn.hidden = !["pending", "approved"].includes(appointment.status);

  notesInput.value = appointment.counselorNotes || "";

  // Disable notes editing and hide save button if appointment is closed
  const appointmentClosed = ["done", "cancelled", "did_not_attend"].includes(
    appointment.status,
  );

  notesInput.readOnly = appointmentClosed;
  saveBtn.hidden = appointmentClosed;
  saveBtn.disabled = appointmentClosed;
  saveBtn.classList.toggle("disabled", appointmentClosed);

  let originalNotes = notesInput.value.trim();

  saveBtn.disabled = appointmentClosed || true;
  saveBtn.classList.toggle("disabled", true);

  notesInput.oninput = () => {
    if (appointmentClosed) {
      return;
    }
    const unchanged = notesInput.value.trim() === originalNotes;

    saveBtn.disabled = unchanged;
    saveBtn.classList.toggle("disabled", unchanged);
  };

  saveBtn.onclick = async () => {
    const notes = notesInput.value.trim();

    if (notes === originalNotes) {
      return;
    }

    if (!notes) {
      createToast("Please enter a note first.", "info");
      return;
    }

    saveBtn.disabled = true;
    try {
      await updateAppointment(appointment, {
        status: appointment.status,
        counselor_notes: notes,
      });

      appointment.counselorNotes = notes;
      originalNotes = notes;
      openAppointmentDetails(appointment);
      createToast("Counselor notes saved.", "success");
    } catch (error) {
      console.error(error);
      saveBtn.disabled = false;
      createToast("Unable to save counselor notes.", "info");
    }
  };
  approveBtn.onclick = async () => {
    approveBtn.disabled = true;
    try {
      await updateAppointment(appointment, {
        status: "approved",
      });

      createToast("Appointment approved.", "success");

      openAppointmentDetails(appointment);
    } catch (error) {
      console.error(error);
      approveBtn.disabled = false;
      createToast("Unable to approve appointment.", "info");
    }
  };

  cancelBtn.onclick = async () => {
    cancelBtn.disabled = true;
    try {
      await updateAppointment(appointment, {
        status: "cancelled",
      });

      createToast("Appointment cancelled.", "success");

      openAppointmentDetails(appointment);
    } catch (error) {
      console.error(error);
      cancelBtn.disabled = false;
      createToast("Unable to cancel appointment.", "info");
    }
  };

  didNotAttendBtn.onclick = async () => {
    didNotAttendBtn.disabled = true;
    try {
      await updateAppointment(appointment, {
        status: "did_not_attend",
      });

      createToast("Appointment marked as did not attend.", "success");

      openAppointmentDetails(appointment);
    } catch (error) {
      console.error(error);
      didNotAttendBtn.disabled = false;
      createToast("Unable to update appointment status.", "info");
    }
  };

  doneBtn.onclick = async () => {
    doneBtn.disabled = true;
    const notes = notesInput.value.trim();

    if (!notes) {
      createToast(
        "Please save counselor notes before completing the appointment.",
        "info",
      );
      notesInput.focus();
      doneBtn.disabled = false;
      return;
    }
    try {
      await updateAppointment(appointment, {
        status: "done",
        counselor_notes: notes,
      });
      appointment.counselorNotes = notes;

      createToast("Appointment marked as done.", "success");

      openAppointmentDetails(appointment);
    } catch (error) {
      console.error(error);
      doneBtn.disabled = false;
      createToast("Unable to update appointment status.", "info");
    }
  };

  switchView("appointment-details");
}

async function loadBackendData() {
  try {
    const inquiries = await fetchJson(`${API_BASE}/api/inquiries`);
    sampleInquiries = (inquiries.items || []).map(mapInquiry);
  } catch (error) {
    console.error(error);
    sampleInquiries = [];
  }

  try {
    const summaries = await fetchJson(`${API_BASE}/api/conversation-summaries`);

    conversationSummaries = (summaries.items || []).map(mapConversationSummary);
  } catch (error) {
    console.error(error);
    conversationSummaries = [];
  }

  try {
    const appointments = await fetchJson(`${API_BASE}/api/appointments`);
    window.backendAppointments = (appointments.items || []).map(mapAppointment);
  } catch (error) {
    console.error(error);
    window.backendAppointments = [];
  }

  try {
    const settings = await fetchJson(`${API_BASE}/api/settings`);
    localStorage.setItem(settingsStorageKey, JSON.stringify(settings));
  } catch (error) {
    console.error(error);
  }

  renderAllTables();
  updateFlaggedCount();
  renderConversationSummaries();
  renderSettingsFromStorage();
  renderReports();
  renderAppointmentDashboard();
}

function openCaseFromReport(name, id, message, category, status, time) {
  openCaseDetails({
    student: name,
    studentId: id,
    message,
    category,
    status,
    time,
  });
}

document.getElementById("save-entry-btn")?.addEventListener("click", () => {
  const name = document.getElementById("entry-name").value.trim();
  const studentId = document.getElementById("entry-id").value.trim();
  const email = document.getElementById("entry-email").value.trim();
  const message = document.getElementById("entry-message").value.trim();
  const category = document.getElementById("entry-category").value;
  const statusValue = document
    .getElementById("entry-status")
    .value.toLowerCase();
  const now = new Date();
  const time = now.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  });

  if (!name || !studentId || !message) {
    createToast(
      "Please fill in Student Name, Student ID, and Message.",
      "info",
    );
    return;
  }

  const status = statusValue === "resolved" ? "resolved" : "neutral";
  fetchJson(`${API_BASE}/api/inquiries`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      student_id: studentId,
      student_name: name,
      student_email: email,
      message,
      category,
      status,
      source: "manual",
    }),
  })
    .then(() => loadBackendData())
    .then(() => {
      [
        "entry-name",
        "entry-id",
        "entry-email",
        "entry-message",
        "entry-notes",
      ].forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.value = "";
      });
      createToast("Entry saved successfully!", "success");
      switchView("inbox");
    })
    .catch(() => createToast("Unable to save entry right now.", "info"));
});

document.getElementById("clear-entry-btn")?.addEventListener("click", () => {
  [
    "entry-name",
    "entry-id",
    "entry-email",
    "entry-message",
    "entry-notes",
  ].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.value = "";
  });
});

function logout() {
  fetch(`${API_BASE}/auth/logout`, { method: "POST" })
    .catch(() => {})
    .finally(() => {
      sessionStorage.removeItem("hau_user");
      createToast("Logged out.", "info");
      if (window.getLoginUrl) {
        setTimeout(() => window.location.replace(window.getLoginUrl()), 700);
      }
    });
}

window.addEventListener("error", (event) => {
  console.error("Unexpected error:", event.error);
});

bindSettingsInteractions();
loadBackendData();

// UI buttons
document
  .getElementById("new-entry-btn")
  ?.addEventListener("click", () => switchView("manual-entry"));

async function addFaqFromButton() {
  const title = await showPrompt(
    "FAQ Title",
    "Short title (e.g. Office Hours)",
  );
  if (!title) return;
  const question = await showPrompt(
    "FAQ Question",
    "Example: What are your office hours?",
  );
  if (!question) return;
  const answer = await showPrompt("FAQ Answer", "Answer text", true);
  const container = createFaqBlock(title, question, answer);
  const faqPanel = getFaqPanel();
  if (appendFaqBlock(container, faqPanel)) {
    createToast("FAQ added", "success");
    saveSettingsToStorage(undefined, false);
  } else {
    createToast("Unable to add FAQ right now", "info");
  }
}

// Add FAQ button
document
  .getElementById("add-faq-btn")
  ?.addEventListener("click", addFaqFromButton);

// Save settings button in the UI
document
  .getElementById("save-settings-btn")
  ?.addEventListener("click", () => saveSettings());

window.saveSettings = saveSettings;
window.goBack = goBack;
window.openCaseFromReport = openCaseFromReport;
window.openCaseDetails = openCaseDetails;
window.logout = window.logout || logout;
window.addFaqFromButton = addFaqFromButton;
