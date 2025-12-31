import { json } from "@sveltejs/kit";
const mockFleetMetrics = {
  total_vms: 3,
  total_customers: 3,
  online_vms: 2,
  offline_vms: 1,
  monthly_revenue: 309.97,
  monthly_cost: 180,
  avg_cpu: 45.2,
  avg_memory: 62.8,
  alerts_count: 3
};
const GET = async () => {
  return json(mockFleetMetrics);
};
export {
  GET
};
