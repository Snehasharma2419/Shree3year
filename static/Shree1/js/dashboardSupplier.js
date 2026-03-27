document.addEventListener('DOMContentLoaded', function() {
    // Selectors
    const selectAll = document.getElementById('selectAll');
    const checkboxes = document.querySelectorAll('.item-checkbox');
    const dispatchBtn = document.getElementById('mainDispatchBtn');
    const form = document.getElementById('bulkDispatchForm');

    /**
     * 1. UPDATE BUTTON STATE
     * Iska kaam hai button ko enable/disable karna aur uska color badalna.
     */
    function updateButtonState() {
        if (!dispatchBtn) return;

        // Sirf un checkboxes ko count karo jo checked hain
        const checkedItems = document.querySelectorAll('.item-checkbox:checked');
        const checkedCount = checkedItems.length;
        
        if (checkedCount > 0) {
            // Button Enable karo aur Blue color (active-btn class) add karo
            dispatchBtn.disabled = false;
            dispatchBtn.classList.add('active-btn');
            dispatchBtn.innerHTML = `<i class="fa-solid fa-paper-plane"></i> Dispatch (${checkedCount}) Items`;
            dispatchBtn.style.cursor = "pointer";
        } else {
            // Button Disable karo aur Grey color rakho
            dispatchBtn.disabled = true;
            dispatchBtn.classList.remove('active-btn');
            dispatchBtn.innerHTML = `<i class="fa-solid fa-paper-plane"></i> Dispatch Selected`;
            dispatchBtn.style.cursor = "not-allowed";
        }
    }

    /**
     * 2. SELECT ALL LOGIC
     * Header waale checkbox par click karne se saare niche waale tick/untick honge.
     */
    if (selectAll) {
        selectAll.addEventListener('change', function() {
            checkboxes.forEach(cb => {
                cb.checked = selectAll.checked;
            });
            updateButtonState();
        });
    }

    /**
     * 3. INDIVIDUAL CHECKBOX LOGIC
     * Agar user manually ek-ek karke tick kare.
     */
    checkboxes.forEach(cb => {
        cb.addEventListener('change', function() {
            // Agar koi ek bhi uncheck kare, toh 'Select All' ko uncheck kar do
            if (!this.checked && selectAll) {
                selectAll.checked = false;
            }
            
            // Agar saare manually check ho jayein, toh 'Select All' ko tick kar do
            const allChecked = Array.from(checkboxes).every(c => c.checked);
            if (allChecked && selectAll) {
                selectAll.checked = true;
            }

            updateButtonState();
        });
    });

    /**
     * 4. FORM SUBMISSION & LOADING STATE
     * Click karne par spinner dikhayega taaki user ko pata chale processing ho rahi hai.
     */
    if (form) {
        form.addEventListener('submit', function(e) {
            const checkedCount = document.querySelectorAll('.item-checkbox:checked').length;
            
            if (checkedCount === 0) {
                e.preventDefault();
                alert("Atleast one item must be selected to dispatch.");
                return;
            }

            // Visual feedback
            dispatchBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing Batch...';
            dispatchBtn.style.opacity = "0.7";
            dispatchBtn.style.pointerEvents = "none"; // Double click prevention
        });
    }

    // Page load hote hi ek baar state check kar lo (in case of refresh with browser cache)
    updateButtonState();
});