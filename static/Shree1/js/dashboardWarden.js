document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. LOGOUT CONFIRMATION ---
    // User ko galti se logout hone se bachane ke liye
    const logoutBtn = document.querySelector('.logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            if(!confirm("Are you sure you want to logout from SHREE?")) {
                e.preventDefault(); // Agar 'Cancel' dabaya toh logout ruk jayega
            }
        });
    }

    // --- 2. SIDEBAR NAVIGATION ---
    // Click karne par active class switch karne ke liye
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            navItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // --- 3. AUTO-REFRESH LOGIC (CRITICAL) ---
    // Jab tak delivery gate par nahi pahunchti, page check karta rahega
    const otpCard = document.querySelector('.otp-display-card');
    
    if (!otpCard) {
        // Agar koi incoming delivery nahi hai, toh har 30 seconds mein
        // page refresh hoga taaki naya OTP aate hi dikh jaye.
        setTimeout(() => {
            location.reload(); 
        }, 30000); 
    }

    // --- 4. SUCCESS/ERROR MESSAGES AUTO-HIDE ---
    // Django messages ko 5 second baad screen se hatane ke liye
    const alerts = document.querySelectorAll('.success-msg, .error-msg');
    alerts.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 500); // Smooth fade out
        }, 5000);
    });

});