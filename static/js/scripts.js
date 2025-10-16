// Real Estate Analyzer - Interactive JavaScript

// Create loading overlay
function createLoadingOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.innerHTML = `
        <div style="text-align: center;">
            <img src="/static/img/cat-loading.svg" alt="Loading..." style="width: 200px; height: 200px; margin-bottom: 1rem;">
            <h3 style="color: white; font-size: 1.5rem; margin-bottom: 0.5rem; font-weight: 700;">
                Kobi is Fetching Properties...
            </h3>
            <p style="color: rgba(255, 255, 255, 0.8); font-size: 1rem;">
                This might take a moment. Hang tight! 🐱
            </p>
            <div style="margin-top: 1.5rem;">
                <div class="loading-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
    
    // Add styles dynamically
    const style = document.createElement('style');
    style.textContent = `
        #loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.95), rgba(139, 92, 246, 0.95));
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            backdrop-filter: blur(10px);
        }
        
        .loading-dots {
            display: flex;
            gap: 8px;
            justify-content: center;
        }
        
        .loading-dots span {
            width: 12px;
            height: 12px;
            background: white;
            border-radius: 50%;
            animation: bounce-dot 1.4s infinite ease-in-out both;
        }
        
        .loading-dots span:nth-child(1) {
            animation-delay: -0.32s;
        }
        
        .loading-dots span:nth-child(2) {
            animation-delay: -0.16s;
        }
        
        @keyframes bounce-dot {
            0%, 80%, 100% {
                transform: scale(0);
            }
            40% {
                transform: scale(1);
            }
        }
    `;
    document.head.appendChild(style);
}

function removeLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.opacity = '0';
        setTimeout(() => overlay.remove(), 300);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Close button for alerts
    const closeButtons = document.querySelectorAll('.btn-close');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
    // Add loading state to search button and show loading overlay
    const searchForm = document.querySelector('form[method="POST"]');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const zipCodeInput = this.querySelector('input[name="zip_code"]');
            if (zipCodeInput && zipCodeInput.value.length === 5) {
                // Show loading overlay immediately
                createLoadingOverlay();
                
                // Update button text
                const submitButton = this.querySelector('button[type="submit"]');
                if (submitButton) {
                    submitButton.disabled = true;
                    const buttonText = submitButton.querySelector('span');
                    if (buttonText) {
                        buttonText.textContent = 'Searching...';
                    }
                }
            }
        });
    }

            }
    // Animate stat cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Only animate cards that are below the fold
    const statCards = document.querySelectorAll('.stat-card, .card');
    statCards.forEach((card, index) => {
        const cardTop = card.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;
        
        // Only animate cards that are below the viewport on initial load
        if (cardTop > windowHeight) {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            observer.observe(card);
        } else {
            // Cards already visible should fade in immediately
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 50); // Stagger the animation
        }
    });

    // Ensure table rows are visible
    const tableRows = document.querySelectorAll('.table tbody tr');
    tableRows.forEach((row, index) => {
        row.style.opacity = '0';
        row.style.transform = 'translateY(10px)';
        row.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        
        setTimeout(() => {
            row.style.opacity = '1';
            row.style.transform = 'translateY(0)';
        }, index * 30); // Stagger table row animations
        
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(0) scale(1.01)';
            this.style.transition = 'transform 0.2s ease';
        });
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Animate Kobi Score badges
    const scoreBadges = document.querySelectorAll('.kobi-score-badge');
    scoreBadges.forEach(badge => {
        badge.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1) rotate(2deg)';
            this.style.transition = 'transform 0.3s ease';
        });
        badge.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) rotate(0deg)';
        });
    });

    // Animate cat icons
    const catIcons = document.querySelectorAll('.kobi-cat-icon');

    // Animate cat icons
    const catIcons = document.querySelectorAll('.kobi-cat-icon');
    catIcons.forEach(icon => {
        icon.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.2) rotate(-5deg)';
            this.style.transition = 'transform 0.3s ease';
        });
        icon.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) rotate(0deg)';
        });
    });

    // Format zip code input
    const zipCodeInput = document.querySelector('input[name="zip_code"]');
    if (zipCodeInput) {
        zipCodeInput.addEventListener('input', function(e) {
            // Remove non-numeric characters
            this.value = this.value.replace(/[^0-9]/g, '');
            
            // Limit to 5 digits
            if (this.value.length > 5) {
                this.value = this.value.slice(0, 5);
            }
        });

        // Add visual feedback
        zipCodeInput.addEventListener('focus', function() {
            this.style.borderColor = 'var(--primary-color)';
            this.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.1)';
        });

        zipCodeInput.addEventListener('blur', function() {
            this.style.borderColor = 'var(--border-color)';
            this.style.boxShadow = 'none';
        });
    }

    // Add smooth scroll behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
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

    // Add pulse animation to high-scoring properties
    const excellentScores = document.querySelectorAll('.kobi-score-excellent');
    excellentScores.forEach(score => {
        setInterval(() => {
            score.style.animation = 'pulse 1s ease';
            setTimeout(() => {
                score.style.animation = '';
            }, 1000);
        }, 5000);
    });

    // Add number counter animation for stat values
    const statValues = document.querySelectorAll('.stat-value');
    statValues.forEach(stat => {
        const text = stat.textContent;
        const number = parseFloat(text.replace(/[^0-9.]/g, ''));
        
        if (!isNaN(number) && number > 0) {
            stat.setAttribute('data-target', number);
            stat.textContent = text.replace(number, '0');
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        animateValue(stat, 0, number, 1000, text);
                        observer.unobserve(entry.target);
                    }
                });
            });
            
            observer.observe(stat);
        }
    });

    function animateValue(element, start, end, duration, originalText) {
        const startTime = performance.now();
        const prefix = originalText.match(/^[^0-9]*/)[0];
        const suffix = originalText.match(/[^0-9]*$/)[0];
        
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = start + (end - start) * easeOutQuart(progress);
            const formatted = formatNumber(current, originalText);
            element.textContent = prefix + formatted + suffix;
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        
        requestAnimationFrame(update);
    }

    function easeOutQuart(x) {
        return 1 - Math.pow(1 - x, 4);
    }

    function formatNumber(num, originalText) {
        if (originalText.includes(',')) {
            return Math.round(num).toLocaleString();
        } else if (originalText.includes('.')) {
            const decimals = (originalText.split('.')[1] || '').replace(/[^0-9]/g, '').length;
            return num.toFixed(decimals);
        }
        return Math.round(num).toString();
    }

    // Add keyboard navigation for property cards
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(alert => alert.remove());
        }
    });

    console.log('🐱 Kobi Score System Initialized!');
});

// Add CSS animation for pulse effect
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
`;
document.head.appendChild(style);
