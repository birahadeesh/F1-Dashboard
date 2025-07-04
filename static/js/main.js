/**
 * F1 Dashboard JavaScript
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss flash messages after 5 seconds
    setTimeout(function () {
        const flashMessages = document.querySelectorAll('.alert');
        flashMessages.forEach(message => {
            const bsAlert = new bootstrap.Alert(message);
            bsAlert.close();
        });
    }, 5000);

    // Enable tooltips everywhere
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle active navigation links
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');

    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath && currentLocation === linkPath) {
            link.classList.add('active');
        }
    });

    // Add loading spinners to tab content when switching tabs
    const tabEls = document.querySelectorAll('button[data-bs-toggle="tab"]');
    if (tabEls.length > 0) {
        tabEls.forEach(tabEl => {
            tabEl.addEventListener('shown.bs.tab', function (event) {
                // Get newly activated tab
                const activeTab = event.target;
                const tabContentId = activeTab.getAttribute('data-bs-target');
                const tabContent = document.querySelector(tabContentId);

                // Add loading animation to tables with many rows
                const table = tabContent.querySelector('table');
                if (table && table.querySelectorAll('tbody tr').length > 10) {
                    animateTableRows(table);
                }
            });
        });

        // Pre-animate the initially visible tab's table
        const activeTab = document.querySelector('.tab-pane.active');
        if (activeTab) {
            const table = activeTab.querySelector('table');
            if (table) {
                animateTableRows(table);
            }
        }
    }

    // Animate F1 car on the hero banner
    createF1CarAnimation();

    // Add racing line effects to cards
    addRacingLineEffects();
});

/**
 * Animate table rows with a staggered fade-in effect
 */
function animateTableRows(table) {
    const rows = table.querySelectorAll('tbody tr');

    rows.forEach((row, index) => {
        // Reset any existing animation
        row.style.opacity = '0';
        row.style.transform = 'translateY(10px)';

        // Apply staggered animation
        setTimeout(() => {
            row.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            row.style.opacity = '1';
            row.style.transform = 'translateY(0)';
        }, 50 * index);
    });
}

/**
 * Create dynamic F1 car animation
 */
function createF1CarAnimation() {
    const heroBanner = document.querySelector('.hero-banner');
    if (!heroBanner) return;

    // Add multiple cars with different speeds
    const speeds = [15, 18, 12];

    speeds.forEach((speed, index) => {
        const car = document.createElement('div');
        car.classList.add('f1-car');
        car.style.bottom = `${10 + (index * 20)}px`;
        car.style.opacity = `${0.7 - (index * 0.2)}`;
        car.style.animation = `raceCar ${speed}s infinite linear`;
        car.style.animationDelay = `${index * 2}s`;

        heroBanner.appendChild(car);
    });
}

/**
 * Add racing line effects to various elements
 */
function addRacingLineEffects() {
    const raceCards = document.querySelectorAll('.race-card');

    raceCards.forEach((card, index) => {
        // Add hover effect that shows a racing line
        card.addEventListener('mouseenter', function () {
            this.style.overflow = 'hidden';

            const line = document.createElement('div');
            line.style.position = 'absolute';
            line.style.height = '2px';
            line.style.background = 'var(--f1-red)';
            line.style.left = '-100%';
            line.style.bottom = '0';
            line.style.width = '100%';
            line.style.transition = 'transform 0.3s ease';
            line.style.transform = 'translateX(100%)';

            this.appendChild(line);

            // Trigger animation
            setTimeout(() => {
                line.style.transform = 'translateX(100%)';
            }, 10);
        });

        card.addEventListener('mouseleave', function () {
            const line = this.querySelector('div[style*="position: absolute"]');
            if (line) {
                line.remove();
            }
        });
    });
}