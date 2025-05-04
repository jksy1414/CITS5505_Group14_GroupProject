// Function to handle the flip card interaction
// This function adds event listeners to each flip card to handle the mouse hover and mobile click events
function flipcard() {
    const flipCards = document.querySelectorAll('.flip-card');

    flipCards.forEach(card => {
        // Hover flip effect (desktop)
        card.addEventListener('mouseenter', () => {
            card.classList.add('flipped');
        });
        card.addEventListener('mouseleave', () => {
            card.classList.remove('flipped');
        });

        // Click flip toggle (mobile & accessibility)
        card.addEventListener('click', () => {
            card.classList.toggle('flipped');
        });
    });
}


// Initialize the flipcard function when the window loads (after the DOM is fully loaded)
window.onload = function () {
    flipcard();
};
