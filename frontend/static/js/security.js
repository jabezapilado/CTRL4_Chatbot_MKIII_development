(() => {
  "use strict";

  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
  const unsafeMethods = new Set(["POST", "PUT", "PATCH", "DELETE"]);
  const originalFetch = window.fetch.bind(window);

  function isSameOrigin(input) {
    const target = input instanceof Request ? input.url : input;
    return new URL(target, window.location.href).origin === window.location.origin;
  }

  function redirectIfStudentSessionWasReplaced(input, response) {
    if (
      isSameOrigin(input) &&
      response.headers.get("X-CTRL4-Session-Replaced") === "1"
    ) {
      window.location.replace("/login?reason=session-replaced");
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
})();
