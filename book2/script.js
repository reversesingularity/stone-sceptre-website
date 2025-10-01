// The Red Hand & The Eternal Throne: A Bard's Chronicle - JavaScript Functionality

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeScrollEffects();
    initializeAnimations();
    initializeBookInteractions();
    initializeResponsiveFeatures();
});

// Navigation functionality
function initializeNavigation() {
    const navbar = document.querySelector('.navbar');
    const navLinks = document.querySelectorAll('.nav-menu a');
    
    // Handle scroll effects on navbar
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Smooth scrolling for navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Only handle anchor links
            if (href.startsWith('#')) {
                e.preventDefault();
                
                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    const navbarHeight = navbar.offsetHeight;
                    const targetPosition = targetElement.offsetTop - navbarHeight;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                    
                    // Update active nav link
                    updateActiveNavLink(targetId);
                }
            }
        });
    });
    
    // Update active navigation link based on scroll position
    window.addEventListener('scroll', function() {
        updateActiveNavLinkOnScroll();
    });
}

// Update active navigation link
function updateActiveNavLink(activeId) {
    const navLinks = document.querySelectorAll('.nav-menu a');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${activeId}`) {
            link.classList.add('active');
        }
    });
}

// Update active navigation link based on scroll position
function updateActiveNavLinkOnScroll() {
    const sections = document.querySelectorAll('section[id]');
    const navbarHeight = document.querySelector('.navbar').offsetHeight;
    const scrollPosition = window.scrollY + navbarHeight + 100;
    
    let currentSection = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        
        if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            currentSection = section.getAttribute('id');
        }
    });
    
    if (currentSection) {
        updateActiveNavLink(currentSection);
    }
}

// Scroll effects and animations
function initializeScrollEffects() {
    // Back to top button
    const backToTopButton = document.querySelector('.back-to-top');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            backToTopButton.classList.add('visible');
        } else {
            backToTopButton.classList.remove('visible');
        }
    });
    
    // Parallax effect for hero section
    const hero = document.querySelector('.hero');
    if (hero) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            hero.style.transform = `translate3d(0, ${rate}px, 0)`;
        });
    }
    
    // Intersection Observer for animation triggers
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animateElements = document.querySelectorAll('.character-card, .chapter-card, .synopsis-content, .author-content');
    animateElements.forEach(element => {
        observer.observe(element);
    });
}

// Animation functionality
function initializeAnimations() {
    // Staggered animations for character cards
    const characterCards = document.querySelectorAll('.character-card');
    
    const cardObserver = new IntersectionObserver(function(entries) {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('animate-fade-in-up');
                }, index * 100);
            }
        });
    }, { threshold: 0.1 });
    
    characterCards.forEach(card => {
        cardObserver.observe(card);
    });
    
    // Chapter cards animation
    const chapterCards = document.querySelectorAll('.chapter-card');
    
    const chapterObserver = new IntersectionObserver(function(entries) {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('animate-fade-in-up');
                }, index * 80);
            }
        });
    }, { threshold: 0.1 });
    
    chapterCards.forEach(card => {
        chapterObserver.observe(card);
    });
    
    // Title animations
    const sectionTitles = document.querySelectorAll('.section-title');
    
    const titleObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
            }
        });
    }, { threshold: 0.5 });
    
    sectionTitles.forEach(title => {
        titleObserver.observe(title);
    });
}

// Book interaction functionality
function initializeBookInteractions() {
    const bookCover = document.querySelector('.book-cover');
    
    if (bookCover) {
        // 3D hover effect
        bookCover.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05) rotateY(5deg)';
        });
        
        bookCover.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) rotateY(0deg)';
        });
        
        // Book preview functionality (placeholder)
        bookCover.addEventListener('click', function() {
            openBookPreview();
        });
    }
}

// Book preview modal (placeholder functionality)
function openBookPreview() {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.className = 'book-preview-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>The Red Hand & The Eternal Throne</h3>
                <button class="modal-close" onclick="closeBookPreview()">&times;</button>
            </div>
            <div class="modal-body">
                <p><strong>Book 2 of The Stone and the Sceptre Chronicles</strong></p>
                <p><em>A Chronicle of the House of Míl Espáine</em></p>
                <p><em>As recorded by Taliesin the Wise-Tongued</em></p>
                <p><em>Bard to King Gathelus of the Celtiberians</em></p>
                <hr>
                <p><strong>Genre:</strong> Christian Historical Fiction / Epic Fantasy</p>
                <p><strong>Setting:</strong> Celtiberian Iberia, 6th Century BCE</p>
                <p><strong>Word Count:</strong> Approximately 150,000 words</p>
                <hr>
                <p>In the days when empires rose and fell like waves upon the shore, when the God of Abraham moved among the nations to accomplish His eternal purposes, there came to the western lands of Iberia a company of exiles bearing within their hearts the weight of promises older than kingdoms...</p>
            </div>
            <div class="modal-footer">
                <button class="btn primary" onclick="window.location.href='#synopsis'">Read Synopsis</button>
                <button class="btn secondary" onclick="closeBookPreview()">Close</button>
            </div>
        </div>
    `;
    
    // Add modal styles
    const modalStyles = `
        .book-preview-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            opacity: 0;
            animation: fadeIn 0.3s ease forwards;
        }
        
        .modal-content {
            background: var(--bg-primary);
            border: 2px solid var(--primary-gold);
            border-radius: var(--border-radius);
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            transform: scale(0.8);
            animation: modalSlideIn 0.3s ease forwards;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.5rem;
            border-bottom: 1px solid var(--primary-gold);
        }
        
        .modal-header h3 {
            color: var(--primary-gold);
            margin: 0;
        }
        
        .modal-close {
            background: none;
            border: none;
            color: var(--text-light);
            font-size: 2rem;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .modal-body {
            padding: 1.5rem;
            color: var(--text-light);
        }
        
        .modal-body hr {
            border: none;
            border-top: 1px solid var(--primary-gold);
            margin: 1rem 0;
            opacity: 0.3;
        }
        
        .modal-footer {
            padding: 1.5rem;
            border-top: 1px solid var(--primary-gold);
            display: flex;
            gap: 1rem;
            justify-content: flex-end;
        }
        
        @keyframes fadeIn {
            to { opacity: 1; }
        }
        
        @keyframes modalSlideIn {
            to { transform: scale(1); }
        }
    `;
    
    // Add styles to head if not already present
    if (!document.querySelector('#modal-styles')) {
        const styleSheet = document.createElement('style');
        styleSheet.id = 'modal-styles';
        styleSheet.textContent = modalStyles;
        document.head.appendChild(styleSheet);
    }
    
    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';
    
    // Close modal when clicking outside
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeBookPreview();
        }
    });
}

