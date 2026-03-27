document.addEventListener('DOMContentLoaded', () => {
    // 1. Sticky Navbar Effect on Scroll
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.padding = '10px 5%';
            navbar.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
        } else {
            navbar.style.background = 'white';
            navbar.style.padding = '15px 5%';
            navbar.style.boxShadow = 'none';
        }
    });

    // 2. Smooth Scrolling for Nav Links (Home, About, Help, Contact)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // 3. Simple Animation for Feature Cards on Hover
    const cards = document.querySelectorAll('.feature-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.borderColor = '#1a56db';
        });
        card.addEventListener('mouseleave', () => {
            card.style.borderColor = '#f1f5f9';
        });
    });

    // 4. Scroll Indicator Fade Out
    const scrollIndicator = document.querySelector('.scroll-indicator');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
            scrollIndicator.style.opacity = '0';
        } else {
            scrollIndicator.style.opacity = '1';
        }
    });
});