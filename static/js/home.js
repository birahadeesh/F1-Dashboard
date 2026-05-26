// F1 Dashboard 2025 — Home Page JS

document.addEventListener('DOMContentLoaded', function () {
    initNavbar();
    initScrollReveal();
    initSmoothScroll();
});

// Navbar scroll effect
function initNavbar() {
    const navbar = document.querySelector('.home-navbar');
    if (!navbar) return;
    const onScroll = () => {
        navbar.classList.toggle('scrolled', window.scrollY > 80);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
}

// Smooth scroll for anchor links
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', e => {
            const target = document.querySelector(a.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

// Scroll reveal using IntersectionObserver
function initScrollReveal() {
    const els = document.querySelectorAll('.reveal');
    if (!els.length) return;
    const obs = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
                obs.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    els.forEach(el => obs.observe(el));
}