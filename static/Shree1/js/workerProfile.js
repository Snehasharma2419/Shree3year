document.addEventListener('DOMContentLoaded', () => {
    // Save Changes Button Click
    const saveBtn = document.querySelector('.btn-primary');
    saveBtn.addEventListener('click', () => {
        alert("Success: Profile details have been updated!");
    });

    // Simple Password validation simulation
    const updatePassBtn = document.querySelectorAll('.btn-primary')[1];
    updatePassBtn.addEventListener('click', () => {
        const inputs = document.querySelectorAll('input[type="password"]');
        if (inputs[1].value !== inputs[2].value) {
            alert("Error: New passwords do not match!");
        } else if (inputs[1].value === "") {
            alert("Error: Please enter a new password.");
        } else {
            alert("Success: Password changed successfully!");
        }
    });
});