export interface BusinessRequest {
	company_name: string;
	website?: string;
	country?: string;
	industry?: string;
	employees?: string;
	contact_name: string;
	contact_role?: string;
	email: string;
	consent_marketing: boolean;
	priority_sales: boolean;
	priority_support: boolean;
	priority_operations: boolean;
	priority_finance: boolean;
	priority_hr: boolean;
	q1: number;
	q2: number;
	q3: number;
	q4: number;
	q5: number;
	q6: number;
	q7: number;
	q8: number;
	q9: number;
	q10: number;
	q11: number;
	q12: number;
}

export interface BusinessResponse {
	total_score: number;
	bucket: 'low' | 'medium' | 'high';
	title: string;
	recommendation: string;
	priorities: string[];
}

export interface HumanRequest {
	name: string;
	email: string;
	country?: string;
	city?: string;
	role?: string;
	languages?: string;
	interest_operations: boolean;
	interest_sales: boolean;
	interest_marketing: boolean;
	interest_tech: boolean;
	interest_other: boolean;
	consent_marketing: boolean;
	hq1: number;
	hq2: number;
	hq3: number;
	hq4: number;
	hq5: number;
	hq6: number;
	hq7: number;
	hq8: number;
	hq9: number;
	hq10: number;
}

export interface HumanResponse {
	total_score: number;
	bucket: 'low' | 'medium' | 'high';
	title: string;
	recommendation: string;
	interests: string[];
}

export async function submitBusiness(request: BusinessRequest): Promise<BusinessResponse> {
	const response = await fetch('/api/business', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(request)
	});

	if (!response.ok) {
		throw new Error(`Business test failed: ${response.statusText}`);
	}

	return (await response.json()) as BusinessResponse;
}

export async function submitHuman(request: HumanRequest): Promise<HumanResponse> {
	const response = await fetch('/api/human', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(request)
	});

	if (!response.ok) {
		throw new Error(`Human test failed: ${response.statusText}`);
	}

	return (await response.json()) as HumanResponse;
}

