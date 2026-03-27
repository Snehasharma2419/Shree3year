document.addEventListener("DOMContentLoaded", function () {
  const attendanceDate = document.getElementById("attendanceDate");
  const radioButtons = document.querySelectorAll('input[type="radio"]');
  const presentDisplay = document.getElementById("present-count");
  const absentDisplay = document.getElementById("absent-count");
  const rateDisplay = document.getElementById("attendance-rate");

  // --- 1. Date Constraint Logic ---
  // Enforce max date again via JS in case of browser inconsistencies
  const today = new Date().toISOString().split("T")[0];
  attendanceDate.setAttribute("max", today);

  attendanceDate.addEventListener("change", function () {
    if (this.value > today) {
      alert("Future dates are not allowed!");
      this.value = today;
    } else {
      // Optional: Auto-submit form to fetch data for the selected previous date
      // this.closest('form').submit();
      // Since the date is outside the main form, you might need a separate redirect logic:
      // window.location.href = `?date=${this.value}`;
    }
  });

  // --- 2. Dynamic Summary Logic ---
  function updateSummary() {
    let present = 0;
    let absent = 0;

    // Count current status based on checked radio inputs
    const checkedButtons = document.querySelectorAll(
      'input[type="radio"]:checked',
    );

    checkedButtons.forEach((radio) => {
      if (radio.value === "Present") {
        present++;
      } else if (radio.value === "Absent") {
        absent++;
      }
    });

    const total = present + absent;
    const rate = total > 0 ? Math.round((present / total) * 100) : 0;

    // Update DOM
    presentDisplay.textContent = present;
    absentDisplay.textContent = absent;
    rateDisplay.textContent = rate + "%";
  }

  // Attach listener to all radio buttons
  radioButtons.forEach((radio) => {
    radio.addEventListener("change", updateSummary);
  });

  // Initial calculation on page load
  updateSummary();
});
