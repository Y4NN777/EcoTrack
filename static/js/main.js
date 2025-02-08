// Initialize GSAP animations
document.addEventListener('DOMContentLoaded', () => {
    if (typeof gsap !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);

        // Navbar animations - quick and subtle
        const navBrand = document.querySelector('.navbar-brand');
        const navItems = document.querySelectorAll('.nav-item');
        
        if (navBrand) {
            gsap.from(navBrand, {
                duration: 0.4,
                y: -20,
                opacity: 0,
                ease: 'power2.out'
            });
        }

        if (navItems.length > 0) {
            gsap.from(navItems, {
                duration: 0.4,
                y: -20,
                opacity: 0,
                stagger: 0.05,
                ease: 'power2.out'
            });
        }

        // Stat cards - simple fade up
        const statCards = document.querySelectorAll('.stat-card');
        if (statCards.length > 0) {
            gsap.set(statCards, { opacity: 1 });
            
            gsap.from(statCards, {
                duration: 0.4,
                y: 20,
                opacity: 0,
                stagger: 0.05,
                ease: 'power2.out'
            });

            // Simple hover effect
            statCards.forEach(card => {
                card.addEventListener('mouseenter', () => {
                    gsap.to(card, {
                        duration: 0.2,
                        y: -3,
                        scale: 1.01,
                        ease: 'power2.out'
                    });
                });

                card.addEventListener('mouseleave', () => {
                    gsap.to(card, {
                        duration: 0.2,
                        y: 0,
                        scale: 1,
                        ease: 'power2.out'
                    });
                });
            });
        }

        // Quick action buttons - simple hover
        const quickActionBtns = document.querySelectorAll('.quick-action-btn');
        if (quickActionBtns.length > 0) {
            quickActionBtns.forEach(btn => {
                btn.addEventListener('mouseenter', () => {
                    gsap.to(btn, {
                        duration: 0.2,
                        y: -2,
                        ease: 'power2.out'
                    });
                });

                btn.addEventListener('mouseleave', () => {
                    gsap.to(btn, {
                        duration: 0.2,
                        y: 0,
                        ease: 'power2.out'
                    });
                });
            });
        }

        // Activity items - simple hover
        const activityItems = document.querySelectorAll('.activity-item');
        if (activityItems.length > 0) {
            activityItems.forEach(item => {
                item.addEventListener('mouseenter', () => {
                    gsap.to(item, {
                        duration: 0.2,
                        x: 3,
                        ease: 'power2.out'
                    });
                });

                item.addEventListener('mouseleave', () => {
                    gsap.to(item, {
                        duration: 0.2,
                        x: 0,
                        ease: 'power2.out'
                    });
                });
            });
        }
    }
});

// Notification System
const notifications = {
    success: function(message) {
        Swal.fire({
            icon: 'success',
            title: 'Success',
            text: message,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer)
                toast.addEventListener('mouseleave', Swal.resumeTimer)
            }
        });
    },
    error: function(message) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: message,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer)
                toast.addEventListener('mouseleave', Swal.resumeTimer)
            }
        });
    },
    warning: function(message) {
        Swal.fire({
            icon: 'warning',
            title: 'Warning',
            text: message,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer)
                toast.addEventListener('mouseleave', Swal.resumeTimer)
            }
        });
    },
    info: function(message) {
        Swal.fire({
            icon: 'info',
            title: 'Info',
            text: message,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer)
                toast.addEventListener('mouseleave', Swal.resumeTimer)
            }
        });
    }
};

// Handle flash messages on page load
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('[data-flash-message]');
    messages.forEach(function(element) {
        const message = element.getAttribute('data-flash-message');
        const category = element.getAttribute('data-flash-category') || 'info';
        if (message) {
            notifications[category](message);
        }
        element.remove();
    });
});

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', (e) => {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
                
                // Shake animation for invalid fields
                gsap.to(field, {
                    duration: 0.1,
                    x: [-10, 10, -10, 10, 0],
                    ease: 'none'
                });
            } else {
                field.classList.remove('is-invalid');
            }
        });

        if (!isValid) {
            e.preventDefault();
            notifications.error('Please fill in all required fields');
        }
    });
}

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', () => {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));

    const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
    popovers.forEach(popover => new bootstrap.Popover(popover));

    // Initialize form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.id && validateForm(form.id);
    });
});
