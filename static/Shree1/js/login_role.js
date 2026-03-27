document.addEventListener('DOMContentLoaded', () => {
    const inputs = document.querySelectorAll('input[required]');
    const btn = document.querySelector('.login-submit-btn');

    inputs.forEach(input => {
        input.addEventListener('input', () => {
            const allFilled = Array.from(inputs).every(i => i.value.trim() !== "");
            if (allFilled) {
                btn.classList.add('btn-grow');
            } else {
                btn.classList.remove('btn-grow');
            }
        });
    });
});