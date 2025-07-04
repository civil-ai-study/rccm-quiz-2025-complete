// 🎯 Enhanced UI/UX Interactions - Modern User Experience
/**
 * Advanced interaction system with smooth animations and responsive feedback
 * Maintains existing functionality while adding modern UX patterns
 */

class EnhancedInteractions {
    constructor() {
        this.isInitialized = false;
        this.animations = new Map();
        this.observers = new Map();
        this.preferences = this.loadUserPreferences();
        
        // Safely initialize only if DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }
    
    init() {
        try {
            this.setupIntersectionObserver();
            this.enhanceFormInteractions();
            this.setupAccessibilityFeatures();
            this.initializeAnimations();
            this.setupPerformanceMonitoring();
            this.isInitialized = true;
            console.log('✨ Enhanced interactions initialized');
        } catch (error) {
            console.warn('Enhanced interactions failed to initialize:', error);
            // Fallback to basic functionality
        }
    }
    
    loadUserPreferences() {
        try {
            const stored = localStorage.getItem('ui_preferences');
            return stored ? JSON.parse(stored) : {
                reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
                highContrast: false,
                fontSize: 'normal',
                theme: 'auto'
            };
        } catch {
            return { reducedMotion: false, highContrast: false, fontSize: 'normal', theme: 'auto' };
        }
    }
    
    saveUserPreferences() {
        try {
            localStorage.setItem('ui_preferences', JSON.stringify(this.preferences));
        } catch (error) {
            console.warn('Could not save user preferences:', error);
        }
    }
    
    setupIntersectionObserver() {
        if (!('IntersectionObserver' in window)) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateElementEntry(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '50px'
        });
        
        // Observe elements that should animate on scroll
        document.querySelectorAll('.enhanced-card, .question-enhanced, .option-enhanced').forEach(el => {
            observer.observe(el);
        });
        
        this.observers.set('intersection', observer);
    }
    
    animateElementEntry(element) {
        if (this.preferences.reducedMotion) return;
        
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        // Use requestAnimationFrame for smooth animation
        requestAnimationFrame(() => {
            element.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        });
    }
    
    enhanceFormInteractions() {
        // Enhanced option selection with smooth feedback
        document.addEventListener('click', (e) => {
            const option = e.target.closest('.option-enhanced, .option-item');
            if (option) {
                this.handleOptionSelection(option, e);
            }
        });
        
        // Enhanced button interactions
        document.addEventListener('click', (e) => {
            const button = e.target.closest('.btn-enhanced, .btn');
            if (button) {
                this.createRippleEffect(button, e);
            }
        });
        
        // Form validation feedback
        this.enhanceFormValidation();
    }
    
    handleOptionSelection(option, event) {
        // Remove previous selections
        const container = option.closest('form, .form-enhanced, fieldset');
        if (container) {
            container.querySelectorAll('.option-enhanced, .option-item').forEach(opt => {
                opt.classList.remove('selected');
                opt.setAttribute('aria-selected', 'false');
            });
        }
        
        // Add selection to clicked option
        option.classList.add('selected');
        option.setAttribute('aria-selected', 'true');
        
        // Trigger radio button if exists
        const radio = option.querySelector('input[type="radio"]');
        if (radio) {
            radio.checked = true;
            radio.dispatchEvent(new Event('change', { bubbles: true }));
        }
        
        // Visual feedback
        this.createSelectionFeedback(option);
        
        // Enable submit button if it exists and is disabled
        const submitBtn = document.querySelector('#submitBtn, .btn-submit');
        if (submitBtn && submitBtn.disabled) {
            submitBtn.disabled = false;
            this.animateButtonEnable(submitBtn);
        }
        
        // Announce selection to screen readers
        this.announceSelection(option);
    }
    
    createSelectionFeedback(option) {
        if (this.preferences.reducedMotion) return;
        
        const feedback = document.createElement('div');
        feedback.className = 'selection-feedback';
        feedback.style.cssText = `
            position: absolute;
            top: 50%;
            left: 50%;
            width: 20px;
            height: 20px;
            background: var(--success-color, #059669);
            border-radius: 50%;
            transform: translate(-50%, -50%) scale(0);
            pointer-events: none;
            z-index: 1000;
        `;
        
        option.style.position = 'relative';
        option.appendChild(feedback);
        
        // Animate feedback
        requestAnimationFrame(() => {
            feedback.style.transition = 'transform 0.4s ease-out, opacity 0.4s ease-out';
            feedback.style.transform = 'translate(-50%, -50%) scale(4)';
            feedback.style.opacity = '0';
        });
        
        // Cleanup
        setTimeout(() => feedback.remove(), 400);
    }
    
