document.addEventListener("DOMContentLoaded", () => {

    /* Notification system */
    let mark_read_buttons = document.querySelectorAll(".mark-all-read-button");
    if (mark_read_buttons) {
        mark_read_buttons.forEach(el => {
            el.addEventListener("click", (event) => {
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
                        mark_read_buttons.forEach(el => {
                            el.closest("li").remove();
                        })
                        document.getElementById("notificationDivider").remove();
                    })
                    .catch(error => {
                        console.log(error);
                    });
            });
        })
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
                        mark_read_buttons.forEach(el => {
                            el.closest("li").remove();
                        })
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
            navbar_dropdown_user = document.getElementById("mobile-navbar-dropdown-user"),
            navbar_open_icon = document.querySelector("#mobile-navbar-button #open-button"),
            navbar_close_icon = document.querySelector("#mobile-navbar-button #close-button");
        if (navbar_dropdown.classList.contains("hidden")) {
            navbar.classList.remove("rounded-b-lg", "mb-2");
            navbar_dropdown.classList.remove("hidden");
            navbar_dropdown_user.classList.add("hidden");
            navbar_open_icon.classList.add("hidden");
            navbar_close_icon.classList.remove("hidden");
        } else {
            navbar.classList.add("rounded-b-lg", "mb-2");
            navbar_dropdown.classList.add("hidden");
            navbar_open_icon.classList.remove("hidden");
            navbar_close_icon.classList.add("hidden");
        }
    });

    document.getElementById("mobile-navbar-button-user").addEventListener("click", () => {
        let navbar = document.getElementById("navbar"),
            navbar_dropdown = document.getElementById("mobile-navbar-dropdown"),
            navbar_dropdown_user = document.getElementById("mobile-navbar-dropdown-user"),
            navbar_open_icon = document.querySelector("#mobile-navbar-button #open-button"),
            navbar_close_icon = document.querySelector("#mobile-navbar-button #close-button");
        if (navbar_dropdown_user.classList.contains("hidden")) {
            navbar.classList.remove("rounded-b-lg", "mb-2");
            navbar_dropdown.classList.add("hidden");
            navbar_dropdown_user.classList.remove("hidden");
            navbar_open_icon.classList.remove("hidden");
            navbar_close_icon.classList.add("hidden");
        } else {
            navbar.classList.add("rounded-b-lg", "mb-2");
            navbar_dropdown_user.classList.add("hidden");
        }
    });

    Array.from(document.querySelectorAll(".mobile-navbar-dropdown-item")).forEach(element => {
        element.addEventListener("click", event => {
            let child_dropdown = element.parentNode.querySelector("ul");
            if (child_dropdown.classList.contains("hidden")) {
                child_dropdown.classList.add("rounded-b-lg");
                child_dropdown.classList.remove("hidden");
            } else {
                child_dropdown.classList.add("hidden");
            }
        });
    });
});
