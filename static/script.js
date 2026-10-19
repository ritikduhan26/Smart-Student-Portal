// Smart Student Portal JavaScript

document.addEventListener("DOMContentLoaded", function () {

    // Highlight the current sidebar page
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll(".sidebar-menu a");

    sidebarLinks.forEach(function (link) {
        const linkPath = new URL(link.href).pathname;

        if (linkPath === currentPath) {
            link.classList.add("active");
        }
    });


    // Ask for confirmation before deleting announcements
    // (the delete buttons are inside forms, so listen for form submit)
    const deleteForms = document.querySelectorAll(
        'form[action*="/announcements/delete/"]'
    );

    deleteForms.forEach(function (form) {
        form.addEventListener("submit", function (event) {
            const confirmed = confirm(
                "Are you sure you want to delete this announcement?"
            );

            if (!confirmed) {
                event.preventDefault();
            }
        });
    });


    // Hide alert messages automatically after 5 seconds
    const alerts = document.querySelectorAll(
        ".alert, .flash-message, .success-message, .error-message"
    );

    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = "opacity 0.5s ease";
            alert.style.opacity = "0";

            setTimeout(function () {
                alert.style.display = "none";
            }, 500);
        }, 5000);
    });

});


// Show or hide password
function togglePassword() {

    const passwordInput = document.getElementById("password");

    if (passwordInput) {
        if (passwordInput.type === "password") {
            passwordInput.type = "text";
        } else {
            passwordInput.type = "password";
        }
    }
}

// Show or hide students enrolled in an assignment
function toggleStudents(elementId) {

    const studentList = document.getElementById(elementId);

    if (!studentList) {
        return;
    }

    if (studentList.style.display === "none") {
        studentList.style.display = "block";
    } else {
        studentList.style.display = "none";
    }
}