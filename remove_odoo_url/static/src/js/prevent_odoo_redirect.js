/** @odoo-module **/

import { registry } from "@web/core/registry";
import { session } from "@web/session";

// Service to fetch and apply custom URL name from system parameter
const customUrlService = {
  dependencies: [],

  start() {
    let customName = "aims"; // Default fallback

    // Fetch the custom URL name from system parameter
    async function fetchCustomUrlName() {
      try {
        const response = await fetch("/web/dataset/call_kw", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            jsonrpc: "2.0",
            method: "call",
            params: {
              model: "ir.config_parameter",
              method: "get_param",
              args: ["web.base.urlname", "enterpriseone"],
              kwargs: {},
            },
            id: new Date().getTime(),
          }),
        });

        const data = await response.json();
        if (data.result) {
          customName = data.result;
        }
      } catch (error) {
        console.log("Using default URL name: enterpriseone");
      }
    }

    // Override window.history methods to intercept /odoo
    function setupInterceptors() {
      const originalPushState = window.history.pushState;
      window.history.pushState = function (state, title, url) {
        if (url && typeof url === "string" && url.includes("/odoo")) {
          url = url.replace(/\/odoo/g, "/" + customName);
        }
        return originalPushState.call(this, state, title, url);
      };

      const originalReplaceState = window.history.replaceState;
      window.history.replaceState = function (state, title, url) {
        if (url && typeof url === "string" && url.includes("/odoo")) {
          url = url.replace(/\/odoo/g, "/" + customName);
        }
        return originalReplaceState.call(this, state, title, url);
      };
    }

    // Check on page load if we're on /odoo and redirect
    if (window.location.pathname.startsWith("/odoo")) {
      fetchCustomUrlName().then(() => {
        const newPath = window.location.pathname.replace(
          /^\/odoo/,
          "/" + customName
        );
        window.location.replace(
          newPath + window.location.search + window.location.hash
        );
      });
    } else {
      // Fetch and setup interceptors
      fetchCustomUrlName().then(() => {
        setupInterceptors();
      });
    }

    return {};
  },
};

registry.category("services").add("customUrlService", customUrlService);
