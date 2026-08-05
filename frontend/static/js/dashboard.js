/* dashboard.js — SOC Staff Dashboard logic */

if (window.requireAuth) {
  window.requireAuth();
}

const API_BASE = window.location.origin;

let sampleInquiries = [];
let conversationSummaries = [];
let flaggedConversations = [];
let appointmentAnalytics = null;
let chatbotAnalytics = null;
let counselorWorkloadAnalytics = null;
let flaggedCaseAnalytics = null;
let reportsAnalytics = null;
let appointmentCalendarMonth = new Date(
  new Date().getFullYear(),
  new Date().getMonth(),
  1,
);

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

function mapFlaggedConversation(row) {
  const createdAt = row.created_at ? new Date(row.created_at) : null;
  return {
    id: row.id,
    category: row.primary_concern || "General inquiry",
    emotion: row.emotion_results || "neutral",
    summary: row.summary || "No summary available.",
    recommendation: row.recommendations || "No recommendation available.",
    escalationReason: row.escalation_reason || "AI safety escalation.",
    status: row.escalation_status || "pending",
    totalMessages: Number(row.total_messages) || 0,
    createdAt,
  };
}

function mapAppointment(row) {
  return {
    id: row.id,
    student: row.student_name || row.full_name || "Unknown",
    studentNumber: row.student_number || "—",
    email: row.student_email || row.email || "",

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

function escapeHtml(value) {
  const escapeMap = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  };

  return String(value ?? "").replace(
    /[&<>"']/g,
    (character) => escapeMap[character],
  );
}

function escapeAppointmentText(value) {
  return escapeHtml(value);
}

function getAppointmentCardText(appointment) {
  return {
    student: escapeAppointmentText(appointment.student),
    studentNumber: escapeAppointmentText(appointment.studentNumber),
    date: escapeAppointmentText(formatAppointmentDate(appointment.date)),
    time: escapeAppointmentText(formatAppointmentTime(appointment.time)),
    mode: escapeAppointmentText(formatAppointmentMode(appointment.mode)),
    source: escapeAppointmentText(formatAppointmentSource(appointment.source)),
    category: escapeAppointmentText(
      formatAppointmentCategory(appointment.category),
    ),
  };
}

const CALENDAR_STATUS_BADGES = {
  pending: ["pending", "Pending"],
  confirmed: ["neutral", "Confirmed"],
  cancelled: ["negative", "Cancelled"],
  rejected: ["negative", "Rejected"],
  completed: ["resolved", "Completed"],
};

function getAppointmentCalendarDate(value) {
  const date = String(value || "");
  return /^\d{4}-\d{2}-\d{2}$/.test(date) ? date : "";
}

function getAppointmentCalendarTimeSortValue(value) {
  const time = String(value || "").trim();
  const twelveHourMatch = time.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);

  if (twelveHourMatch) {
    const hour = Number(twelveHourMatch[1]);
    const minute = Number(twelveHourMatch[2]);

    if (hour >= 1 && hour <= 12 && minute >= 0 && minute <= 59) {
      const normalizedHour =
        (hour % 12) + (twelveHourMatch[3].toUpperCase() === "PM" ? 12 : 0);
      return normalizedHour * 60 + minute;
    }
  }

  const twentyFourHourMatch = time.match(/^(\d{1,2}):(\d{2})$/);
  if (twentyFourHourMatch) {
    const hour = Number(twentyFourHourMatch[1]);
    const minute = Number(twentyFourHourMatch[2]);

    if (hour >= 0 && hour <= 23 && minute >= 0 && minute <= 59) {
      return hour * 60 + minute;
    }
  }

  return Number.MAX_SAFE_INTEGER;
}

function createAppointmentCalendarStatusBadge(status) {
  const normalizedStatus = String(status || "").toLowerCase();
  const [className, label] =
    CALENDAR_STATUS_BADGES[normalizedStatus] || CALENDAR_STATUS_BADGES.pending;
  const badge = document.createElement("span");

  badge.className = `badge ${className}`;
  badge.textContent = label;

  return badge;
}

function createAppointmentCalendarEvent(appointment) {
  const event = document.createElement("button");
  const date = formatAppointmentDate(appointment.date);
  const time = formatAppointmentTime(appointment.time);
  const status = String(appointment.status || "pending").toLowerCase();

  event.type = "button";
  event.className = "appointment-calendar-event";
  event.setAttribute(
    "aria-label",
    [
      appointment.student || "Unknown student",
      appointment.studentNumber || "No student number",
      date,
      time,
      CALENDAR_STATUS_BADGES[status]?.[1] || "Pending",
    ].join(", "),
  );

  const student = document.createElement("strong");
  student.className = "appointment-calendar-event-student";
  student.textContent = appointment.student || "Unknown";

  const studentNumber = document.createElement("span");
  studentNumber.className = "appointment-calendar-event-student-number";
  studentNumber.textContent = appointment.studentNumber || "—";

  const appointmentDate = document.createElement("time");
  appointmentDate.className = "appointment-calendar-event-date";
  appointmentDate.dateTime = getAppointmentCalendarDate(appointment.date);
  appointmentDate.textContent = date;

  const appointmentTime = document.createElement("time");
  appointmentTime.className = "appointment-calendar-event-time";
  appointmentTime.textContent = time;

  const statusContainer = document.createElement("span");
  statusContainer.className = "appointment-calendar-event-status";
  statusContainer.appendChild(createAppointmentCalendarStatusBadge(status));

  event.append(
    student,
    studentNumber,
    appointmentDate,
    appointmentTime,
    statusContainer,
  );
  event.addEventListener("click", () => openAppointmentDetails(appointment));

  return event;
}

function renderAppointmentCalendar() {
  const grid = document.getElementById("appointment-calendar-grid");
  const monthLabel = document.getElementById("appointment-calendar-month");

  if (!grid || !monthLabel) {
    return;
  }

  const year = appointmentCalendarMonth.getFullYear();
  const month = appointmentCalendarMonth.getMonth();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const firstWeekday = new Date(year, month, 1).getDay();
  const totalCells = Math.ceil((firstWeekday + daysInMonth) / 7) * 7;
  const appointmentsByDate = new Map();

  (window.backendAppointments || []).forEach((appointment) => {
    const date = getAppointmentCalendarDate(appointment.date);
    if (!date) {
      return;
    }

    const items = appointmentsByDate.get(date) || [];
    items.push(appointment);
    appointmentsByDate.set(date, items);
  });

  monthLabel.textContent = new Date(year, month, 1).toLocaleDateString(
    "en-US",
    {
      month: "long",
      year: "numeric",
    },
  );
  grid.replaceChildren();

  for (let index = 0; index < totalCells; index += 1) {
    const dayNumber = index - firstWeekday + 1;
    const day = document.createElement("section");
    day.className = "appointment-calendar-day";

    if (dayNumber < 1 || dayNumber > daysInMonth) {
      day.classList.add("is-outside-month");
      grid.appendChild(day);
      continue;
    }

    const date = `${year}-${String(month + 1).padStart(2, "0")}-${String(
      dayNumber,
    ).padStart(2, "0")}`;
    const heading = document.createElement("time");
    heading.className = "appointment-calendar-day-number";
    heading.dateTime = date;
    heading.textContent = String(dayNumber);
    day.appendChild(heading);

    const events = document.createElement("div");
    events.className = "appointment-calendar-events";
    const appointments = appointmentsByDate.get(date) || [];

    appointments
      .sort(
        (left, right) =>
          getAppointmentCalendarTimeSortValue(left.time) -
          getAppointmentCalendarTimeSortValue(right.time),
      )
      .forEach((appointment) => {
        events.appendChild(createAppointmentCalendarEvent(appointment));
      });

    day.appendChild(events);
    grid.appendChild(day);
  }
}

function bindAppointmentCalendar() {
  document
    .getElementById("appointment-calendar-previous")
    ?.addEventListener("click", () => {
      appointmentCalendarMonth = new Date(
        appointmentCalendarMonth.getFullYear(),
        appointmentCalendarMonth.getMonth() - 1,
        1,
      );
      renderAppointmentCalendar();
    });

  document
    .getElementById("appointment-calendar-next")
    ?.addEventListener("click", () => {
      appointmentCalendarMonth = new Date(
        appointmentCalendarMonth.getFullYear(),
        appointmentCalendarMonth.getMonth() + 1,
        1,
      );
      renderAppointmentCalendar();
    });
}

function renderAppointmentDashboard() {
  renderAppointmentStatistics();
  renderAppointmentAnalytics();
  renderAppointmentCalendar();
  renderAppointmentRequests();
  renderTodaysAppointments();
  renderAppointmentHistory();
  renderFlaggedAppointmentCases();
  renderManualAppointmentEntry();
}

function renderAnalyticsRows(
  containerId,
  rows,
  labelKey,
  emptyMessage = "No appointment data for this period.",
) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.replaceChildren();

  if (!rows.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 2;
    cell.textContent = emptyMessage;
    row.appendChild(cell);
    container.appendChild(row);
    return;
  }

  rows.forEach((item) => {
    const row = document.createElement("tr");
    const label = document.createElement("td");
    const count = document.createElement("td");
    label.textContent = item[labelKey];
    count.textContent = String(item.count);
    row.append(label, count);
    container.appendChild(row);
  });
}

