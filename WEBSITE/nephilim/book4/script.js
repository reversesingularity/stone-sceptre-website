// The Jerusalem Indictment: The Nephilim Chronicles Book Four — Coming Soon
// Vanilla JS only. No external libraries.

document.addEventListener('DOMContentLoaded', function () {
    initializeNavigation();
    initializeScrollEffects();
    initializeAnimations();
    initializeWaitlistCTA();
});

/* ═══════════════════════════════════════════════════
   NAVIGATION
═══════════════════════════════════════════════════ */
function initializeNavigation() {
    const navbar    = document.querySelector('.navbar');
    const navLinks  = document.querySelectorAll('.nav-menu a');
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu   = document.querySelector('.nav-menu');

    let navTicking = false;
    window.addEventListener('scroll', function () {
        if (!navTicking) {
            requestAnimationFrame(function () {
                if (navbar) navbar.classList.toggle('scrolled', window.scrollY > 100);
                navTicking = false;
            });
            navTicking = true;
        }
    }, { passive: true });

    navLinks.forEach(function (link) {
        link.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href && href.startsWith('#')) {
                e.preventDefault();
                const targetEl = document.getElementById(href.substring(1));
                if (targetEl) {
                    const bannerH = (document.querySelector('.series-banner') || { offsetHeight: 0 }).offsetHeight;
                    const navH    = navbar ? navbar.offsetHeight : 0;
                    const top     = targetEl.getBoundingClientRect().top + window.pageYOffset - bannerH - navH - 24;
                    window.scrollTo({ top: Math.max(0, top), behavior: 'smooth' });
                }
                if (navMenu) navMenu.classList.remove('nav-open');
            }
        });
    });

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function () {
            navMenu.classList.toggle('nav-open');
            this.setAttribute('aria-expanded', navMenu.classList.contains('nav-open'));
        });
    }

    let activeTicking = false;
    window.addEventListener('scroll', function () {
        if (!activeTicking) {
            requestAnimationFrame(function () {
                updateActiveNav();
                activeTicking = false;
            });
            activeTicking = true;
        }
    }, { passive: true });
}

function updateActiveNav() {
    const navbar    = document.querySelector('.navbar');
    const banner    = document.querySelector('.series-banner');
    const offset    = (navbar ? navbar.offsetHeight : 0) + (banner ? banner.offsetHeight : 0) + 60;
    const scrollPos = window.scrollY + offset;
    let   current   = '';

    document.querySelectorAll('section[id]').forEach(function (sec) {
        if (scrollPos >= sec.offsetTop && scrollPos < sec.offsetTop + sec.offsetHeight) {
            current = sec.id;
        }
    });

    document.querySelectorAll('.nav-menu a').forEach(function (link) {
        link.classList.toggle('active', link.getAttribute('href') === '#' + current);
    });
}

/* ═══════════════════════════════════════════════════
   SCROLL EFFECTS
═══════════════════════════════════════════════════ */
function initializeScrollEffects() {
    const scrollBtn = document.querySelector('.scroll-top');
    if (scrollBtn) {
        let btnTicking = false;
        window.addEventListener('scroll', function () {
            if (!btnTicking) {
                requestAnimationFrame(function () {
                    scrollBtn.classList.toggle('visible', window.scrollY > 300);
                    btnTicking = false;
                });
                btnTicking = true;
            }
        }, { passive: true });
        scrollBtn.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
}

/* ═══════════════════════════════════════════════════
   STAGGERED CARD ANIMATIONS
═══════════════════════════════════════════════════ */
function initializeAnimations() {
    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry, i) {
            if (entry.isIntersecting) {
                setTimeout(function () {
                    entry.target.classList.add('animate-fade-in-up');
                }, i * 80);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.08 });

    document.querySelectorAll(
        '.feature-card, .testimonial-card, .available-card, .section-title, .synopsis-content'
    ).forEach(function (el) {
        observer.observe(el);
    });
}

/* ═══════════════════════════════════════════════════
   WAITLIST CTA — smooth scroll to form
═══════════════════════════════════════════════════ */
function initializeWaitlistCTA() {
    const ctaBtn = document.querySelector('.sticky-cta-btn');
    if (!ctaBtn) return;

    ctaBtn.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href && href.startsWith('#')) {
            e.preventDefault();
            const targetEl = document.getElementById(href.substring(1));
            if (targetEl) {
                const navbar  = document.querySelector('.navbar');
                const banner  = document.querySelector('.series-banner');
                const offset  = (navbar ? navbar.offsetHeight : 0) + (banner ? banner.offsetHeight : 0) + 24;
                const top     = targetEl.getBoundingClientRect().top + window.pageYOffset - offset;
                window.scrollTo({ top: Math.max(0, top), behavior: 'smooth' });
                const firstInput = targetEl.querySelector('input[type="email"]');
                if (firstInput) setTimeout(function () { firstInput.focus(); }, 600);
            }
        }
    });
}
