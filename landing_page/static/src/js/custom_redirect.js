/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class CustomDashboard extends Component {
  static template = "dashboard_page";

  setup() {
    super.setup();
    this.action = useService("action");
    this.orm = useService("orm");
    this.notification = useService("notification");
    console.log("CustomDashboard component setup completed");
  }

  async onDashboardClick(moduleName) {
    console.log("Dashboard clicked:", moduleName);

    // Configuration mapping: module name to XML ID and menu ID
    const moduleConfig = {
      accounting: {
        xmlId: "enterpriseone_account_dashboard.action_enterpriseone_dashboard",
        menuXmlId: "account.menu_finance", // Accounting root menu
        name: "Accounting",
      },

      purchase: {
        xmlId: "h_jubran_prd.action_h_jubran_purchase_request",
        menuXmlId: "h_jubran_prd.menu_purchase_request_under_purchase",
        name: "Purchase",
      },
      inventory: {
        xmlId: "stock.action_picking_tree_all",
        menuXmlId: "stock.menu_stock_root",
        name: "Inventory",
      },
      hr: {
        xmlId: "hr.open_view_employee_list_my",
        menuXmlId: "hr.menu_hr_root",
        name: "HR",
      },
      sales: {
        xmlId: "sale.action_orders",
        menuXmlId: "sale.sale_menu_root",
        name: "Sales",
      },
      project: {
        xmlId: "h_jubran_prd.action_h_jubran_project",
        menuXmlId: "h_jubran_prd.menu_h_jubran_project_root",
        name: "Project Budget",
      },
    };

    const config = moduleConfig[moduleName];
    if (!config) {
      console.warn("No configuration found for module:", moduleName);
      this.notification.add(`Module not configured: ${moduleName}`, {
        type: "warning",
      });
      return;
    }

    try {
      // First, get the menu ID
      let menuId = null;
      if (config.menuXmlId) {
        const [menuModule, menuName] = config.menuXmlId.split(".");
        const menuData = await this.orm.searchRead(
          "ir.model.data",
          [
            ["module", "=", menuModule],
            ["name", "=", menuName],
            ["model", "=", "ir.ui.menu"],
          ],
          ["res_id"],
        );

        if (menuData && menuData.length > 0) {
          menuId = menuData[0].res_id;
          console.log("Found menu ID:", menuId);
        }
      }

      // Then get the action
      const [module, actionName] = config.xmlId.split(".");
      const actionData = await this.orm.searchRead(
        "ir.model.data",
        [
          ["module", "=", module],
          ["name", "=", actionName],
        ],
        ["res_id", "model"],
      );

      if (actionData && actionData.length > 0) {
        const actionId = actionData[0].res_id;
        const actionModel = actionData[0].model;

        console.log("Found action:", {
          id: actionId,
          model: actionModel,
          xmlId: config.xmlId,
          menuId: menuId,
        });

        // Execute the action with menu context
        const actionOptions = {
          clearBreadcrumbs: true,
          stackPosition: "replaceCurrentAction",
        };

        // Add menu_id to the action options if we found it
        if (menuId) {
          actionOptions.additionalContext = {
            active_id: menuId,
          };
        }

        await this.action.doAction(actionId, actionOptions);

        // Set the active menu in the UI
        if (menuId) {
          const menuService = this.env.services.menu;
          if (menuService && menuService.setCurrentMenu) {
            menuService.setCurrentMenu(menuId);
          }
        }
      } else {
        throw new Error(`Action not found: ${config.xmlId}`);
      }
    } catch (error) {
      console.error("Error opening module:", moduleName, error);
      this.notification.add(
        `Failed to open ${config.name}. Currently, the model is not available`,
        {
          type: "danger",
          sticky: true,
        },
      );
    }
  }
}

registry.category("actions").add("custom_redirect", CustomDashboard);

console.log("CustomDashboard registered successfully");
