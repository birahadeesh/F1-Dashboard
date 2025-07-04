// F1 Dashboard Home Page JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Initialize all elements that need JavaScript functionality
    initNavbar();
    initPitStopCountdown();
    initScrollAnimation();

    // Add animation classes to elements when they come into view
    initScrollReveal();
});

// Navbar background change on scroll
function initNavbar() {
    const navbar = document.querySelector('.home-navbar');
    if (!navbar) return;

    window.addEventListener('scroll', function () {
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Smooth scrolling for navbar links
    document.querySelectorAll('.nav-link[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Pit Stop Countdown Animation
function initPitStopCountdown() {
    const pitLights = document.querySelectorAll('.pit-light');
    if (pitLights.length === 0) return;

    function startSequence() {
        // Reset all lights
        pitLights.forEach(light => {
            light.classList.remove('red');
            light.classList.remove('green');
        });

        // Red lights sequence
        let currentLight = 0;

        const redInterval = setInterval(() => {
            if (currentLight < pitLights.length) {
                pitLights[currentLight].classList.add('red');
                currentLight++;
            } else {
                clearInterval(redInterval);

                // Wait and then turn all lights green
                setTimeout(() => {
                    pitLights.forEach(light => {
                        light.classList.remove('red');
                        light.classList.add('green');
                    });

                    // Reset after a few seconds
                    setTimeout(() => {
                        pitLights.forEach(light => {
                            light.classList.remove('green');
                        });

                        // Restart the sequence after a pause
                        setTimeout(startSequence, 3000);
                    }, 2000);
                }, 1000);
            }
        }, 500);
    }

    // Start the initial sequence
    startSequence();
}

// Smooth scroll animation for the scroll down button
function initScrollAnimation() {
    const scrollDownButton = document.querySelector('.scroll-down a');
    if (!scrollDownButton) return;

    scrollDownButton.addEventListener('click', function (e) {
        e.preventDefault();

        const targetSection = document.querySelector(this.getAttribute('href'));
        if (targetSection) {
            targetSection.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
}

// Add animation to elements when they come into view
function initScrollReveal() {
    const elements = document.querySelectorAll('.preview-card, .circuit, .about-content, .about-image');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.15
    });

    elements.forEach(element => {
        observer.observe(element);
        element.classList.add('reveal-item');
    });
}

// Circuit carousel functionality
document.addEventListener('DOMContentLoaded', function () {
    const prevButton = document.querySelector('.carousel-control-prev');
    const nextButton = document.querySelector('.carousel-control-next');
    const carouselItems = document.querySelectorAll('.carousel-item');

    if (!prevButton || !nextButton || carouselItems.length === 0) return;

    // Initialize first item as active
    carouselItems[0].classList.add('active');

    let currentIndex = 0;

    nextButton.addEventListener('click', function () {
        carouselItems[currentIndex].classList.remove('active');
        currentIndex = (currentIndex + 1) % carouselItems.length;
        carouselItems[currentIndex].classList.add('active');
    });

    prevButton.addEventListener('click', function () {
        carouselItems[currentIndex].classList.remove('active');
        currentIndex = (currentIndex - 1 + carouselItems.length) % carouselItems.length;
        carouselItems[currentIndex].classList.add('active');
    });
});

// F1 car animation on hover for about section
document.addEventListener('DOMContentLoaded', function () {
    const carElement = document.querySelector('.f1-car-animation');
    if (!carElement) return;

    const aboutSection = document.querySelector('.about-section');
    if (!aboutSection) return;

    aboutSection.addEventListener('mouseenter', function () {
        carElement.classList.add('racing');
    });

    aboutSection.addEventListener('mouseleave', function () {
        carElement.classList.remove('racing');
    });
});

// Add additional styles for scroll reveal animations
document.addEventListener('DOMContentLoaded', function () {
    const style = document.createElement('style');
    style.innerHTML = `
        .reveal-item {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.8s ease, transform 0.8s ease;
        }
        
        .reveal-item.revealed {
            opacity: 1;
            transform: translateY(0);
        }
        
        .circuit.reveal-item {
            transform: translateY(30px) scale(0.95);
        }
        
        .circuit.reveal-item.revealed {
            transform: translateY(0) scale(1);
        }
    `;
    document.head.appendChild(style);
}); 