    createRippleEffect(button, event) {
        if (this.preferences.reducedMotion) return;
        
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        const ripple = document.createElement('div');
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            pointer-events: none;
            z-index: 1;
        `;
        
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);
        
        // Animate ripple
        requestAnimationFrame(() => {
            ripple.style.transition = 'transform 0.6s ease-out, opacity 0.6s ease-out';
            ripple.style.transform = 'scale(1)';
            ripple.style.opacity = '0';
        });
        
        // Cleanup
        setTimeout(() => ripple.remove(), 600);
    }
    
    animateButtonEnable(button) {
        if (this.preferences.reducedMotion) return;
        
        button.style.transition = 'all 0.3s ease-out';
        button.style.transform = 'scale(1.05)';
        
        setTimeout(() => {
            button.style.transform = 'scale(1)';
        }, 150);
    }
    
    enhanceFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    this.showValidationFeedback(form);
                }
            });
        });
    }
    
    validateForm(form) {
        const requiredRadios = form.querySelectorAll('input[type="radio"][required]');
        const radioGroups = new Set();
        
        requiredRadios.forEach(radio => {
            radioGroups.add(radio.name);
        });
        
        for (const groupName of radioGroups) {
            const groupRadios = form.querySelectorAll(`input[type="radio"][name="${groupName}"]`);
            const isChecked = Array.from(groupRadios).some(radio => radio.checked);
            
            if (!isChecked) {
                return false;
            }
        }
        
        return true;
    }
    
    showValidationFeedback(form) {
        // Create or update validation message
        let message = form.querySelector('.validation-message');
        if (!message) {
            message = document.createElement('div');
            message.className = 'validation-message';
            message.style.cssText = `
                background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
                color: #991b1b;
                padding: 1rem;
                border-radius: 0.5rem;
                margin-bottom: 1rem;
                border: 1px solid #f87171;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            `;
            form.insertBefore(message, form.firstChild);
        }
        
