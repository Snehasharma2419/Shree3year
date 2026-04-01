document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("addItemModal");
  const openBtn = document.getElementById("openModalBtn");
  const closeBtn = document.querySelector(".close-modal");
  const cancelBtn = document.querySelector(".btn-cancel");

  // Open Modal
  if (openBtn) {
    openBtn.addEventListener("click", function () {
      modal.style.display = "block";
    });
  }

  // Close Modal (Cross button)
  if (closeBtn) {
    closeBtn.addEventListener("click", function () {
      modal.style.display = "none";
    });
  }

  // Close Modal (Cancel button)
  if (cancelBtn) {
    cancelBtn.addEventListener("click", function () {
      modal.style.display = "none";
    });
  }

  // Close Modal (Outside click)
  window.addEventListener("click", function (event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  });
});