/** @odoo-module **/

import { Component, useState, onWillStart, useRef, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class EnterpriseOneAccountDashboard extends Component {
  static template = "enterpriseone_account_dashboard.DashboardTemplate";

  setup() {
    this.orm = useService("orm");
    this.currency = useService("currency");
    this.companyService = useService("company");

    this.state = useState({
      totalIncome: 0,
      todayIncome: 0,
      totalExpense: 0,
      todayExpense: 0,
      currencyId: null,
    });

    this.chartRef = useRef("chartCanvas");

    onWillStart(async () => {
      const company = this.companyService.currentCompany;
      this.state.currencyId = company ? company.currency_id : null;

      await this.loadData();
      // DON'T call createChart here - DOM doesn't exist yet!
    });

    // Call createChart AFTER component is mounted (DOM is ready)
    onMounted(() => {
      this.createChart();
    });
  }

  async loadData() {
    const today = new Date().toISOString().split("T")[0];
    let fiscalYearStart = `${new Date().getFullYear()}-01-01`;
    let fiscalYearEnd = `${new Date().getFullYear()}-12-31`;

    try {
      const fiscalYears = await this.orm.call(
        "account.fiscal.year",
        "search_read",
        [
          [
            ["date_from", "<=", today],
            ["date_to", ">=", today],
          ],
        ],
        ["date_from", "date_to"]
      );
      if (fiscalYears.length) {
        fiscalYearStart = fiscalYears[0].date_from;
        fiscalYearEnd = fiscalYears[0].date_to;
      }
    } catch (e) {
      console.warn("Using calendar year as fiscal period fallback");
    }

    // === INCOME: Cash/Bank inflows (debits) ===
    const liquidityAccounts = await this.orm.searchRead(
      "account.account",
      [["account_type", "=", "asset_cash"]],
      ["id"]
    );
    const liquidityIds = liquidityAccounts.map((a) => a.id);

    if (liquidityIds.length) {
      const lines = await this.orm.searchRead(
        "account.move.line",
        [
          ["move_id.state", "=", "posted"],
          ["account_id", "in", liquidityIds],
          ["date", ">=", fiscalYearStart],
          ["date", "<=", fiscalYearEnd],
        ],
        ["debit", "date"]
      );

      this.state.totalIncome = lines.reduce(
        (sum, line) => sum + (line.debit || 0),
        0
      );
      this.state.todayIncome = lines
        .filter((line) => line.date === today)
        .reduce((sum, line) => sum + (line.debit || 0), 0);
    }

    // === EXPENSES ===
    const expenseAccounts = await this.orm.searchRead(
      "account.account",
      [["internal_group", "=", "expense"]],
      ["id"]
    );
    const expenseIds = expenseAccounts.map((a) => a.id);

    if (expenseIds.length) {
      const lines = await this.orm.searchRead(
        "account.move.line",
        [
          ["move_id.state", "=", "posted"],
          ["account_id", "in", expenseIds],
          ["date", ">=", fiscalYearStart],
          ["date", "<=", fiscalYearEnd],
        ],
        ["debit", "date"]
      );

      this.state.totalExpense = lines.reduce(
        (sum, line) => sum + (line.debit || 0),
        0
      );
      this.state.todayExpense = lines
        .filter((line) => line.date === today)
        .reduce((sum, line) => sum + (line.debit || 0), 0);
    }
  }

  formatAmount(amount) {
    if (!this.state.currencyId) return amount.toString();
    return this.currency.format(amount, {
      currencyId: this.state.currencyId,
    });
  }

  createChart() {
    // Check if Chart.js is available
    if (typeof Chart === "undefined") {
      console.error(
        "❌ Chart.js is not loaded! Make sure chart.min.js is in your manifest."
      );
      return;
    }

    const canvas = this.chartRef.el;
    if (!canvas) {
      console.error("❌ Canvas element not found! Check your template t-ref.");
      return;
    }

    console.log("✅ Creating chart with data:", {
      income: this.state.totalIncome,
      expense: this.state.totalExpense,
    });

    // Destroy existing chart if it exists
    if (this.chart) {
      this.chart.destroy();
    }

    const ctx = canvas.getContext("2d");
    this.chart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["Total Income", "Total Expense"],
        datasets: [
          {
            label: "Amount",
            data: [this.state.totalIncome, this.state.totalExpense],
            backgroundColor: [
              "rgba(75, 192, 192, 0.6)",
              "rgba(255, 99, 132, 0.6)",
            ],
            borderColor: ["rgba(75, 192, 192, 1)", "rgba(255, 99, 132, 1)"],
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });

    console.log("✅ Chart created successfully!");
  }
}

registry
  .category("actions")
  .add("enterpriseone_account_dashboard", EnterpriseOneAccountDashboard);

console.log("✅ Dashboard module loaded");
console.log("✅ Chart.js available:", typeof Chart !== "undefined");