function renderAppointmentAnalytics() {
  const analytics = appointmentAnalytics;
  if (!analytics) return;

  const total = document.getElementById("appointment-analytics-total");
  const range = document.getElementById("appointment-analytics-range");
  if (total) total.textContent = String(analytics.total_appointments || 0);

  if (range) {
    const { start_date: startDate, end_date: endDate } = analytics.filters || {};
    range.textContent =
      startDate || endDate
        ? `${startDate || "Beginning"} to ${endDate || "Present"}`
        : "All authorized appointment records";
  }

  renderAnalyticsRows(
    "appointment-analytics-statuses",
    analytics.status_distribution || [],
    "status",
  );
  renderAnalyticsRows("appointment-analytics-daily", analytics.daily_trends || [], "date");
  renderAnalyticsRows("appointment-analytics-weekly", analytics.weekly_trends || [], "week");
  renderAnalyticsRows("appointment-analytics-monthly", analytics.monthly_trends || [], "month");
  renderAnalyticsRows(
    "appointment-analytics-counselors",
    analytics.counselor_counts || [],
    "counselor_name",
  );
  renderAnalyticsRows(
    "appointment-analytics-programs",
    analytics.program_statistics || [],
    "program",
  );
}

function renderChatbotAnalytics() {
  const analytics = chatbotAnalytics;
  if (!analytics) return;

  const valueFor = (elementId, value, fallback = "0") => {
    const element = document.getElementById(elementId);
    if (element) element.textContent = value ?? fallback;
  };

  valueFor(
    "chatbot-analytics-total-messages",
    String(analytics.total_chatbot_messages || 0),
  );
  valueFor(
    "chatbot-analytics-finalizations",
    String(analytics.conversation_finalization_count || 0),
  );
  valueFor(
    "chatbot-analytics-escalations",
    String(analytics.escalation_count || 0),
  );
  valueFor(
    "chatbot-analytics-average-length",
    analytics.average_finalized_conversation_length === null
      ? "—"
      : String(analytics.average_finalized_conversation_length),
    "—",
  );

  const volume = analytics.message_volume || {};
  renderAnalyticsRows(
    "chatbot-analytics-emotions",
    analytics.persisted_emotion_result_distribution || [],
    "emotion_result",
    "No persisted inquiry records for this period.",
  );
  renderAnalyticsRows(
    "chatbot-analytics-daily",
    volume.daily || [],
    "date",
    "No persisted inquiry records for this period.",
  );
  renderAnalyticsRows(
    "chatbot-analytics-weekly",
    volume.weekly || [],
    "week",
    "No persisted inquiry records for this period.",
  );
  renderAnalyticsRows(
    "chatbot-analytics-monthly",
    volume.monthly || [],
    "month",
    "No persisted inquiry records for this period.",
  );
}

async function loadChatbotAnalytics() {
  const startDate = document.getElementById("chatbot-analytics-start-date")?.value;
  const endDate = document.getElementById("chatbot-analytics-end-date")?.value;
  const query = new URLSearchParams();
  if (startDate) query.set("start_date", startDate);
  if (endDate) query.set("end_date", endDate);

  const suffix = query.size ? `?${query.toString()}` : "";
  const result = await fetchJson(
    `${API_BASE}/api/dashboard/chatbot/analytics${suffix}`,
  );
  chatbotAnalytics = result.data || null;
  renderChatbotAnalytics();
}

function bindChatbotAnalyticsFilters() {
  document
    .getElementById("chatbot-analytics-apply")
    ?.addEventListener("click", async () => {
      try {
        await loadChatbotAnalytics();
      } catch (error) {
        console.error(error);
        createToast("Unable to load chatbot analytics.", "info");
      }
    });

  document
    .getElementById("chatbot-analytics-reset")
    ?.addEventListener("click", async () => {
      const startDate = document.getElementById("chatbot-analytics-start-date");
      const endDate = document.getElementById("chatbot-analytics-end-date");
      if (startDate) startDate.value = "";
      if (endDate) endDate.value = "";

      try {
        await loadChatbotAnalytics();
      } catch (error) {
        console.error(error);
        createToast("Unable to load chatbot analytics.", "info");
      }
    });
}

function renderCounselorWorkloadAnalytics() {
  const analytics = counselorWorkloadAnalytics;
  if (!analytics) return;

  const values = [
    [
      "counselor-workload-authorized-appointments",
      analytics.authorized_appointment_count,
    ],
    [
      "counselor-workload-pending-appointments",
      analytics.pending_appointment_count,
    ],
    [
      "counselor-workload-confirmed-appointments",
      analytics.confirmed_appointment_count,
    ],
    [
      "counselor-workload-completed-appointments",
      analytics.completed_appointment_count,
    ],
    ["counselor-workload-active-referrals", analytics.active_referral_count],
    [
      "counselor-workload-active-interventions",
      analytics.active_intervention_count,
    ],
    [
      "counselor-workload-completed-interventions",
      analytics.completed_intervention_count,
    ],
  ];

  values.forEach(([elementId, value]) => {
    const element = document.getElementById(elementId);
    if (element) element.textContent = String(value || 0);
  });

  renderAnalyticsRows(
    "counselor-workload-programs",
    analytics.workload_by_program || [],
    "program",
    "No authorized appointment records for this period.",
  );
}

async function loadCounselorWorkloadAnalytics() {
  const startDate = document.getElementById(
    "counselor-workload-start-date",
  )?.value;
  const endDate = document.getElementById(
    "counselor-workload-end-date",
  )?.value;
  const query = new URLSearchParams();
  if (startDate) query.set("start_date", startDate);
  if (endDate) query.set("end_date", endDate);

  const suffix = query.size ? `?${query.toString()}` : "";
  const result = await fetchJson(
    `${API_BASE}/api/dashboard/counselor-workload${suffix}`,
  );
  counselorWorkloadAnalytics = result.data || null;
  renderCounselorWorkloadAnalytics();
}

function bindCounselorWorkloadAnalyticsFilters() {
  document
    .getElementById("counselor-workload-apply")
    ?.addEventListener("click", async () => {
      try {
        await loadCounselorWorkloadAnalytics();
      } catch (error) {
        console.error(error);
        createToast("Unable to load counselor workload analytics.", "info");
      }
    });

  document
    .getElementById("counselor-workload-reset")
    ?.addEventListener("click", async () => {
      const startDate = document.getElementById(
        "counselor-workload-start-date",
      );
      const endDate = document.getElementById("counselor-workload-end-date");
      if (startDate) startDate.value = "";
      if (endDate) endDate.value = "";

      try {
        await loadCounselorWorkloadAnalytics();
      } catch (error) {
        console.error(error);
        createToast("Unable to load counselor workload analytics.", "info");
      }
    });
}

function renderFlaggedCaseAnalytics() {
  const analytics = flaggedCaseAnalytics;
  if (!analytics) return;

  const values = [
    ["flagged-case-analytics-total", analytics.total_flagged_cases],
    [
      "flagged-case-analytics-pending",
      analytics.pending_flagged_case_reviews,
    ],
    ["flagged-case-analytics-reviewed", analytics.reviewed_flagged_cases],
    ["flagged-case-analytics-referrals", analytics.referral_count],
    ["flagged-case-analytics-interventions", analytics.intervention_count],
    [
      "flagged-case-analytics-confidential",
      analytics.current_confidential_case_count,
    ],
  ];

  values.forEach(([elementId, value]) => {
    const element = document.getElementById(elementId);
    if (element) element.textContent = String(value || 0);
  });

  const trends = analytics.escalation_trends || {};
  renderAnalyticsRows(
    "flagged-case-analytics-statuses",
    analytics.persisted_case_status_distribution || [],
    "status",
    "No flagged-case records for this period.",
  );
  renderAnalyticsRows(
    "flagged-case-analytics-daily",
    trends.daily || [],
    "date",
    "No escalation records for this period.",
  );
  renderAnalyticsRows(
    "flagged-case-analytics-weekly",
    trends.weekly || [],
    "week",
    "No escalation records for this period.",
  );
  renderAnalyticsRows(
    "flagged-case-analytics-monthly",
    trends.monthly || [],
    "month",
    "No escalation records for this period.",
  );
}

async function loadFlaggedCaseAnalytics() {
  const startDate = document.getElementById(
    "flagged-case-analytics-start-date",
  )?.value;
  const endDate = document.getElementById(
    "flagged-case-analytics-end-date",
  )?.value;
  const query = new URLSearchParams();
  if (startDate) query.set("start_date", startDate);
  if (endDate) query.set("end_date", endDate);

  const suffix = query.size ? `?${query.toString()}` : "";
  const result = await fetchJson(
    `${API_BASE}/api/dashboard/flagged-cases/analytics${suffix}`,
  );
  flaggedCaseAnalytics = result.data || null;
  renderFlaggedCaseAnalytics();
}

function bindFlaggedCaseAnalyticsFilters() {
  document
    .getElementById("flagged-case-analytics-apply")
    ?.addEventListener("click", async () => {
      try {
        await loadFlaggedCaseAnalytics();
      } catch (error) {
        console.error(error);
        createToast("Unable to load flagged case analytics.", "info");
      }
    });

  document
    .getElementById("flagged-case-analytics-reset")
    ?.addEventListener("click", async () => {
      const startDate = document.getElementById(
        "flagged-case-analytics-start-date",
      );
      const endDate = document.getElementById(
        "flagged-case-analytics-end-date",
      );
      if (startDate) startDate.value = "";
      if (endDate) endDate.value = "";

      try {
        await loadFlaggedCaseAnalytics();
      } catch (error) {
        console.error(error);
        createToast("Unable to load flagged case analytics.", "info");
      }
    });
}

