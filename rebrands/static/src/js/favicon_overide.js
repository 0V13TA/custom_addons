(function() {
    function setFavicon(url) {
        let link = document.querySelector("link[rel~='icon']");
        if (!link) {
            link = document.createElement("link");
            link.rel = "icon";
            document.head.appendChild(link);
        }
        link.href = url;
    }

    document.addEventListener("DOMContentLoaded", function() {
        setFavicon("/rebrands/static/src/img/app_favicon.ico");
    });

    // Ensure it persists even if Odoo re-renders page dynamically
    const observer = new MutationObserver(() => {
        setFavicon("/rebrands/static/src/img/app_favicon.ico");
    });

    observer.observe(document.head, { childList: true, subtree: true });
})();
