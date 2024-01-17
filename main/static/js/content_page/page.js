document.addEventListener("DOMContentLoaded", () => {
    /* Copy the url to the users clipboard on click */
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            navigator.clipboard.writeText(this.href).then();
        });
    });
});
