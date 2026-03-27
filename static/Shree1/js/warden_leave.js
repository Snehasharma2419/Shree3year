// Function ko window scope mein rakhein taaki HTML access kar sake
window.toggleModal = function(show) {
    const modal = document.getElementById('leaveModal');
    if (modal) {
        modal.style.display = show ? 'flex' : 'none';
    } else {
        console.error("Error: 'leaveModal' ID wala element nahi mila!");
    }
};

// NEW: Warden vs Worker selection logic handle karne ke liye
window.toggleEmployeeSelect = function() {
    const actionSelect = document.getElementById('actionSelect');
    const employeeGroup = document.getElementById('employeeSelectGroup');
    const workerSelect = document.getElementById('worker_id_select');

    if (actionSelect.value === 'self') {
        employeeGroup.style.display = 'none'; // Warden ke liye dropdown hide karein
        workerSelect.required = false;       // Validation hata dein
    } else {
        employeeGroup.style.display = 'block'; // Worker ke liye dropdown show karein
        workerSelect.required = true;
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('leaveModal');

    // Modal ke bahar click karne par band karein
    window.onclick = function(event) {
        if (event.target === modal) {
            window.toggleModal(false);
        }
    };

    // ESC key se modal band karein
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            window.toggleModal(false);
        }
    });

    // View Details Button logic
    const viewBtns = document.querySelectorAll('.btn-view');
    viewBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const row = e.target.closest('tr');
            if (row) {
                const name = row.cells[0].innerText;
                alert("Viewing details for: " + name);
            }
        });
    });
});