async function loadAppointmentAnalytics() {
  const startDate = document.getElementById("appointment-analytics-start-date")?.value;
  const endDate = document.getElementById("appointment-analytics-end-date")?.value;
  const query = new URLSearchParams();
  if (startDate) query.set("start_date", startDate);
  if (endDate) query.set("end_date", endDate);

  const suffix = query.size ? `?${query.toString()}` : "";
  const result = await fetchJson(
    `${API_BASE}/api/dashboard/appointments/analytics${suffix}`,
  );
  appointmentAnalytics = result.data || null;
  renderAppointmentAnalytics();
}

function bindAppointmentAnalyticsFilters() {
  document
    .getElementById("appointment-analytics-apply")
    ?.addEventListener("click", async () => {
      try {
        await loadAppointmentAnalytics();
      } catch (error) {
        console.error(error);
        createToast("Unable to load appointment analytics.", "info");
      }
    });

  document
    .getElementById("appointment-analytics-reset")
    ?.addEventListener("click", async () => {
      const startDate = document.getElementById("appointment-analytics-start-date");
      const endDate = document.getElementById("appointment-analytics-end-date");
      if (startDate) startDate.value = "";
      if (endDate) endDate.value = "";

      try {
        await loadAppointmentAnalytics();
      } catch (error) {
        console.error(error);
        createToast("Unable to load appointment analytics.", "info");
      }
    });

}

function getSearchedAppointments() {
  const appointments = window.backendAppointments || [];
  const query = document
    .getElementById("appointment-search-input")
    ?.value.trim()
    .toLowerCase();

  if (!query) {
    return appointments;
  }

  return appointments.filter((appointment) =>
    [appointment.student, appointment.studentNumber].some((value) =>
      String(value || "")
        .toLowerCase()
        .includes(query),
    ),
  );
}

function renderSearchedAppointmentSections() {
  renderAppointmentRequests();
  renderTodaysAppointments();
  renderAppointmentHistory();
}

function bindAppointmentSearch() {
  const input = document.getElementById("appointment-search-input");

  input?.addEventListener("input", renderSearchedAppointmentSections);
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
      appointment.status === "completed" &&
      normalizeDate(appointment.date) === today,
  ).length;

  document.getElementById("appointments-today-count").textContent = totalToday;

  document.getElementById("pending-appointments-count").textContent =
    pendingCount;

  document.getElementById("completed-appointments-count").textContent =
    completedToday;
}

function renderAppointmentRequests() {
  const appointments = getSearchedAppointments();

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
  const appointments = getSearchedAppointments();

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

  // Manual appointments are created with a "confirmed" status,
  // so no special-case filtering is required here.
  const confirmedAppointments = appointments.filter(
    (appointment) => appointment.status === "confirmed",
  );

  const container = document.getElementById("todays-appointments-container");

  if (!container) return;

  container.innerHTML = "";

  if (!confirmedAppointments.length) {
    container.innerHTML = `
      <p class="sub">
        No confirmed appointments.
      </p>
    `;

    return;
  }

  confirmedAppointments.forEach((appointment) => {
    const card = createTodaysAppointmentCard(appointment);
    container.appendChild(card);
  });
}

