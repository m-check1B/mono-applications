import { c as attr, e as ensure_array_like, d as attr_class, f as stringify } from "../../../../chunks/index2.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let recordings = [];
    let loading = true;
    let error = "";
    let selectedStatus = "";
    let selectedAgent = null;
    let searchQuery = "";
    const statusColors = {
      pending: "bg-gray-100 text-gray-800",
      recording: "bg-blue-100 text-blue-800",
      processing: "bg-yellow-100 text-yellow-800",
      completed: "bg-green-100 text-green-800",
      failed: "bg-red-100 text-red-800",
      deleted: "bg-gray-100 text-gray-600"
    };
    async function loadRecordings() {
      try {
        const token = localStorage.getItem("token");
        const params = new URLSearchParams();
        if (selectedStatus) ;
        if (selectedAgent) ;
        const response = await fetch(`http://localhost:8000/api/recordings?${params}`, {
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
          }
        });
        if (!response.ok) throw new Error("Failed to load recordings");
        recordings = await response.json();
        loading = false;
      } catch (e) {
        error = e instanceof Error ? e.message : "Failed to load recordings";
        loading = false;
      }
    }
    function formatDuration(seconds) {
      if (!seconds) return "N/A";
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${mins}:${secs.toString().padStart(2, "0")}`;
    }
    function formatFileSize(bytes) {
      if (!bytes) return "N/A";
      const mb = bytes / (1024 * 1024);
      return `${mb.toFixed(2)} MB`;
    }
    function formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    }
    $$renderer2.push(`<div class="container mx-auto px-4 py-8"><div class="mb-8"><h1 class="text-3xl font-bold text-gray-900 mb-2">Call Recordings</h1> <p class="text-gray-600">Manage and review call recordings</p></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="bg-white rounded-lg shadow mb-6 p-6"><div class="grid grid-cols-1 md:grid-cols-3 gap-4"><div><label class="block text-sm font-medium text-gray-700 mb-2">Status</label> `);
    $$renderer2.select(
      {
        value: selectedStatus,
        onchange: loadRecordings,
        class: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      },
      ($$renderer3) => {
        $$renderer3.option({ value: "" }, ($$renderer4) => {
          $$renderer4.push(`All Statuses`);
        });
        $$renderer3.option({ value: "pending" }, ($$renderer4) => {
          $$renderer4.push(`Pending`);
        });
        $$renderer3.option({ value: "recording" }, ($$renderer4) => {
          $$renderer4.push(`Recording`);
        });
        $$renderer3.option({ value: "processing" }, ($$renderer4) => {
          $$renderer4.push(`Processing`);
        });
        $$renderer3.option({ value: "completed" }, ($$renderer4) => {
          $$renderer4.push(`Completed`);
        });
        $$renderer3.option({ value: "failed" }, ($$renderer4) => {
          $$renderer4.push(`Failed`);
        });
      }
    );
    $$renderer2.push(`</div> <div><label class="block text-sm font-medium text-gray-700 mb-2">Search</label> <input type="text"${attr("value", searchQuery)} placeholder="Search by call SID or phone..." class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"/></div> <div class="flex items-end"><button class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">Refresh</button></div></div></div> <div class="bg-white rounded-lg shadow overflow-hidden">`);
    if (loading) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="p-8 text-center text-gray-500"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div> Loading recordings...</div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (error) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="p-8 text-center text-red-600"><p class="text-lg font-semibold mb-2">Error</p> <p>${escape_html(error)}</p></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        if (recordings.length === 0) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="p-8 text-center text-gray-500"><p class="text-lg mb-2">No recordings found</p> <p class="text-sm">Recordings will appear here once calls are recorded</p></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
          $$renderer2.push(`<div class="overflow-x-auto"><table class="min-w-full divide-y divide-gray-200"><thead class="bg-gray-50"><tr><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Call SID</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Caller</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Size</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th></tr></thead><tbody class="bg-white divide-y divide-gray-200"><!--[-->`);
          const each_array = ensure_array_like(recordings);
          for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
            let recording = each_array[$$index];
            $$renderer2.push(`<tr class="hover:bg-gray-50"><td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${escape_html(recording.call_sid)}</td><td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${escape_html(recording.caller_phone || "Unknown")}</td><td class="px-6 py-4 whitespace-nowrap"><span${attr_class(`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${stringify(statusColors[recording.status] || "bg-gray-100 text-gray-800")}`)}>${escape_html(recording.status)}</span></td><td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${escape_html(formatDuration(recording.duration_seconds))}</td><td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${escape_html(formatFileSize(recording.file_size_bytes))}</td><td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${escape_html(formatDate(recording.started_at))}</td><td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">`);
            if (recording.status === "completed") {
              $$renderer2.push("<!--[-->");
              $$renderer2.push(`<button class="text-blue-600 hover:text-blue-900">Download</button> `);
              if (recording.has_transcription) {
                $$renderer2.push("<!--[-->");
                $$renderer2.push(`<button class="text-green-600 hover:text-green-900">Transcript</button>`);
              } else {
                $$renderer2.push("<!--[!-->");
              }
              $$renderer2.push(`<!--]-->`);
            } else {
              $$renderer2.push("<!--[!-->");
            }
            $$renderer2.push(`<!--]--></td></tr>`);
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
