document.addEventListener("DOMContentLoaded", () => {
  // --- Handle Profile Update ---
  const saveProfileBtn = document.querySelector(".profile-form .btn-primary");
  
  if (saveProfileBtn) {
    saveProfileBtn.addEventListener("click", (e) => {
      // Prevent actual form submission for now (since it's a demo)
      e.preventDefault();
      
      // You can add validation logic here if needed
      
      alert("Profile details updated successfully!");
    });
  }

  // --- Handle Password Update ---
  const passwordSection = document.querySelector(".password-section");
  const updatePasswordBtn = passwordSection ? passwordSection.querySelector(".btn-primary") : null;

  if (updatePasswordBtn) {
    updatePasswordBtn.addEventListener("click", (e) => {
      e.preventDefault();
      
      const inputs = passwordSection.querySelectorAll("input");
      const currentPass = inputs[0].value;
      const newPass = inputs[1].value;
      const confirmPass = inputs[2].value;

      // Basic Validation
      if (!currentPass || !newPass || !confirmPass) {
        alert("Please fill in all password fields.");
        return;
      }

      if (newPass !== confirmPass) {
        alert("New password and Confirm password do not match!");
        return;
      }

      if (newPass.length < 6) {
        alert("New password must be at least 6 characters long.");
        return;
      }

      // Success
      alert("Password changed successfully!");
      
      // Clear fields
      inputs.forEach(input => input.value = "");
    });
  }
});