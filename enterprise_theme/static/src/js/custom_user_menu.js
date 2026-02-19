/** @odoo-module **/

import { UserMenu } from "@web/webclient/user_menu/user_menu";
import { patch } from "@web/core/utils/patch";

patch(UserMenu.prototype, {
    getElements() {
        const elements = super.getElements();
        // Filter to keep only the logout element
        return elements.filter(item => item.id === "logout");
    },
    async willStart() {
        await super.willStart();
        console.log(this);
        // Method 1: Patch the menu items directly
        if (this._userMenuItems) {
            this._userMenuItems = this._userMenuItems.filter(item => item.id === "logout");
        }
        
        // Method 2: Override the entire menu items getter
        Object.defineProperty(this, "menuItems", {
            get: function() {
                return [
                    {
                        id: "logout",
                        description: "Log out",
                        callback: () => this.onLogout(),
                        sequence: 10,
                        class: "dropdown-item",
                    }
                ];
            },
            configurable: true,
        });
    },
    

    // Method 3: Clean up after render if needed
    onMounted() {
        super.onMounted();
        setTimeout(() => {
            const items = this.el.querySelectorAll('.dropdown-item');
            console.log(items);
            items.forEach(item => {
                if (!item.dataset.menu || item.dataset.menu !== "logout") {
                    item.remove();
                }
            });
        }, 0);
    }
});