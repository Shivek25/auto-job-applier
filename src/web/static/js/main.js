// src/web/static/js/main.js
document.addEventListener("DOMContentLoaded", () => {
  // Highlight active nav item
  const currentPath = window.location.pathname;
  document.querySelectorAll("nav .links a").forEach(link => {
    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });

  // Handle run batch confirmation
  const runForm = document.getElementById("run-batch-form");
  if (runForm) {
    runForm.addEventListener("submit", (e) => {
      const btn = runForm.querySelector("button");
      btn.disabled = true;
      btn.innerHTML = "⏳ Running Batch...";
    });
  }
});
