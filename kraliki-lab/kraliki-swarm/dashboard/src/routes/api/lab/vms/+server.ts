import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

interface VM {
	id: string;
	hostname: string;
	ip_address: string;
	customer_id: string;
	tier: string;
	status: string;
	cpu_cores: number;
	memory_gb: number;
	disk_gb: number;
	version: string;
	last_heartbeat?: string;
}

const mockVMs: VM[] = [
	{
		id: 'vm-001',
		hostname: 'lab-kraliki-customer1',
		ip_address: '10.0.0.1',
		customer_id: 'cust-001',
		tier: 'starter',
		status: 'online',
		cpu_cores: 2,
		memory_gb: 4,
		disk_gb: 40,
		version: '1.0.0',
		last_heartbeat: new Date().toISOString()
	},
	{
		id: 'vm-002',
		hostname: 'lab-kraliki-customer2',
		ip_address: '10.0.0.2',
		customer_id: 'cust-002',
		tier: 'professional',
		status: 'online',
		cpu_cores: 4,
		memory_gb: 8,
		disk_gb: 80,
		version: '1.0.0',
		last_heartbeat: new Date().toISOString()
	},
	{
		id: 'vm-003',
		hostname: 'lab-kraliki-customer3',
		ip_address: '10.0.0.3',
		customer_id: 'cust-003',
		tier: 'enterprise',
		status: 'offline',
		cpu_cores: 8,
		memory_gb: 16,
		disk_gb: 160,
		version: '1.0.0',
		last_heartbeat: new Date(Date.now() - 3600000).toISOString()
	}
];

export const GET: RequestHandler = async () => {
	return json(mockVMs);
};
