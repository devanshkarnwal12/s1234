// dark_mode.js

// Function to toggle between dark and light themes
function toggleTheme() {
    const body = document.body;
    body.classList.toggle('dark-mode');  // Toggle 'dark-mode' class on the body element

    // Save the user's theme preference in localStorage
    if (body.classList.contains('dark-mode')) {
        localStorage.setItem('theme', 'dark');
    } else {
        localStorage.setItem('theme', 'light');
    }
}

// Load saved theme on page load
window.onload = () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
    }
};

// Attach the toggle function to the button
document.getElementById('toggle-dark-mode').addEventListener('click', toggleTheme);
