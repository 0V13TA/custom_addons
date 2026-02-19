/** @odoo-module **/

// Force blue styling on all menus, including the specific CSS variable
(function() {
    // Immediately inject CSS with important rules
    function injectStyles() {
        // Create style element if it doesn't exist
        if (!document.getElementById('hemis_custom_styles')) {
            const styleTag = document.createElement('style');
            styleTag.id = 'hemis_custom_styles';
            styleTag.innerHTML = `
                /* Override the CSS variable itself */
                :root {
                    --NavBar-entry-backgroundColor: #0165fc !important;
                }
                
                /* Direct override for the specific menu items */
                .o_main_navbar .o_menu_sections .o_nav_entry, 
                .o_main_navbar .o_menu_sections .dropdown-toggle {
                    background: #0165fc !important;
                    border: 1px solid transparent !important;
                }
                
                /* Header styling */
                .hemis_custom_header {
                    background-color: #0165fc !important;
                    color: white !important;
                    padding: 10px 0 !important;
                    text-align: center !important;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
                }
                
                /* Override all navbar and menu styles */
                .o_main_navbar, 
                .o_menu_sections,
                .o_sub_menu,
                .o_navbar_apps_menu {
                    background-color: #0165fc !important;
                    border-color: rgba(255,255,255,0.2) !important;
                }
                
                /* Menu items text color */
                .o_main_navbar a,
                .o_main_navbar button,
                .o_main_navbar span,
                .o_menu_sections a,
                .o_menu_sections button,
                .o_menu_sections span,
                .o_sub_menu a,
                .o_sub_menu button,
                .o_sub_menu span,
                .dropdown-toggle,
                .dropdown-item {
                    color: white !important;
                }
                
                /* Dropdown menus */
                .dropdown-menu {
                    background-color: #0165fc !important;
                    border-color: rgba(255,255,255,0.2) !important;
                }
                
                /* Hover states */
                .o_main_navbar a:hover,
                .o_main_navbar button:hover,
                .o_menu_sections a:hover,
                .o_menu_sections button:hover,
                .o_sub_menu a:hover,
                .dropdown-item:hover,
                .dropdown-toggle:hover {
                    background-color: #1a4e83 !important;
                }
            `;
            document.head.appendChild(styleTag);
        }
    }
    
    // Inject HEMIS header if it doesn't exist
    function injectHeader() {
        if (!document.querySelector('.hemis_custom_header')) {
            const headerDiv = document.createElement('div');
            headerDiv.className = 'hemis_custom_header';
            headerDiv.innerHTML = `
                <div style="max-width: 1200px; margin: 0 auto; padding: 0 15px;">
                    <h1 style="font-size: 22px; margin: 0; font-weight: normal;color:#fff">
                        EnterpriseOne
                    </h1>
                </div>
            `;
            
            // Insert before navbar
            const navbar = document.querySelector('.o_main_navbar');
            if (navbar && navbar.parentNode) {
                navbar.parentNode.insertBefore(headerDiv, navbar);
            }
        }
    }
    
    // Apply all styling
    function applyAll() {
        injectStyles();
        injectHeader();
        
        // Also directly modify the element styles for absolute certainty
        const menuItems = document.querySelectorAll('.o_main_navbar .o_menu_sections .o_nav_entry, .o_main_navbar .o_menu_sections .dropdown-toggle');
        menuItems.forEach(item => {
            item.style.setProperty('background', '#0165fc', 'important');
            item.style.setProperty('background-color', '#0165fc', 'important');
        });
    }
    
    // Run on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyAll);
    } else {
        applyAll();
    }
    
    // Re-apply periodically
    setInterval(applyAll, 500);
    
    // Apply when DOM changes
    const observer = new MutationObserver(applyAll);
    if (document.body) {
        observer.observe(document.body, { childList: true, subtree: true });
    } else {
        document.addEventListener('DOMContentLoaded', function() {
            observer.observe(document.body, { childList: true, subtree: true });
        });
    }
})();