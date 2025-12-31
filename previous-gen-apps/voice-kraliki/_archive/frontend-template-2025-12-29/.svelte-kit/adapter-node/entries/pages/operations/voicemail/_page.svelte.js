import { c as attr, e as ensure_array_like, d as attr_class, f as stringify } from "../../../../chunks/index2.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let voicemails = [];
    let loading = true;
    let error = "";
    let selectedStatus = "";
    let currentAgentId = 1;
    let selectedVoicemails = /* @__PURE__ */ new Set();
    const statusColors = {
      new: "bg-blue-100 text-blue-800 font-semibold",
      heard: "bg-gray-100 text-gray-800",
      saved: "bg-green-100 text-green-800",
      archived: "bg-yellow-100 text-yellow-800",
      deleted: "bg-red-100 text-red-600"
    };
    const priorityIcons = {
      1: "⚠️"
      // Urgent
    };
    async function loadVoicemails() {
      try {
        const token = localStorage.getItem("token");
        const params = new URLSearchParams({ agent_id: currentAgentId.toString() });
        if (selectedStatus) ;
        const response = await fetch(`http://localhost:8000/api/voicemails?${params}`, {
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
          }
        });
        if (!response.ok) throw new Error("Failed to load voicemails");
        voicemails = await response.json();
        loading = false;
      } catch (e) {
        error = e instanceof Error ? e.message : "Failed to load voicemails";
        loading = false;
      }
    }
    function formatDuration(seconds) {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${mins}:${secs.toString().padStart(2, "0")}`;
    }
    function formatDate(dateString) {
      const date = new Date(dateString);
      const now = /* @__PURE__ */ new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 6e4);
      if (diffMins < 60) return `${diffMins}m ago`;
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) return `${diffHours}h ago`;
      const diffDays = Math.floor(diffHours / 24);
      if (diffDays < 7) return `${diffDays}d ago`;
      return date.toLocaleDateString();
    }
    $$renderer2.push(`<div class="container mx-auto px-4 py-8"><div class="mb-8"><h1 class="text-3xl font-bold text-gray-900 mb-2">Voicemail Inbox</h1> <p class="text-gray-600">Manage your voicemail messages</p></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="bg-white rounded-lg shadow mb-6 p-6"><div class="flex flex-wrap items-center gap-4"><div class="flex-1">`);
    $$renderer2.select(
      {
        value: selectedStatus,
        onchange: loadVoicemails,
        class: "w-full md:w-auto px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      },
      ($$renderer3) => {
        $$renderer3.option({ value: "" }, ($$renderer4) => {
          $$renderer4.push(`All Messages`);
        });
        $$renderer3.option({ value: "new" }, ($$renderer4) => {
          $$renderer4.push(`New`);
        });
        $$renderer3.option({ value: "heard" }, ($$renderer4) => {
          $$renderer4.push(`Heard`);
        });
        $$renderer3.option({ value: "saved" }, ($$renderer4) => {
          $$renderer4.push(`Saved`);
        });
        $$renderer3.option({ value: "archived" }, ($$renderer4) => {
          $$renderer4.push(`Archived`);
        });
      }
    );
    $$renderer2.push(`</div> `);
    if (selectedVoicemails.size > 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="flex gap-2"><button class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">Mark as Heard</button> <button class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">Save</button> <button class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors">Archive</button></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <button class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">Refresh</button></div></div> <div class="bg-white rounded-lg shadow overflow-hidden">`);
    if (loading) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="p-8 text-center text-gray-500"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div> Loading voicemails...</div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (error) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="p-8 text-center text-red-600"><p class="text-lg font-semibold mb-2">Error</p> <p>${escape_html(error)}</p></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        if (voicemails.length === 0) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="p-8 text-center text-gray-500"><p class="text-lg mb-2">No voicemails</p> <p class="text-sm">Your voicemail inbox is empty</p></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
          $$renderer2.push(`<div class="overflow-x-auto"><table class="min-w-full divide-y divide-gray-200"><thead class="bg-gray-50"><tr><th class="px-6 py-3 text-left"><input type="checkbox"${attr("checked", selectedVoicemails.size === voicemails.length, true)} class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"/></th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">From</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Received</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th></tr></thead><tbody class="bg-white divide-y divide-gray-200"><!--[-->`);
          const each_array = ensure_array_like(voicemails);
          for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
            let voicemail = each_array[$$index];
            $$renderer2.push(`<tr${attr_class(`hover:bg-gray-50 ${stringify(voicemail.status === "new" ? "bg-blue-50" : "")}`)}><td class="px-6 py-4 whitespace-nowrap"><input type="checkbox"${attr("checked", selectedVoicemails.has(voicemail.id), true)} class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"/></td><td class="px-6 py-4 whitespace-nowrap"><div class="flex items-center">`);
            if (voicemail.priority === 1) {
              $$renderer2.push("<!--[-->");
              $$renderer2.push(`<span class="mr-2">${escape_html(priorityIcons[1])}</span>`);
            } else {
              $$renderer2.push("<!--[!-->");
            }
            $$renderer2.push(`<!--]--> <div><div class="text-sm font-medium text-gray-900">${escape_html(voicemail.caller_name || "Unknown")}</div> <div class="text-sm text-gray-500">${escape_html(voicemail.caller_phone)}</div></div></div></td><td class="px-6 py-4 whitespace-nowrap"><span${attr_class(`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${stringify(statusColors[voicemail.status] || "bg-gray-100 text-gray-800")}`)}>${escape_html(voicemail.status)}</span> `);
            if (voicemail.has_transcription) {
              $$renderer2.push("<!--[-->");
              $$renderer2.push(`<span class="ml-2" title="Has transcript">📝</span>`);
            } else {
              $$renderer2.push("<!--[!-->");
            }
            $$renderer2.push(`<!--]--></td><td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${escape_html(formatDuration(voicemail.recording_duration_seconds))}</td><td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${escape_html(formatDate(voicemail.created_at))}</td><td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2"><button class="text-blue-600 hover:text-blue-900">▶ Play</button> `);
            if (voicemail.has_transcription) {
              $$renderer2.push("<!--[-->");
              $$renderer2.push(`<button class="text-green-600 hover:text-green-900">Transcript</button>`);
            } else {
              $$renderer2.push("<!--[!-->");
            }
            $$renderer2.push(`<!--]--> <button class="text-red-600 hover:text-red-900">Delete</button></td></tr>`);
          }
          $$renderer2.push(`<!--]--></tbody></table></div>`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div></div>`);
  });
}
export {
  _page as default
};
