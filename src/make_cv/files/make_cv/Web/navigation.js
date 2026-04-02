(function () {
  const PARENT_ORIGIN = "https://sites.clarkson.edu";
  let lastSentHeight = 0;
  let rafId = null;

  function getHeight() {
    const body = document.body;
    const html = document.documentElement;
    if (!body || !html) return 0;

    return Math.ceil(Math.max(
      body.scrollHeight || 0,
      body.offsetHeight || 0,
      body.clientHeight || 0,
      html.scrollHeight || 0,
      html.offsetHeight || 0,
      html.clientHeight || 0
    ));
  }

  function currentPage() {
    return window.location.pathname.split("/").pop() + (window.location.hash || "");
  }

  function sendPageSync() {
    if (window.parent === window) return;

    parent.postMessage(
      { type: "sync-page", page: currentPage() },
      PARENT_ORIGIN
    );
  }

  function sendHeight(force) {
    if (window.parent === window) return;

    const h = getHeight();
    if (!h) return;

    if (!force && Math.abs(h - lastSentHeight) < 4) return;
    lastSentHeight = h;

    parent.postMessage(
      { type: "iframe-height", height: h },
      PARENT_ORIGIN
    );
  }

  function queueSend(force) {
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(function () {
      sendPageSync();
      sendHeight(force);
    });
  }

  function pageFromUrl(url) {
    return url.pathname.split("/").pop() + (url.hash || "");
  }

  function isInternalHtmlLink(url) {
    var file = url.pathname.split("/").pop();
    return (
      url.origin === window.location.origin &&
      /^[A-Za-z0-9._-]+\.html?$/i.test(file)
    );
  }

  function onClick(e) {
    const a = e.target.closest("a[href]");
    if (!a) return;

    if (a.target && a.target !== "_self") return;

    const rawHref = a.getAttribute("href");
    if (!rawHref) return;
    if (/^(javascript:|mailto:|tel:)/i.test(rawHref)) return;

    const url = new URL(rawHref, window.location.href);

    if (!isInternalHtmlLink(url)) return;

    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();

    if (window.parent !== window) {
      parent.postMessage(
        { type: "navigate-page", page: pageFromUrl(url) },
        PARENT_ORIGIN
      );
    } else {
      window.location.href = url.href;
    }
  }

  function init() {
    document.addEventListener("click", onClick, true);

    queueSend(true);

    window.addEventListener("load", function () {
      queueSend(true);
    });

    window.addEventListener("resize", function () {
      queueSend(true);
    });

    window.addEventListener("pageshow", function () {
      queueSend(true);
    });

    window.addEventListener("hashchange", function () {
      queueSend(true);
    });

    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () {
        queueSend(true);
      }).catch(function () {});
    }

    if (window.ResizeObserver) {
      const ro = new ResizeObserver(function () {
        queueSend(false);
      });

      ro.observe(document.documentElement);
      if (document.body) ro.observe(document.body);
    }

    setTimeout(function () { queueSend(true); }, 0);
    setTimeout(function () { queueSend(true); }, 100);
    setTimeout(function () { queueSend(true); }, 400);
    setTimeout(function () { queueSend(true); }, 1000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();