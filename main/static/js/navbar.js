document.addEventListener("DOMContentLoaded", () => {

    /* Notification system */
    let mark_read_button = document.getElementById("markAllAsReadButton");
    if (mark_read_button) {
        document.getElementById("markAllAsReadButton").addEventListener("click", (event) => {
            let element = event.target.closest("button"),
                url = element.getAttribute("data-url");
            fetch(url)
                .then(response => {
                    return response.json();
                })
                .then(data => {
                    document.querySelectorAll(".notification-list-item").forEach((element) => {
                        element.remove()
                    });
                    document.getElementById("notifications-count").textContent = "0";
                    document.getElementById("notifications-count").remove();
                    document.getElementById("markAllAsReadButton").closest("li").remove();
                    document.getElementById("notificationDivider").remove();
                })
                .catch(error => {
                    console.log(error);
                });
        });
    }
    Array.from(document.getElementsByClassName("notificationMarkReadButton")).forEach(element => {
        element.addEventListener("mousedown", (event) => {
            event.preventDefault();
        });
        element.addEventListener("click", (event) => {
            let element = event.target.closest("button"),
                url = element.getAttribute("data-url");
            fetch(url)
                .then(response => {
                    return response.json();
                })
                .then(data => {
                    element.closest("li").remove();
                    document.getElementById("notifications-count").textContent--;
                    if (document.getElementById("notifications-count").textContent === "0") {
                        document.getElementById("notifications-count").remove();
                        document.getElementById("markAllAsReadButton").closest("li").remove();
                    }
                })
                .catch(error => {
                    console.log(error);
                });
        });
    });

    /* Mobile navbar dropdown */
    document.getElementById("mobile-navbar-button").addEventListener("click", () => {
        let navbar = document.getElementById("navbar"),
            navbar_dropdown = document.getElementById("mobile-navbar-dropdown"),
            navbar_open_icon = document.querySelector("#mobile-navbar-button #open-button"),
            navbar_close_icon = document.querySelector("#mobile-navbar-button #close-button");
        if (navbar_dropdown.classList.contains("hidden")) {
            navbar.classList.remove("rounded-lg", "mb-2");
            navbar.classList.add("rounded-t-lg");
            navbar_dropdown.classList.remove("hidden");
            navbar_open_icon.classList.add("hidden");
            navbar_close_icon.classList.remove("hidden");
        } else {
            navbar.classList.add("rounded-lg", "mb-2");
            navbar.classList.remove("rounded-t-lg");
            navbar_dropdown.classList.add("hidden");
            navbar_open_icon.classList.remove("hidden");
            navbar_close_icon.classList.add("hidden");

        }
    });

    Array.from(document.querySelectorAll(".mobile-navbar-dropdown-item")).forEach(element => {
        element.addEventListener("click", event => {
            let child_dropdown = element.parentNode.querySelector("ul");
            if (child_dropdown.classList.contains("hidden")) {
                child_dropdown.classList.remove("hidden");
            } else {
                child_dropdown.classList.add("hidden");
            }
        });
    });
});
