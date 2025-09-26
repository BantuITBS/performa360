function toggleMenu() {
    var menu = document.getElementById('menuLinks');
    if (menu.style.display === 'block') {
        menu.style.display = 'none';
    } else {
        menu.style.display = 'block';
    }
}

// Hamburger menu toggle
document.getElementById('hamburger-menu').addEventListener('click', function () {
const menuLinks = document.getElementById('menu-links');
menuLinks.style.display = menuLinks.style.display === 'block' ? 'none' : 'block';
});


// Toggle Contact Details
function toggleContactDetails() {
const contactDetails = document.getElementById('contact-details');
contactDetails.style.display = contactDetails.style.display === 'block' ? 'none' : 'block';
}
