// Close book preview modal
function closeBookPreview() {
    const modal = document.querySelector('.book-preview-modal');
    if (modal) {
        modal.style.animation = 'fadeOut 0.3s ease forwards';
        setTimeout(() => {
            document.body.removeChild(modal);
            document.body.style.overflow = '';
        }, 300);
    }
}

// Responsive features
function initializeResponsiveFeatures() {
    // Mobile menu toggle (if needed in future)
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
    }
    
    // Responsive font sizing
    function adjustFontSizes() {
        const viewportWidth = window.innerWidth;
        const root = document.documentElement;
        
        if (viewportWidth < 480) {
            root.style.fontSize = '14px';
        } else if (viewportWidth < 768) {
            root.style.fontSize = '15px';
        } else {
            root.style.fontSize = '16px';
        }
    }
    
    // Adjust on load and resize
    adjustFontSizes();
    window.addEventListener('resize', adjustFontSizes);
}

// Scroll to top function
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Performance optimization for scroll events
const debouncedScrollHandler = debounce(function() {
    // Handle scroll events here if needed
}, 10);

window.addEventListener('scroll', debouncedScrollHandler);

// Add CSS animation keyframes dynamically
const additionalStyles = `
    @keyframes fadeOut {
        to { opacity: 0; }
    }
    
    @keyframes slideInLeft {
        from {
            transform: translateX(-100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .animate-slide-in-left {
        animation: slideInLeft 0.8s ease-out forwards;
    }
    
    .animate-slide-in-right {
        animation: slideInRight 0.8s ease-out forwards;
    }
`;

// Add additional styles to head
const additionalStyleSheet = document.createElement('style');
additionalStyleSheet.textContent = additionalStyles;
document.head.appendChild(additionalStyleSheet);

// Export functions for global access
window.scrollToTop = scrollToTop;
window.openBookPreview = openBookPreview;
window.closeBookPreview = closeBookPreview;