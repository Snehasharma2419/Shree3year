document.addEventListener("DOMContentLoaded", () => {
  // Handle Approve Buttons
  const approveBtns = document.querySelectorAll(".btn-approve");
  approveBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      // In a real app, you would send an AJAX request to Django here
      if (confirm("Are you sure you want to approve this leave request?")) {
        const row = this.closest("tr");
        const statusSpan = row.querySelector(".status");

        // Visual update for demo
        statusSpan.textContent = "Approved";
        statusSpan.classList.remove("pending");
        statusSpan.style.backgroundColor = "#dcfce7";
        statusSpan.style.color = "#16a34a";

        // Disable buttons after action
        row.querySelectorAll("button").forEach((b) => (b.disabled = true));
        alert("Leave Approved Successfully");
      }
    });
  });

  // Handle Reject Buttons
  const rejectBtns = document.querySelectorAll(".btn-reject");
  rejectBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      if (confirm("Are you sure you want to reject this leave request?")) {
        const row = this.closest("tr");
        const statusSpan = row.querySelector(".status");

        // Visual update for demo
        statusSpan.textContent = "Rejected";
        statusSpan.classList.remove("pending");
        statusSpan.style.backgroundColor = "#fee2e2";
        statusSpan.style.color = "#dc2626";

        // Disable buttons after action
        row.querySelectorAll("button").forEach((b) => (b.disabled = true));
        alert("Leave Rejected");
      }
    });
  });
});
