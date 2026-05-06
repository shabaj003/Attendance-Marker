/**
 * Attendance System - Interactive Animations & Effects
 */

// ============================================
// 1. ANIMATED COUNTER FOR STATISTICS
// ============================================

function animateCounter(element, target, duration = 2000) {
    const increment = target / (duration / 16);
    let current = 0;
    
    const counter = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(counter);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// Initialize counters when page loads
document.addEventListener('DOMContentLoaded', () => {
    const statValues = document.querySelectorAll('.stat-card .value');
    
    statValues.forEach(element => {
        const originalText = element.textContent;
        const numericValue = parseInt(originalText.replace(/\D/g, ''));
        
        if (!isNaN(numericValue)) {
            element.textContent = '0';
            
            // Animate when element comes into view
            const observer = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting) {
                    animateCounter(element, numericValue);
                    observer.unobserve(element);
                }
            }, { threshold: 0.5 });
            
            observer.observe(element);
        }
    });
});

// ============================================
// 2. PAGE SCROLL ANIMATIONS
// ============================================

window.addEventListener('scroll', () => {
    // Add animations to elements as they come into view
    const elements = document.querySelectorAll('.card, .stat-card, .alert');
    
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementBottom = element.getBoundingClientRect().bottom;
        
        if (elementTop < window.innerHeight && elementBottom > 0) {
            element.style.opacity = '1';
        }
    });
});

// ============================================
// 3. BUTTON CLICK RIPPLE EFFECT ENHANCEMENT
// ============================================

document.addEventListener('click', (e) => {
    if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
        const button = e.target.tagName === 'BUTTON' ? e.target : e.target.closest('button');
        
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');
        
        button.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }
});

// ============================================
// 4. FORM VALIDATION ANIMATIONS
// ============================================

const forms = document.querySelectorAll('form');

forms.forEach(form => {
    form.addEventListener('submit', function(e) {
        const inputs = this.querySelectorAll('input, select, textarea');
        
        inputs.forEach((input, index) => {
            if (!input.value && input.required) {
                input.classList.add('error-shake');
                setTimeout(() => {
                    input.classList.remove('error-shake');
                }, 500);
            }
        });
    });
    
    // Add validation feedback animations
    form.querySelectorAll('input, select, textarea').forEach(input => {
        input.addEventListener('invalid', function() {
            this.classList.add('error-shake');
        });
        
        input.addEventListener('input', function() {
            this.classList.remove('error-shake');
        });
    });
});

// ============================================
// 5. LOADING STATE ANIMATIONS
// ============================================

function showLoadingAnimation(buttonElement) {
    if (!buttonElement) return;
    
    const originalText = buttonElement.innerHTML;
    const spinner = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>';
    
    buttonElement.innerHTML = spinner + 'Loading...';
    buttonElement.disabled = true;
    buttonElement.style.pointerEvents = 'none';
    
    return () => {
        buttonElement.innerHTML = originalText;
        buttonElement.disabled = false;
        buttonElement.style.pointerEvents = 'auto';
    };
}

// Auto-animate form submit buttons
document.addEventListener('submit', (e) => {
    const submitBtn = e.target.querySelector('button[type="submit"]');
    if (submitBtn) {
        showLoadingAnimation(submitBtn);
    }
});

// ============================================
// 6. NOTIFICATION ANIMATIONS
// ============================================

function showNotification(message, type = 'info', duration = 3000) {
    const alertDiv = document.createElement('div');
    const alertClasses = ['alert', `alert-${type}`, 'position-fixed', 'top-0', 'end-0', 'm-3'];
    
    alertDiv.className = alertClasses.join(' ');
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-dismiss after duration
    setTimeout(() => {
        alertDiv.style.animation = 'fadeOut 0.3s ease-out forwards';
        setTimeout(() => alertDiv.remove(), 300);
    }, duration);
}

// ============================================
// 7. HOVER GLOW EFFECTS
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card, .stat-card');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            card.style.setProperty('--mouse-x', `${x}px`);
            card.style.setProperty('--mouse-y', `${y}px`);
        });
    });
});

