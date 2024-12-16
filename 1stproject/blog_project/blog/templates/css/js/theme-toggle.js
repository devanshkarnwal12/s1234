// theme-toggle.js
document.addEventListener("DOMContentLoaded", function() {
    const toggleButton = document.getElementById("theme-toggle");
    const currentTheme = localStorage.getItem("theme") || "light";
    
    if (currentTheme === "dark") {
        document.body.classList.add("dark-mode");
    }

    toggleButton.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");
        const newTheme = document.body.classList.contains("dark-mode") ? "dark" : "light";
        localStorage.setItem("theme", newTheme);
    });
});
