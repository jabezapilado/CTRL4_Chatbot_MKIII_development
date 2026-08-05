/* Persistent in-app appointment notifications. */

(() => {
  "use strict";

  const API_BASE = window.location.origin;
  let notifications = [];
  let root;
  let panel;
  let list;
  let count;

  function isRead(notification) {
    return (
      notification.is_read === true ||
      notification.is_read === 1 ||
      notification.is_read === "1"
    );
  }

  function formatCreatedAt(value) {
    const createdAt = new Date(value);
    if (Number.isNaN(createdAt.getTime())) {
      return String(value || "");
    }

    return createdAt.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  }

  function renderNotifications() {
    const unreadCount = notifications.filter(
      (notification) => !isRead(notification),
    ).length;

    count.textContent = unreadCount ? String(unreadCount) : "";
    count.hidden = unreadCount === 0;
    list.replaceChildren();

    if (!notifications.length) {
      const empty = document.createElement("p");
      empty.className = "notifications-empty";
      empty.textContent = "No notifications.";
      list.appendChild(empty);
      return;
    }

    notifications.forEach((notification) => {
      const item = document.createElement("article");
      item.className = "notification-item";
      if (isRead(notification)) {
        item.classList.add("is-read");
      }

      const heading = document.createElement("h3");
      heading.textContent = String(notification.title || "Notification");
      item.appendChild(heading);

      const message = document.createElement("p");
      message.textContent = String(notification.message || "");
      item.appendChild(message);

      const footer = document.createElement("div");
      footer.className = "notification-item-footer";

      const createdAt = document.createElement("time");
      createdAt.textContent = formatCreatedAt(notification.created_at);
      footer.appendChild(createdAt);

      if (!isRead(notification)) {
        const markRead = document.createElement("button");
        markRead.type = "button";
        markRead.className = "notification-mark-read";
        markRead.textContent = "Mark as read";
        markRead.addEventListener("click", () => {
          markNotificationRead(notification.id, markRead);
        });
        footer.appendChild(markRead);
      } else {
        const readState = document.createElement("span");
        readState.className = "notification-read-state";
        readState.textContent = "Read";
        footer.appendChild(readState);
      }

      item.appendChild(footer);
      list.appendChild(item);
    });
  }

  function showLoadError() {
    list.replaceChildren();
    const error = document.createElement("p");
    error.className = "notifications-empty";
    error.textContent = "Unable to load notifications.";
    list.appendChild(error);
  }

  async function loadNotifications() {
    try {
      const response = await fetch(`${API_BASE}/api/notifications`);
      const payload = await response.json();

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          root.remove();
          return;
        }
        throw new Error(payload.message || "Unable to load notifications.");
      }

      notifications = Array.isArray(payload.data?.items)
        ? payload.data.items
        : [];
      renderNotifications();
    } catch (error) {
      console.error("Unable to load notifications:", error);
      showLoadError();
    }
  }

  async function markNotificationRead(notificationId, button) {
    button.disabled = true;

    try {
      const response = await fetch(
        `${API_BASE}/api/notifications/${encodeURIComponent(notificationId)}/read`,
        { method: "PATCH" },
      );
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.message || "Unable to mark notification as read.");
      }

      const notification = notifications.find(
        (item) => item.id === notificationId,
      );
      if (notification) {
        notification.is_read = 1;
      }
      renderNotifications();
    } catch (error) {
      button.disabled = false;
      console.error("Unable to mark notification as read:", error);
    }
  }

  function initializeNotifications() {
    root = document.createElement("section");
    root.className = "notifications-widget";
    root.setAttribute("aria-label", "Notifications");

    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "notifications-toggle";
    toggle.setAttribute("aria-expanded", "false");
    toggle.textContent = "Notifications";

    count = document.createElement("span");
    count.className = "notifications-count";
    count.hidden = true;
    toggle.appendChild(count);

    panel = document.createElement("div");
    panel.className = "notifications-panel";
    panel.hidden = true;

    const title = document.createElement("h2");
    title.textContent = "Notifications";
    panel.appendChild(title);

    list = document.createElement("div");
    list.className = "notifications-list";
    panel.appendChild(list);

    toggle.addEventListener("click", () => {
      const opening = panel.hidden;
      panel.hidden = !opening;
      toggle.setAttribute("aria-expanded", String(opening));
      if (opening) {
        loadNotifications();
      }
    });

    root.append(toggle, panel);
    document.body.appendChild(root);
    loadNotifications();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeNotifications);
  } else {
    initializeNotifications();
  }
})();
