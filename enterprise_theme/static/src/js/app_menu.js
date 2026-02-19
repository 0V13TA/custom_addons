/** @odoo-module **/

import { session } from "@web/session";
import { jsonRpc } from "@web/core/network/rpc";
import { UserMenu } from "@web/webclient/user_menu/user_menu";
import { patch } from "@web/core/utils/patch";

document.addEventListener("DOMContentLoaded", () => {
    const isAdmin = session.is_system;
    customizeAppDisplay(isAdmin);
    bindAppClickEvents();
    initAppGrid();
});

function customizeAppDisplay(isAdmin) {
    const containerSelector = isAdmin ? '.admin_apps' : '.user_apps';
    const container = document.querySelector(containerSelector);
    if (!container) return;
    container.innerHTML = '';

    const apps = getAppsForUser(isAdmin);
    const grid = document.createElement('div');
    grid.classList.add('apps_grid');
    container.appendChild(grid);

    apps.forEach(app => {
        const item = createAppItem(app);
        grid.appendChild(item);
    });
}

function getAppsForUser(isAdmin) {
    return isAdmin
        ? [
              { id: 'dash', name: 'Dashboard', icon: 'fa-dashboard', description: 'Admin overview' },
              { id: 'apps', name: 'Applications', icon: 'fa-cubes', description: 'Manage applications' },
              { id: 'users', name: 'Users', icon: 'fa-users', description: 'User management' },
              { id: 'settings', name: 'Settings', icon: 'fa-cogs', description: 'System configuration' },
              { id: 'accounting', name: 'Accounting', icon: 'fa-money', description: 'Financial management' },
              { id: 'logs', name: 'System Logs', icon: 'fa-list', description: 'View system logs' },
          ]
        : [
              { id: 'dashboard', name: 'Dashboard', icon: 'fa-dashboard', description: 'Your overview' },
              { id: 'accounting', name: 'Accounting', icon: 'fa-money', description: 'Financial management' },
              { id: 'reports', name: 'Reports', icon: 'fa-bar-chart', description: 'View reports' },
              { id: 'documents', name: 'Documents', icon: 'fa-file-text', description: 'Document management' },
          ];
}

function createAppItem(app) {
    const item = document.createElement('div');
    item.classList.add('app_item', app.id);
    item.dataset.appId = app.id;

    const icon = document.createElement('div');
    icon.classList.add('app_icon');
    icon.innerHTML = `<i class="fa ${app.icon}"></i>`;

    const name = document.createElement('div');
    name.classList.add('app_name');
    name.textContent = app.name;

    const desc = document.createElement('div');
    desc.classList.add('app_description');
    desc.textContent = app.description;

    item.append(icon, name, desc);
    return item;
}

function bindAppClickEvents() {
    document.addEventListener('click', function (e) {
        const appItem = e.target.closest('.app_item');
        if (appItem) {
            const appId = appItem.dataset.appId;
            window.location.href = `/web#menu_id=${appId}`;
        }
    });
}

function initAppGrid() {
    const categoryTabs = document.querySelectorAll('.category_tab');
    const appTiles = document.querySelectorAll('.app_tile');

    categoryTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const category = tab.dataset.category;
            categoryTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            appTiles.forEach(tile => {
                if (category === 'all' || tile.classList.contains(category)) {
                    tile.style.display = '';
                } else {
                    tile.style.display = 'none';
                }
            });
        });
    });

    const searchInput = document.querySelector('.app_search_input');
    const searchButton = document.querySelector('.app_search_button');

    function searchApps() {
        const term = searchInput?.value.toLowerCase() || '';
        appTiles.forEach(tile => {
            const name = tile.querySelector('.app_name')?.textContent.toLowerCase() || '';
            const desc = tile.querySelector('.app_description')?.textContent.toLowerCase() || '';
            tile.style.display = (name.includes(term) || desc.includes(term)) ? '' : 'none';
        });
    }

    searchInput?.addEventListener('input', searchApps);
    searchButton?.addEventListener('click', searchApps);

    if (session.is_system) {
        document.querySelector('.hemis_app_view')?.classList.add('admin');
    }

    document.querySelectorAll('.app_launch_btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            if (href) window.location.href = href;
        });
    });
}

patch(UserMenu.prototype, ({ setup }) => ({
    setup() {
        setup.call(this);
        this._getUserFromAPI();
        this._removeCompanyMenu();
    },

    _getUserFromAPI() {
        const token = sessionStorage.getItem("external_token");
        if (!token) return;

        jsonRpc("/get_api_user_info", "call", { token })
            .then((result) => {
                if (result && !result.error) {
                    const userNameElem = document.querySelector(".hemis_user .user_name");
                    if (userNameElem && result.name) userNameElem.textContent = result.name;
                    if (result.role) sessionStorage.setItem("user_role", result.role);
                } else {
                    console.error("Error fetching user info:", result.error);
                }
            })
            .catch((error) => {
                console.error("API request failed:", error);
            });
    },

    _removeCompanyMenu() {
        setTimeout(() => {
            const companyMenu = document.querySelector(".o_user_menu .dropdown-menu .dropdown-item[href*='my']");
            if (companyMenu) {
                companyMenu.remove();
            }
        }, 500);
    },
}));
