// The Cauldron of God: The Nephilim Chronicles Book Two
// JavaScript — Vanilla JS only, no external libraries

document.addEventListener('DOMContentLoaded', function () {
    initializeNavigation();
    initializeScrollEffects();
    initializeAnimations();
    initializeBookInteractions();
    initializeResponsiveFeatures();
});

function initializeNavigation() {
    const navbar    = document.querySelector('.navbar');
    const navLinks  = document.querySelectorAll('.nav-menu a');
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu   = document.querySelector('.nav-menu');

    window.addEventListener('scroll', function () {
        if (window.scrollY > 100) { navbar.classList.add('scrolled'); }
        else { navbar.classList.remove('scrolled'); }
    });

    navLinks.forEach(function (link) {
        link.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href && href.startsWith('#')) {
                e.preventDefault();
                const targetId      = href.substring(1);
                const targetElement = document.getElementById(targetId);
                if (targetElement) {
                    const bannerHeight = (document.querySelector('.series-banner') || { offsetHeight: 0 }).offsetHeight;
                    const navbarHeight = navbar.offsetHeight;
                    const totalOffset  = bannerHeight + navbarHeight + 24;
                    const targetTop    = targetElement.getBoundingClientRect().top + window.pageYOffset - totalOffset;
                    window.scrollTo({ top: Math.max(0, targetTop), behavior: 'smooth' });
                    updateActiveNavLink(targetId);
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

    window.addEventListener('scroll', updateActiveNavLinkOnScroll);
}

function updateActiveNavLink(activeId) {
    document.querySelectorAll('.nav-menu a').forEach(function (link) {
        link.classList.remove('active');
        if (link.getAttribute('href') === '#' + activeId) { link.classList.add('active'); }
    });
}

function updateActiveNavLinkOnScroll() {
    const navbar      = document.querySelector('.navbar');
    const banner      = document.querySelector('.series-banner');
    const totalOffset = (navbar ? navbar.offsetHeight : 0) + (banner ? banner.offsetHeight : 0) + 60;
    const scrollPos   = window.scrollY + totalOffset;
    let   currentSection = '';
    document.querySelectorAll('section[id]').forEach(function (section) {
        if (scrollPos >= section.offsetTop && scrollPos < section.offsetTop + section.offsetHeight) {
            currentSection = section.id;
        }
    });
    if (currentSection) updateActiveNavLink(currentSection);
}

function initializeScrollEffects() {
    const scrollBtn = document.querySelector('.scroll-top, .back-to-top');
    if (scrollBtn) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 300) { scrollBtn.classList.add('visible'); }
            else { scrollBtn.classList.remove('visible'); }
        });
        scrollBtn.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    const hero = document.querySelector('.hero');
    if (hero) {
        window.addEventListener('scroll', function () {
            hero.style.backgroundPositionY = (window.pageYOffset * -0.3) + 'px';
        });
    }

    const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -40px 0px' };
    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) { entry.target.classList.add('animate-fade-in-up'); }
        });
    }, observerOptions);
    document.querySelectorAll('.synopsis-content, .author-content').forEach(function (el) { observer.observe(el); });
}

function initializeAnimations() {
    const charObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry, index) {
            if (entry.isIntersecting) {
                setTimeout(function () { entry.target.classList.add('animate-fade-in-up'); }, index * 90);
                charObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.08 });
    document.querySelectorAll('.character-card').forEach(function (card) { charObserver.observe(card); });

    const chapObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry, index) {
            if (entry.isIntersecting) {
                setTimeout(function () { entry.target.classList.add('animate-fade-in-up'); }, index * 70);
                chapObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.06 });
    document.querySelectorAll('.chapter-card').forEach(function (card) { chapObserver.observe(card); });

    const titleObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) { entry.target.classList.add('animate-fade-in-up'); titleObserver.unobserve(entry.target); }
        });
    }, { threshold: 0.4 });
    document.querySelectorAll('.section-title').forEach(function (title) { titleObserver.observe(title); });
}

function initializeBookInteractions() {
    const bookCover = document.querySelector('.book-cover-3d');
    if (!bookCover) return;
    if (window.matchMedia('(hover: none)').matches) return;
    let isFlipped = false;

    bookCover.addEventListener('mousemove', function (e) {
        if (isFlipped) return;
        const rect    = this.getBoundingClientRect();
        const centerX = rect.left + rect.width  / 2;
        const centerY = rect.top  + rect.height / 2;
        const deltaX  = (e.clientX - centerX) / (rect.width  / 2);
        const deltaY  = (e.clientY - centerY) / (rect.height / 2);
        this.style.transform = 'rotateY(' + (-15 + deltaX * 8) + 'deg) rotateX(' + (5 - deltaY * 5) + 'deg)';
    });

    bookCover.addEventListener('mouseleave', function () {
        if (!isFlipped) { this.style.transform = 'rotateY(-15deg) rotateX(5deg)'; }
    });

    bookCover.addEventListener('click', function () {
        isFlipped = !isFlipped;
        this.style.transition = 'transform 0.7s ease';
        this.style.transform = isFlipped ? 'rotateY(165deg) rotateX(0deg) scale(1.03)' : 'rotateY(-15deg) rotateX(5deg)';
    });
}

function initializeResponsiveFeatures() {
    window.addEventListener('resize', function () { updateActiveNavLinkOnScroll(); });
}

function scrollToTop() { window.scrollTo({ top: 0, behavior: 'smooth' }); }