        message.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
            選択肢を選んでください。
        `;
        
        // Animate message appearance
        if (!this.preferences.reducedMotion) {
            message.style.opacity = '0';
            message.style.transform = 'translateY(-10px)';
            
            requestAnimationFrame(() => {
                message.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
                message.style.opacity = '1';
                message.style.transform = 'translateY(0)';
            });
        }
        
        // Focus first radio button for accessibility
        const firstRadio = form.querySelector('input[type="radio"]');
        if (firstRadio) {
            firstRadio.focus();
        }
    }
    
    setupAccessibilityFeatures() {
        // Enhanced keyboard navigation
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardNavigation(e);
        });
        
        // High contrast mode toggle
        this.setupHighContrastMode();
        
        // Font size controls
        this.setupFontSizeControls();
        
        // Screen reader announcements
        this.setupScreenReaderSupport();
    }
    
    handleKeyboardNavigation(event) {
        const focusedElement = document.activeElement;
        
        // Arrow key navigation for options
        if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
            const options = Array.from(document.querySelectorAll('.option-enhanced, .option-item'));
            const currentIndex = options.indexOf(focusedElement.closest('.option-enhanced, .option-item'));
            
            if (currentIndex !== -1) {
                event.preventDefault();
                const nextIndex = event.key === 'ArrowDown' 
                    ? (currentIndex + 1) % options.length
                    : (currentIndex - 1 + options.length) % options.length;
                
                const nextOption = options[nextIndex];
                const radio = nextOption.querySelector('input[type="radio"]');
                if (radio) {
                    radio.focus();
                }
            }
        }
        
        // Enter/Space to select option
        if (event.key === 'Enter' || event.key === ' ') {
            const option = focusedElement.closest('.option-enhanced, .option-item');
            if (option) {
                event.preventDefault();
                this.handleOptionSelection(option, event);
            }
        }
    }
    
    setupHighContrastMode() {
        const toggleHighContrast = () => {
            this.preferences.highContrast = !this.preferences.highContrast;
            document.body.classList.toggle('high-contrast', this.preferences.highContrast);
            this.saveUserPreferences();
        };
        
        // Apply saved preference
        if (this.preferences.highContrast) {
            document.body.classList.add('high-contrast');
        }
        
        // Add toggle control (can be bound to a button)
        window.toggleHighContrast = toggleHighContrast;
    }
    
    setupFontSizeControls() {
        const setFontSize = (size) => {
            this.preferences.fontSize = size;
            document.body.className = document.body.className.replace(/font-size-\w+/g, '');
            document.body.classList.add(`font-size-${size}`);
            this.saveUserPreferences();
        };
        
        // Apply saved preference
        if (this.preferences.fontSize !== 'normal') {
            setFontSize(this.preferences.fontSize);
        }
        
        // Expose controls globally
        window.setFontSize = setFontSize;
    }
    
    setupScreenReaderSupport() {
        // Create live region for announcements
        if (!document.getElementById('sr-announcements')) {
            const liveRegion = document.createElement('div');
            liveRegion.id = 'sr-announcements';
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.setAttribute('aria-atomic', 'true');
            liveRegion.style.cssText = `
                position: absolute;
                left: -10000px;
                width: 1px;
                height: 1px;
                overflow: hidden;
            `;
            document.body.appendChild(liveRegion);
        }
    }
    
    announceSelection(option) {
        const liveRegion = document.getElementById('sr-announcements');
        if (!liveRegion) return;
        
        const optionText = option.querySelector('.option-text, label')?.textContent?.trim() || '選択肢';
        const letter = option.querySelector('.option-letter')?.textContent?.trim() || '';
        
        liveRegion.textContent = `選択肢${letter} ${optionText} を選択しました`;
        
        // Clear after announcement
        setTimeout(() => {
            liveRegion.textContent = '';
        }, 1000);
    }
    
    initializeAnimations() {
        if (this.preferences.reducedMotion) return;
        
        // Stagger animation for initial page load
        const animateElements = document.querySelectorAll('.enhanced-card, .question-enhanced');
        animateElements.forEach((el, index) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }
    
    setupPerformanceMonitoring() {
        // Monitor animation performance
        if ('PerformanceObserver' in window) {
            try {
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (entry.duration > 16) { // > 60fps threshold
                            console.warn('Slow animation detected:', entry);
                        }
                    }
                });
                
                observer.observe({ entryTypes: ['measure'] });
                this.observers.set('performance', observer);
            } catch (error) {
                console.warn('Performance monitoring not available:', error);
            }
        }
    }
    
    // Utility methods for external use
    showLoading(element, text = '読み込み中...') {
        if (!element) return;
        
        const loadingHTML = `
            <div class="loading-enhanced">
                <div class="loading-spinner"></div>
                <span>${text}</span>
            </div>
        `;
        
        element.innerHTML = loadingHTML;
    }
    
    hideLoading(element, originalContent = '') {
        if (!element) return;
        element.innerHTML = originalContent;
    }
    
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--${type}-color, #0284c7);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            box-shadow: var(--shadow-lg);
            z-index: 1000;
            transform: translateX(100%);
            transition: transform 0.3s ease-out;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Animate in
        requestAnimationFrame(() => {
            notification.style.transform = 'translateX(0)';
        });
        
        // Auto remove
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, duration);
        
        return notification;
    }
    
    // Cleanup method
    destroy() {
        this.observers.forEach(observer => observer.disconnect());
        this.observers.clear();
        this.animations.clear();
        this.isInitialized = false;
    }
}

// Initialize enhanced interactions
const enhancedUI = new EnhancedInteractions();

// Export for global use
window.enhancedUI = enhancedUI;

// Backward compatibility with existing code
if (typeof selectOption === 'undefined') {
    window.selectOption = (option, event) => {
        const optionElement = typeof option === 'string' 
            ? document.querySelector(`#option${option}`)?.closest('.option-enhanced, .option-item')
            : option;
            
        if (optionElement) {
            enhancedUI.handleOptionSelection(optionElement, event || {});
        }
    };
}

// Enhanced form validation for existing forms
if (typeof validateQuizForm === 'undefined') {
    window.validateQuizForm = () => {
        const form = document.querySelector('#questionForm, form');
        return form ? enhancedUI.validateForm(form) : true;
    };
}

console.log('🎨 Enhanced UI/UX system loaded and ready');