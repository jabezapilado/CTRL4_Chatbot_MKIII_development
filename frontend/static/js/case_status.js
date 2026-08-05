const studentCaseStatusList = document.getElementById(
  "student-case-status-list",
);
const studentCaseStatusMessage = document.getElementById(
  "student-case-status-message",
);
const API_BASE = window.location.origin;

function formatCaseDate(value) {
  if (!value) return "Unavailable";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Unavailable" : date.toLocaleString();
}

function getCaseStatusClass(status) {
  return String(status || "in progress")
    .toLowerCase()
    .replaceAll(" ", "-");
}

function appendCaseDate(container, label, value) {
  const item = document.createElement("div");
  item.className = "student-case-status-date";
  const heading = document.createElement("span");
  const content = document.createElement("strong");
  heading.textContent = label;
  content.textContent = formatCaseDate(value);
  item.append(heading, content);
  container.appendChild(item);
}

function createStudentCaseStatusCard(caseStatus) {
  const card = document.createElement("article");
  card.className = "student-case-status-card";

  const header = document.createElement("div");
  header.className = "student-case-status-header";
  const title = document.createElement("h2");
  title.textContent = "Guidance Case";
  const badge = document.createElement("span");
  badge.className = `student-case-status-badge ${getCaseStatusClass(
    caseStatus.case_status,
  )}`;
  badge.textContent = caseStatus.case_status || "In Progress";
  header.append(title, badge);

  const progress = document.createElement("p");
  progress.className = "student-case-status-progress";
  progress.textContent =
    caseStatus.progress_text || "Case status is unavailable.";

  const dates = document.createElement("div");
  dates.className = "student-case-status-dates";
  appendCaseDate(dates, "Submitted", caseStatus.submitted_at);
  appendCaseDate(dates, "Last Updated", caseStatus.updated_at);

  card.append(header, progress, dates);
  return card;
}

function renderStudentCaseStatuses(caseStatuses) {
  studentCaseStatusList.replaceChildren();
  if (!caseStatuses.length) {
    const empty = document.createElement("p");
    empty.className = "student-case-status-empty";
    empty.textContent = "You do not have any guidance cases to display.";
    studentCaseStatusList.appendChild(empty);
    return;
  }

  caseStatuses.forEach((caseStatus) => {
    studentCaseStatusList.appendChild(createStudentCaseStatusCard(caseStatus));
  });
}

async function loadStudentCaseStatuses() {
  studentCaseStatusList.replaceChildren();
  const loading = document.createElement("p");
  loading.className = "student-case-status-loading";
  loading.textContent = "Loading case status...";
  studentCaseStatusList.appendChild(loading);

  try {
    const response = await fetch(`${API_BASE}/api/student/cases`);
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.message || "Unable to retrieve case status.");
    }
    renderStudentCaseStatuses(payload.data?.items || []);
  } catch (error) {
    console.error(error);
    studentCaseStatusList.replaceChildren();
    const message = document.createElement("p");
    message.className = "student-case-status-error";
    message.textContent = "Unable to load your case status right now.";
    studentCaseStatusList.appendChild(message);
  }
}

studentCaseStatusMessage.replaceChildren();
void loadStudentCaseStatuses();
