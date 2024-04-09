document.addEventListener("DOMContentLoaded", () => {
    /* Display mobile sidebar panel on click */
    document.querySelector("#content-page-sidebar-mobile .sidebar-button").addEventListener("click", (event) => {
        event.target.closest("div").classList.add("hidden");
        document.querySelector("#content-page-sidebar-mobile .sidebar-panel").classList.remove("hidden");
    });

    /* Close mobile sidebar panel on click */
    document.addEventListener("click", (event) => {
        if (!document.querySelector("#content-page-sidebar-mobile").contains(event.target)) {
            document.querySelector("#content-page-sidebar-mobile .sidebar-panel").classList.add("hidden");
            document.querySelector("#content-page-sidebar-mobile .sidebar-button").classList.remove("hidden");
        }
    });

    /* Adjust position of desktop sidebar when viewport changes */
    function adjust_desktop_sidebar_position() {
        let desktop_sidebar = document.getElementById("content-page-sidebar-desktop"),
            content_div = document.getElementById("content-div");
        if (window.innerWidth - content_div.getBoundingClientRect().right < desktop_sidebar.offsetWidth) {
            desktop_sidebar.style.right = window.innerWidth - content_div.getBoundingClientRect().right + 5 + "px";
            desktop_sidebar.getElementsByTagName("ul")[0].classList.add("bg-slate-700");
        } else {
            desktop_sidebar.style.right = window.innerWidth - content_div.getBoundingClientRect().right - desktop_sidebar.offsetWidth - 15 + "px";
            desktop_sidebar.getElementsByTagName("ul")[0].classList.remove("bg-slate-700");
        }
    }

    adjust_desktop_sidebar_position();
    visualViewport.addEventListener("resize", () => {
        adjust_desktop_sidebar_position();
    });

    /*
     * Highlight entries in sidebar as users scroll to them
     * Credit to Dakota Lee Martinez https://dakotaleemartinez.com/tutorials/how-to-add-active-highlight-to-table-of-contents/
     */
    function calc_header_height() {
        return document.querySelector(".content-page-body h2").offsetHeight;
    }

    let header_height = calc_header_height();
    visualViewport.addEventListener("resize", () => {
        header_height = calc_header_height();
    });

    class Scroller {
        static init() {
            this.sidebar_links_desktop = Array.from(document.getElementById("content-page-sidebar-desktop").querySelectorAll("li")).slice(1);
            this.sidebar_links_mobile = Array.from(document.getElementById("content-page-sidebar-mobile").querySelectorAll("li")).slice(1);
            this.headers = Array.from(document.querySelectorAll(".content-page-body h2, .content-page-body h3"));
            this.current_header_classes = ["text-white"];
            this.ticking = false;
            window.addEventListener("scroll", (e) => {
                this.onScroll()
            });
            this.update();
        }

        static onScroll() {
            if (!this.ticking) {
                requestAnimationFrame(this.update.bind(this));
                this.ticking = true;
            }
        }

        static update() {
            let activeIndex = this.headers.findIndex((header) => {
                return header.getBoundingClientRect().top > header_height;
            });
            if (activeIndex > 0) {
                activeIndex--;
            } else if (activeIndex === -1) {
                activeIndex = this.headers.length - 1;
            }
            this.sidebar_links_desktop.forEach(link => link.classList.remove(...this.current_header_classes));
            this.sidebar_links_desktop[activeIndex].classList.add(...this.current_header_classes);
            this.sidebar_links_mobile.forEach(link => link.classList.remove(...this.current_header_classes));
            this.sidebar_links_mobile[activeIndex].classList.add(...this.current_header_classes);
            this.ticking = false;
        }
    }

    Scroller.init();
});