// ============================================
// 8. SMOOTH SCROLL TO SECTION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Add highlight animation
                targetElement.style.animation = 'glow 0.5s ease-out';
                setTimeout(() => {
                    targetElement.style.animation = '';
                }, 500);
            }
        });
    });
});

// ============================================
// 9. PAGE TRANSITION ANIMATION
// ============================================

window.addEventListener('beforeunload', () => {
    document.body.style.animation = 'fadeOut 0.3s ease-out forwards';
});

// ============================================
// 10. TABLE ROW HOVER ANIMATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    const tableRows = document.querySelectorAll('table tbody tr');
    
    tableRows.forEach((row, index) => {
        row.style.animationDelay = `${index * 0.05}s`;
        row.classList.add('fade-in-delayed-1');
        
        row.addEventListener('mouseenter', () => {
            row.style.transform = 'translateX(8px)';
        });
        
        row.addEventListener('mouseleave', () => {
            row.style.transform = 'translateX(0)';
        });
    });
});

// ============================================
// 11. MODAL ANIMATION ENHANCEMENT
// ============================================

const modals = document.querySelectorAll('.modal');

modals.forEach(modal => {
    const bsModal = new bootstrap.Modal(modal);
    
    modal.addEventListener('show.bs.modal', () => {
        modal.classList.add('modal-animate-in');
    });
    
    modal.addEventListener('hide.bs.modal', () => {
        modal.classList.add('modal-animate-out');
        setTimeout(() => {
            modal.classList.remove('modal-animate-in', 'modal-animate-out');
        }, 300);
    });
});

// ============================================
// 12. TOOLTIP ANIMATIONS
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
});

// ============================================
// 13. PROGRESS BAR ANIMATION
// ============================================

function animateProgressBar(element, targetPercent, duration = 1000) {
    const startPercent = 0;
    const increment = (targetPercent - startPercent) / (duration / 16);
    let current = startPercent;
    
    const interval = setInterval(() => {
        current += increment;
        if (current >= targetPercent) {
            element.style.width = targetPercent + '%';
            clearInterval(interval);
        } else {
            element.style.width = current + '%';
        }
    }, 16);
}

// ============================================
// 14. STAGGERED ANIMATION HELPER
// ============================================

function animateStaggered(selector, delayBase = 0.1) {
    const elements = document.querySelectorAll(selector);
    
    elements.forEach((element, index) => {
        element.style.animationDelay = `${index * delayBase}s`;
        element.classList.add('fade-in-delayed-' + (Math.min(index + 1, 4)));
    });
}

// ============================================
// 15. VISIBILITY OBSERVER FOR ANIMATIONS
// ============================================

const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            entry.target.style.opacity = '1';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe all animated elements
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.card, .stat-card, .alert, .btn').forEach(el => {
        observer.observe(el);
    });
});

// ============================================
// 16. UTILITY FUNCTION: ADD RIPPLE CSS
// ============================================

const style = document.createElement('style');
style.textContent = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: rippleAnimation 0.6s ease-out;
        pointer-events: none;
    }
    
    @keyframes rippleAnimation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .error-shake {
        animation: shake 0.5s ease-in !important;
    }
    
    .modal-animate-in {
        animation: bounceIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) !important;
    }
    
    .modal-animate-out {
        animation: fadeOut 0.3s ease-out forwards !important;
    }
    
    @keyframes fadeOut {
        from {
            opacity: 1;
        }
        to {
            opacity: 0;
        }
    }
`;

document.head.appendChild(style);

// ============================================
// 17. ACCESSIBILITY: PREFERS REDUCED MOTION
// ============================================

if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.documentElement.style.setProperty('--animation-duration', '0.01ms');
    document.documentElement.style.setProperty('--animation-timing', 'linear');
    
    // Remove animations for users with reduced motion preference
    const allElements = document.querySelectorAll('*');
    allElements.forEach(el => {
        el.style.animation = 'none !important';
        el.style.transition = 'none !important';
    });
}
