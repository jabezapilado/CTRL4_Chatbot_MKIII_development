/* Administrator account-listing page.  Authorization remains server-side. */

const ADMIN_API_BASE = window.location.origin;
const accountListBody = document.getElementById("account-list-body");
const accountListMessage = document.getElementById("account-list-message");

function accountNumber(account) {
  return account.student_number || account.staff_number || "—";
}

function appendAccountCell(row, value) {
  const cell = document.createElement("td");
  cell.textContent = value || "—";
  row.appendChild(cell);
}

function renderAccounts(accounts) {
  accountListBody.replaceChildren();

  if (!accounts.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 5;
    cell.textContent = "No accounts match the selected filters.";
    row.appendChild(cell);
    accountListBody.appendChild(row);
    return;
  }

  accounts.forEach((account) => {
    const row = document.createElement("tr");
    appendAccountCell(row, account.full_name);
    appendAccountCell(row, account.email);
    appendAccountCell(row, account.role);
    appendAccountCell(row, account.status);
    appendAccountCell(row, accountNumber(account));
    accountListBody.appendChild(row);
  });
}

async function loadAccounts() {
  const params = new URLSearchParams();
  const query = document.getElementById("account-search").value.trim();
  const role = document.getElementById("account-role-filter").value;
  const status = document.getElementById("account-status-filter").value;

  if (query) params.set("q", query);
  if (role) params.set("role", role);
  if (status) params.set("status", status);

  accountListMessage.textContent = "Loading accounts…";
  try {
    const response = await fetch(
      `${ADMIN_API_BASE}/api/accounts${params.size ? `?${params}` : ""}`,
    );
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.message || "Unable to retrieve accounts.");
    }
    renderAccounts(payload.data?.items || []);
    accountListMessage.textContent = "";
  } catch (error) {
    accountListBody.replaceChildren();
    accountListMessage.textContent = error.message || "Unable to retrieve accounts.";
  }
}

document
  .getElementById("account-search-btn")
  .addEventListener("click", loadAccounts);
document.getElementById("account-search").addEventListener("keydown", (event) => {
  if (event.key === "Enter") loadAccounts();
});
document.getElementById("admin-logout-btn").addEventListener("click", () => {
  window.logout();
});

loadAccounts();
