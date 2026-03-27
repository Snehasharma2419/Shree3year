document.addEventListener("DOMContentLoaded", function () {
  const buttons = document.querySelectorAll(".status-btn");
  const dateInput = document.getElementById("attendanceDate");

  // ✅ Get today's date
  const today = new Date().toISOString().split("T")[0];

  // ✅ Set date input to today only
  if (dateInput) {
    dateInput.value = today;
    dateInput.min = today;
    dateInput.max = today;
  }

  // Page load hote hi initial numbers set karein
  updateSummary();

  buttons.forEach((button) => {
    button.addEventListener("click", function () {
      // ✅ CHECK DATE BEFORE ALLOWING CLICK
      if (dateInput && dateInput.value !== today) {
        alert("You can only mark attendance for today!");
        return; // ❌ STOP execution
      }

      const workerId = this.getAttribute("data-worker");
      const status = this.getAttribute("data-status");

      const btnContainer = this.closest(".attendance-btns");

      // 1. HIDDEN INPUT UPDATE (Database ke liye)
      const hiddenInput = document.getElementById("input_" + workerId);
      if (hiddenInput) {
        hiddenInput.value = status;
      }

      // 2. UI UPDATE (Colors change karna)
      btnContainer
        .querySelectorAll(".status-btn")
        .forEach((btn) => btn.classList.remove("active"));
      this.classList.add("active");

      // 3. SUMMARY UPDATE
      updateSummary();
    });
  });

  // ✅ DISABLE BUTTONS IF DATE CHANGED (Extra Protection)
  if (dateInput) {
    dateInput.addEventListener("change", function () {
      if (this.value !== today) {
        alert("You can only select today's date!");

        // Disable all buttons
        buttons.forEach((btn) => (btn.disabled = true));
      } else {
        // Enable back
        buttons.forEach((btn) => (btn.disabled = false));
      }
    });
  }

  function updateSummary() {
    const rows = document.querySelectorAll(".attendance-table tbody tr");
    const total = rows.length;

    const present = document.querySelectorAll(".btn-present.active").length;
    const absent = document.querySelectorAll(".btn-absent.active").length;
    const leave = document.querySelectorAll(".btn-leave.active").length;

    if (document.getElementById("presentCountDisplay"))
      document.getElementById("presentCountDisplay").innerText = present;

    if (document.getElementById("absentCountDisplay"))
      document.getElementById("absentCountDisplay").innerText = absent;

    if (document.getElementById("leaveCountDisplay"))
      document.getElementById("leaveCountDisplay").innerText = leave;

    if (total > 0 && document.getElementById("rateDisplay")) {
      const rate = Math.round((present / total) * 100);
      document.getElementById("rateDisplay").innerText = rate + "%";
    }
  }
});
