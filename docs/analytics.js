/* Google Analytics 4 for the public research library.
   Tracks catalog pages and publication-reader visits, not raw PDF opens. */
(() => {
  if (window.__tennesonAnalyticsLoaded) return;
  window.__tennesonAnalyticsLoaded = true;
  const measurementId = "G-LCTRDYBHHM";
  let pageLocation = window.location.href;
  let pageTitle = document.title;
  let pageReferrer = document.referrer;

  // Each publication uses the shared PDF.js reader in an iframe.
  // Attribute that visit to the paper's URL instead of /pdf-reader.html.
  if (window.location.pathname.endsWith("/pdf-reader.html")) {
    const file = new URLSearchParams(window.location.search).get("file");
    if (file && file.startsWith("/pub/") && /\.pdf$/i.test(file)) {
      pageLocation = window.location.origin + file.slice(0, file.lastIndexOf("/") + 1);
      pageTitle = decodeURIComponent(file.slice(file.lastIndexOf("/") + 1))
        .replace(/\.pdf$/i, "").replace(/_/g, " ");
    }
    try {
      if (window.parent !== window && window.parent.location.origin === window.location.origin) {
        pageTitle = window.parent.document.title || pageTitle;
        pageReferrer = window.parent.document.referrer || pageReferrer;
      }
    } catch (_) { /* Standalone or cross-origin reader. */ }
  }

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  const tag = document.createElement("script");
  tag.async = true;
  tag.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(measurementId);
  document.head.appendChild(tag);
  window.gtag("js", new Date());
  window.gtag("config", measurementId, {
    page_location: pageLocation,
    page_title: pageTitle,
    page_referrer: pageReferrer
  });
})();
