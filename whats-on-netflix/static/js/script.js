// Highlight active nav link
document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;
    if (path === '/')          document.getElementById('nav-home')?.classList.add('active-nav');
    if (path === '/dashboard') document.getElementById('nav-dash')?.classList.add('active-nav');
    if (path === '/about')     document.getElementById('nav-about')?.classList.add('active-nav');
});

// Add active-nav style dynamically
const style = document.createElement('style');
style.textContent = '.active-nav { color: #fff !important; }';
document.head.appendChild(style);