function renderAppointmentHistory() {
  const appointments = getSearchedAppointments();

  const historyAppointments = appointments.filter((appointment) =>
    ["completed", "cancelled", "rejected"].includes(appointment.status),
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

        const name = document.createElement("strong");
        name.textContent = student.full_name || "Unknown";
        const detail = document.createElement("small");
        detail.textContent = `${student.student_number || "—"} • ${student.program || "—"}`;
        option.append(name, document.createElement("br"), detail);

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
  const text = getAppointmentCardText(appointment);
  card.innerHTML = `
    <div class="appointment-card-header">
      <div>
        <h4>${text.student}</h4>
        <p class="sub">${text.studentNumber}</p>
      </div>
      ${badgeHTML(appointment.status)}
    </div>
    <div class="appointment-card-body">
      <div class="appointment-meta-grid">
        <div><span>Date</span><strong>${text.date}</strong></div>
        <div><span>Time</span><strong>${text.time}</strong></div>
        <div><span>Mode</span><strong>${text.mode}</strong></div>
        <div><span>Source</span><strong>${text.source}</strong></div>
      </div>
      <p><strong>${text.category}</strong></p>
    </div>
    <div class="appointment-card-footer">
      <button class="btn btn-outline appointment-view-btn">
        View Details
      </button>
      <button
          class="btn btn-primary appointment-confirm-btn"
      >
          Confirm
      </button>
      <button
          class="btn btn-outline appointment-cancel-btn"
      >
          Cancel
      </button>
    </div>
  `;
  const confirmButton = card.querySelector(".appointment-confirm-btn");
  const cancelButton = card.querySelector(".appointment-cancel-btn");
  const viewButton = card.querySelector(".appointment-view-btn");
  viewButton?.addEventListener("click", () => {
    openAppointmentDetails(appointment);
  });
  confirmButton?.addEventListener("click", () => {
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
  const text = getAppointmentCardText(appointment);
  card.innerHTML = `
    <div class="appointment-card-header">
      <div>
        <h4>${text.student}</h4>
        <p class="sub">${text.studentNumber}</p>
      </div>
      ${badgeHTML(appointment.status)}
    </div>
    <div class="appointment-card-body">
      <div class="appointment-meta-grid">
        <div><span>Date</span><strong>${text.date}</strong></div>
        <div><span>Time</span><strong>${text.time}</strong></div>
        <div><span>Mode</span><strong>${text.mode}</strong></div>
        <div><span>Source</span><strong>${text.source}</strong></div>
      </div>
      <p><strong>${text.category}</strong></p>
    </div>
    <div class="appointment-card-footer">
      <button class="btn btn-outline appointment-view-btn">
        View Details
      </button>
      <button
        class="btn btn-primary appointment-complete-btn"
      >
        Complete
      </button>
      <button
        class="btn btn-outline appointment-cancel-btn"
      >
        Cancel
      </button>
    </div>
  `;
  const completeButton = card.querySelector(".appointment-complete-btn");
  const cancelButton = card.querySelector(".appointment-cancel-btn");
  const viewButton = card.querySelector(".appointment-view-btn");
  viewButton?.addEventListener("click", () => {
    openAppointmentDetails(appointment);
  });
  completeButton?.addEventListener("click", () => {
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
  const text = getAppointmentCardText(appointment);
  card.innerHTML = `
    <div class="appointment-card-header">
      <div>
        <h4>${text.student}</h4>
        <p class="sub">${text.studentNumber}</p>
      </div>
      ${badgeHTML(appointment.status)}
    </div>
    <div class="appointment-card-body">
      <div class="appointment-meta-grid">
        <div><span>Date</span><strong>${text.date}</strong></div>
        <div><span>Time</span><strong>${text.time}</strong></div>
        <div><span>Mode</span><strong>${text.mode}</strong></div>
        <div><span>Source</span><strong>${text.source}</strong></div>
      </div>
      <p><strong>${text.category}</strong></p>
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

async function updateCounselorNotes(appointment, counselorNotes) {
  await fetchJson(`${API_BASE}/api/appointments/${appointment.id}/notes`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ counselor_notes: counselorNotes }),
  });

  appointment.counselorNotes = counselorNotes;
}

function createFlaggedAppointmentCaseCard(summary) {
  const card = document.createElement("div");

  card.className = "appointment-card";

  card.innerHTML = `
    <div class="appointment-card-header">
      <h4>${escapeHtml(summary.student)}</h4>
      <p class="sub">${escapeHtml(summary.studentId)}</p>
    </div>

    <div class="appointment-card-body">
      <p><strong>${escapeHtml(summary.category)}</strong></p>

      <p>
        Emotion:
        ${escapeHtml(capitalize(summary.emotion))}
      </p>

      <p>
        Recommendation:
        ${escapeHtml(summary.recommendation || "No recommendation available.")}
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
    switchView("flagged");
  });

  return card;
}

function createFaqBlock(title, question, answer) {
  const container = document.createElement("div");
  container.className = "faq-block";
  container.innerHTML = `
    <div class="faq-block-header">
      <div class="faq-title">${escapeHtml(title)}</div>
      <div class="faq-q">${escapeHtml(question)}</div>
    </div>
    <div class="faq-block-body">
      <textarea>${escapeHtml(answer || "")}</textarea>
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
    actions: "",
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
    actions:
      '<button class="btn btn-outline" data-dashboard-action="back">Back</button>',
  },

  reports: {
    title: "Reports",
    sub: "Review authorized aggregate analytics and export staff reports.",
    actions: '<div class="report-period-badge">This Month</div>',
  },
  settings: {
    title: "Settings & FAQ Management",
    sub: "Update chatbot responses, office details, categories, and escalation messages.",
    actions:
      '<button class="btn btn-primary" data-dashboard-action="save-settings">Save Changes</button>',
  },
  "case-details": {
    title: "Case Details",
    sub: "Review student concern, chatbot classification, and counselor action.",
    actions:
      '<button class="btn btn-outline" data-dashboard-action="back">Back to Dashboard</button>',
  },
  "appointment-details": {
    title: "Appointment Details",
    sub: "Review appointment information, manage its status, and record counselor notes.",
    actions:
      '<button class="btn btn-outline" data-dashboard-action="back">Back to Appointments</button>',
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
    confirmed: ["neutral", "Confirmed"],
    completed: ["resolved", "Completed"],
    cancelled: ["negative", "Cancelled"],
    rejected: ["negative", "Rejected"],
  };
  const [cls, label] = map[status] || ["pending", "Pending"];
  return `<span class="badge ${cls}">${label}</span>`;
}

function updateHeader(viewId) {
  const meta = viewMeta[viewId] || {};
  headerTitle.textContent = meta.title || "";
  headerSub.textContent = meta.sub || "";
  headerActions.innerHTML = meta.actions || "";

  headerActions
    .querySelector('[data-dashboard-action="back"]')
    ?.addEventListener("click", goBack);
  headerActions
    .querySelector('[data-dashboard-action="save-settings"]')
    ?.addEventListener("click", saveSettings);

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

function makeRow(inquiry) {
  const tr = document.createElement("tr");
  const actionsCell = "<td></td>";

  const preview = inquiry.summary
    ? inquiry.summary.length > 80
      ? inquiry.summary.slice(0, 80) + "..."
      : inquiry.summary
    : inquiry.message || "No preview available";

  tr.innerHTML = `
    <td>
      <div class="student-cell">
        <div class="student-avatar">${escapeHtml(initials(inquiry.student))}</div>
        <div>
          <div class="student-name">${escapeHtml(inquiry.student)}</div>
          <div class="student-id">${escapeHtml(inquiry.studentId)}</div>
        </div>
      </div>
    </td>
    <td>
      <div class="msg-preview">
        ${escapeHtml(preview)}
      </div>
    </td>
    <td>${escapeHtml(inquiry.category)}</td>
    <td>${badgeHTML(inquiry.status)}</td>
    <td class="time-cell">${escapeHtml(inquiry.time)}</td>
    ${actionsCell}
  `;

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
  renderFlaggedConversations();
  renderConversationTable("resolved-tbody", "resolved");
}

function appendTableCell(row, value) {
  const cell = document.createElement("td");
  cell.textContent = value;
  row.appendChild(cell);
}

function renderFlaggedConversations() {
  const tbody = document.getElementById("flagged-tbody");
  if (!tbody) return;

  tbody.replaceChildren();

  if (!flaggedConversations.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 6;
    cell.style.cssText = "text-align:center;color:var(--gray-400);padding:30px";
    cell.textContent = "No flagged conversations found.";
    row.appendChild(cell);
    tbody.appendChild(row);
    return;
  }

  flaggedConversations.forEach((conversation) => {
    const row = document.createElement("tr");
    appendTableCell(row, "Confidential conversation");
    appendTableCell(row, conversation.summary);
    appendTableCell(row, conversation.category);
    appendTableCell(
      row,
      conversation.status === "reviewed" ? "Reviewed" : "Pending review",
    );
    appendTableCell(
      row,
      conversation.createdAt
        ? conversation.createdAt.toLocaleString()
        : "Unavailable",
    );

    const actionCell = document.createElement("td");
    const viewButton = document.createElement("button");
    viewButton.type = "button";
    viewButton.className = "action-link";
    viewButton.textContent = "View";
    viewButton.addEventListener("click", () => {
      openFlaggedConversationDetails(conversation);
    });
    actionCell.appendChild(viewButton);
    row.appendChild(actionCell);
    tbody.appendChild(row);
  });
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
    const createdAt = summary.createdAt
      ? summary.createdAt.toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
          year: "numeric",
        })
      : "—";

    tr.innerHTML = `
      <td>${escapeHtml(summary.student)}</td>
      <td>${escapeHtml(summary.category)}</td>
      <td>${escapeHtml(capitalize(summary.emotion))}</td>
      <td>${escapeHtml(createdAt)}</td>
      <td>
        <button
          class="action-link view-summary-btn"
          data-id="${escapeHtml(summary.id)}"
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
  renderDashboardOverview();
}

function overviewValue(elementId, value) {
  const element = document.getElementById(elementId);
  if (element) element.textContent = String(value || 0);
}

function latestTrendRow(trends) {
  const rows = trends || [];
  return rows.length ? rows[rows.length - 1] : null;
}

function renderDashboardOverview() {
  const reports = reportsAnalytics;
  if (!reports) return;

  const appointment = reports.appointment || {};
  const chatbot = reports.chatbot || {};
  const workload = reports.workload || {};
  const flaggedCases = reports.flaggedCases || {};

  overviewValue(
    "reports-overview-appointments",
    appointment.total_appointments,
  );
  overviewValue(
    "reports-overview-pending-cases",
    flaggedCases.pending_flagged_case_reviews,
  );
  overviewValue(
    "reports-overview-chatbot-messages",
    chatbot.total_chatbot_messages,
  );
  overviewValue(
    "reports-overview-active-referrals",
    workload.active_referral_count,
  );

  appendReportRows("reports-overview-appointment-summary", [
    ["Total appointments", appointment.total_appointments || 0],
    ...(appointment.status_distribution || []).map((item) => [
      `Persisted appointment status: ${item.status}`,
      item.count,
    ]),
  ]);
  appendReportRows("reports-overview-chatbot-summary", [
    ["Total chatbot messages", chatbot.total_chatbot_messages || 0],
    ["Conversation finalizations", chatbot.conversation_finalization_count || 0],
    ["Escalations", chatbot.escalation_count || 0],
  ]);
  appendReportRows("reports-overview-workload-summary", [
    ["Authorized appointments", workload.authorized_appointment_count || 0],
    ["Pending appointments", workload.pending_appointment_count || 0],
    ["Confirmed appointments", workload.confirmed_appointment_count || 0],
    ["Completed appointments", workload.completed_appointment_count || 0],
    ["Active referrals", workload.active_referral_count || 0],
    ["Active interventions", workload.active_intervention_count || 0],
    ["Completed interventions", workload.completed_intervention_count || 0],
  ]);
  appendReportRows("reports-overview-flagged-case-summary", [
    ["Total flagged cases", flaggedCases.total_flagged_cases || 0],
    [
      "Pending flagged-case reviews",
      flaggedCases.pending_flagged_case_reviews || 0,
    ],
    ["Reviewed flagged cases", flaggedCases.reviewed_flagged_cases || 0],
    ["Current confidential cases", flaggedCases.current_confidential_case_count || 0],
  ]);

  const recentActivity = [
    ["Appointment activity", latestTrendRow(appointment.daily_trends)],
    [
      "Chatbot message activity",
      latestTrendRow((chatbot.message_volume || {}).daily),
    ],
    [
      "Flagged-case escalation activity",
      latestTrendRow((flaggedCases.escalation_trends || {}).daily),
    ],
  ]
    .filter(([, trend]) => trend)
    .map(([label, trend]) => [`${label}: ${trend.date}`, trend.count]);
  appendReportRows("reports-overview-recent-activity", recentActivity);
}

function navigateOverview(target) {
  const destinations = {
    appointment: { view: "appointments", panelId: "appointment-analytics-panel" },
    chatbot: { view: "reports", panelId: "chatbot-analytics-panel" },
    workload: { view: "reports", panelId: "counselor-workload-panel" },
    "flagged-cases": { view: "reports", panelId: "flagged-case-analytics-panel" },
  };
  const destination = destinations[target];
  if (!destination) return;

  switchView(destination.view);
  document.getElementById(destination.panelId)?.scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
}

function bindDashboardOverviewNavigation() {
  document.querySelectorAll("[data-overview-target]").forEach((button) => {
    button.addEventListener("click", () => {
      navigateOverview(button.dataset.overviewTarget);
    });
  });
}

function appendReportRows(containerId, rows) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.replaceChildren();

  if (!rows.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 2;
    cell.textContent = "No aggregate data for this period.";
    row.appendChild(cell);
    container.appendChild(row);
    return;
  }

  rows.forEach(([labelText, value]) => {
    const row = document.createElement("tr");
    const label = document.createElement("td");
    const count = document.createElement("td");
    label.textContent = labelText;
    count.textContent = String(value);
    row.append(label, count);
    container.appendChild(row);
  });
}

function trendReportRows(label, trends) {
  return (trends || []).map((item) => [
    `${label}: ${item.date || item.week || item.month}`,
    item.count,
  ]);
}

function renderCombinedReports() {
  const reports = reportsAnalytics;
  if (!reports) return;

  const appointment = reports.appointment || {};
  const chatbot = reports.chatbot || {};
  const workload = reports.workload || {};
  const flaggedCases = reports.flaggedCases || {};

  appendReportRows("reports-appointment-rows", [
    ["Total appointments", appointment.total_appointments || 0],
    ...(appointment.status_distribution || []).map((item) => [
      `Status: ${item.status}`,
      item.count,
    ]),
    ...trendReportRows("Daily trend", appointment.daily_trends),
    ...trendReportRows("Weekly trend", appointment.weekly_trends),
    ...trendReportRows("Monthly trend", appointment.monthly_trends),
    ...(appointment.program_statistics || []).map((item) => [
      `Program: ${item.program}`,
      item.count,
    ]),
  ]);

  const chatbotVolume = chatbot.message_volume || {};
  appendReportRows("reports-chatbot-rows", [
    ["Total chatbot messages", chatbot.total_chatbot_messages || 0],
    ["Conversation finalizations", chatbot.conversation_finalization_count || 0],
    ["Escalations", chatbot.escalation_count || 0],
    [
      "Average finalized conversation length",
      chatbot.average_finalized_conversation_length ?? "—",
    ],
    ...(chatbot.persisted_emotion_result_distribution || []).map((item) => [
      `Persisted emotion result: ${item.emotion_result}`,
      item.count,
    ]),
    ...trendReportRows("Daily message volume", chatbotVolume.daily),
    ...trendReportRows("Weekly message volume", chatbotVolume.weekly),
    ...trendReportRows("Monthly message volume", chatbotVolume.monthly),
  ]);

  appendReportRows("reports-workload-rows", [
    ["Authorized appointments", workload.authorized_appointment_count || 0],
    ["Pending appointments", workload.pending_appointment_count || 0],
    ["Confirmed appointments", workload.confirmed_appointment_count || 0],
    ["Completed appointments", workload.completed_appointment_count || 0],
    ["Active referrals", workload.active_referral_count || 0],
    ["Active interventions", workload.active_intervention_count || 0],
    ["Completed interventions", workload.completed_intervention_count || 0],
    ...(workload.workload_by_program || []).map((item) => [
      `Authorized program: ${item.program}`,
      item.count,
    ]),
  ]);

  const escalationTrends = flaggedCases.escalation_trends || {};
  appendReportRows("reports-flagged-case-rows", [
    ["Total flagged cases", flaggedCases.total_flagged_cases || 0],
    [
      "Pending flagged-case reviews",
      flaggedCases.pending_flagged_case_reviews || 0,
    ],
    ["Reviewed flagged cases", flaggedCases.reviewed_flagged_cases || 0],
    ["Referrals", flaggedCases.referral_count || 0],
    ["Interventions", flaggedCases.intervention_count || 0],
    [
      "Current confidential cases",
      flaggedCases.current_confidential_case_count || 0,
    ],
    ...(flaggedCases.persisted_case_status_distribution || []).map((item) => [
      `Persisted case status: ${item.status}`,
      item.count,
    ]),
    ...trendReportRows("Daily escalation trend", escalationTrends.daily),
    ...trendReportRows("Weekly escalation trend", escalationTrends.weekly),
    ...trendReportRows("Monthly escalation trend", escalationTrends.monthly),
  ]);
}

function selectedReportDateRange() {
  return {
    startDate: document.getElementById("reports-start-date")?.value || "",
    endDate: document.getElementById("reports-end-date")?.value || "",
  };
}

function analyticsQuery(startDate, endDate) {
  const query = new URLSearchParams();
  if (startDate) query.set("start_date", startDate);
  if (endDate) query.set("end_date", endDate);
  return query.size ? `?${query.toString()}` : "";
}

async function loadCombinedReports() {
  const { startDate, endDate } = selectedReportDateRange();
  const suffix = analyticsQuery(startDate, endDate);
  const [appointment, chatbot, workload, flaggedCases] = await Promise.all([
    fetchJson(`${API_BASE}/api/dashboard/appointments/analytics${suffix}`),
    fetchJson(`${API_BASE}/api/dashboard/chatbot/analytics${suffix}`),
    fetchJson(`${API_BASE}/api/dashboard/counselor-workload${suffix}`),
    fetchJson(`${API_BASE}/api/dashboard/flagged-cases/analytics${suffix}`),
  ]);

  reportsAnalytics = {
    appointment: appointment.data || {},
    chatbot: chatbot.data || {},
    workload: workload.data || {},
    flaggedCases: flaggedCases.data || {},
  };
  renderCombinedReports();
  renderDashboardOverview();
}

function csvCell(value) {
  const text = String(value ?? "");
  const safeText = /^[=+\-@]/.test(text) ? `'${text}` : text;
  return `"${safeText.replaceAll('"', '""')}"`;
}

function reportCsvRows() {
  const reports = reportsAnalytics;
  if (!reports) return [];

  const { startDate, endDate } = selectedReportDateRange();
  const rows = [
    ["Report", "Generated at", "", new Date().toISOString()],
    ["Report", "Start date", "", startDate || "All records"],
    ["Report", "End date", "", endDate || "All records"],
    ["Section", "Metric", "Period", "Value"],
  ];
  const add = (section, metric, value, period = "") => {
    rows.push([section, metric, period, value]);
  };
  const addTrends = (section, metric, trends) => {
    (trends || []).forEach((item) => {
      add(section, metric, item.count, item.date || item.week || item.month);
    });
  };

  const appointment = reports.appointment || {};
  add("Appointment", "Total appointments", appointment.total_appointments || 0);
  (appointment.status_distribution || []).forEach((item) =>
    add("Appointment", "Persisted appointment status", item.count, item.status),
  );
  addTrends("Appointment", "Daily trend", appointment.daily_trends);
  addTrends("Appointment", "Weekly trend", appointment.weekly_trends);
  addTrends("Appointment", "Monthly trend", appointment.monthly_trends);
  (appointment.program_statistics || []).forEach((item) =>
    add("Appointment", "Program appointments", item.count, item.program),
  );

  const chatbot = reports.chatbot || {};
  add("Chatbot", "Total chatbot messages", chatbot.total_chatbot_messages || 0);
  add("Chatbot", "Conversation finalizations", chatbot.conversation_finalization_count || 0);
  add("Chatbot", "Escalations", chatbot.escalation_count || 0);
  add(
    "Chatbot",
    "Average finalized conversation length",
    chatbot.average_finalized_conversation_length ?? "",
  );
  (chatbot.persisted_emotion_result_distribution || []).forEach((item) =>
    add("Chatbot", "Persisted emotion result", item.count, item.emotion_result),
  );
  const chatbotVolume = chatbot.message_volume || {};
  addTrends("Chatbot", "Daily message volume", chatbotVolume.daily);
  addTrends("Chatbot", "Weekly message volume", chatbotVolume.weekly);
  addTrends("Chatbot", "Monthly message volume", chatbotVolume.monthly);

  const workload = reports.workload || {};
  [
    ["Authorized appointments", workload.authorized_appointment_count],
    ["Pending appointments", workload.pending_appointment_count],
    ["Confirmed appointments", workload.confirmed_appointment_count],
    ["Completed appointments", workload.completed_appointment_count],
    ["Active referrals", workload.active_referral_count],
    ["Active interventions", workload.active_intervention_count],
    ["Completed interventions", workload.completed_intervention_count],
  ].forEach(([metric, value]) => add("Counselor Workload", metric, value || 0));
  (workload.workload_by_program || []).forEach((item) =>
    add("Counselor Workload", "Authorized program appointments", item.count, item.program),
  );

  const flaggedCases = reports.flaggedCases || {};
  [
    ["Total flagged cases", flaggedCases.total_flagged_cases],
    ["Pending flagged-case reviews", flaggedCases.pending_flagged_case_reviews],
    ["Reviewed flagged cases", flaggedCases.reviewed_flagged_cases],
    ["Referrals", flaggedCases.referral_count],
    ["Interventions", flaggedCases.intervention_count],
    ["Current confidential cases", flaggedCases.current_confidential_case_count],
  ].forEach(([metric, value]) => add("Flagged Case", metric, value || 0));
  (flaggedCases.persisted_case_status_distribution || []).forEach((item) =>
    add("Flagged Case", "Persisted case status", item.count, item.status),
  );
  const escalationTrends = flaggedCases.escalation_trends || {};
  addTrends("Flagged Case", "Daily escalation trend", escalationTrends.daily);
  addTrends("Flagged Case", "Weekly escalation trend", escalationTrends.weekly);
  addTrends("Flagged Case", "Monthly escalation trend", escalationTrends.monthly);

  return rows;
}

function downloadReportsCsv() {
  const rows = reportCsvRows();
  if (!rows.length) {
    createToast("Load reports before downloading CSV.", "info");
    return;
  }

  const csv = rows.map((row) => row.map(csvCell).join(",")).join("\r\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.href = url;
  link.download = "guidance-analytics-report.csv";
  link.click();
  URL.revokeObjectURL(url);
}

function bindReportsControls() {
  document
    .getElementById("reports-apply")
    ?.addEventListener("click", async () => {
      try {
        await loadCombinedReports();
      } catch (error) {
        console.error(error);
        createToast("Unable to load reports.", "info");
      }
    });

  document
    .getElementById("reports-reset")
    ?.addEventListener("click", async () => {
      const startDate = document.getElementById("reports-start-date");
      const endDate = document.getElementById("reports-end-date");
      if (startDate) startDate.value = "";
      if (endDate) endDate.value = "";

      try {
        await loadCombinedReports();
      } catch (error) {
        console.error(error);
        createToast("Unable to load reports.", "info");
      }
    });

  document
    .getElementById("reports-export-csv")
    ?.addEventListener("click", downloadReportsCsv);
}

function updateFlaggedCount() {
  const count = flaggedConversations.length;
  const flaggedCount = document.getElementById("flagged-count");
  const statFlagged = document.getElementById("stat-flagged");
  const statFlagged2 = document.getElementById("stat-flagged-2");
  if (flaggedCount) flaggedCount.textContent = count;
  if (statFlagged) statFlagged.textContent = count;
  if (statFlagged2) statFlagged2.textContent = count;
}

function formatCaseNoteTimestamp(timestamp) {
  if (!timestamp) return "Timestamp unavailable";
  const date = new Date(timestamp);
  return Number.isNaN(date.getTime())
    ? "Timestamp unavailable"
    : date.toLocaleString();
}

function renderCaseNotes(notes, onEdit) {
  const list = document.getElementById("case-notes-list");
  if (!list) return;

  list.replaceChildren();
  if (!notes.length) {
    const empty = document.createElement("p");
    empty.className = "sub";
    empty.textContent = "No counselor notes have been added.";
    list.appendChild(empty);
    return;
  }

  notes.forEach((note) => {
    const entry = document.createElement("article");
    entry.className = "case-note-entry";

    const text = document.createElement("p");
    text.className = "case-note-text";
    text.textContent = note.note_text;

    const footer = document.createElement("div");
    footer.className = "case-note-footer";
    const timestamp = document.createElement("span");
    const createdAt = formatCaseNoteTimestamp(note.created_at);
    const updatedAt = formatCaseNoteTimestamp(note.updated_at);
    timestamp.textContent =
      note.created_at === note.updated_at
        ? `Created ${createdAt}`
        : `Created ${createdAt} · Updated ${updatedAt}`;
    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.className = "action-link";
    editButton.textContent = "Edit";
    editButton.addEventListener("click", () => onEdit(note));
    footer.append(timestamp, editButton);

    entry.append(text, footer);
    list.appendChild(entry);
  });
}

function formatReferralStatus(status) {
  return String(status || "pending")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function getReferralStatusBadgeClass(status) {
  const classes = {
    pending: "pending",
    in_progress: "neutral",
    completed: "resolved",
    cancelled: "negative",
  };
  return classes[status] || "pending";
}

function renderReferralHistory(history) {
  const list = document.createElement("ul");
  list.className = "referral-history";
  history.forEach((item) => {
    const entry = document.createElement("li");
    entry.textContent = `${formatReferralStatus(item.status)}: ${formatCaseNoteTimestamp(item.created_at)}`;
    list.appendChild(entry);
  });
  return list;
}

function renderReferralNotes(notes) {
  const list = document.createElement("ul");
  list.className = "referral-notes-history";
  notes.forEach((note) => {
    const entry = document.createElement("li");
    entry.textContent = `${formatCaseNoteTimestamp(note.created_at)}: ${note.note_text}`;
    list.appendChild(entry);
  });
  return list;
}

function renderReferrals(referrals, onStatusChange, onAddNote) {
  const list = document.getElementById("case-referrals-list");
  if (!list) return;

  list.replaceChildren();
  if (!referrals.length) {
    const empty = document.createElement("p");
    empty.className = "sub";
    empty.textContent = "No internal referrals have been created.";
    list.appendChild(empty);
    return;
  }

  referrals.forEach((referral) => {
    const entry = document.createElement("article");
    entry.className = "referral-entry";

    const header = document.createElement("div");
    header.className = "referral-entry-header";
    const destination = document.createElement("h5");
    destination.textContent = referral.destination;
    const status = document.createElement("span");
    status.className = `badge ${getReferralStatusBadgeClass(referral.status)}`;
    status.textContent = formatReferralStatus(referral.status);
    header.append(destination, status);

    const reason = document.createElement("p");
    reason.textContent = referral.referral_reason;

    const footer = document.createElement("div");
    footer.className = "referral-entry-footer";
    const timestamps = document.createElement("span");
    timestamps.textContent =
      referral.created_at === referral.updated_at
        ? `Created ${formatCaseNoteTimestamp(referral.created_at)}`
        : `Created ${formatCaseNoteTimestamp(referral.created_at)} · Updated ${formatCaseNoteTimestamp(referral.updated_at)}`;
    footer.appendChild(timestamps);

    const statusControl = document.createElement("div");
    statusControl.className = "referral-status-control";
    const statusLabel = document.createElement("label");
    statusLabel.textContent = "Referral Status";
    const statusSelect = document.createElement("select");
    ["pending", "in_progress", "completed", "cancelled"].forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = formatReferralStatus(value);
      option.selected = value === referral.status;
      statusSelect.appendChild(option);
    });
    statusSelect.addEventListener("change", () => {
      onStatusChange(referral, statusSelect.value);
    });
    statusControl.append(statusLabel, statusSelect);

    const historyHeading = document.createElement("strong");
    historyHeading.textContent = "Status History";
    const notesHeading = document.createElement("strong");
    notesHeading.textContent = "Referral Notes";

    const noteEditor = document.createElement("div");
    noteEditor.className = "referral-note-editor";
    const noteInput = document.createElement("textarea");
    noteInput.placeholder = "Add a confidential referral note.";
    const addNoteButton = document.createElement("button");
    addNoteButton.type = "button";
    addNoteButton.className = "btn btn-outline btn-sm";
    addNoteButton.textContent = "Add Referral Note";
    addNoteButton.disabled = true;
    addNoteButton.classList.add("disabled");
    noteInput.addEventListener("input", () => {
      const empty = !noteInput.value.trim();
      addNoteButton.disabled = empty;
      addNoteButton.classList.toggle("disabled", empty);
    });
    addNoteButton.addEventListener("click", () => {
      const noteText = noteInput.value.trim();
      if (noteText) onAddNote(referral, noteText);
    });
    noteEditor.append(noteInput, addNoteButton);

    entry.append(
      header,
      reason,
      footer,
      statusControl,
      historyHeading,
      renderReferralHistory(referral.status_history || []),
      notesHeading,
      renderReferralNotes(referral.notes || []),
      noteEditor,
    );
    list.appendChild(entry);
  });
}

function formatInterventionProgress(progressStatus) {
  return String(progressStatus || "planned")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function getInterventionProgressBadgeClass(progressStatus) {
  const classes = {
    planned: "pending",
    ongoing: "neutral",
    completed: "resolved",
    discontinued: "negative",
  };
  return classes[progressStatus] || "pending";
}

function renderInterventionHistory(history) {
  const list = document.createElement("ul");
  list.className = "intervention-history";
  history.forEach((item) => {
    const entry = document.createElement("li");
    const progress = formatInterventionProgress(item.progress_status);
    const timestamp = formatCaseNoteTimestamp(item.created_at);
    entry.textContent = item.outcome
      ? `${progress}: ${timestamp}. Outcome: ${item.outcome}`
      : `${progress}: ${timestamp}`;
    list.appendChild(entry);
  });
  return list;
}

function renderInterventions(interventions, onProgressChange, onOutcome) {
  const list = document.getElementById("case-interventions-list");
  if (!list) return;

  list.replaceChildren();
  if (!interventions.length) {
    const empty = document.createElement("p");
    empty.className = "sub";
    empty.textContent = "No confidential interventions have been created.";
    list.appendChild(empty);
    return;
  }

  interventions.forEach((intervention) => {
    const entry = document.createElement("article");
    entry.className = "intervention-entry";
    const isTerminal = ["completed", "discontinued"].includes(
      intervention.progress_status,
    );
    const hasOutcome = Boolean(intervention.outcome);

    const header = document.createElement("div");
    header.className = "intervention-entry-header";
    const type = document.createElement("h5");
    type.textContent = intervention.intervention_type;
    const status = document.createElement("span");
    status.className = `badge ${getInterventionProgressBadgeClass(intervention.progress_status)}`;
    status.textContent = formatInterventionProgress(
      intervention.progress_status,
    );
    header.append(type, status);

    const objective = document.createElement("p");
    objective.textContent = intervention.objective;
    const footer = document.createElement("div");
    footer.className = "intervention-entry-footer";
    const timestamps = document.createElement("span");
    timestamps.textContent =
      intervention.created_at === intervention.updated_at
        ? `Created ${formatCaseNoteTimestamp(intervention.created_at)}`
        : `Created ${formatCaseNoteTimestamp(intervention.created_at)} · Updated ${formatCaseNoteTimestamp(intervention.updated_at)}`;
    footer.appendChild(timestamps);

    const progressControl = document.createElement("div");
    progressControl.className = "intervention-progress-control";
    const progressLabel = document.createElement("label");
    progressLabel.textContent = "Progress";
    const progressSelect = document.createElement("select");
    ["planned", "ongoing", "completed", "discontinued"].forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = formatInterventionProgress(value);
      option.selected = value === intervention.progress_status;
      progressSelect.appendChild(option);
    });
    progressSelect.disabled = hasOutcome;
    progressSelect.addEventListener("change", () => {
      onProgressChange(intervention, progressSelect.value);
    });
    progressControl.append(progressLabel, progressSelect);

    const completeButton = document.createElement("button");
    completeButton.type = "button";
    completeButton.className = "btn btn-outline btn-sm";
    completeButton.textContent = "Mark Completed";
    completeButton.hidden = isTerminal || hasOutcome;
    completeButton.addEventListener("click", () => {
      onProgressChange(intervention, "completed");
    });

    const historyHeading = document.createElement("strong");
    historyHeading.textContent = "Intervention History";

    entry.append(
      header,
      objective,
      footer,
      progressControl,
      completeButton,
      historyHeading,
      renderInterventionHistory(intervention.history || []),
    );

    if (hasOutcome) {
      const outcomeHeading = document.createElement("strong");
      outcomeHeading.textContent = "Outcome";
      const outcome = document.createElement("p");
      outcome.textContent = intervention.outcome;
      entry.append(outcomeHeading, outcome);
    } else if (isTerminal) {
      const outcomeEditor = document.createElement("div");
      outcomeEditor.className = "intervention-outcome-editor";
      const outcomeInput = document.createElement("textarea");
      outcomeInput.placeholder =
        "Record the confidential intervention outcome.";
      const outcomeButton = document.createElement("button");
      outcomeButton.type = "button";
      outcomeButton.className = "btn btn-primary btn-sm";
      outcomeButton.textContent = "Record Outcome";
      outcomeButton.disabled = true;
      outcomeButton.classList.add("disabled");
      outcomeInput.addEventListener("input", () => {
        const empty = !outcomeInput.value.trim();
        outcomeButton.disabled = empty;
        outcomeButton.classList.toggle("disabled", empty);
      });
      outcomeButton.addEventListener("click", () => {
        const outcome = outcomeInput.value.trim();
        if (outcome) onOutcome(intervention, outcome);
      });
      outcomeEditor.append(outcomeInput, outcomeButton);
      entry.appendChild(outcomeEditor);
    }

    list.appendChild(entry);
  });
}

function formatConfidentialityStatus(confidentialityStatus) {
  return confidentialityStatus === "confidential"
    ? "Confidential"
    : "Not Confidential";
}

function renderCaseConfidentiality(confidentiality) {
  const current = document.getElementById("case-confidentiality-current");
  if (!current) return;

  current.replaceChildren();
  const status = document.createElement("span");
  status.className = `badge ${
    confidentiality.confidentiality_status === "confidential"
      ? "negative"
      : "resolved"
  }`;
  status.textContent = formatConfidentialityStatus(
    confidentiality.confidentiality_status,
  );
  current.appendChild(status);

  if (confidentiality.confidentiality_reason) {
    const reason = document.createElement("p");
    reason.textContent = confidentiality.confidentiality_reason;
    current.appendChild(reason);
  }

  if (confidentiality.history?.length) {
    const historyHeading = document.createElement("strong");
    historyHeading.textContent = "Confidentiality History";
    const history = document.createElement("ul");
    history.className = "case-confidentiality-history";
    confidentiality.history.forEach((item) => {
      const entry = document.createElement("li");
      const timestamp = formatCaseNoteTimestamp(item.created_at);
      const reason = item.confidentiality_reason
        ? ` Reason: ${item.confidentiality_reason}`
        : "";
      entry.textContent = `${formatConfidentialityStatus(item.confidentiality_status)}: ${timestamp}.${reason}`;
      history.appendChild(entry);
    });
    current.append(historyHeading, history);
  }
}

async function openFlaggedConversationDetails(conversation) {
  try {
    const response = await fetchJson(
      `${API_BASE}/api/flagged-conversations/${conversation.id}`,
    );
    const detail = response.data;
    const reviewButton = document.getElementById("case-resolve-btn");
    const pendingButton = document.getElementById("case-pending-btn");
    const notesCard = document.querySelector(".staff-notes-card");
    const notesInput = document.getElementById("case-notes-input");
    const saveNotesButton = document.getElementById("save-notes-btn");
    const referralsCard = document.getElementById("case-referrals-card");
    const referralDestination = document.getElementById("referral-destination");
    const referralReason = document.getElementById("referral-reason");
    const referralNote = document.getElementById("referral-note");
    const createReferralButton = document.getElementById("create-referral-btn");
    const interventionsCard = document.getElementById(
      "case-interventions-card",
    );
    const interventionType = document.getElementById("intervention-type");
    const interventionObjective = document.getElementById(
      "intervention-objective",
    );
    const createInterventionButton = document.getElementById(
      "create-intervention-btn",
    );
    const confidentialityCard = document.getElementById(
      "case-confidentiality-card",
    );
    const confidentialityReason = document.getElementById(
      "case-confidentiality-reason",
    );
    const markConfidentialButton = document.getElementById(
      "mark-case-confidential-btn",
    );
    const removeConfidentialityButton = document.getElementById(
      "remove-case-confidential-btn",
    );
    const notesResponse = await fetchJson(
      `${API_BASE}/api/flagged-conversations/${conversation.id}/notes`,
    );
    const notes = notesResponse.data?.items || [];
    const referralsResponse = await fetchJson(
      `${API_BASE}/api/flagged-conversations/${conversation.id}/referrals`,
    );
    const referrals = referralsResponse.data?.items || [];
    const interventionsResponse = await fetchJson(
      `${API_BASE}/api/flagged-conversations/${conversation.id}/interventions`,
    );
    const interventions = interventionsResponse.data?.items || [];
    const confidentialityResponse = await fetchJson(
      `${API_BASE}/api/flagged-conversations/${conversation.id}/confidentiality`,
    );
    let confidentiality = confidentialityResponse.data;
    let editingNoteId = null;

    document.getElementById("case-avatar").textContent = "FC";
    document.getElementById("case-name").textContent = "Flagged Conversation";
    document.getElementById("case-meta").textContent =
      "Confidential staff conversation record";
    document.getElementById("case-message").textContent = detail.summary;
    document.getElementById("case-category").textContent =
      detail.primary_concern || "General inquiry";
    document.getElementById("case-emotion").textContent = capitalize(
      detail.emotion_results || "neutral",
    );
    document.getElementById("case-time").textContent = detail.created_at
      ? new Date(detail.created_at).toLocaleString()
      : "Unavailable";
    document.getElementById("case-recommendation").textContent =
      detail.recommendations || "No recommendation available.";
    document.getElementById("case-total-messages").textContent = String(
      detail.total_messages || 0,
    );
    document.getElementById("case-student-messages").textContent =
      "Not retained";
    document.getElementById("case-ai-messages").textContent = "Not retained";
    document.getElementById("case-escalation-status").textContent =
      detail.escalation_status === "reviewed" ? "Reviewed" : "Pending review";
    document.getElementById("case-escalation-reason").textContent =
      detail.escalation_reason || "AI safety escalation.";
    document.getElementById("case-status-label").textContent =
      detail.escalation_status === "reviewed" ? "Reviewed" : "Pending review";

    const badge = document.getElementById("case-badge");
    badge.className =
      detail.escalation_status === "reviewed"
        ? "badge resolved"
        : "badge negative";
    badge.textContent =
      detail.escalation_status === "reviewed" ? "Reviewed" : "Pending review";

    pendingButton.hidden = true;
    notesCard.hidden = false;
    referralsCard.hidden = false;
    interventionsCard.hidden = false;
    confidentialityCard.hidden = false;
    reviewButton.textContent = "Mark as Reviewed";
    reviewButton.disabled = detail.escalation_status === "reviewed";
    reviewButton.classList.toggle("disabled", reviewButton.disabled);
    reviewButton.onclick = async () => {
      try {
        const reviewed = await fetchJson(
          `${API_BASE}/api/flagged-conversations/${conversation.id}/review`,
          { method: "PATCH" },
        );
        conversation.status = reviewed.data.escalation_status;
        renderFlaggedConversations();
        updateFlaggedCount();
        await openFlaggedConversationDetails(conversation);
        createToast("Flagged conversation marked as reviewed.", "success");
      } catch (error) {
        console.error(error);
        createToast("Unable to mark flagged conversation as reviewed.", "info");
      }
    };

    function resetNoteEditor() {
      editingNoteId = null;
      notesInput.value = "";
      saveNotesButton.textContent = "Add Note";
      saveNotesButton.disabled = true;
      saveNotesButton.classList.add("disabled");
    }

    function startEditingNote(note) {
      editingNoteId = note.id;
      notesInput.value = note.note_text;
      saveNotesButton.textContent = "Update Note";
      saveNotesButton.disabled = false;
      saveNotesButton.classList.remove("disabled");
      notesInput.focus();
    }

    notesInput.oninput = () => {
      const empty = !notesInput.value.trim();
      saveNotesButton.disabled = empty;
      saveNotesButton.classList.toggle("disabled", empty);
    };
    saveNotesButton.onclick = async () => {
      const noteText = notesInput.value.trim();
      if (!noteText) return;

      try {
        const isEditing = editingNoteId !== null;
        const endpoint = isEditing
          ? `${API_BASE}/api/flagged-conversations/${conversation.id}/notes/${editingNoteId}`
          : `${API_BASE}/api/flagged-conversations/${conversation.id}/notes`;
        const response = await fetchJson(endpoint, {
          method: isEditing ? "PATCH" : "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ note_text: noteText }),
        });
        const savedNote = response.data;
        const index = notes.findIndex((note) => note.id === savedNote.id);
        if (index >= 0) {
          notes[index] = savedNote;
        } else {
          notes.push(savedNote);
        }
        renderCaseNotes(notes, startEditingNote);
        resetNoteEditor();
        createToast(
          isEditing ? "Counselor note updated." : "Counselor note added.",
          "success",
        );
      } catch (error) {
        console.error(error);
        createToast("Unable to save counselor note.", "info");
      }
    };

    renderCaseNotes(notes, startEditingNote);
    resetNoteEditor();

    function resetReferralEditor() {
      referralDestination.value = "";
      referralReason.value = "";
      referralNote.value = "";
      createReferralButton.disabled = true;
      createReferralButton.classList.add("disabled");
    }

    function updateReferralButton() {
      const incomplete =
        !referralDestination.value || !referralReason.value.trim();
      createReferralButton.disabled = incomplete;
      createReferralButton.classList.toggle("disabled", incomplete);
    }

    async function replaceReferral(savedReferral) {
      const index = referrals.findIndex(
        (referral) => referral.id === savedReferral.id,
      );
      if (index >= 0) {
        referrals[index] = savedReferral;
      } else {
        referrals.push(savedReferral);
      }
      renderReferrals(referrals, updateReferralStatus, addReferralNote);
    }

    async function updateReferralStatus(referral, status) {
      try {
        const response = await fetchJson(
          `${API_BASE}/api/flagged-conversations/${conversation.id}/referrals/${referral.id}/status`,
          {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status }),
          },
        );
        await replaceReferral(response.data);
        createToast("Referral status updated.", "success");
      } catch (error) {
        console.error(error);
        createToast("Unable to update referral status.", "info");
      }
    }

    async function addReferralNote(referral, noteText) {
      try {
        const response = await fetchJson(
          `${API_BASE}/api/flagged-conversations/${conversation.id}/referrals/${referral.id}/notes`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ note_text: noteText }),
          },
        );
        await replaceReferral(response.data);
        createToast("Referral note added.", "success");
      } catch (error) {
        console.error(error);
        createToast("Unable to add referral note.", "info");
      }
    }

    referralDestination.onchange = updateReferralButton;
    referralReason.oninput = updateReferralButton;
    createReferralButton.onclick = async () => {
      if (createReferralButton.disabled) return;
      try {
        const response = await fetchJson(
          `${API_BASE}/api/flagged-conversations/${conversation.id}/referrals`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              destination: referralDestination.value,
              referral_reason: referralReason.value.trim(),
              note_text: referralNote.value.trim(),
            }),
          },
        );
        await replaceReferral(response.data);
        resetReferralEditor();
        createToast("Referral created.", "success");
      } catch (error) {
        console.error(error);
        createToast("Unable to create referral.", "info");
      }
    };

    renderReferrals(referrals, updateReferralStatus, addReferralNote);
    resetReferralEditor();

    function resetInterventionEditor() {
      interventionType.value = "";
      interventionObjective.value = "";
      createInterventionButton.disabled = true;
      createInterventionButton.classList.add("disabled");
    }

    function updateInterventionButton() {
      const incomplete =
        !interventionType.value || !interventionObjective.value.trim();
      createInterventionButton.disabled = incomplete;
      createInterventionButton.classList.toggle("disabled", incomplete);
    }

    async function replaceIntervention(savedIntervention) {
      const index = interventions.findIndex(
        (intervention) => intervention.id === savedIntervention.id,
      );
      if (index >= 0) {
        interventions[index] = savedIntervention;
      } else {
        interventions.push(savedIntervention);
      }
      renderInterventions(
        interventions,
        updateInterventionProgress,
        recordInterventionOutcome,
      );
    }

    async function updateInterventionProgress(intervention, progressStatus) {
      try {
        const response = await fetchJson(
          `${API_BASE}/api/flagged-conversations/${conversation.id}/interventions/${intervention.id}/progress`,
          {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ progress_status: progressStatus }),
          },
        );
        await replaceIntervention(response.data);
        createToast("Intervention progress updated.", "success");
      } catch (error) {
        console.error(error);
        createToast("Unable to update intervention progress.", "info");
      }
    }

    async function recordInterventionOutcome(intervention, outcome) {
      try {
        const response = await fetchJson(
          `${API_BASE}/api/flagged-conversations/${conversation.id}/interventions/${intervention.id}/outcome`,
          {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ outcome }),
          },
        );
        await replaceIntervention(response.data);
        createToast("Intervention outcome recorded.", "success");
      } catch (error) {
        console.error(error);
        createToast("Unable to record intervention outcome.", "info");
      }
    }

    interventionType.onchange = updateInterventionButton;
    interventionObjective.oninput = updateInterventionButton;
    createInterventionButton.onclick = async () => {
      if (createInterventionButton.disabled) return;
      try {
        const response = await fetchJson(
          `${API_BASE}/api/flagged-conversations/${conversation.id}/interventions`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              intervention_type: interventionType.value,
              objective: interventionObjective.value.trim(),
            }),
          },
        );
        await replaceIntervention(response.data);
        resetInterventionEditor();
        createToast("Intervention created.", "success");
      } catch (error) {
        console.error(error);
        createToast("Unable to create intervention.", "info");
      }
    };

    renderInterventions(
      interventions,
      updateInterventionProgress,
      recordInterventionOutcome,
    );
    resetInterventionEditor();

    function updateConfidentialityControls() {
      const isConfidential =
        confidentiality.confidentiality_status === "confidential";
      confidentialityReason.value = "";
      confidentialityReason.hidden = isConfidential;
      document.querySelector(
        'label[for="case-confidentiality-reason"]',
      ).hidden = isConfidential;
      markConfidentialButton.hidden = isConfidential;
      markConfidentialButton.disabled = true;
      markConfidentialButton.classList.add("disabled");
      removeConfidentialityButton.hidden = !isConfidential;
      renderCaseConfidentiality(confidentiality);
    }

    async function updateConfidentiality(status, reason) {
      try {
        const response = await fetchJson(
          `${API_BASE}/api/flagged-conversations/${conversation.id}/confidentiality`,
          {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              confidentiality_status: status,
              confidentiality_reason: reason,
            }),
          },
        );
        confidentiality = response.data;
        updateConfidentialityControls();
        createToast(
          status === "confidential"
            ? "Case marked confidential."
            : "Case confidentiality removed.",
          "success",
        );
      } catch (error) {
        console.error(error);
        createToast("Unable to update case confidentiality.", "info");
      }
    }

    confidentialityReason.oninput = () => {
      const empty = !confidentialityReason.value.trim();
      markConfidentialButton.disabled = empty;
      markConfidentialButton.classList.toggle("disabled", empty);
    };
    markConfidentialButton.onclick = () => {
      const reason = confidentialityReason.value.trim();
      if (reason) updateConfidentiality("confidential", reason);
    };
    removeConfidentialityButton.onclick = () => {
      updateConfidentiality("not_confidential");
    };
    updateConfidentialityControls();

    switchView("case-details");
  } catch (error) {
    console.error(error);
    createToast("Unable to open flagged conversation.", "info");
  }
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

    case "confirmed":
      badge.classList.add("neutral");
      badge.textContent = "Confirmed";
      break;

    case "completed":
      badge.classList.add("resolved");
      badge.textContent = "Completed";
      break;

    case "cancelled":
      badge.classList.add("negative");
      badge.textContent = "Cancelled";
      break;

    case "rejected":
      badge.classList.add("negative");
      badge.textContent = "Rejected";
      break;

    default:
      badge.classList.add("pending");
      badge.textContent = appointment.status;
  }

  const notesInput = document.getElementById("appointment-notes-input");
  const saveBtn = document.getElementById("save-appointment-notes-btn");

  const confirmBtn = document.getElementById("appointment-confirm-btn");
  const completeBtn = document.getElementById("appointment-complete-btn");
  const rejectBtn = document.getElementById("appointment-reject-btn");
  const cancelBtn = document.getElementById("appointment-cancel-btn");

  // Action button visibility logic
  const isPending = appointment.status === "pending";
  const isConfirmed = appointment.status === "confirmed";

  confirmBtn.hidden = !isPending;
  rejectBtn.hidden = !isPending;
  completeBtn.hidden = !isConfirmed;
  cancelBtn.hidden = !["pending", "confirmed"].includes(appointment.status);

  notesInput.value = appointment.counselorNotes || "";

  // Disable notes editing and hide save button if appointment is closed
  const appointmentClosed = ["completed", "cancelled", "rejected"].includes(
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
      await updateCounselorNotes(appointment, notes);
      originalNotes = notes;
      openAppointmentDetails(appointment);
      createToast("Counselor notes saved.", "success");
    } catch (error) {
      console.error(error);
      saveBtn.disabled = false;
      createToast("Unable to save counselor notes.", "info");
    }
  };
  confirmBtn.onclick = async () => {
    confirmBtn.disabled = true;
    try {
      await updateAppointment(appointment, {
        status: "confirmed",
      });

      createToast("Appointment confirmed.", "success");

      openAppointmentDetails(appointment);
    } catch (error) {
      console.error(error);
      confirmBtn.disabled = false;
      createToast("Unable to confirm appointment.", "info");
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

  rejectBtn.onclick = async () => {
    rejectBtn.disabled = true;
    try {
      await updateAppointment(appointment, {
        status: "rejected",
      });

      createToast("Appointment rejected.", "success");

      openAppointmentDetails(appointment);
    } catch (error) {
      console.error(error);
      rejectBtn.disabled = false;
      createToast("Unable to update appointment status.", "info");
    }
  };

  completeBtn.onclick = async () => {
    completeBtn.disabled = true;
    const notes = notesInput.value.trim();

    if (!notes) {
      createToast(
        "Please save counselor notes before completing the appointment.",
        "info",
      );
      notesInput.focus();
      completeBtn.disabled = false;
      return;
    }
    try {
      if (notes !== originalNotes) {
        await updateCounselorNotes(appointment, notes);
        originalNotes = notes;
      }

      await updateAppointment(appointment, {
        status: "completed",
      });

      createToast("Appointment marked as completed.", "success");

      openAppointmentDetails(appointment);
    } catch (error) {
      console.error(error);
      completeBtn.disabled = false;
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
    const flagged = await fetchJson(`${API_BASE}/api/flagged-conversations`);
    flaggedConversations = (flagged.data?.items || []).map(
      mapFlaggedConversation,
    );
  } catch (error) {
    console.error(error);
    flaggedConversations = [];
  }

  try {
    const appointments = await fetchJson(`${API_BASE}/api/appointments`);
    window.backendAppointments = (appointments.data?.items || []).map(
      mapAppointment,
    );
  } catch (error) {
    console.error(error);
    window.backendAppointments = [];
  }

  try {
    await loadAppointmentAnalytics();
  } catch (error) {
    console.error(error);
    appointmentAnalytics = null;
  }

  try {
    await loadChatbotAnalytics();
  } catch (error) {
    console.error(error);
    chatbotAnalytics = null;
  }

  try {
    await loadCounselorWorkloadAnalytics();
  } catch (error) {
    console.error(error);
    counselorWorkloadAnalytics = null;
  }

  try {
    await loadFlaggedCaseAnalytics();
  } catch (error) {
    console.error(error);
    flaggedCaseAnalytics = null;
  }

  try {
    await loadCombinedReports();
  } catch (error) {
    console.error(error);
    reportsAnalytics = null;
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
bindAppointmentSearch();
bindAppointmentCalendar();
bindAppointmentAnalyticsFilters();
bindChatbotAnalyticsFilters();
bindCounselorWorkloadAnalyticsFilters();
bindFlaggedCaseAnalyticsFilters();
bindReportsControls();
bindDashboardOverviewNavigation();
loadBackendData();

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
window.logout = window.logout || logout;
window.addFaqFromButton = addFaqFromButton;
