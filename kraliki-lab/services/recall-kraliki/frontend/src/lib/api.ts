/**
 * API client for recall-kraliki backend
 */

const API_BASE = 'http://127.0.0.1:3020/api';

export interface SearchRequest {
	query: string;
	category?: string;
	tags?: string[];
	limit?: number;
	search_type?: 'keyword' | 'semantic' | 'hybrid';
}

export interface SearchResult {
	id: string;
	category: string;
	title: string;
	content: string;
	tags: string[];
	score: number;
	file_path: string;
}

export interface CaptureRequest {
	content: string;
	category?: string;
	tags?: string[];
	metadata?: Record<string, any>;
	auto_categorize?: boolean;
	auto_link?: boolean;
}

export interface CaptureResponse {
	id: string;
	category: string;
	tags: string[];
	wikilinks: string[];
	related_items: string[];
	file_path: string;
}

export interface MemoryItem {
	id: string;
	category: string;
	title: string;
	content: string;
	tags: string[];
	file_path: string;
	wikilinks?: string[];
	related?: string[];
}

/**
 * Search memory items
 */
export async function searchItems(request: SearchRequest) {
	const response = await fetch(`${API_BASE}/search`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(request)
	});

	if (!response.ok) {
		throw new Error(`Search failed: ${response.statusText}`);
	}

	return await response.json();
}

/**
 * Capture new memory item
 */
export async function captureItem(request: CaptureRequest): Promise<CaptureResponse> {
	const response = await fetch(`${API_BASE}/capture`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(request)
	});

	if (!response.ok) {
		throw new Error(`Capture failed: ${response.statusText}`);
	}

	return await response.json();
}

/**
 * Get specific memory item
 */
export async function getItem(category: string, itemId: string): Promise<MemoryItem> {
	const response = await fetch(`${API_BASE}/capture/${category}/${itemId}`);

	if (!response.ok) {
		throw new Error(`Failed to get item: ${response.statusText}`);
	}

	return await response.json();
}

/**
 * Get recent memory items
 */
export async function getRecentItems(category?: string, limit: number = 20) {
	const params = new URLSearchParams();
	if (category) params.append('category', category);
	params.append('limit', limit.toString());

	const response = await fetch(`${API_BASE}/capture/recent?${params}`);

	if (!response.ok) {
		throw new Error(`Failed to get recent items: ${response.statusText}`);
	}

	return await response.json();
}

/**
 * Get available categories
 */
export async function getCategories() {
	const response = await fetch(`${API_BASE}/capture/categories`);

	if (!response.ok) {
		throw new Error(`Failed to get categories: ${response.statusText}`);
	}

	return await response.json();
}

/**
 * Get knowledge graph data
 */
export async function getGraph(
	category?: string,
	tag?: string,
	depth: number = 2,
	limit: number = 100
) {
	const params = new URLSearchParams();
	if (category) params.append('category', category);
	if (tag) params.append('tag', tag);
	params.append('depth', depth.toString());
	params.append('limit', limit.toString());

	const response = await fetch(`${API_BASE}/graph?${params}`);

	if (!response.ok) {
		throw new Error(`Failed to get graph: ${response.statusText}`);
	}

	return await response.json();
}

/**
 * Detect patterns
 */
export async function detectPatterns(category?: string, limit: number = 100) {
	const params = new URLSearchParams();
	if (category) params.append('category', category);
	params.append('limit', limit.toString());

	const response = await fetch(`${API_BASE}/graph/patterns?${params}`);

	if (!response.ok) {
		throw new Error(`Failed to detect patterns: ${response.statusText}`);
	}

	return await response.json();
}
