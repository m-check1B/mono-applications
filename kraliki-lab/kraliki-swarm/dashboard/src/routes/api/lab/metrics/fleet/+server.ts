import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

interface FleetMetrics {
	total_vms: number;
	total_customers: number;
	online_vms: number;
	offline_vms: number;
	monthly_revenue: number;
	monthly_cost: number;
	avg_cpu: number;
	avg_memory: number;
	alerts_count: number;
}

const mockFleetMetrics: FleetMetrics = {
	total_vms: 3,
	total_customers: 3,
	online_vms: 2,
	offline_vms: 1,
	monthly_revenue: 309.97,
	monthly_cost: 180.00,
	avg_cpu: 45.2,
	avg_memory: 62.8,
	alerts_count: 3
};

export const GET: RequestHandler = async () => {
	return json(mockFleetMetrics);
};
