import { json } from "@sveltejs/kit";
const mockAlerts = [
  {
    id: "alert-001",
    vm_id: "vm-003",
    customer_id: "cust-003",
    type: "vm_offline",
    severity: "high",
    message: "VM lab-kraliki-customer3 has been offline for 1 hour",
    created_at: new Date(Date.now() - 36e5).toISOString(),
    resolved: false
  },
  {
    id: "alert-002",
    vm_id: "vm-001",
    customer_id: "cust-001",
    type: "disk_space",
    severity: "warning",
    message: "VM lab-kraliki-customer1 disk usage at 85%",
    created_at: new Date(Date.now() - 72e5).toISOString(),
    resolved: false
  },
  {
    id: "alert-003",
    type: "api_quota",
    severity: "info",
    message: "Fleet-wide API quota usage at 75%",
    created_at: new Date(Date.now() - 18e5).toISOString(),
    resolved: false
  }
];
const GET = async ({ url }) => {
  const resolvedParam = url.searchParams.get("resolved");
  const resolvedOnly = resolvedParam === "true";
  const unresolvedOnly = resolvedParam === "false";
  let alerts = mockAlerts;
  if (resolvedOnly) {
    alerts = alerts.filter((a) => a.resolved);
  } else if (unresolvedOnly) {
    alerts = alerts.filter((a) => !a.resolved);
  }
  return json(alerts);
};
export {
  GET
};
