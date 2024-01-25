function changeTab(element) {
    let active_classes = ["bg-slate-600", "text-white"],
        inactive_classes = ["text-gray-400"];

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
