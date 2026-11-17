"use strict";

// Dark mode: follows the system until the reader picks one with the toggle;
// the choice is remembered. The saved choice is applied in <head> before paint.
(function () {
  var root = document.documentElement;
  var media = window.matchMedia("(prefers-color-scheme: dark)");

  function isDark() {
    if (root.dataset.theme) return root.dataset.theme === "dark";
    return media.matches;
  }

  document.addEventListener("click", function (e) {
    if (!e.target.closest(".theme-toggle")) return;
    var next = isDark() ? "light" : "dark";
    root.dataset.theme = next;
    localStorage.setItem("theme", next);
  });
})();
