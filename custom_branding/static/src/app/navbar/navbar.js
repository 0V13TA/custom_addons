/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Navbar } from "@point_of_sale/app/navbar/navbar";

// Patch Navbar to add debugging
patch(Navbar.prototype, {
    setup() {
        super.setup();
        console.log("[Custom Branding Navbar] Navbar setup called");
    },
    
    get logoSource() {
        const logo = this.pos.company_logo_base64 || "/web/static/img/logo.png";
        console.log("[Custom Branding Navbar] Logo source:", logo ? (logo.substring(0, 50) + "...") : "null");
        console.log("[Custom Branding Navbar] pos.company_logo_base64:", this.pos.company_logo_base64 ? (this.pos.company_logo_base64.substring(0, 50) + "...") : "null");
        console.log("[Custom Branding Navbar] pos.company:", this.pos.company);
        console.log("[Custom Branding Navbar] pos.company.pos_logo:", this.pos.company?.pos_logo ? (this.pos.company.pos_logo.substring(0, 50) + "...") : "null");
        return logo;
    },
});


