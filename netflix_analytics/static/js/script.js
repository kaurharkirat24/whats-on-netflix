// Add simple scroll fade-in effects for cards and sections
document.addEventListener("DOMContentLoaded", function() {
    const cards = document.querySelectorAll('.chart-card');
    cards.forEach(card => {
        card.classList.add('zoom-in');
    });
});
