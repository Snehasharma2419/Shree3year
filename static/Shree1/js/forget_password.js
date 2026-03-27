document.getElementById('resetForm').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent the form from actually submitting to a server for this demo

    const userId = document.getElementById('userId').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    // Basic Validation
    if (newPassword !== confirmPassword) {
        alert("Passwords do not match. Please try again.");
        return;
    }

    if (newPassword.length < 5) {
        alert("Password must be at least 5 characters long.");
        return;
    }

    // Success Simulation
    console.log("Form Submitted Successfully");
    console.log("User ID:", userId);
    console.log("New Password:", newPassword);
    
    alert("Password reset successful for User ID: " + userId);
    // Here you would typically send the data to your backend
});