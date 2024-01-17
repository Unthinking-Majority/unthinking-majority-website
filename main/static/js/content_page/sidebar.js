function convertRemToPixels(rem) {
    return rem * parseFloat(getComputedStyle(document.documentElement).fontSize);
}

document.addEventListener("DOMContentLoaded", () => {
    /* Fix sticky sidebar margins when scrolling down */
    let observer = new IntersectionObserver(([e]) => {
        e.target.querySelector(".sidebar-button").classList.toggle('top-8', e.intersectionRatio < 1);
        e.target.querySelector(".sidebar-panel").classList.toggle('top-8', e.intersectionRatio < 1);
        e.target.querySelector(".sidebar-button").classList.toggle('-top-1', e.intersectionRatio === 1);
        e.target.querySelector(".sidebar-panel").classList.toggle('-top-1', e.intersectionRatio === 1);
    }, {threshold: [1]});
    observer.observe(document.getElementById("content-page-sidebar"));

    /* Display sidebar panel on click */
    document.querySelector("#content-page-sidebar .sidebar-button").addEventListener("click", (event) => {
        event.target.closest("div").classList.add("hidden");
        document.querySelector("#content-page-sidebar .sidebar-panel").classList.remove("hidden");
    });

    /* Close sidebar panel on click */
    document.addEventListener("click", (event) => {
        if (!document.querySelector("#content-page-sidebar").contains(event.target)) {
            document.querySelector("#content-page-sidebar .sidebar-panel").classList.add("hidden");
            document.querySelector("#content-page-sidebar .sidebar-button").classList.remove("hidden");
        }
    });

    /* Highlight entries in sidebar as users scroll to them */
    let headers = document.querySelectorAll(".content-page-body h2, .content-page-body h3");
    document.addEventListener("scroll", () => {
        /* Check if we've reached the top */
        if (window.scrollY === 0) {
            console.log("sir, we've landed on the moon. You're not going to like what you hear, but we're not the first ones to have done so... and these don't look like human footprints.")
        }
        /* Check if we've reached the bottom */
        if ((window.innerHeight + Math.round(window.scrollY)) >= document.documentElement.scrollHeight) {
            console.log("sir, we've reached the bottom of the marina trench.");
        }
    });
    let header_observer = new IntersectionObserver(([e]) => {
        if (e.isIntersecting) {
            console.log(e.target);
            console.log("ah yeah we active.");
        }
    }, {rootMargin: "-95% 0px 0px 0px"});
    headers.forEach(header => {header_observer.observe(header)});
});
