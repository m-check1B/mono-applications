import { json } from "@sveltejs/kit";
const ESPO_URL = "http://127.0.0.1:8080";
const ESPO_USER = process.env.ESPOCRM_ADMIN_USERNAME || "admin";
const ESPO_PASS = process.env.ESPOCRM_ADMIN_PASSWORD || "l2XYNO0UDMDhNazDKgEk";
const ESPO_AUTH = Buffer.from(`${ESPO_USER}:${ESPO_PASS}`).toString("base64");
async function fetchEspo(endpoint) {
  try {
    const response = await fetch(`${ESPO_URL}/api/v1/${endpoint}`, {
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": `Basic ${ESPO_AUTH}`,
        "Espo-Authorization": ESPO_AUTH
      }
    });
    if (!response.ok) {
      return null;
    }
    return await response.json();
  } catch (e) {
    console.error(`CRM API error for ${endpoint}:`, e);
    return null;
  }
}
async function getStats() {
  const [contacts, leads, opportunities, accounts, tasks, meetings] = await Promise.all([
    fetchEspo("Contact?select=id&maxSize=1"),
    fetchEspo("Lead?select=id&maxSize=1"),
    fetchEspo("Opportunity?select=id&maxSize=1"),
    fetchEspo("Account?select=id&maxSize=1"),
    fetchEspo("Task?select=id&maxSize=1"),
    fetchEspo("Meeting?select=id&maxSize=1")
  ]);
  return {
    contacts: contacts?.total || 0,
    leads: leads?.total || 0,
    opportunities: opportunities?.total || 0,
    accounts: accounts?.total || 0,
    tasks: tasks?.total || 0,
    meetings: meetings?.total || 0
  };
}
async function getRecentLeads() {
  const data = await fetchEspo("Lead?orderBy=createdAt&order=desc&maxSize=10");
  if (!data?.list) return [];
  return data.list.map((lead) => ({
    id: lead.id,
    name: lead.name,
    status: lead.status,
    source: lead.source,
    createdAt: lead.createdAt,
    assignedUserName: lead.assignedUserName
  }));
}
async function getOpenOpportunities() {
  const data = await fetchEspo("Opportunity?where[0][type]=notEquals&where[0][attribute]=stage&where[0][value]=Closed%20Won&where[1][type]=notEquals&where[1][attribute]=stage&where[1][value]=Closed%20Lost&orderBy=closeDate&order=asc&maxSize=10");
  if (!data?.list) return [];
  return data.list.map((opp) => ({
    id: opp.id,
    name: opp.name,
    stage: opp.stage,
    amount: opp.amount || 0,
    probability: opp.probability || 0,
    accountName: opp.accountName,
    closeDate: opp.closeDate
  }));
}
async function getPendingTasks() {
  const data = await fetchEspo("Task?where[0][type]=notEquals&where[0][attribute]=status&where[0][value]=Completed&orderBy=dateEnd&order=asc&maxSize=10");
  if (!data?.list) return [];
  return data.list.map((task) => ({
    id: task.id,
    name: task.name,
    status: task.status,
    priority: task.priority || "Normal",
    dateEnd: task.dateEnd,
    parentType: task.parentType,
    parentName: task.parentName
  }));
}
const GET = async () => {
  try {
    const healthCheck = await fetch(`${ESPO_URL}/api/v1/App/user`, {
      headers: {
        "Authorization": `Basic ${ESPO_AUTH}`,
        "Espo-Authorization": ESPO_AUTH
      }
    }).catch(() => null);
    const isOnline = healthCheck?.ok || false;
    if (!isOnline) {
      const serverCheck = await fetch(`${ESPO_URL}/api/v1/App/user`).catch(() => null);
      const serverResponds = serverCheck !== null;
      return json({
        online: false,
        stats: null,
        leads: [],
        opportunities: [],
        tasks: [],
        lastUpdated: (/* @__PURE__ */ new Date()).toISOString(),
        error: serverResponds ? "EspoCRM authentication failed" : "EspoCRM is not running or not accessible"
      });
    }
    const [stats, leads, opportunities, tasks] = await Promise.all([
      getStats(),
      getRecentLeads(),
      getOpenOpportunities(),
      getPendingTasks()
    ]);
    return json({
      online: true,
      stats,
      leads,
      opportunities,
      tasks,
      lastUpdated: (/* @__PURE__ */ new Date()).toISOString()
    });
  } catch (e) {
    console.error("CRM API error:", e);
    return json({
      online: false,
      stats: null,
      leads: [],
      opportunities: [],
      tasks: [],
      lastUpdated: (/* @__PURE__ */ new Date()).toISOString(),
      error: e instanceof Error ? e.message : "Unknown error"
    }, { status: 500 });
  }
};
export {
  GET
};
