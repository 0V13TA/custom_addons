import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";


const userMenuRegistry = registry.category("user_menuitems");

// Remove the original 'preferences' item
userMenuRegistry.remove("documentation");
userMenuRegistry.remove("support");
userMenuRegistry.remove("shortcuts");
userMenuRegistry.remove("separator");
userMenuRegistry.remove("profile");
userMenuRegistry.remove("odoo_account");
userMenuRegistry.remove("install_pwa");


function overridePreferences(env) {
    const url = "https://enterpriseone.com.ng/";
    return {
        type: "item",
        id: "enterprise_page",
        description: _t("Documentation"),   // ✅ now works
        href: url,    // your custom URL        
        callback: () => {
            window.open(url, "_blank");
                },
        sequence: 20,
    };
}

registry.category("user_menuitems").add("enterprise_page", overridePreferences, { override: true });
