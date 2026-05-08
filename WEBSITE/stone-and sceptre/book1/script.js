document.addEventListener('DOMContentLoaded', function () {

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function (link) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Fade-in sections via IntersectionObserver
    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -100px 0px' });

    document.querySelectorAll('.content-section').forEach(function (section) {
        observer.observe(section);
    });

    // Journey map: animate route points in sequence
    document.querySelectorAll('.route-point').forEach(function (point, index) {
        setTimeout(function () {
            point.style.opacity = '1';
            point.style.transform = 'scale(1)';
        }, index * 500);
    });

    // --- RAF-gated scroll handlers ---

    // 1. Active nav link tracking
    let navTicking = false;
    window.addEventListener('scroll', function () {
        if (!navTicking) {
            requestAnimationFrame(function () {
                const sections = document.querySelectorAll('section[id]');
                const navLinks = document.querySelectorAll('.main-nav a');
                let current = '';
                sections.forEach(function (section) {
                    if (window.pageYOffset >= section.offsetTop - 100 &&
                        window.pageYOffset < section.offsetTop + section.offsetHeight) {
                        current = section.getAttribute('id');
                    }
                });
                navLinks.forEach(function (link) {
                    link.classList.toggle('active', link.getAttribute('href') === '#' + current);
                });
                navTicking = false;
            });
            navTicking = true;
        }
    }, { passive: true });

    // 2. Scroll-to-top button visibility
    const scrollTopBtn = document.querySelector('.scroll-top');
    let scrollTopTicking = false;
    window.addEventListener('scroll', function () {
        if (!scrollTopTicking) {
            requestAnimationFrame(function () {
                scrollTopBtn.classList.toggle('visible', window.scrollY > 400);
                scrollTopTicking = false;
            });
            scrollTopTicking = true;
        }
    }, { passive: true });

    if (scrollTopBtn) {
        scrollTopBtn.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // 3. Hero parallax
    let parallaxTicking = false;
    window.addEventListener('scroll', function () {
        if (!parallaxTicking) {
            requestAnimationFrame(function () {
                const scrolled = window.pageYOffset;
                const rate = scrolled * -0.5;
                const stormClouds = document.querySelector('.storm-clouds');
                const divineLight = document.querySelector('.divine-light');
                const seaWaves = document.querySelector('.sea-waves');
                const mysticalIslands = document.querySelector('.mystical-islands');
                if (stormClouds) stormClouds.style.transform = 'translateY(' + (rate * 0.3) + 'px)';
                if (divineLight) divineLight.style.transform = 'translateX(-50%) translateY(' + (rate * 0.2) + 'px)';
                if (seaWaves) seaWaves.style.transform = 'translateY(' + (rate * 0.4) + 'px)';
                if (mysticalIslands) mysticalIslands.style.transform = 'translateY(' + (rate * 0.1) + 'px)';
                parallaxTicking = false;
            });
            parallaxTicking = true;
        }
    }, { passive: true });

    // Stone of Destiny hover glow
    const stone = document.querySelector('.stone-of-destiny');
    if (stone) {
        stone.addEventListener('mouseenter', function () {
            this.style.boxShadow = '0 0 40px rgba(255,215,0,1), 0 0 60px rgba(255,215,0,0.8)';
            this.style.transform = 'translateX(-50%) scale(1.2)';
        });
        stone.addEventListener('mouseleave', function () {
            this.style.boxShadow = '0 0 20px rgba(255,215,0,0.8)';
            this.style.transform = 'translateX(-50%) scale(1)';
        });
    }
});
