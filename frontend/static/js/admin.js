/* Administrator account-management portal. Server-side RBAC remains authoritative. */

const ADMIN_API_BASE = window.location.origin;
let programs = [];

const accountListBody = document.getElementById("account-list-body");
const accountListMessage = document.getElementById("account-list-message");
const accountFilterForm = document.getElementById("account-filter-form");
const accountSearch = document.getElementById("account-search");
const accountRoleFilter = document.getElementById("account-role-filter");
const accountStatusFilter = document.getElementById("account-status-filter");
const accountDialog = document.getElementById("account-dialog");
const accountForm = document.getElementById("account-form");
const accountFormMessage = document.getElementById("account-form-message");
const accountRole = document.getElementById("account-role");
const accountProgram = document.getElementById("account-program");
const accountAssignedPrograms = document.getElementById(
  "account-assigned-programs",
);
const studentProfileFields = document.getElementById("student-profile-fields");
const staffProfileFields = document.getElementById("staff-profile-fields");
const accountPasswordField = document.getElementById("account-password-field");
const accountPassword = document.getElementById("account-password");
const accountFormSubmit = document.getElementById("account-form-submit");

let editingAccount = null;

function accountNumber(account) {
  return account.student_number || account.staff_number || "—";
}

function parseList(value) {
  if (Array.isArray(value)) return value;
  if (typeof value !== "string" || !value.trim()) return [];

  try {
    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function accountPrograms(account) {
  if (account.role === "student") return account.program || "—";
  if (account.role === "staff") {
    const programs = parseList(account.assigned_programs);
    return programs.length ? programs.join(", ") : "—";
  }
  return "—";
}

function roleLabel(role) {
  return (
    {
      student: "Student",
      staff: "Guidance staff",
      admin: "Administrator",
    }[role] || "Unknown"
  );
}

function setFeedback(element, message = "", type = "") {
  element.textContent = message;
  element.classList.toggle("is-error", type === "error");
  element.classList.toggle("is-success", type === "success");
}

function appendAccountCell(row, value, label) {
  const cell = document.createElement("td");
  cell.dataset.label = label;
  cell.textContent = value || "—";
  row.appendChild(cell);
  return cell;
}

function renderAccountSummary(accounts) {
  const counts = accounts.reduce(
    (summary, account) => {
      summary.total += 1;
      summary[account.role] = (summary[account.role] || 0) + 1;
      summary[account.status] = (summary[account.status] || 0) + 1;
      return summary;
    },
    { total: 0, student: 0, staff: 0, admin: 0, active: 0, disabled: 0 },
  );

  document.getElementById("account-summary-total").textContent = String(
    counts.total,
  );
  document.getElementById("account-summary-students").textContent = String(
    counts.student,
  );
  document.getElementById("account-summary-staff").textContent = String(
    counts.staff,
  );
  document.getElementById("account-summary-admins").textContent = String(
    counts.admin,
  );
  document.getElementById("account-summary-status").textContent =
    `${counts.active} / ${counts.disabled}`;
}

function renderAccountSummaryUnavailable() {
  [
    "account-summary-total",
    "account-summary-students",
    "account-summary-staff",
    "account-summary-admins",
    "account-summary-status",
  ].forEach((elementId) => {
    document.getElementById(elementId).textContent = "—";
  });
}

function createActionButton(label, className, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.textContent = label;
  button.addEventListener("click", onClick);
  return button;
}

function renderAccounts(accounts) {
  renderAccountSummary(accounts);
  accountListBody.replaceChildren();

  if (!accounts.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 7;
    cell.className = "admin-empty-state";
    cell.textContent = "No accounts match the selected filters.";
    row.appendChild(cell);
    accountListBody.appendChild(row);
    return;
  }

  accounts.forEach((account) => {
    const row = document.createElement("tr");
    appendAccountCell(row, account.full_name, "Name");
    appendAccountCell(row, account.email, "Email");
    appendAccountCell(row, roleLabel(account.role), "Role");

    const statusCell = document.createElement("td");
    statusCell.dataset.label = "Status";
    const status = document.createElement("span");
    status.className = `admin-status admin-status--${
      account.status === "active" ? "active" : "disabled"
    }`;
    status.textContent = account.status === "active" ? "Active" : "Disabled";
    statusCell.appendChild(status);
    row.appendChild(statusCell);

    appendAccountCell(row, accountNumber(account), "Account number");
    appendAccountCell(
      row,
      accountPrograms(account),
      "Program / assigned programs",
    );

    const actionsCell = document.createElement("td");
    actionsCell.dataset.label = "Actions";
    const actions = document.createElement("div");
    actions.className = "admin-row-actions";
    actions.appendChild(
      createActionButton("Edit", "btn btn-outline btn-sm", () => {
        openAccountForm(account);
      }),
    );

    if (account.status === "active") {
      actions.appendChild(
        createActionButton("Deactivate", "btn btn-outline btn-sm", () => {
          deactivateAccount(account);
        }),
      );
    }

    actionsCell.appendChild(actions);
    row.appendChild(actionsCell);
    accountListBody.appendChild(row);
  });
}

function accountQuery() {
  const params = new URLSearchParams();
  const query = accountSearch.value.trim();
  const role = accountRoleFilter.value;
  const status = accountStatusFilter.value;

  if (query) params.set("q", query);
  if (role) params.set("role", role);
  if (status) params.set("status", status);
  return params;
}

async function responsePayload(response, fallbackMessage) {
  const payload = await response.json();
  if (!response.ok || !payload.success) {
    throw new Error(payload.message || fallbackMessage);
  }
  return payload;
}

async function loadAccounts() {
  const params = accountQuery();
  setFeedback(accountListMessage, "Loading accounts…");

  try {
    const response = await fetch(
      `${ADMIN_API_BASE}/api/accounts${params.size ? `?${params}` : ""}`,
    );
    const payload = await responsePayload(
      response,
      "Unable to retrieve accounts.",
    );
    renderAccounts(payload.data?.items || []);
    setFeedback(accountListMessage);
  } catch (error) {
    accountListBody.replaceChildren();
    renderAccountSummaryUnavailable();
    setFeedback(
      accountListMessage,
      error.message || "Unable to retrieve accounts.",
      "error",
    );
  }
}

function populateProgramSelect() {
  accountProgram.replaceChildren();
  const empty = document.createElement("option");
  empty.value = "";
  empty.textContent = "Select program";
  accountProgram.appendChild(empty);

  programs.forEach((program) => {
    const option = document.createElement("option");
    option.value = program.display_name;
    option.textContent = program.display_name;
    accountProgram.appendChild(option);
  });
}

function renderAssignedPrograms(selectedPrograms = []) {
  const selected = new Set(selectedPrograms);
  accountAssignedPrograms.replaceChildren();

  programs.forEach((program) => {
    const label = document.createElement("label");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.name = "assigned_programs";
    checkbox.value = program.display_name;
    checkbox.checked = selected.has(program.display_name);
    const text = document.createElement("span");
    text.textContent = program.display_name;
    label.append(checkbox, text);
    accountAssignedPrograms.appendChild(label);
  });
}

function renderProgramCatalog(catalog) {
  const list = document.getElementById("program-catalog-list");
  list.replaceChildren();
  catalog.forEach((program) => {
    const row = document.createElement("article");
    const title = document.createElement("strong");
    const detail = document.createElement("span");
    const toggle = createActionButton(
      program.active ? "Deactivate" : "Activate",
      "btn btn-outline btn-sm",
      () => void updateProgram(program.code, { active: !program.active }),
    );
    const edit = createActionButton("Edit", "btn btn-outline btn-sm", () => {
      const displayName = window.prompt(
        "Program display name",
        program.display_name,
      );
      if (displayName && displayName.trim() !== program.display_name) {
        void updateProgram(program.code, { display_name: displayName.trim() });
      }
    });
    row.className = "program-catalog-row";
    title.textContent = program.display_name;
    detail.textContent = `${program.code} · ${program.active ? "Active" : "Inactive"}`;
    row.append(title, detail, edit, toggle);
    list.appendChild(row);
  });
}

async function loadPrograms() {
  const message = document.getElementById("program-catalog-message");
  setFeedback(message, "Loading program catalog…");
  try {
    const response = await fetch(`${ADMIN_API_BASE}/api/accounts/programs`);
    const payload = await responsePayload(
      response,
      "Unable to retrieve programs.",
    );
    const catalog = payload.data?.items || [];
    programs = catalog.filter((program) => program.active);
    populateProgramSelect();
    renderAssignedPrograms(
      editingAccount ? parseList(editingAccount.assigned_programs) : [],
    );
    renderProgramCatalog(catalog);
    setFeedback(message);
  } catch (error) {
    programs = [];
    populateProgramSelect();
    renderAssignedPrograms();
    setFeedback(
      message,
      error.message || "Unable to retrieve programs.",
      "error",
    );
  }
}

async function updateProgram(code, updates) {
  const message = document.getElementById("program-catalog-message");
  try {
    const response = await fetch(
      `${ADMIN_API_BASE}/api/accounts/programs/${encodeURIComponent(code)}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates),
      },
    );
    const payload = await responsePayload(
      response,
      "Unable to update program.",
    );
    setFeedback(message, payload.message, "success");
    await loadPrograms();
  } catch (error) {
    setFeedback(message, error.message || "Unable to update program.", "error");
  }
}

function syncRoleFields() {
  const role = accountRole.value;
  const editing = Boolean(editingAccount);
  studentProfileFields.hidden = role !== "student";
  staffProfileFields.hidden = role !== "staff";
  accountPasswordField.hidden = editing;
  accountPassword.required = !editing;
  accountRole.disabled = editing;
}

function setFormValues(account = null) {
  editingAccount = account;
  accountForm.reset();
  populateProgramSelect();

  if (account) {
    document.getElementById("account-dialog-kicker").textContent =
      "Existing account";
    document.getElementById("account-dialog-title").textContent =
      "Edit account";
    accountFormSubmit.textContent = "Save changes";
    document.getElementById("account-full-name").value =
      account.full_name || "";
    document.getElementById("account-email").value = account.email || "";
    document.getElementById("account-gender").value = account.gender || "";
    accountRole.value = account.role || "student";
    accountProgram.value = account.program || "";
    renderAssignedPrograms(parseList(account.assigned_programs));
  } else {
    document.getElementById("account-dialog-kicker").textContent =
      "New account";
    document.getElementById("account-dialog-title").textContent =
      "Create account";
    accountFormSubmit.textContent = "Create account";
    accountRole.value = "student";
    renderAssignedPrograms();
  }

  syncRoleFields();
  setFeedback(accountFormMessage);
}

function openAccountForm(account = null) {
  setFormValues(account);
  accountDialog.showModal();
  document.getElementById("account-full-name").focus();
}

function closeAccountForm() {
  if (accountDialog.open) accountDialog.close();
}

function formRole() {
  return editingAccount?.role || accountRole.value;
}

function selectedPrograms() {
  return Array.from(
    accountAssignedPrograms.querySelectorAll(
      'input[name="assigned_programs"]:checked',
    ),
    (checkbox) => checkbox.value,
  );
}

function accountPayload() {
  const role = formRole();
  const payload = {
    full_name: document.getElementById("account-full-name").value.trim(),
    email: document.getElementById("account-email").value.trim(),
    gender: document.getElementById("account-gender").value,
  };

  if (!payload.full_name || !payload.email || !payload.gender) {
    throw new Error("Full name, email address, and gender are required.");
  }

  if (!editingAccount) {
    const password = accountPassword.value;
    if (!password) throw new Error("A temporary password is required.");
    payload.password = password;
    payload.role = role;
  }

  if (role === "student") {
    payload.program = accountProgram.value;
    if (!payload.program) throw new Error("A student program is required.");
  }

  if (role === "staff") {
    payload.assigned_programs = selectedPrograms();
  }

  return payload;
}

function accountEndpoint(account) {
  if (account.role === "staff") return `/api/accounts/staff/${account.id}`;
  if (account.role === "admin") return `/api/accounts/admin/${account.id}`;
  return `/api/accounts/${account.id}`;
}

async function saveAccount(event) {
  event.preventDefault();
  let payload;
  try {
    payload = accountPayload();
  } catch (error) {
    setFeedback(accountFormMessage, error.message, "error");
    return;
  }

  const isEdit = Boolean(editingAccount);
  accountFormSubmit.disabled = true;
  setFeedback(
    accountFormMessage,
    isEdit ? "Saving changes…" : "Creating account…",
  );

  try {
    const response = await fetch(
      `${ADMIN_API_BASE}${isEdit ? accountEndpoint(editingAccount) : "/api/accounts"}`,
      {
        method: isEdit ? "PATCH" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
    );
    const result = await responsePayload(
      response,
      isEdit ? "Unable to update account." : "Unable to create account.",
    );
    closeAccountForm();
    setFeedback(accountListMessage, result.message, "success");
    await loadAccounts();
    setFeedback(accountListMessage, result.message, "success");
  } catch (error) {
    setFeedback(
      accountFormMessage,
      error.message ||
        (isEdit ? "Unable to update account." : "Unable to create account."),
      "error",
    );
  } finally {
    accountFormSubmit.disabled = false;
  }
}

async function deactivateAccount(account) {
  const confirmed = window.confirm(
    "Deactivate this account? A disabled account cannot sign in, and this portal does not provide reactivation.",
  );
  if (!confirmed) return;

  setFeedback(accountListMessage, "Deactivating account…");
  try {
    const response = await fetch(
      `${ADMIN_API_BASE}${accountEndpoint(account)}`,
      { method: "DELETE" },
    );
    const result = await responsePayload(
      response,
      "Unable to deactivate account.",
    );
    await loadAccounts();
    setFeedback(accountListMessage, result.message, "success");
  } catch (error) {
    setFeedback(
      accountListMessage,
      error.message || "Unable to deactivate account.",
      "error",
    );
  }
}

function resetFilters() {
  accountFilterForm.reset();
  loadAccounts();
}

document.getElementById("create-account-btn").addEventListener("click", () => {
  openAccountForm();
});
document
  .getElementById("account-reset-btn")
  .addEventListener("click", resetFilters);
document
  .getElementById("account-dialog-close")
  .addEventListener("click", closeAccountForm);
document
  .getElementById("account-form-cancel")
  .addEventListener("click", closeAccountForm);
accountRole.addEventListener("change", () => {
  renderAssignedPrograms();
  syncRoleFields();
});
accountFilterForm.addEventListener("submit", (event) => {
  event.preventDefault();
  loadAccounts();
});
accountForm.addEventListener("submit", saveAccount);
accountDialog.addEventListener("click", (event) => {
  if (event.target === accountDialog) closeAccountForm();
});
document.getElementById("admin-logout-btn").addEventListener("click", () => {
  window.logout();
});

document
  .getElementById("program-catalog-form")
  .addEventListener("submit", async (event) => {
    event.preventDefault();
    const code = document.getElementById("program-code");
    const displayName = document.getElementById("program-display-name");
    const message = document.getElementById("program-catalog-message");
    try {
      const response = await fetch(`${ADMIN_API_BASE}/api/accounts/programs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          code: code.value,
          display_name: displayName.value,
        }),
      });
      const payload = await responsePayload(
        response,
        "Unable to create program.",
      );
      event.currentTarget.reset();
      setFeedback(message, payload.message, "success");
      await loadPrograms();
    } catch (error) {
      setFeedback(
        message,
        error.message || "Unable to create program.",
        "error",
      );
    }
  });

void loadPrograms();
loadAccounts();
