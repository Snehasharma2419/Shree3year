document.addEventListener('DOMContentLoaded', function() {
    // 1. Dynamic Greeting based on time
    const introHeader = document.querySelector('.intro h1');
    const hour = new Date().getHours();
    let greeting = "Worker Dashboard";

    if (hour < 12) greeting = "Good Morning, Worker";
    else if (hour < 18) greeting = "Good Afternoon, Worker";
    else greeting = "Good Evening, Worker";
    
    if(introHeader) introHeader.innerText = greeting;

    // 2. Animation for Stat Cards (Counter effect)
    const stats = document.querySelectorAll('.stat-info h3');
    stats.forEach(stat => {
        stat.style.transition = "transform 0.3s ease";
        stat.addEventListener('mouseenter', () => {
            stat.style.transform = "scale(1.1)";
        });
        stat.addEventListener('mouseleave', () => {
            stat.style.transform = "scale(1)";
        });
    });

    // 3. Simple Notification Alert
    const notifications = document.querySelectorAll('.notification');
    notifications.forEach(note => {
        note.addEventListener('click', function() {
            const text = this.querySelector('div').innerText;
            alert("Notification Detail: " + text);
        });
    });

    // 4. Logout Confirmation
    const logoutBtn = document.querySelector('.logout-btn');
    if (logoutBtn) {
        logoutBtn.onclick = function(e) {
            if (!confirm("Are you sure you want to logout?")) {
                e.preventDefault();
            }
        };
    }
});