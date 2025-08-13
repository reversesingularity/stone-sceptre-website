// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Parallax effect for hero section elements
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        
        // Move background elements at different speeds for depth
        const stormClouds = document.querySelector('.storm-clouds');
        const divineLight = document.querySelector('.divine-light');
        const seaWaves = document.querySelector('.sea-waves');
        const mysticalIslands = document.querySelector('.mystical-islands');
        
        if (stormClouds) {
            stormClouds.style.transform = `translateY(${rate * 0.3}px)`;
        }
        
        if (divineLight) {
            divineLight.style.transform = `translateX(-50%) translateY(${rate * 0.2}px)`;
        }
        
        if (seaWaves) {
            seaWaves.style.transform = `translateY(${rate * 0.4}px)`;
        }
        
        if (mysticalIslands) {
            mysticalIslands.style.transform = `translateY(${rate * 0.1}px)`;
        }
    });

    // Fade in animation for content sections
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);

    // Observe all content sections
    const contentSections = document.querySelectorAll('.content-section');
    contentSections.forEach(section => {
        observer.observe(section);
    });

    // Add active class to navigation based on scroll position
    window.addEventListener('scroll', function() {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.main-nav a');
        
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            const sectionHeight = section.offsetHeight;
            
            if (window.pageYOffset >= sectionTop && 
                window.pageYOffset < sectionTop + sectionHeight) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });

    // Enhanced character card hover effects
    const characterCards = document.querySelectorAll('.character-card');
    characterCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
            this.style.boxShadow = '0 15px 35px rgba(212, 175, 55, 0.3)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.3)';
        });
    });

    // Chapter card hover effects
    const chapterCards = document.querySelectorAll('.chapter-card');
    chapterCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const chapterNumber = this.querySelector('.chapter-number');
            if (chapterNumber) {
                chapterNumber.style.background = 'linear-gradient(135deg, #ffd700 0%, #ffed4e 100%)';
                chapterNumber.style.color = '#0a1133';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            const chapterNumber = this.querySelector('.chapter-number');
            if (chapterNumber) {
                chapterNumber.style.background = 'linear-gradient(135deg, #d4af37 0%, #c9a961 100%)';
                chapterNumber.style.color = '#0a1133';
            }
        });
    });

    // Journey map animation
    const journeyPoints = document.querySelectorAll('.route-point');
    journeyPoints.forEach((point, index) => {
        setTimeout(() => {
            point.style.opacity = '1';
            point.style.transform = 'scale(1)';
        }, index * 500);
    });

    // Add typing effect to main title
    const mainTitle = document.querySelector('.main-title');
    if (mainTitle) {
        const titleText = mainTitle.textContent;
        mainTitle.textContent = '';
        mainTitle.style.borderRight = '3px solid #d4af37';
        
        let index = 0;
        function typeWriter() {
            if (index < titleText.length) {
                mainTitle.textContent += titleText.charAt(index);
                index++;
                setTimeout(typeWriter, 100);
            } else {
                setTimeout(() => {
                    mainTitle.style.borderRight = 'none';
                }, 1000);
            }
        }
        
        setTimeout(typeWriter, 1000);
    }

    // Add glow effect to stone of destiny on hover
    const stoneOfDestiny = document.querySelector('.stone-of-destiny');
    if (stoneOfDestiny) {
        stoneOfDestiny.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 0 40px rgba(255, 215, 0, 1), 0 0 60px rgba(255, 215, 0, 0.8)';
            this.style.transform = 'translateX(-50%) scale(1.2)';
        });
        
        stoneOfDestiny.addEventListener('mouseleave', function() {
            this.style.boxShadow = '0 0 20px rgba(255, 215, 0, 0.8)';
            this.style.transform = 'translateX(-50%) scale(1)';
        });
    }
});

// Lightning animation trigger
function triggerLightning() {
    const lightning = document.querySelector('.lightning');
    if (lightning) {
        lightning.style.opacity = '1';
        setTimeout(() => {
            lightning.style.opacity = '0';
        }, 200);
    }
}

// Trigger lightning every 8-12 seconds
setInterval(() => {
    if (Math.random() > 0.5) {
        triggerLightning();
    }
}, Math.random() * 4000 + 8000);
