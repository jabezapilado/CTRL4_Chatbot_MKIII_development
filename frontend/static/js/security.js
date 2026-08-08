(() => {
  "use strict";

  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
  const unsafeMethods = new Set(["POST", "PUT", "PATCH", "DELETE"]);
  const originalFetch = window.fetch.bind(window);

  function isSameOrigin(input) {
    const target = input instanceof Request ? input.url : input;
    return new URL(target, window.location.href).origin === window.location.origin;
  }

  window.fetch = (input, init = {}) => {
    const method = (init.method || (input instanceof Request && input.method) || "GET")
      .toUpperCase();

    if (!csrfToken || !unsafeMethods.has(method) || !isSameOrigin(input)) {
      return originalFetch(input, init);
    }

    const headers = new Headers(
      init.headers || (input instanceof Request ? input.headers : undefined),
    );
    headers.set("X-CSRF-Token", csrfToken);
    return originalFetch(input, { ...init, headers });
  };
})();
