document.addEventListener('DOMContentLoaded', function() {
    // Form validation for registration
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (validateRegisterForm()) {
                this.submit();
            }
        });

        // Real-time password strength indicator
        const passwordInput = document.getElementById('password');
        const passwordStrength = document.getElementById('password-strength');
        
        passwordInput.addEventListener('input', function() {
            updatePasswordStrength(this.value);
        });
    }

    // Form validation for login
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (validateLoginForm()) {
                this.submit();
            }
        });
    }
});

function validateRegisterForm() {
    const firstName = document.getElementById('first_name').value;
    const lastName = document.getElementById('last_name').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    // Reset error messages
    clearErrors();

    let isValid = true;

    // First Name validation
    if (!firstName || firstName.length < 2) {
        showError('first_name', 'First name must be at least 2 characters long');
        isValid = false;
    }

    // Last Name validation
    if (!lastName || lastName.length < 2) {
        showError('last_name', 'Last name must be at least 2 characters long');
        isValid = false;
    }

    // Username validation
    if (!username || username.length < 4) {
        showError('username', 'Username must be at least 4 characters long');
        isValid = false;
    }

    // Password validation
    if (!isPasswordStrong(password)) {
        showError('password', 'Password must be at least 6 characters long and contain uppercase, lowercase, number, and special character');
        isValid = false;
    }

    // Confirm password validation
    if (password !== confirmPassword) {
        showError('confirm_password', 'Passwords do not match');
        isValid = false;
    }

    return isValid;
}

function validateLoginForm() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    clearErrors();
    let isValid = true;

    if (!username) {
        showError('username', 'Please enter your username');
        isValid = false;
    }

    if (!password) {
        showError('password', 'Please enter your password');
        isValid = false;
    }

    return isValid;
}

function isPasswordStrong(password) {
    const minLength = 6;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    return password.length >= minLength && 
           hasUpperCase && 
           hasLowerCase && 
           hasNumbers && 
           hasSpecialChar;
}

function updatePasswordStrength(password) {
    const strengthBar = document.getElementById('password-strength');
    const strengthText = document.getElementById('strength-text');

    let strength = 0;
    let feedback = '';

    if (password.length >= 6) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++;

    switch (strength) {
        case 0:
            feedback = 'Very Weak';
            strengthBar.style.width = '20%';
            strengthBar.className = 'password-strength-bar very-weak';
            break;
        case 1:
            feedback = 'Weak';
            strengthBar.style.width = '40%';
            strengthBar.className = 'password-strength-bar weak';
            break;
        case 2:
            feedback = 'Fair';
            strengthBar.style.width = '60%';
            strengthBar.className = 'password-strength-bar fair';
            break;
        case 3:
            feedback = 'Good';
            strengthBar.style.width = '80%';
            strengthBar.className = 'password-strength-bar good';
            break;
        case 4:
        case 5:
            feedback = 'Strong';
            strengthBar.style.width = '100%';
            strengthBar.className = 'password-strength-bar strong';
            break;
    }

    strengthText.textContent = feedback;
}

function showError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.classList.add('is-invalid');
    field.parentNode.appendChild(errorDiv);
}

function clearErrors() {
    document.querySelectorAll('.is-invalid').forEach(field => {
        field.classList.remove('is-invalid');
    });
    document.querySelectorAll('.invalid-feedback').forEach(errorDiv => {
        errorDiv.remove();
    });
}
