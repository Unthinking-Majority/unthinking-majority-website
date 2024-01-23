document.addEventListener("DOMContentLoaded", () => {
    /* Fix sticky sidebar margins when scrolling down */
    let observer = new IntersectionObserver(([e]) => {
        e.target.querySelector(".sidebar-button").classList.toggle('top-8', e.intersectionRatio < 1);
        e.target.querySelector(".sidebar-panel").classList.toggle('top-8', e.intersectionRatio < 1);
        e.target.querySelector(".sidebar-button").classList.toggle('-top-1', e.intersectionRatio === 1);
        e.target.querySelector(".sidebar-panel").classList.toggle('-top-1', e.intersectionRatio === 1);
    }, {threshold: [1]});
    observer.observe(document.getElementById("content-page-sidebar-mobile"));

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
            desktop_sidebar.style.right = window.innerWidth - content_div.getBoundingClientRect().right+ 5 + "px";
            desktop_sidebar.getElementsByTagName("ul")[0].classList.add("bg-slate-700");
        } else {
            desktop_sidebar.style.right = window.innerWidth - content_div.getBoundingClientRect().right - desktop_sidebar.offsetWidth + "px";
            desktop_sidebar.getElementsByTagName("ul")[0].classList.remove("bg-slate-700");
        }
    }
    adjust_desktop_sidebar_position();
    visualViewport.addEventListener("resize", () => {
        adjust_desktop_sidebar_position();
    });
});
