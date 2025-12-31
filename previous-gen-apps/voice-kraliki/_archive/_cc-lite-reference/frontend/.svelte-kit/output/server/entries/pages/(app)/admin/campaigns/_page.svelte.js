import "clsx";
import { y as ensure_array_like } from "../../../../../chunks/index2.js";
import { B as Button } from "../../../../../chunks/Button.js";
import { C as Card } from "../../../../../chunks/Card.js";
import { B as Badge } from "../../../../../chunks/Badge.js";
import { t as trpc } from "../../../../../chunks/client.js";
import { e as escape_html } from "../../../../../chunks/escaping.js";
import { a as attr } from "../../../../../chunks/attributes.js";
function CampaignManagement($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let campaigns = [];
    let showCreateModal = false;
    let showEditModal = false;
    let showDeleteModal = false;
    let selectedCampaign = null;
    let formData = {
      name: "",
      description: "",
      script: "",
      priority: "medium",
      targetCallsPerDay: 100,
      startDate: "",
      endDate: ""
    };
    const resetForm = () => {
      formData = {
        name: "",
        description: "",
        script: "",
        priority: "medium",
        targetCallsPerDay: 100,
        startDate: "",
        endDate: ""
      };
    };
    const handleCreate = async () => {
      try {
        const newCampaign = await trpc.campaign.create.mutate({
          name: formData.name,
          description: formData.description,
          script: formData.script,
          priority: formData.priority,
          targetCallsPerDay: formData.targetCallsPerDay,
          startDate: formData.startDate ? new Date(formData.startDate).toISOString() : void 0,
          endDate: formData.endDate ? new Date(formData.endDate).toISOString() : void 0
        });
        campaigns = [
          ...campaigns,
          { ...newCampaign, _count: { sessions: 0, metrics: 0 } }
        ];
        showCreateModal = false;
        resetForm();
      } catch (err) {
        console.error("Failed to create campaign:", err);
        alert(`Failed to create campaign: ${err.message}`);
      }
    };
    const handleEdit = (campaign) => {
      selectedCampaign = campaign;
      formData = {
        name: campaign.name,
        description: campaign.description || "",
        script: "",
        priority: "medium",
        targetCallsPerDay: 100,
        startDate: "",
        endDate: ""
      };
      showEditModal = true;
    };
    const handleUpdate = async () => {
      if (!selectedCampaign) return;
      try {
        const updated = await trpc.campaign.update.mutate({
          id: selectedCampaign.id,
          name: formData.name,
          description: formData.description,
          script: formData.script,
          priority: formData.priority,
          targetCallsPerDay: formData.targetCallsPerDay
        });
        campaigns = campaigns.map((c) => c.id === selectedCampaign.id ? { ...c, name: formData.name, description: formData.description } : c);
        showEditModal = false;
        resetForm();
        selectedCampaign = null;
      } catch (err) {
        console.error("Failed to update campaign:", err);
        alert(`Failed to update campaign: ${err.message}`);
      }
    };
    const handleToggleCampaign = async (campaign) => {
      try {
        if (campaign.active) {
          await trpc.campaign.pause.mutate({ id: campaign.id });
        } else {
          await trpc.campaign.start.mutate({ id: campaign.id });
        }
        campaigns = campaigns.map((c) => c.id === campaign.id ? { ...c, active: !c.active } : c);
      } catch (err) {
        console.error("Failed to toggle campaign:", err);
        alert(`Failed to ${campaign.active ? "pause" : "start"} campaign: ${err.message}`);
      }
    };
    const handleDelete = async () => {
      if (!selectedCampaign) return;
      try {
        await trpc.campaign.delete.mutate({ id: selectedCampaign.id });
        campaigns = campaigns.filter((c) => c.id !== selectedCampaign.id);
        showDeleteModal = false;
        selectedCampaign = null;
      } catch (err) {
        console.error("Failed to delete campaign:", err);
        alert(`Failed to delete campaign: ${err.message}`);
      }
    };
    const getStatusColor = (active) => {
      return active ? "success" : "gray";
    };
    $$renderer2.push(`<div class="space-y-6">`);
    Card($$renderer2, {
      children: ($$renderer3) => {
        $$renderer3.push(`<div class="p-6"><div class="flex items-center justify-between"><div><h2 class="text-2xl font-bold text-gray-900 dark:text-white">Campaign Management</h2> <p class="text-gray-600 dark:text-gray-400 mt-1">Create and manage outbound calling campaigns</p></div> `);
        Button($$renderer3, {
          variant: "primary",
          onclick: () => showCreateModal = true,
          children: ($$renderer4) => {
            $$renderer4.push(`<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg> New Campaign`);
          }
        });
        $$renderer3.push(`<!----></div></div>`);
      }
    });
    $$renderer2.push(`<!----> `);
    {
      let header = function($$renderer3) {
        $$renderer3.push(`<div class="flex justify-between items-center"><h3 class="text-lg font-semibold text-gray-900 dark:text-white">Active Campaigns</h3> <div class="flex gap-2">`);
        Badge($$renderer3, {
          variant: "gray",
          class: "text-xs",
          children: ($$renderer4) => {
            $$renderer4.push(`<!---->Total: ${escape_html(campaigns.length)}`);
          }
        });
        $$renderer3.push(`<!----> `);
        Badge($$renderer3, {
          variant: "success",
          class: "text-xs",
          children: ($$renderer4) => {
            $$renderer4.push(`<!---->Active: ${escape_html(campaigns.filter((c) => c.active).length)}`);
          }
        });
        $$renderer3.push(`<!----></div></div>`);
      };
      Card($$renderer2, {
        header,
        children: ($$renderer3) => {
          $$renderer3.push(`<div class="overflow-x-auto">`);
          if (campaigns.length === 0) {
            $$renderer3.push("<!--[-->");
            $$renderer3.push(`<div class="text-center py-8 text-gray-500">No campaigns found</div>`);
          } else {
            $$renderer3.push("<!--[!-->");
            $$renderer3.push(`<table class="w-full"><thead class="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700"><tr><th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Name</th><th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th><th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Calls</th><th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Metrics</th><th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Created</th><th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th></tr></thead><tbody class="divide-y divide-gray-200 dark:divide-gray-700"><!--[-->`);
            const each_array = ensure_array_like(campaigns);
            for (let i = 0, $$length = each_array.length; i < $$length; i++) {
              let campaign = each_array[i];
              $$renderer3.push(`<tr class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"><td class="px-4 py-3"><div><p class="font-medium text-gray-900 dark:text-white">${escape_html(campaign.name)}</p> `);
              if (campaign.description) {
                $$renderer3.push("<!--[-->");
                $$renderer3.push(`<p class="text-sm text-gray-500 truncate max-w-xs">${escape_html(campaign.description)}</p>`);
              } else {
                $$renderer3.push("<!--[!-->");
              }
              $$renderer3.push(`<!--]--></div></td><td class="px-4 py-3">`);
              Badge($$renderer3, {
                variant: getStatusColor(campaign.active),
                class: "text-xs",
                children: ($$renderer4) => {
                  $$renderer4.push(`<!---->${escape_html(campaign.active ? "Active" : "Paused")}`);
                }
              });
              $$renderer3.push(`<!----></td><td class="px-4 py-3"><span class="text-gray-900 dark:text-white">${escape_html(campaign._count.sessions)}</span></td><td class="px-4 py-3"><span class="text-gray-900 dark:text-white">${escape_html(campaign._count.metrics)}</span></td><td class="px-4 py-3"><p class="text-sm text-gray-500">${escape_html(new Date(campaign.createdAt).toLocaleDateString())}</p></td><td class="px-4 py-3"><div class="flex gap-2">`);
              Button($$renderer3, {
                size: "sm",
                variant: campaign.active ? "warning" : "success",
                onclick: () => handleToggleCampaign(campaign),
                children: ($$renderer4) => {
                  $$renderer4.push(`<!---->${escape_html(campaign.active ? "Pause" : "Start")}`);
                }
              });
              $$renderer3.push(`<!----> `);
              Button($$renderer3, {
                size: "sm",
                variant: "secondary",
                onclick: () => handleEdit(campaign),
                children: ($$renderer4) => {
                  $$renderer4.push(`<!---->Edit`);
                }
              });
              $$renderer3.push(`<!----> `);
              Button($$renderer3, {
                size: "sm",
                variant: "danger",
                onclick: () => {
                  selectedCampaign = campaign;
                  showDeleteModal = true;
                },
                disabled: campaign.active,
                children: ($$renderer4) => {
                  $$renderer4.push(`<!---->Delete`);
                }
              });
              $$renderer3.push(`<!----></div></td></tr>`);
            }
            $$renderer3.push(`<!--]--></tbody></table>`);
          }
          $$renderer3.push(`<!--]--></div>`);
        }
      });
    }
    $$renderer2.push(`<!----></div> `);
    if (showCreateModal) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"><div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto"><h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Create New Campaign</h3> <div class="space-y-4"><div><label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Campaign Name *</label> <input type="text"${attr("value", formData.name)} placeholder="Enter campaign name" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"/></div> <div><label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label> <textarea placeholder="Describe the campaign objectives" rows="3" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">`);
      const $$body = escape_html(formData.description);
      if ($$body) {
        $$renderer2.push(`${$$body}`);
      }
      $$renderer2.push(`</textarea></div> <div><label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Call Script</label> <textarea placeholder="Enter the script for agents to follow" rows="4" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">`);
      const $$body_1 = escape_html(formData.script);
      if ($$body_1) {
        $$renderer2.push(`${$$body_1}`);
      }
      $$renderer2.push(`</textarea></div> <div class="grid grid-cols-2 gap-4"><div><label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Priority</label> `);
      $$renderer2.select(
        {
          value: formData.priority,
          class: "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
        },
        ($$renderer3) => {
          $$renderer3.option({ value: "low" }, ($$renderer4) => {
            $$renderer4.push(`Low`);
          });
          $$renderer3.option({ value: "medium" }, ($$renderer4) => {
            $$renderer4.push(`Medium`);
          });
          $$renderer3.option({ value: "high" }, ($$renderer4) => {
            $$renderer4.push(`High`);
          });
        }
      );
      $$renderer2.push(`</div> <div><label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Target Calls/Day</label> <input type="number"${attr("value", formData.targetCallsPerDay)} class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"/></div></div> <div class="grid grid-cols-2 gap-4"><div><label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Start Date</label> <input type="date"${attr("value", formData.startDate)} class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"/></div> <div><label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">End Date</label> <input type="date"${attr("value", formData.endDate)} class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"/></div></div></div> <div class="flex gap-2 justify-end mt-6">`);
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
        disabled: !formData.name,
        children: ($$renderer3) => {
          $$renderer3.push(`<!---->Create Campaign`);
        }
      });
      $$renderer2.push(`<!----></div></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (showEditModal && selectedCampaign) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"><div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto"><h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Edit Campaign</h3> <div class="space-y-4"><div><label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Campaign Name *</label> <input type="text"${attr("value", formData.name)} class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"/></div> <div><label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label> <textarea rows="3" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">`);
      const $$body_2 = escape_html(formData.description);
      if ($$body_2) {
        $$renderer2.push(`${$$body_2}`);
      }
      $$renderer2.push(`</textarea></div></div> <div class="flex gap-2 justify-end mt-6">`);
      Button($$renderer2, {
        variant: "secondary",
        onclick: () => {
          showEditModal = false;
          resetForm();
          selectedCampaign = null;
        },
        children: ($$renderer3) => {
          $$renderer3.push(`<!---->Cancel`);
        }
      });
      $$renderer2.push(`<!----> `);
      Button($$renderer2, {
        variant: "primary",
        onclick: handleUpdate,
        disabled: !formData.name,
        children: ($$renderer3) => {
          $$renderer3.push(`<!---->Save Changes`);
        }
      });
      $$renderer2.push(`<!----></div></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (showDeleteModal && selectedCampaign) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"><div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4"><h3 class="text-lg font-bold text-red-600 mb-4">Delete Campaign</h3> <p class="text-gray-700 dark:text-gray-300 mb-4">Are you sure you want to delete the campaign "${escape_html(selectedCampaign.name)}"?</p> <p class="text-sm text-gray-500 dark:text-gray-400">This action cannot be undone. All associated data will be permanently removed.</p> <div class="flex gap-2 justify-end mt-6">`);
      Button($$renderer2, {
        variant: "secondary",
        onclick: () => {
          showDeleteModal = false;
          selectedCampaign = null;
        },
        children: ($$renderer3) => {
          $$renderer3.push(`<!---->Cancel`);
        }
      });
      $$renderer2.push(`<!----> `);
      Button($$renderer2, {
        variant: "danger",
        onclick: handleDelete,
        children: ($$renderer3) => {
          $$renderer3.push(`<!---->Delete`);
        }
      });
      $$renderer2.push(`<!----></div></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
  });
}
function _page($$renderer) {
  $$renderer.push(`<div class="space-y-6"><div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6"><h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Campaign Management</h1> <p class="text-gray-600 dark:text-gray-400">Manage all outbound calling campaigns from this central dashboard.</p></div> `);
  CampaignManagement($$renderer);
  $$renderer.push(`<!----></div>`);
}
export {
  _page as default
};
