// static/scripts/login.js
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.login-form');
    if (form) {
        form.addEventListener('submit', (event) => {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            if (!email || !password) {
                event.preventDefault();
                const errorDiv = document.createElement('p');
                errorDiv.className = 'error-message';
                errorDiv.textContent = 'Por favor, preencha todos os campos.';
                form.prepend(errorDiv);
            }
        });
    }
});