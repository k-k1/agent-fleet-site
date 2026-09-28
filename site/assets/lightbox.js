// Open a screenshot link in a lightbox instead of leaving the page for the bare image,
// which has no way back from inside the Console's browser pane. The links stay plain
// <a href> so the image still opens without JavaScript, and modified clicks (new tab,
// new window) are left to the browser.
(() => {
  if (typeof HTMLDialogElement !== "function") return;
  const links = document.querySelectorAll("a[data-lightbox]");
  if (!links.length) return;

  const ja = document.documentElement.lang === "ja";
  const dialog = document.createElement("dialog");
  dialog.className = "lightbox";
  const close = document.createElement("button");
  close.type = "button";
  close.className = "lightbox-close";
  close.setAttribute("aria-label", ja ? "閉じる" : "Close");
  close.textContent = "×";
  const figure = document.createElement("figure");
  const img = document.createElement("img");
  const caption = document.createElement("figcaption");
  figure.append(img, caption);
  dialog.append(close, figure);
  document.body.append(dialog);

  // Any click closes it: the image is already as large as the viewport allows, and a
  // click that does nothing reads as broken. Escape closes a modal dialog natively.
  dialog.addEventListener("click", () => dialog.close());
  dialog.addEventListener("close", () => img.removeAttribute("src"));

  for (const link of links) {
    link.addEventListener("click", (e) => {
      if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      e.preventDefault();
      const thumb = link.querySelector("img");
      img.src = link.href;
      img.alt = thumb ? thumb.alt : "";
      caption.textContent = img.alt;
      dialog.showModal();
    });
  }
})();
