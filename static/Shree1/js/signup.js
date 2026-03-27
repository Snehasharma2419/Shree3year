// signup.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    
    form.onsubmit = function(e) {
        const password = document.querySelector('.pass-field').value;
        const confirm = document.querySelector('.confirm-field').value;

        if (password !== confirm) {
            e.preventDefault(); // Prevent Django from receiving mismatched passwords
            alert("Passwords do not match! Please try again.");
        }
    };
});