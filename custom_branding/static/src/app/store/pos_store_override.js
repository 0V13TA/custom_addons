/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

// Patch the POS store to ensure custom branding fields are available
patch(PosStore.prototype, {
    /**
     * Override processServerData to set custom logo in company_logo_base64
     */
    async processServerData() {
        console.log("[Custom Branding] processServerData called");
        await super.processServerData();
        
        console.log("[Custom Branding] Company loaded:", this.company);
        console.log("[Custom Branding] Company ID:", this.company?.id);
        console.log("[Custom Branding] Company name:", this.company?.name);
        console.log("[Custom Branding] Company pos_logo exists:", !!this.company?.pos_logo);
        console.log("[Custom Branding] Company pos_logo length:", this.company?.pos_logo?.length);
        console.log("[Custom Branding] Company pos_company_name:", this.company?.pos_company_name);
        console.log("[Custom Branding] Company logo exists:", !!this.company?.logo);
        console.log("[Custom Branding] Company logo length:", this.company?.logo?.length);
        
        // After company is loaded, set custom logo if available
        if (this.company && this.company.pos_logo) {
            // Use custom POS logo instead of default company logo
            this.company_logo_base64 = `data:image/png;base64,${this.company.pos_logo}`;
            console.log("[Custom Branding] Set company_logo_base64 from pos_logo, length:", this.company_logo_base64.length);
        } else if (this.company && this.company.logo) {
            // Fallback to default company logo
            this.company_logo_base64 = `data:image/png;base64,${this.company.logo}`;
            console.log("[Custom Branding] Set company_logo_base64 from default logo, length:", this.company_logo_base64.length);
        } else {
            console.log("[Custom Branding] No logo found, company_logo_base64 remains:", this.company_logo_base64);
        }
        
        console.log("[Custom Branding] Final company_logo_base64 set:", !!this.company_logo_base64);
    },
    
    /**
     * Override getReceiptHeaderData to ensure custom branding fields are included
     */
    getReceiptHeaderData(order) {
        const result = super.getReceiptHeaderData(order);
        
        // Ensure custom branding fields are available in company data
        if (result.company && this.company) {
            // Custom logo (if set, use it; otherwise keep default)
            if (this.company.pos_logo) {
                result.company.pos_logo = this.company.pos_logo;
            }
            // Custom company name (if set, use it; otherwise keep default)
            if (this.company.pos_company_name) {
                result.company.pos_company_name = this.company.pos_company_name;
            }
            // Footer text
            if (this.company.pos_receipt_footer_text) {
                result.company.pos_receipt_footer_text = this.company.pos_receipt_footer_text;
            }
        }
        
        return result;
    },
});

