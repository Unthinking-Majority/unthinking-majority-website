/* Simple js for switching displayable content on page using tabs/buttons */

function changeTab(element) {
    let active_classes = ["bg-slate-800", "text-white", "shadow-slate-700/50", "pointer-events-none"],
        inactive_classes = ["bg-gray-200", "hover:scale-105", "hover:bg-slate-800", "hover:text-gray-200"];

    /* Hide the actual content of each tab */
    Array.from(document.getElementsByClassName("tab-content")).forEach(el => {
        el.classList.add("hidden");
    });

    /* Reset styling for all tab buttons */
    Array.from(document.getElementsByClassName("tab-button")).forEach(el => {
        el.classList.remove(...active_classes);
        el.classList.add(...inactive_classes);
    });

    /* Add active styling to the selected tab */
    element.classList.add(...active_classes);
    element.classList.remove(...inactive_classes);
    document.getElementById(element.dataset.table).classList.remove("hidden");
}

document.addEventListener("DOMContentLoaded", () => {
    /* Set active tab to active_tab in get params, otherwise set first tab active */
    let params = new URLSearchParams(window.location.search);
    if (params.get("active_tab")) {
        changeTab(document.getElementById(params.get("active_tab")));
    } else {
        changeTab(document.querySelectorAll(".tab-button")[0]);
    }

    document.querySelectorAll(".tab-button").forEach(el => {
        el.addEventListener("click", () => {
            changeTab(el);
        });
    });
});
