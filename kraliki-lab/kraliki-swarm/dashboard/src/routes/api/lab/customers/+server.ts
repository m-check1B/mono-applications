import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

interface Customer {
	id: string;
	name: string;
	email: string;
	company?: string;
	tier: string;
	billing_status: string;
	monthly_fee: number;
}

const mockCustomers: Customer[] = [
	{
		id: 'cust-001',
		name: 'John Smith',
		email: 'john@company1.com',
		company: 'Company One',
		tier: 'starter',
		billing_status: 'active',
		monthly_fee: 29.99
	},
	{
		id: 'cust-002',
		name: 'Jane Doe',
		email: 'jane@company2.com',
		company: 'Company Two',
		tier: 'professional',
		billing_status: 'active',
		monthly_fee: 79.99
	},
	{
		id: 'cust-003',
		name: 'Bob Johnson',
		email: 'bob@company3.com',
		company: 'Company Three',
		tier: 'enterprise',
		billing_status: 'active',
		monthly_fee: 199.99
	}
];

export const GET: RequestHandler = async () => {
	return json(mockCustomers);
};
