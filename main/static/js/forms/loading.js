document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("form").forEach(el => {
        el.addEventListener("submit", () => {
            let submit_button = el.querySelector(":scope button[type='submit']");
            submit_button.querySelector(":scope svg").classList.remove("hidden");
            submit_button.disabled = true;
            submit_button.classList.add("text-white", "bg-gray-800");
        });
    });
});