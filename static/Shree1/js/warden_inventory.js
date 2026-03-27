document.addEventListener('DOMContentLoaded', function() {
    // 1. SEARCH LOGIC
    // Jab user search input mein enter dabaye toh form submit ho jaye
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault(); // Default submit rokna agar zaroori ho
                this.closest('form').submit(); 
            }
        });
    }

    // 2. DYNAMIC STATUS UPDATE (Optional UI Polish)
    // Agar aap chahte hain ki typing karte hi status badge ka color change ho
    const qtyInputs = document.querySelectorAll('.qty-input');
    qtyInputs.forEach(input => {
        input.addEventListener('input', function() {
            const row = this.closest('tr');
            const currentStock = parseFloat(row.querySelector('.stock-val').innerText);
            const requiredStock = parseFloat(row.cells[3].innerText); // Required Stock column
            const change = parseFloat(this.value) || 0;
            
            const predictedStock = currentStock + change;
            const statusTag = row.querySelector('.status-tag');
            
            // Temporary UI feedback: Status change dikhana bina save kiye
            if (predictedStock < (requiredStock * 0.2)) {
                statusTag.className = 'status-tag critical';
                statusTag.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i> Critical';
            } else if (predictedStock < (requiredStock * 0.5)) {
                statusTag.className = 'status-tag low';
                statusTag.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Low';
            } else {
                statusTag.className = 'status-tag good';
                statusTag.innerHTML = '<i class="fa-solid fa-check"></i> Good';
            }
        });
    });
});