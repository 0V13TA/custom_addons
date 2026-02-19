/** @odoo-module **/

console.log("Persist Menu Script Loaded");

// 1. Save Active Menu on Click
document.addEventListener('click', function(e) {
    // Find the closest menu link
    const link = e.target.closest('.o_menu_sections a, .o_main_navbar .o_menu_sections .dropdown-toggle');
    if (link) {
        // Save the text content (e.g., "Student", "Dashboard")
        const menuName = link.innerText.trim();
        sessionStorage.setItem('hemis_active_menu_name', menuName);
        
        // Immediately highlight
        applyHighlight(link);
    }
}, true); // Capture phase

// 2. Apply Highlight Logic
function applyHighlight(targetElement) {
    // Remove class from everyone
    document.querySelectorAll('.hemis-persist-underline').forEach(el => {
        el.classList.remove('hemis-persist-underline');
    });
    
    // Add to target
    if (targetElement) {
        targetElement.classList.add('hemis-persist-underline');
    }
}

// 3. Restore from Storage (Polling to handle Odoo re-renders)
setInterval(() => {
    const activeName = sessionStorage.getItem('hemis_active_menu_name');
    if (activeName) {
        // Find links with matching text
        const allLinks = document.querySelectorAll('.o_menu_sections a, .o_main_navbar .o_menu_sections .dropdown-toggle');
        let found = false;
        
        allLinks.forEach(link => {
            if (link.innerText.trim() === activeName) {
                // Only re-apply if missing (optimization)
                if (!link.classList.contains('hemis-persist-underline')) {
                    applyHighlight(link);
                }
                found = true;
            }
        });
    }
}, 300); // Check every 300ms
