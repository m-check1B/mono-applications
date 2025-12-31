import { a as attr } from "../../../../../chunks/attributes.js";
import { e as escape_html } from "../../../../../chunks/escaping.js";
import { B as Button } from "../../../../../chunks/Button.js";
import { C as Card } from "../../../../../chunks/Card.js";
import { B as Badge } from "../../../../../chunks/Badge.js";
import "../../../../../chunks/client.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let users = [];
    let showCreateModal = false;
    let formData = {
      email: "",
      firstName: "",
      lastName: "",
      role: "AGENT",
      password: ""
    };
    const resetForm = () => {
      formData = {
        email: "",
        firstName: "",
        lastName: "",
        role: "AGENT",
        password: ""
      };
    };
    const handleCreate = async () => {
      try {
        console.log("Creating user:", formData);
        const newUser = {
          id: Date.now().toString(),
          ...formData,
          status: "OFFLINE",
          createdAt: (/* @__PURE__ */ new Date()).toISOString()
        };
        users = [...users, newUser];
        showCreateModal = false;
        resetForm();
      } catch (err) {
        alert(`Failed to create user: ${err.message}`);
      }
    };
    $$renderer2.push(`<div class="space-y-6">`);
    Card($$renderer2, {
      children: ($$renderer3) => {
        $$renderer3.push(`<div class="p-6"><div class="flex items-center justify-between"><div><h1 class="text-2xl font-bold text-gray-900 dark:text-white">User Management</h1> <p class="text-gray-600 dark:text-gray-400 mt-1">Manage system users and their roles</p></div> `);
        Button($$renderer3, {
          variant: "primary",
          onclick: () => showCreateModal = true,
          children: ($$renderer4) => {
            $$renderer4.push(`<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg> New User`);
          }
        });
        $$renderer3.push(`<!----></div></div>`);
      }
    });
    $$renderer2.push(`<!----> `);
    {
      let header = function($$renderer3) {
        $$renderer3.push(`<div class="flex justify-between items-center"><h3 class="text-lg font-semibold text-gray-900 dark:text-white">All Users</h3> `);
        Badge($$renderer3, {
          variant: "gray",
          class: "text-xs",
          children: ($$renderer4) => {
            $$renderer4.push(`<!---->Total: ${escape_html(users.length)}`);
          }
        });
        $$renderer3.push(`<!----></div>`);
      };
      Card($$renderer2, {
        header,
        children: ($$renderer3) => {
          {
            $$renderer3.push("<!--[-->");
            $$renderer3.push(`<div class="text-center py-8"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div> <p class="mt-4 text-gray-600 dark:text-gray-400">Loading users...</p></div>`);
          }
          $$renderer3.push(`<!--]-->`);
        }
      });
    }
    $$renderer2.push(`<!----></div> `);
    if (showCreateModal) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"><div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4"><h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Create New User</h3> <div class="space-y-4"><div><label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email *</label> <input type="email"${attr("value", formData.email)} placeholder="user@example.com" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"/></div> <div class="grid grid-cols-2 gap-4"><div><label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">First Name *</label> <input type="text"${attr("value", formData.firstName)} class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"/></div> <div><label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Last Name *</label> <input type="text"${attr("value", formData.lastName)} class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"/></div></div> <div><label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Role *</label> `);
      $$renderer2.select(
        {
          value: formData.role,
          class: "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
        },
        ($$renderer3) => {
          $$renderer3.option({ value: "AGENT" }, ($$renderer4) => {
            $$renderer4.push(`Agent`);
          });
          $$renderer3.option({ value: "SUPERVISOR" }, ($$renderer4) => {
            $$renderer4.push(`Supervisor`);
          });
          $$renderer3.option({ value: "ADMIN" }, ($$renderer4) => {
            $$renderer4.push(`Admin`);
          });
        }
      );
      $$renderer2.push(`</div> <div><label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Password *</label> <input type="password"${attr("value", formData.password)} class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"/></div></div> <div class="flex gap-2 justify-end mt-6">`);
      Button($$renderer2, {
        variant: "secondary",
        onclick: () => {
          showCreateModal = false;
          resetForm();
        },
        children: ($$renderer3) => {
          $$renderer3.push(`<!---->Cancel`);
        }
      });
      $$renderer2.push(`<!----> `);
      Button($$renderer2, {
        variant: "primary",
        onclick: handleCreate,
        disabled: !formData.email || !formData.firstName || !formData.lastName || !formData.password,
        children: ($$renderer3) => {
          $$renderer3.push(`<!---->Create User`);
        }
      });
      $$renderer2.push(`<!----></div></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
  });
}
export {
  _page as default
};
