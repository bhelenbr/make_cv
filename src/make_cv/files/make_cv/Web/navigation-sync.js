(function () {
  function getFileName() {
    return location.pathname.split("/").pop() || "webli1.html";
  }

  function postToParent(payload) {
    if (window.top !== window.self) {
      try {
        window.top.postMessage(payload, "*");
      } catch (e) {}
    }
  }

  function syncCurrentPage() {
    postToParent({
      type: "sync-page",
      page: getFileName()
    });
  }

  document.addEventListener("click", function (e) {
    var a = e.target.closest("a");
    if (!a) return;

    var href = a.getAttribute("href");
    if (!href) return;

    if (
      href.startsWith("#") ||
      href.startsWith("mailto:") ||
      href.startsWith("tel:") ||
      href.startsWith("javascript:") ||
      href.startsWith("http://") ||
      href.startsWith("https://")
    ) {
      return;
    }

    if (/\.html?($|[?#])/.test(href)) {
      e.preventDefault();   // this is the missing part
      e.stopPropagation();

      postToParent({
        type: "navigate-page",
        page: href.split("#")[0].split("?")[0]
      });
    }
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", syncCurrentPage);
  } else {
    syncCurrentPage();
  }
})();
