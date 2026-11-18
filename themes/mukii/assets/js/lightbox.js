// Project pages: click an image to see it large; click again (or Esc) to close.
(function () {
  var box = document.createElement("div");
  box.className = "lightbox";
  box.innerHTML = "<img alt=\"\">";
  var big = box.firstChild;
  function close() { box.classList.remove("is-open"); big.removeAttribute("src"); }
  box.addEventListener("click", close);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
  document.body.appendChild(box);
  document.querySelectorAll(".content-container figure img").forEach(function (img) {
    img.addEventListener("click", function () {
      big.src = img.dataset.full || img.currentSrc || img.src;
      big.alt = img.alt;
      box.classList.add("is-open");
    });
  });
})();
