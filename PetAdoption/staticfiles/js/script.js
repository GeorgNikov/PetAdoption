<!-- Hide and show password -->

function togglePasswordVisibility(passwordFieldId, iconElement) {
    const passwordField = document.getElementById(passwordFieldId);
    const isPasswordVisible = passwordField.type === "text";

    // Toggle the password field type
    passwordField.type = isPasswordVisible ? "password" : "text";

    // Change the icon based on visibility
    iconElement.innerHTML = isPasswordVisible
    iconElement.innerHTML = isPasswordVisible
        ? '<img src="https://img.icons8.com/ios-filled/24/000000/invisible.png" alt="Hide Password" />'
        : '<img src="https://img.icons8.com/ios-filled/24/000000/visible.png" alt="Show Password" />';

}


// Function to show hidden boxes
function showBoxes(boxesToShow) {
    const hiddenBoxes = document.querySelectorAll('.box.hidden');
    hiddenBoxes.forEach((box, index) => {
        if (index < boxesToShow) {
            box.classList.remove('hidden');
        }
    });

    // Hide button if all boxes are shown
    if (document.querySelectorAll('.box.hidden').length === 0) {
        // If you had a button, you could hide it here
    }
}

// Function to handle scroll event for auto-load
function lazyLoadOnScroll() {
    const hiddenBoxes = document.querySelectorAll('.box.hidden');

    // Check if user has scrolled near the bottom
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 100) {
        showBoxes(6); // Load more boxes
    }
}

// Initial setup
document.addEventListener('DOMContentLoaded', () => {
    showBoxes(4); // Show the first 4 boxes initially
    window.addEventListener('scroll', lazyLoadOnScroll); // Add scroll event listener
});


function previewImage(event) {
    const reader = new FileReader();
    reader.onload = function () {
        const preview = document.getElementById('profileImagePreview');
        preview.src = reader.result;
    };
    reader.readAsDataURL(event.target.files[0]);
}


    // Wait 3 seconds, then fade out the error banner
    setTimeout(function() {
        const errorBanner = document.getElementById('message-banner');
        if (errorBanner) {
            errorBanner.style.transition = 'opacity 1s ease-out';
            errorBanner.style.opacity = '0';

            // Remove the element from the DOM after the fade-out effect
            setTimeout(function() {
                errorBanner.style.display = 'none';
            }, 1000); // Matches the fade duration
        }
    }, 4000); // 3 seconds

